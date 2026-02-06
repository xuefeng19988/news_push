#!/usr/bin/env python3
"""
实时监控仪表板
提供文本格式的系统状态监控面板，适合消息推送
"""

import time
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from monitoring.health_check import HealthChecker
    from utils.logger import Logger
except ImportError as e:
    print(f"[Dashboard] 导入模块失败: {e}")
    # 创建简单的替代类
    class HealthChecker:
        def check_all(self):
            return {"overall_status": "unknown", "checks": {}}
    
    class Logger:
        def __init__(self, name):
            self.name = name
        
        def info(self, msg):
            print(f"[{self.name}] INFO: {msg}")


class MonitorDashboard:
    """监控仪表板"""
    
    def __init__(self):
        self.health_checker = HealthChecker()
        self.logger = Logger(__name__)
        self.history = []  # 历史记录，用于趋势分析
        self.max_history = 24  # 保存24次检查记录
        
        self.logger.info("监控仪表板初始化")
    
    def generate_dashboard(self, quick_mode: bool = False) -> str:
        """
        生成监控仪表板
        
        Args:
            quick_mode: 是否使用快速模式（跳过新闻源检查）
            
        Returns:
            仪表板文本
        """
        try:
            start_time = time.time()
            
            # 执行健康检查
            if quick_mode:
                try:
                    # 尝试使用快速检查方法
                    report = self.health_checker.check_quick()
                except AttributeError:
                    # 如果快速检查方法不存在，回退到完整检查
                    report = self.health_checker.check_all()
            else:
                report = self.health_checker.check_all()
            
            # 执行增强版系统资源检查
            enhanced_result = self.health_checker.check_system_resources_enhanced()
            
            # 保存到历史
            self._add_to_history(report, enhanced_result)
            
            # 生成仪表板
            dashboard = self._create_dashboard_content(report, enhanced_result, time.time() - start_time)
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"生成仪表板失败: {e}")
            return self._create_error_dashboard(str(e))
    
    def _create_dashboard_content(self, report: Dict[str, Any], 
                                 enhanced_result: Dict[str, Any],
                                 check_time: float) -> str:
        """创建仪表板内容"""
        overall_status = report.get('overall_status', 'unknown')
        timestamp = datetime.now()
        
        # 基础仪表板
        dashboard = "📊 智能新闻推送系统 - 实时监控仪表板\n"
        dashboard += "=" * 60 + "\n"
        dashboard += f"🕐 时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        dashboard += f"📈 状态: {self._get_status_emoji(overall_status)} {overall_status}\n"
        dashboard += f"⏱️  检查耗时: {check_time:.2f}秒\n\n"
        
        # 1. 系统资源部分
        dashboard += self._create_system_resources_section(enhanced_result)
        dashboard += "\n"
        
        # 2. 组件状态部分
        dashboard += self._create_components_section(report)
        dashboard += "\n"
        
        # 3. 趋势分析部分（如果有历史数据）
        if len(self.history) >= 2:
            dashboard += self._create_trends_section()
            dashboard += "\n"
        
        # 4. 最近问题部分
        dashboard += self._create_issues_section(report)
        dashboard += "\n"
        
        # 5. 建议部分
        dashboard += self._create_recommendations_section(report, enhanced_result)
        
        dashboard += "=" * 60 + "\n"
        dashboard += "💡 提示: 系统每小时自动检查一次，关键问题会立即通知\n"
        
        return dashboard
    
    def _create_system_resources_section(self, enhanced_result: Dict[str, Any]) -> str:
        """创建系统资源部分"""
        section = "🖥️ 系统资源状态:\n"
        
        if enhanced_result.get('status') == 'healthy' and 'metrics' in enhanced_result:
            metrics = enhanced_result['metrics']
            
            # CPU信息
            if 'cpu' in metrics:
                cpu = metrics['cpu']
                cpu_usage = cpu.get('percent', 0)
                cpu_cores = cpu.get('count', '?')
                section += f"  • CPU: {cpu_usage}% ({cpu_cores}核)\n"
            
            # 内存信息
            if 'memory' in metrics:
                memory = metrics['memory']
                mem_usage = memory.get('percent', 0)
                mem_used = memory.get('used_gb', 0)
                mem_total = memory.get('total_gb', 0)
                section += f"  • 内存: {mem_usage}% ({mem_used:.1f}/{mem_total:.1f}GB)\n"
            
            # 磁盘信息
            if 'disk' in metrics:
                disk = metrics['disk']
                disk_usage = disk.get('project_path_percent', 0)
                disk_free = disk.get('project_free_gb', 0)
                section += f"  • 磁盘: {disk_usage}% (剩余 {disk_free:.1f}GB)\n"
            
            # 负载信息
            if 'load' in metrics:
                load = metrics['load']
                load_1min = load.get('1min', 0)
                load_5min = load.get('5min', 0)
                load_15min = load.get('15min', 0)
                section += f"  • 负载: {load_1min:.2f} ({load_5min:.2f}, {load_15min:.2f})\n"
            
            # 警告和严重问题
            details = enhanced_result.get('details', {})
            warnings = details.get('warnings', [])
            criticals = details.get('criticals', [])
            
            if criticals:
                section += f"  ⚠️  严重问题: {len(criticals)}个\n"
            elif warnings:
                section += f"  ⚠️  警告: {len(warnings)}个\n"
            else:
                section += "  ✅ 资源状态正常\n"
        else:
            section += "  ❓ 无法获取系统资源信息\n"
        
        return section
    
    def _create_components_section(self, report: Dict[str, Any]) -> str:
        """创建组件状态部分"""
        section = "🔧 系统组件状态:\n"
        
        checks = report.get('checks', {})
        
        # 定义组件显示顺序和友好名称
        component_order = [
            ('database', '数据库'),
            ('news_sources', '新闻源'),
            ('message_platforms', '消息平台'),
            ('system_resources', '系统资源')
        ]
        
        for check_id, friendly_name in component_order:
            if check_id in checks:
                check_result = checks[check_id]
                status = check_result.get('status', 'unknown')
                emoji = self._get_status_emoji(status)
                
                # 获取详细信息
                details = check_result.get('details', {})
                
                section += f"  {emoji} {friendly_name}: {status}"
                
                # 添加简要信息
                if check_id == 'news_sources' and 'working_count' in details:
                    working = details.get('working_count', 0)
                    total = details.get('total_count', 0)
                    section += f" ({working}/{total}个可用)"
                elif check_id == 'database' and 'error' not in details:
                    section += " (连接正常)"
                elif 'error' in details:
                    error_msg = details['error'][:30] + '...' if len(details['error']) > 30 else details['error']
                    section += f" ({error_msg})"
                
                section += "\n"
        
        # 统计状态
        status_counts = report.get('status_counts', {})
        healthy = status_counts.get('healthy', 0)
        total_components = sum(status_counts.values())
        
        if total_components > 0:
            health_percentage = (healthy / total_components) * 100
            section += f"  📊 健康度: {health_percentage:.1f}% ({healthy}/{total_components}个组件)\n"
        
        return section
    
    def _create_trends_section(self) -> str:
        """创建趋势分析部分"""
        if len(self.history) < 2:
            return ""
        
        section = "📈 趋势分析:\n"
        
        # 分析最近的健康状态变化
        recent_history = self.history[-min(6, len(self.history)):]  # 最近6次
        
        status_changes = []
        last_status = None
        
        for record in recent_history:
            timestamp = record.get('timestamp')
            status = record.get('overall_status', 'unknown')
            
            if last_status is None:
                last_status = status
            elif status != last_status:
                # 状态变化
                time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M')
                status_changes.append(f"{time_str}: {last_status}→{status}")
                last_status = status
        
        if status_changes:
            section += "  • 最近状态变化:\n"
            for change in status_changes[-3:]:  # 显示最近3次变化
                section += f"    - {change}\n"
        else:
            section += "  • 状态稳定，无变化\n"
        
        # 统计历史健康比例
        healthy_count = sum(1 for r in recent_history if r.get('overall_status') == 'healthy')
        total_count = len(recent_history)
        
        if total_count > 0:
            health_rate = (healthy_count / total_count) * 100
            section += f"  • 近期健康率: {health_rate:.1f}% ({healthy_count}/{total_count}次)\n"
        
        return section
    
    def _create_issues_section(self, report: Dict[str, Any]) -> str:
        """创建问题部分"""
        section = "🚨 当前问题:\n"
        
        issues = []
        checks = report.get('checks', {})
        
        for check_id, check_result in checks.items():
            status = check_result.get('status', 'unknown')
            
            if status in ['warning', 'unhealthy']:
                component_name = check_result.get('component', check_id)
                details = check_result.get('details', {})
                
                if 'error' in details:
                    issues.append(f"  • {component_name}: {details['error']}")
                elif 'warnings' in details and details['warnings']:
                    for warning in details['warnings'][:2]:  # 最多显示2个警告
                        issues.append(f"  • {component_name}: {warning}")
                else:
                    issues.append(f"  • {component_name}: 状态异常 ({status})")
        
        if issues:
            for issue in issues[:3]:  # 最多显示3个问题
                section += issue + "\n"
            if len(issues) > 3:
                section += f"    ... 还有 {len(issues) - 3} 个问题\n"
        else:
            section += "  ✅ 未发现问题\n"
        
        return section
    
    def _create_recommendations_section(self, report: Dict[str, Any], 
                                       enhanced_result: Dict[str, Any]) -> str:
        """创建建议部分"""
        section = "💡 建议:\n"
        
        recommendations = []
        
        # 检查系统资源建议
        if enhanced_result.get('status') == 'healthy' and 'metrics' in enhanced_result:
            metrics = enhanced_result['metrics']
            
            # 内存建议
            if 'memory' in metrics:
                memory = metrics['memory']
                mem_percent = memory.get('percent', 0)
                
                if mem_percent > 80:
                    recommendations.append("内存使用率偏高，建议检查是否有内存泄漏")
                elif mem_percent > 90:
                    recommendations.append("内存使用率极高，建议立即优化")
            
            # 磁盘建议
            if 'disk' in metrics:
                disk = metrics['disk']
                disk_percent = disk.get('project_path_percent', 0)
                
                if disk_percent > 85:
                    recommendations.append("磁盘空间紧张，建议清理日志文件")
                elif disk_percent > 95:
                    recommendations.append("磁盘空间严重不足，需要立即处理")
        
        # 检查消息平台建议
        checks = report.get('checks', {})
        message_platforms = checks.get('message_platforms', {})
        
        if message_platforms.get('status') == 'warning':
            details = message_platforms.get('details', {})
            if 'error' in details and 'WeChat' in details['error']:
                recommendations.append("微信推送未配置，不影响核心功能")
        
        # 默认建议
        if not recommendations:
            recommendations.append("系统运行正常，继续保持")
            recommendations.append("建议定期检查日志和监控仪表板")
        
        for i, rec in enumerate(recommendations[:2], 1):  # 最多2条建议
            section += f"  {i}. {rec}\n"
        
        return section
    
    def _add_to_history(self, report: Dict[str, Any], enhanced_result: Dict[str, Any]):
        """添加到历史记录"""
        history_entry = {
            'timestamp': time.time(),
            'overall_status': report.get('overall_status', 'unknown'),
            'check_time': report.get('check_time_seconds', 0),
            'status_counts': report.get('status_counts', {}),
            'system_summary': enhanced_result.get('details', {}).get('summary', '')
        }
        
        self.history.append(history_entry)
        
        # 限制历史记录长度
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def _get_status_emoji(self, status: str) -> str:
        """获取状态对应的表情符号"""
        emoji_map = {
            'healthy': '✅',
            'warning': '⚠️',
            'unhealthy': '❌',
            'critical': '🛑',
            'unknown': '❓'
        }
        return emoji_map.get(status, '❓')
    
    def _create_error_dashboard(self, error_message: str) -> str:
        """创建错误仪表板"""
        dashboard = "❌ 监控仪表板生成失败\n"
        dashboard += "=" * 60 + "\n"
        dashboard += f"错误信息: {error_message}\n"
        dashboard += f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        dashboard += "=" * 60 + "\n"
        dashboard += "💡 建议检查监控系统配置和连接\n"
        return dashboard
    
    def generate_compact_dashboard(self) -> str:
        """
        生成简洁版仪表板（适合消息推送）
        
        Returns:
            简洁版仪表板文本
        """
        try:
            # 只执行增强版系统资源检查（更快）
            enhanced_result = self.health_checker.check_system_resources_enhanced()
            
            # 获取当前时间
            timestamp = datetime.now().strftime('%H:%M')
            
            # 生成简洁版
            dashboard = f"📊 {timestamp} 系统状态\n"
            
            if enhanced_result.get('status') == 'healthy' and 'metrics' in enhanced_result:
                metrics = enhanced_result['metrics']
                
                # CPU和内存
                cpu_percent = metrics.get('cpu', {}).get('percent', '?')
                mem_percent = metrics.get('memory', {}).get('percent', '?')
                disk_percent = metrics.get('disk', {}).get('project_path_percent', '?')
                
                dashboard += f"🖥️ CPU: {cpu_percent}% | 内存: {mem_percent}% | 磁盘: {disk_percent}%\n"
                
                # 简要状态
                details = enhanced_result.get('details', {})
                warnings = len(details.get('warnings', []))
                criticals = len(details.get('criticals', []))
                
                if criticals > 0:
                    dashboard += f"🛑 {criticals}个严重问题\n"
                elif warnings > 0:
                    dashboard += f"⚠️  {warnings}个警告\n"
                else:
                    dashboard += "✅ 运行正常\n"
            else:
                dashboard += "❓ 状态未知\n"
            
            return dashboard
            
        except Exception as e:
            return f"❌ 状态检查失败: {str(e)[:50]}"


def test_dashboard():
    """测试仪表板"""
    print("🧪 测试监控仪表板")
    print("=" * 60)
    
    dashboard = MonitorDashboard()
    
    print("📊 生成完整仪表板...")
    full_dashboard = dashboard.generate_dashboard()
    print(full_dashboard)
    
    print("\n📱 生成简洁版仪表板...")
    compact_dashboard = dashboard.generate_compact_dashboard()
    print(compact_dashboard)
    
    print("\n✅ 监控仪表板测试完成")


if __name__ == "__main__":
    test_dashboard()
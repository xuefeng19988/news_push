#!/usr/bin/env python3
"""
增强版监控推送服务
包含告警升级管理和更智能的推送规则
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from monitoring.health_check import HealthChecker
    from monitoring.monitor_dashboard import MonitorDashboard
    from monitoring.alert_escalation import AlertEscalationManager, AlertSeverity
    from utils.logger import Logger
    from utils.message_sender import send_whatsapp_message
except ImportError as e:
    print(f"[MonitorPushEnhanced] 导入模块失败: {e}")
    # 创建简单的替代函数
    def send_whatsapp_message(message):
        print(f"[模拟发送] {message[:100]}...")
        return True
    
    class HealthChecker:
        def check_all(self):
            return {"overall_status": "unknown", "checks": {}}
    
    class MonitorDashboard:
        def generate_dashboard(self, quick_mode=False):
            return "📊 监控仪表板\n测试模式"
        
        def generate_compact_dashboard(self):
            return "📱 简洁仪表板"
    
    class AlertEscalationManager:
        def __init__(self, storage_file):
            pass
        def process_health_report(self, report):
            return []
        def generate_escalation_summary(self):
            return "📊 告警升级摘要\n测试模式"
    
    class Logger:
        def __init__(self, name):
            self.name = name
        
        def info(self, msg):
            print(f"[{self.name}] INFO: {msg}")
        
        def error(self, msg):
            print(f"[{self.name}] ERROR: {msg}")
        
        def warning(self, msg):
            print(f"[{self.name}] WARNING: {msg}")


class MonitorPushEnhanced:
    """增强版监控推送服务"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化增强版监控推送服务
        
        Args:
            config_dir: 配置目录路径
        """
        self.config_dir = config_dir
        self.health_checker = HealthChecker(config_dir)
        self.dashboard = MonitorDashboard()
        self.alert_manager = AlertEscalationManager("alert_history.json")
        self.logger = Logger(__name__)
        
        # 推送配置（增强版）
        self.push_config = {
            'enable_regular_monitoring': True,      # 启用定期监控
            'regular_interval_hours': 4,            # 定期推送间隔（小时）
            'enable_alert_pushing': True,           # 启用告警推送
            'enable_escalation_pushing': True,      # 启用升级告警推送
            'escalation_min_level': 2,              # 触发推送的最小升级级别
            'last_regular_push': None,              # 上次定期推送时间
            'alert_cooldown_minutes': 30,           # 相同告警冷却时间（分钟）
            'escalation_cooldown_minutes': 60,      # 升级告警冷却时间（分钟）
        }
        
        # 推送历史记录
        self.push_history = []
        self.max_push_history = 100
        
        self.logger.info("增强版监控推送服务初始化")
    
    def check_and_push(self, force_push: bool = False) -> Dict[str, Any]:
        """
        增强版检查推送（包含告警升级管理）
        
        Args:
            force_push: 是否强制推送（忽略时间间隔）
            
        Returns:
            推送结果
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'checked': False,
            'pushed': False,
            'push_type': None,
            'escalated': False,
            'escalation_level': 0,
            'message': '',
            'error': None
        }
        
        try:
            # 1. 检查系统状态（使用快速检查）
            start_time = time.time()
            
            # 先获取增强版系统资源检查
            enhanced_result = self.health_checker.check_system_resources_enhanced()
            
            # 使用快速健康检查
            try:
                health_report = self.health_checker.check_quick()
            except AttributeError:
                health_report = self.health_checker.check_all()
            
            check_time = time.time() - start_time
            
            overall_status = health_report.get('overall_status', 'unknown')
            
            result['checked'] = True
            result['check_time'] = check_time
            result['overall_status'] = overall_status
            
            # 保存报告用于告警升级处理
            self.last_health_report = health_report
            
            # 2. 处理告警升级
            escalated_alerts = self.alert_manager.process_health_report(health_report)
            
            if escalated_alerts:
                result['escalated'] = True
                max_level = max([a.escalation_level for a in escalated_alerts])
                result['escalation_level'] = max_level
            
            # 3. 判断是否需要推送
            should_push, push_type = self._should_push(health_report, escalated_alerts, force_push)
            
            if not should_push:
                result['message'] = f"无需推送 (状态: {overall_status}, 类型: {push_type})"
                return result
            
            # 4. 生成推送消息（增强版，包含告警升级信息）
            message = self._generate_enhanced_message(health_report, enhanced_result, 
                                                     escalated_alerts, push_type)
            
            # 5. 发送消息
            success = send_whatsapp_message(message)
            
            if success:
                result['pushed'] = True
                result['push_type'] = push_type
                result['message'] = f"成功推送 {push_type} 报告"
                
                # 更新推送记录
                self._update_push_record(push_type, escalated_alerts)
                
                self.logger.info(f"推送 {push_type} 报告成功")
                if escalated_alerts:
                    self.logger.info(f"包含 {len(escalated_alerts)} 个升级告警")
            else:
                result['error'] = "发送消息失败"
                self.logger.error("推送报告失败")
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"检查并推送时出错: {e}")
        
        return result
    
    def _should_push(self, report: Dict[str, Any], 
                    escalated_alerts: List[Any],
                    force_push: bool) -> tuple:
        """
        判断是否需要推送（增强版，考虑告警升级）
        
        Returns:
            (should_push, push_type)
        """
        overall_status = report.get('overall_status', 'unknown')
        
        # 1. 强制推送
        if force_push:
            return True, 'manual'
        
        # 2. 升级告警推送
        if self.push_config['enable_escalation_pushing'] and escalated_alerts:
            # 检查是否有达到最小升级级别的告警
            high_level_alerts = [
                a for a in escalated_alerts 
                if a.escalation_level >= self.push_config['escalation_min_level']
            ]
            
            if high_level_alerts and not self._is_escalation_cooldown():
                return True, 'escalation_alert'
        
        # 3. 紧急告警推送 (unhealthy状态)
        if overall_status == 'unhealthy':
            if not self._is_alert_cooldown('unhealthy'):
                return True, 'critical_alert'
        
        # 4. 警告推送
        elif overall_status == 'warning':
            if not self._is_alert_cooldown('warning'):
                return True, 'warning_alert'
        
        # 5. 定期监控推送
        current_time = datetime.now()
        last_regular = self.push_config.get('last_regular_push')
        
        if self.push_config['enable_regular_monitoring']:
            if last_regular is None:
                # 第一次推送
                return True, 'regular_monitor'
            else:
                # 检查是否到了推送时间
                hours_since_last = (current_time - last_regular).total_seconds() / 3600
                if hours_since_last >= self.push_config['regular_interval_hours']:
                    return True, 'regular_monitor'
        
        return False, 'none'
    
    def _generate_enhanced_message(self, health_report: Dict[str, Any], 
                                  enhanced_result: Dict[str, Any],
                                  escalated_alerts: List[Any],
                                  push_type: str) -> str:
        """
        生成增强版推送消息（包含告警升级信息）
        """
        overall_status = health_report.get('overall_status', 'unknown')
        timestamp = datetime.now()
        
        if push_type == 'escalation_alert':
            # 升级告警消息
            high_level_alerts = [
                a for a in escalated_alerts 
                if a.escalation_level >= self.push_config['escalation_min_level']
            ]
            
            message = f"📈 告警升级通知\n"
            message += f"时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"升级告警: {len(high_level_alerts)} 个\n\n"
            
            # 列出升级告警
            for i, alert in enumerate(high_level_alerts[:3], 1):  # 最多3个
                duration_hours = (timestamp - alert.first_seen).total_seconds() / 3600
                level_emoji = '⚠️' if alert.escalation_level == 1 else '❗' if alert.escalation_level == 2 else '🛑'
                
                message += f"{level_emoji} {alert.component} (级别{alert.escalation_level})\n"
                message += f"   问题: {alert.message}\n"
                message += f"   持续时间: {duration_hours:.1f}小时\n\n"
            
            if len(high_level_alerts) > 3:
                message += f"   还有 {len(high_level_alerts) - 3} 个升级告警...\n\n"
            
            # 添加系统状态
            if enhanced_result.get('status') == 'healthy' and 'metrics' in enhanced_result:
                metrics = enhanced_result['metrics']
                cpu_percent = metrics.get('cpu', {}).get('percent', '?')
                mem_percent = metrics.get('memory', {}).get('percent', '?')
                message += f"📊 系统资源: CPU {cpu_percent}%, 内存 {mem_percent}%\n"
            
            message += "\n💡 建议: 长时间未解决的问题可能需要人工干预"
            
        elif push_type in ['critical_alert', 'warning_alert']:
            # 基础告警消息（继承自父类逻辑，但添加升级信息）
            emoji = '🛑' if push_type == 'critical_alert' else '⚠️'
            alert_level = '严重告警' if push_type == 'critical_alert' else '警告'
            
            message = f"{emoji} 系统{alert_level} {emoji}\n"
            message += f"时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"状态: {overall_status}\n\n"
            
            # 添加问题详情
            issues = self._extract_issues(health_report)
            if issues:
                message += "发现问题:\n"
                for issue in issues[:3]:
                    message += f"• {issue}\n"
                if len(issues) > 3:
                    message += f"  ... 还有 {len(issues) - 3} 个问题\n"
            
            # 如果有升级告警，添加相关信息
            if escalated_alerts:
                message += f"\n📈 其中 {len(escalated_alerts)} 个问题正在升级\n"
            
            # 添加系统资源摘要
            if enhanced_result.get('status') == 'healthy' and 'metrics' in enhanced_result:
                metrics = enhanced_result['metrics']
                cpu_percent = metrics.get('cpu', {}).get('percent', '?')
                mem_percent = metrics.get('memory', {}).get('percent', '?')
                message += f"\n📊 系统资源: CPU {cpu_percent}%, 内存 {mem_percent}%\n"
            
            message += "\n💡 请检查系统状态"
            
        elif push_type == 'regular_monitor':
            # 定期监控消息（添加告警摘要）
            message = self.dashboard.generate_compact_dashboard()
            
            # 添加告警摘要
            escalation_summary = self.alert_manager.generate_escalation_summary()
            if "无活动告警" not in escalation_summary:
                message += f"\n{escalation_summary}"
            
        elif push_type == 'manual':
            # 手动推送（使用完整仪表板）
            message = self.dashboard.generate_dashboard(quick_mode=True)
            
            # 添加告警摘要
            escalation_summary = self.alert_manager.generate_escalation_summary()
            message += f"\n\n{escalation_summary}"
        
        else:
            # 默认消息
            message = f"📊 系统状态报告\n时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n状态: {overall_status}"
        
        # 确保消息长度合适
        max_length = 4096
        if len(message) > max_length:
            message = message[:max_length-100] + "\n...\n⚠️ 消息过长，已截断"
        
        return message
    
    def _extract_issues(self, report: Dict[str, Any]) -> List[str]:
        """从报告中提取问题"""
        issues = []
        checks = report.get('checks', {})
        
        for check_id, check_result in checks.items():
            status = check_result.get('status', 'unknown')
            
            if status in ['warning', 'unhealthy']:
                component_name = check_result.get('component', check_id)
                details = check_result.get('details', {})
                
                if 'error' in details:
                    issues.append(f"{component_name}: {details['error']}")
                elif 'warnings' in details and details['warnings']:
                    for warning in details['warnings'][:2]:
                        issues.append(f"{component_name}: {warning}")
                else:
                    issues.append(f"{component_name}: 状态异常")
        
        return issues
    
    def _is_alert_cooldown(self, alert_type: str) -> bool:
        """检查告警是否在冷却期内"""
        # 简化实现，实际应基于推送历史
        current_time = datetime.now()
        cooldown_minutes = self.push_config.get('alert_cooldown_minutes', 30)
        
        # 查找最近的相同类型推送
        recent_pushes = [
            push for push in self.push_history
            if push.get('type') == alert_type
        ]
        
        if not recent_pushes:
            return False
        
        latest_push = max(recent_pushes, key=lambda x: x.get('timestamp', ''))
        
        if 'timestamp' in latest_push:
            try:
                push_time = datetime.fromisoformat(latest_push['timestamp'])
                minutes_since_last = (current_time - push_time).total_seconds() / 60
                
                return minutes_since_last < cooldown_minutes
            except:
                return False
        
        return False
    
    def _is_escalation_cooldown(self) -> bool:
        """检查升级告警是否在冷却期内"""
        return self._is_alert_cooldown('escalation_alert')
    
    def _update_push_record(self, push_type: str, escalated_alerts: List[Any] = None):
        """更新推送记录"""
        current_time = datetime.now()
        
        # 更新最后推送时间
        if push_type == 'regular_monitor':
            self.push_config['last_regular_push'] = current_time
        
        # 保存推送历史
        push_record = {
            'type': push_type,
            'timestamp': current_time.isoformat(),
            'escalated_count': len(escalated_alerts) if escalated_alerts else 0
        }
        
        self.push_history.append(push_record)
        
        # 限制历史记录长度
        if len(self.push_history) > self.max_push_history:
            self.push_history = self.push_history[-self.max_push_history:]
    
    def get_status_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        try:
            # 快速检查
            health_report = self.health_checker.check_quick()
            
            # 获取告警状态
            active_alerts = self.alert_manager.get_active_alerts()
            escalated_alerts = self.alert_manager.get_escalated_alerts(min_level=1)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': health_report.get('overall_status', 'unknown'),
                'active_alerts': len(active_alerts),
                'escalated_alerts': len(escalated_alerts),
                'push_history_count': len(self.push_history)
            }
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }


def test_enhanced_monitor():
    """测试增强版监控推送服务"""
    print("🧪 测试增强版监控推送服务")
    print("=" * 60)
    
    service = MonitorPushEnhanced()
    
    print("1. 测试检查功能（不推送）...")
    result = service.check_and_push(force_push=False)
    
    print(f"   检查结果:")
    print(f"     状态: {result.get('overall_status', 'unknown')}")
    print(f"     检查耗时: {result.get('check_time', 0):.2f}秒")
    print(f"     是否推送: {result.get('pushed', False)}")
    print(f"     告警升级: {result.get('escalated', False)}")
    
    if result.get('escalated'):
        print(f"     升级级别: {result.get('escalation_level', 0)}")
    
    print()
    print("2. 测试状态摘要...")
    summary = service.get_status_summary()
    print(f"   状态摘要: {summary}")
    
    print()
    print("3. 测试消息生成（模拟）...")
    
    # 模拟升级告警
    test_alerts = []
    try:
        from monitoring.alert_escalation import AlertRecord, AlertSeverity, AlertState
        
        # 创建一个模拟的升级告警
        test_alert = AlertRecord(
            alert_id="test_1",
            component="消息平台",
            severity=AlertSeverity.WARNING,
            message="微信推送未配置",
            first_seen=datetime.now() - timedelta(hours=2),
            last_seen=datetime.now(),
            state=AlertState.NEW,
            escalation_level=2,
            count=5
        )
        test_alerts.append(test_alert)
    except:
        pass
    
    # 测试升级告警消息生成
    test_report = {
        'overall_status': 'warning',
        'checks': {
            'message_platforms': {
                'status': 'warning',
                'component': '消息平台',
                'details': {'error': '微信推送未配置'}
            }
        }
    }
    
    test_enhanced = {
        'status': 'healthy',
        'metrics': {
            'cpu': {'percent': 45.2},
            'memory': {'percent': 78.3}
        }
    }
    
    escalation_message = service._generate_enhanced_message(
        test_report, test_enhanced, test_alerts, 'escalation_alert'
    )
    
    print(f"   升级告警消息预览:\n{escalation_message[:200]}...")
    
    print()
    print("✅ 增强版监控推送服务测试完成")


if __name__ == "__main__":
    test_enhanced_monitor()
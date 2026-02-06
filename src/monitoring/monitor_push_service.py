#!/usr/bin/env python3
"""
监控推送服务
定期推送系统监控状态和告警
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
    from monitoring.monitor_dashboard import MonitorDashboard
    from utils.logger import Logger
    from utils.message_sender import send_whatsapp_message
except ImportError as e:
    print(f"[MonitorPushService] 导入模块失败: {e}")
    # 创建简单的替代函数
    def send_whatsapp_message(message):
        print(f"[模拟发送] {message[:100]}...")
        return True
    
    class HealthChecker:
        def check_all(self):
            return {"overall_status": "unknown", "checks": {}}
    
    class MonitorDashboard:
        def generate_dashboard(self):
            return "📊 监控仪表板\n测试模式"
    
    class Logger:
        def __init__(self, name):
            self.name = name
        
        def info(self, msg):
            print(f"[{self.name}] INFO: {msg}")
        
        def error(self, msg):
            print(f"[{self.name}] ERROR: {msg}")
        
        def warning(self, msg):
            print(f"[{self.name}] WARNING: {msg}")


class MonitorPushService:
    """监控推送服务"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化监控推送服务
        
        Args:
            config_dir: 配置目录路径
        """
        self.config_dir = config_dir
        self.health_checker = HealthChecker(config_dir)
        self.dashboard = MonitorDashboard()
        self.logger = Logger(__name__)
        
        # 告警状态跟踪
        self.alert_history = []
        self.max_alert_history = 100
        
        # 推送配置
        self.push_config = {
            'enable_regular_monitoring': True,  # 启用定期监控
            'regular_interval_hours': 4,        # 定期推送间隔（小时）
            'enable_alert_pushing': True,       # 启用告警推送
            'last_regular_push': None,          # 上次定期推送时间
            'alert_cooldown_minutes': 30,       # 相同告警冷却时间（分钟）
        }
        
        self.logger.info("监控推送服务初始化")
    
    def check_and_push(self, force_push: bool = False) -> Dict[str, Any]:
        """
        检查系统状态并推送报告
        
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
            'message': '',
            'error': None
        }
        
        try:
            # 1. 检查系统状态（使用快速检查）
            start_time = time.time()
            
            # 先获取增强版系统资源检查（包含我们需要的信息）
            enhanced_result = self.health_checker.check_system_resources_enhanced()
            
            # 使用快速健康检查（跳过耗时的新闻源检查）
            try:
                # 尝试使用快速检查方法
                health_report = self.health_checker.check_quick()
            except AttributeError:
                # 如果快速检查方法不存在，回退到完整检查
                health_report = self.health_checker.check_all()
            
            check_time = time.time() - start_time
            
            overall_status = health_report.get('overall_status', 'unknown')
            
            result['checked'] = True
            result['check_time'] = check_time
            result['overall_status'] = overall_status
            
            # 2. 判断是否需要推送
            should_push, push_type = self._should_push(health_report, force_push)
            
            if not should_push:
                result['message'] = f"无需推送 (状态: {overall_status}, 类型: {push_type})"
                return result
            
            # 3. 生成推送消息
            message = self._generate_push_message(health_report, enhanced_result, push_type)
            
            # 4. 发送消息
            success = send_whatsapp_message(message)
            
            if success:
                result['pushed'] = True
                result['push_type'] = push_type
                result['message'] = f"成功推送 {push_type} 报告"
                
                # 更新推送记录
                self._update_push_record(push_type)
                
                self.logger.info(f"推送 {push_type} 报告成功")
            else:
                result['error'] = "发送消息失败"
                self.logger.error("推送报告失败")
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"检查并推送时出错: {e}")
        
        return result
    
    def _should_push(self, report: Dict[str, Any], force_push: bool) -> tuple:
        """
        判断是否需要推送
        
        Returns:
            (should_push, push_type)
        """
        overall_status = report.get('overall_status', 'unknown')
        
        # 1. 强制推送
        if force_push:
            return True, 'manual'
        
        # 2. 紧急告警推送 (unhealthy状态)
        if overall_status == 'unhealthy':
            # 检查是否在冷却期内
            if not self._is_alert_cooldown('unhealthy'):
                return True, 'critical_alert'
        
        # 3. 警告推送
        elif overall_status == 'warning':
            # 检查是否在冷却期内
            if not self._is_alert_cooldown('warning'):
                return True, 'warning_alert'
        
        # 4. 定期监控推送
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
    
    def _generate_push_message(self, health_report: Dict[str, Any], 
                              enhanced_result: Dict[str, Any], 
                              push_type: str) -> str:
        """
        根据推送类型生成消息
        
        Args:
            health_report: 健康检查报告
            enhanced_result: 增强版系统资源结果
            push_type: 推送类型
            
        Returns:
            推送消息
        """
        overall_status = health_report.get('overall_status', 'unknown')
        timestamp = datetime.now()
        
        if push_type in ['critical_alert', 'warning_alert']:
            # 告警消息
            emoji = '🛑' if push_type == 'critical_alert' else '⚠️'
            alert_level = '严重告警' if push_type == 'critical_alert' else '警告'
            
            message = f"{emoji} 系统{alert_level} {emoji}\n"
            message += f"时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"状态: {overall_status}\n\n"
            
            # 添加问题详情
            issues = self._extract_issues(health_report)
            if issues:
                message += "发现问题:\n"
                for issue in issues[:3]:  # 最多3个问题
                    message += f"• {issue}\n"
                if len(issues) > 3:
                    message += f"  ... 还有 {len(issues) - 3} 个问题\n"
            else:
                message += "状态异常，但未识别到具体问题\n"
            
            # 添加系统资源摘要
            if enhanced_result.get('status') == 'healthy' and 'metrics' in enhanced_result:
                metrics = enhanced_result['metrics']
                cpu_percent = metrics.get('cpu', {}).get('percent', '?')
                mem_percent = metrics.get('memory', {}).get('percent', '?')
                message += f"\n📊 系统资源: CPU {cpu_percent}%, 内存 {mem_percent}%\n"
            
            message += "\n💡 请立即检查系统状态"
            
        elif push_type == 'regular_monitor':
            # 定期监控消息（使用简洁版仪表板）
            message = self.dashboard.generate_compact_dashboard()
            
            # 如果有问题，添加简要说明
            if overall_status != 'healthy':
                issues = self._extract_issues(health_report)
                if issues:
                    message += f"\n⚠️ 发现问题: {len(issues)}个"
            
        elif push_type == 'manual':
            # 手动推送（使用快速模式的完整仪表板）
            message = self.dashboard.generate_dashboard(quick_mode=True)
        
        else:
            # 默认消息
            message = f"📊 系统状态报告\n时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n状态: {overall_status}"
        
        # 确保消息长度合适（WhatsApp限制）
        max_length = 4096  # WhatsApp消息长度限制
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
        """
        检查告警是否在冷却期内
        
        Args:
            alert_type: 告警类型
            
        Returns:
            是否在冷却期内
        """
        current_time = datetime.now()
        cooldown_minutes = self.push_config.get('alert_cooldown_minutes', 30)
        
        # 查找最近的相同类型告警
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.get('type') == alert_type
        ]
        
        if not recent_alerts:
            return False
        
        # 获取最近一次告警
        latest_alert = max(recent_alerts, key=lambda x: x.get('timestamp', ''))
        
        # 检查时间间隔
        if 'timestamp' in latest_alert:
            try:
                alert_time = datetime.fromisoformat(latest_alert['timestamp'])
                minutes_since_last = (current_time - alert_time).total_seconds() / 60
                
                return minutes_since_last < cooldown_minutes
            except:
                return False
        
        return False
    
    def _update_push_record(self, push_type: str):
        """更新推送记录"""
        current_time = datetime.now()
        
        # 更新最后推送时间
        if push_type == 'regular_monitor':
            self.push_config['last_regular_push'] = current_time
        
        # 保存告警历史
        if push_type in ['critical_alert', 'warning_alert']:
            self.alert_history.append({
                'type': push_type,
                'timestamp': current_time.isoformat(),
                'message': f"{push_type} at {current_time.strftime('%H:%M')}"
            })
            
            # 限制历史记录长度
            if len(self.alert_history) > self.max_alert_history:
                self.alert_history = self.alert_history[-self.max_alert_history:]
    
    def run_scheduled_monitor(self, interval_hours: int = 4):
        """
        运行定时监控（阻塞式，适合作为服务运行）
        
        Args:
            interval_hours: 检查间隔（小时）
        """
        self.logger.info(f"启动定时监控服务，间隔 {interval_hours} 小时")
        
        try:
            while True:
                try:
                    # 执行检查并推送
                    result = self.check_and_push()
                    
                    if result.get('pushed'):
                        self.logger.info(f"定时推送完成: {result['push_type']}")
                    else:
                        self.logger.info(f"定时检查完成，未推送: {result.get('message', '')}")
                    
                except Exception as e:
                    self.logger.error(f"定时监控执行失败: {e}")
                
                # 等待下一轮
                time.sleep(interval_hours * 3600)
                
        except KeyboardInterrupt:
            self.logger.info("定时监控服务停止")
        except Exception as e:
            self.logger.error(f"定时监控服务异常退出: {e}")


def test_monitor_push_service():
    """测试监控推送服务"""
    print("🧪 测试监控推送服务")
    print("=" * 60)
    
    service = MonitorPushService()
    
    print("📤 测试强制推送（手动模式）...")
    result = service.check_and_push(force_push=True)
    print(f"  结果: {result}")
    
    print("\n📊 测试告警判断...")
    # 模拟一个警告状态
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
    
    should_push, push_type = service._should_push(test_report, force_push=False)
    print(f"  状态: warning, 应该推送: {should_push}, 类型: {push_type}")
    
    # 测试消息生成
    print("\n💬 测试告警消息生成...")
    test_enhanced = {
        'status': 'healthy',
        'metrics': {
            'cpu': {'percent': 45.2},
            'memory': {'percent': 78.3}
        }
    }
    
    alert_message = service._generate_push_message(test_report, test_enhanced, 'warning_alert')
    print(f"  告警消息预览:\n{alert_message[:200]}...")
    
    print("\n✅ 监控推送服务测试完成")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='监控推送服务')
    parser.add_argument('--push', '-p', action='store_true', help='立即推送监控报告')
    parser.add_argument('--schedule', '-s', action='store_true', help='启动定时监控服务')
    parser.add_argument('--interval', '-i', type=int, default=4, help='定时监控间隔（小时）')
    parser.add_argument('--test', '-t', action='store_true', help='运行测试')
    
    args = parser.parse_args()
    
    if args.test:
        test_monitor_push_service()
        return
    
    service = MonitorPushService()
    
    if args.push:
        print("🚀 立即推送监控报告...")
        result = service.check_and_push(force_push=True)
        
        if result.get('pushed'):
            print(f"✅ 推送成功: {result.get('push_type')}")
        else:
            print(f"⚠️  未推送: {result.get('message', '未知原因')}")
            if result.get('error'):
                print(f"   错误: {result['error']}")
    
    elif args.schedule:
        print(f"⏰ 启动定时监控服务，间隔 {args.interval} 小时...")
        service.run_scheduled_monitor(args.interval)
    
    else:
        # 默认：检查但不一定推送
        print("🔍 检查系统状态...")
        result = service.check_and_push(force_push=False)
        
        print(f"📊 检查结果:")
        print(f"  状态: {result.get('overall_status', 'unknown')}")
        print(f"  检查耗时: {result.get('check_time', 0):.2f}秒")
        print(f"  是否推送: {result.get('pushed', False)}")
        if result.get('push_type'):
            print(f"  推送类型: {result.get('push_type')}")
        if result.get('message'):
            print(f"  消息: {result.get('message')}")


if __name__ == "__main__":
    main()
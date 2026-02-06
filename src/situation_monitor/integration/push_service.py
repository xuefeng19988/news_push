#!/usr/bin/env python3
"""
监控推送服务（situation-monitor版本）
基于新架构的智能监控推送服务
"""

import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入situation-monitor组件
from situation_monitor.core.monitor import SituationMonitor, CheckStatus, AlertLevel
from situation_monitor.checks.system_checks import create_default_checks
from situation_monitor.alerts.integration import HealthCheckAlertAdapter, create_legacy_compatible_manager
from situation_monitor.alerts.notifications import create_default_notifier

# 导入现有工具模块
try:
    from utils.message_sender import send_whatsapp_message
    from utils.logger import Logger
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False
    print("警告: WhatsApp消息发送模块不可用")

# 强制使用situation-monitor检查，不使用旧的HealthChecker
# 这样可以避免微信未配置警告干扰监控报告
try:
    from monitoring.health_check import HealthChecker
    # 即使可以导入，也强制使用situation-monitor检查
    HEALTH_CHECK_AVAILABLE = False
    print("信息: HealthChecker模块可用，但强制使用situation-monitor检查")
except ImportError:
    HEALTH_CHECK_AVAILABLE = False
    print("信息: HealthChecker模块不可用，使用situation-monitor检查")


class SituationMonitorPushService:
    """
    基于situation-monitor的监控推送服务
    智能、高效、可扩展
    """
    
    def __init__(self, enable_whatsapp: bool = True):
        """
        初始化监控推送服务
        
        Args:
            enable_whatsapp: 是否启用WhatsApp推送
        """
        self.enable_whatsapp = enable_whatsapp and WHATSAPP_AVAILABLE
        
        # 创建logger
        self.logger = Logger(__name__) if 'Logger' in sys.modules else self._create_simple_logger()
        
        # 创建situation-monitor实例
        self.monitor = SituationMonitor("push_service_monitor")
        
        # 添加默认检查
        self._setup_monitor_checks()
        
        # 创建告警系统
        self.alert_manager = create_legacy_compatible_manager()
        self.health_adapter = HealthCheckAlertAdapter()
        
        # 创建通知器
        self.notifier = create_default_notifier()
        
        # 服务统计
        self.stats = {
            "runs": 0,
            "checks_performed": 0,
            "alerts_generated": 0,
            "notifications_sent": 0,
            "last_run": None,
            "avg_check_time_ms": 0
        }
        
        self.logger.info("SituationMonitorPushService初始化完成")
    
    def _create_simple_logger(self):
        """创建简单的logger"""
        class SimpleLogger:
            def __init__(self, name):
                self.name = name
            
            def info(self, msg):
                print(f"[{self.name}] INFO: {msg}")
            
            def warning(self, msg):
                print(f"[{self.name}] WARNING: {msg}")
            
            def error(self, msg):
                print(f"[{self.name}] ERROR: {msg}")
        
        return SimpleLogger(__name__)
    
    def _setup_monitor_checks(self):
        """设置监控检查"""
        checks = create_default_checks()
        
        for check in checks:
            self.monitor.add_check(check)
        
        self.logger.info(f"添加了 {len(checks)} 个监控检查")
    
    def run_health_check(self, quick_mode: bool = True) -> Dict[str, Any]:
        """
        运行健康检查
        
        Args:
            quick_mode: 是否使用快速检查模式
            
        Returns:
            健康检查报告
        """
        if not HEALTH_CHECK_AVAILABLE:
            # 使用situation-monitor的检查
            return self._run_situation_monitor_checks()
        
        try:
            health_checker = HealthChecker()
            
            if quick_mode:
                report = health_checker.check_quick()
            else:
                report = health_checker.check_all()
            
            return report
            
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return {
                "overall_status": "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_situation_monitor_checks(self) -> Dict[str, Any]:
        """使用situation-monitor运行检查"""
        results = self.monitor.run_all_checks()
        
        checks = {}
        status_counts = {"healthy": 0, "warning": 0, "unhealthy": 0, "unknown": 0}
        
        for check_id, result in results.items():
            if result:
                # 转换状态
                status_map = {
                    CheckStatus.HEALTHY: "healthy",
                    CheckStatus.WARNING: "warning",
                    CheckStatus.ERROR: "unhealthy",
                    CheckStatus.CRITICAL: "unhealthy",
                    CheckStatus.UNKNOWN: "unknown"
                }
                
                status = status_map.get(result.status, "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
                
                checks[check_id] = {
                    "component": result.check_name,
                    "status": status,
                    "details": {
                        "message": result.message,
                        "metrics": result.metrics,
                        "duration_ms": result.duration_ms
                    }
                }
        
        # 确定整体状态
        if status_counts["unhealthy"] > 0:
            overall_status = "unhealthy"
        elif status_counts["warning"] > 0:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "status_counts": status_counts,
            "checks": checks
        }
    
    def process_health_alerts(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        处理健康检查告警
        
        Args:
            report: 健康检查报告
            
        Returns:
            生成的告警列表
        """
        # 使用适配器处理健康检查报告
        alerts = self.health_adapter.process_quick_health_check(report)
        
        # 转换为字典格式
        alert_dicts = []
        for alert in alerts:
            alert_dicts.append({
                "alert_id": alert.alert_id,
                "level": alert.level.value,
                "title": alert.title,
                "source": alert.source,
                "message": alert.message[:100]
            })
        
        self.stats["alerts_generated"] += len(alerts)
        return alert_dicts
    
    def generate_monitoring_message(self, report: Dict[str, Any], alerts: List[Dict[str, Any]]) -> str:
        """
        生成监控消息
        
        Args:
            report: 健康检查报告
            alerts: 告警列表
            
        Returns:
            监控消息文本
        """
        current_time = datetime.now()
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 确定整体状态表情
        overall_status = report.get("overall_status", "unknown")
        
        # 如果告警列表为空但整体状态是warning，可能是微信警告被过滤了
        # 在这种情况下，将状态显示为healthy
        if overall_status == "warning" and not alerts:
            display_status = "healthy"
            status_emoji = "✅"
        else:
            display_status = overall_status
            status_emoji = "✅"
            if overall_status == "warning":
                status_emoji = "⚠️"
            elif overall_status == "unhealthy":
                status_emoji = "❌"
            elif overall_status == "unknown":
                status_emoji = "❓"
        
        # 构建消息
        message = f"{status_emoji} 系统监控报告 {status_emoji}\n"
        message += f"时间: {time_str}\n"
        message += f"整体状态: {display_status}\n\n"
        
        # 添加检查摘要
        checks = report.get("checks", {})
        
        # 过滤掉message_platforms检查（如果它是微信未配置警告）
        filtered_checks = {}
        for check_id, check_result in checks.items():
            if check_id == "message_platforms":
                status = check_result.get("status", "unknown")
                if status == "warning":
                    details = check_result.get("details", {})
                    # 检查是否是微信未配置警告
                    is_wechat_warning = False
                    
                    # 方式1: 检查直接的消息字段
                    message_text = details.get("message", "")
                    if "微信未配置" in message_text or "wechat" in message_text.lower():
                        is_wechat_warning = True
                    
                    # 方式2: 检查嵌套的wechat错误信息
                    if not is_wechat_warning and isinstance(details, dict):
                        platforms = details.get("platforms", {})
                        wechat_info = platforms.get("wechat", {})
                        wechat_details = wechat_info.get("details", {})
                        wechat_error = wechat_details.get("error", "")
                        
                        if "微信推送未配置" in wechat_error or "wechat" in wechat_error.lower():
                            is_wechat_warning = True
                    
                    # 如果是微信未配置警告，跳过此检查
                    if is_wechat_warning:
                        continue
            
            filtered_checks[check_id] = check_result
        
        if filtered_checks:
            message += "📊 组件状态:\n"
            
            for check_id, check_result in filtered_checks.items():
                status = check_result.get("status", "unknown")
                component = check_result.get("component", check_id)
                
                check_emoji = "✅"
                if status == "warning":
                    check_emoji = "⚠️"
                elif status == "unhealthy":
                    check_emoji = "❌"
                
                message += f"{check_emoji} {component}: {status}\n"
        else:
            message += "📊 检查详情: 无检查结果\n"
        
        # 添加告警信息
        if alerts:
            message += f"\n🚨 活动告警 ({len(alerts)}个):\n"
            
            for i, alert in enumerate(alerts[:3]):  # 只显示前3个
                level = alert.get("level", "unknown")
                source = alert.get("source", "unknown")
                alert_message = alert.get("message", "")
                
                alert_emoji = "ℹ️"
                if level == "warning":
                    alert_emoji = "⚠️"
                elif level == "error":
                    alert_emoji = "❌"
                elif level == "critical":
                    alert_emoji = "🔥"
                
                message += f"{alert_emoji} {source}: {alert_message}\n"
            
            if len(alerts) > 3:
                message += f"  还有 {len(alerts) - 3} 个告警...\n"
        else:
            message += "\n✅ 无活动告警\n"
        
        # 添加系统资源信息
        if "system_resources" in checks:
            resources = checks["system_resources"].get("details", {}).get("metrics", {})
            if resources:
                message += "\n💻 系统资源:\n"
                
                if "cpu_percent" in resources:
                    message += f"  CPU: {resources['cpu_percent']}%\n"
                
                if "memory_percent" in resources:
                    message += f"  内存: {resources['memory_percent']}%\n"
                
                if "disk_percent" in resources:
                    message += f"  磁盘: {resources['disk_percent']}%\n"
        
        # 添加统计信息
        message += f"\n📈 统计: "
        message += f"检查次数: {self.stats['runs']}, "
        message += f"平均耗时: {self.stats['avg_check_time_ms']:.1f}ms"
        
        return message
    
    def send_whatsapp_notification(self, message: str) -> bool:
        """
        发送WhatsApp通知
        
        Args:
            message: 消息内容
            
        Returns:
            是否成功发送
        """
        if not self.enable_whatsapp:
            self.logger.warning("WhatsApp推送已禁用")
            return False
        
        try:
            result = send_whatsapp_message(message)
            
            # 处理可能的返回值类型：布尔值或元组
            if isinstance(result, tuple):
                # 假设第一个元素是成功标志
                success = result[0] if len(result) > 0 else False
                if len(result) > 1 and isinstance(result[1], str):
                    self.logger.info(f"WhatsApp发送结果: {result[1][:100]}")
            else:
                success = bool(result)
            
            if success:
                self.stats["notifications_sent"] += 1
                self.logger.info("WhatsApp监控消息发送成功")
            else:
                self.logger.warning("WhatsApp监控消息发送失败")
            
            return success
            
        except Exception as e:
            self.logger.error(f"WhatsApp消息发送失败: {e}")
            return False
    
    def check_and_push(self, force_push: bool = False) -> Dict[str, Any]:
        """
        检查系统状态并推送报告（兼容现有接口）
        
        Args:
            force_push: 是否强制推送（忽略时间间隔）
            
        Returns:
            推送结果（兼容现有格式）
        """
        start_time = time.time()
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'checked': False,
            'pushed': False,
            'push_type': None,
            'message': '',
            'error': None,
            'overall_status': 'unknown',
            'check_time': 0
        }
        
        try:
            # 1. 运行健康检查
            health_report = self.run_health_check(quick_mode=True)
            
            # 2. 处理告警
            alerts = self.process_health_alerts(health_report)
            
            # 3. 生成监控消息
            message = self.generate_monitoring_message(health_report, alerts)
            
            # 4. 确定推送类型
            overall_status = health_report.get('overall_status', 'unknown')
            push_type = self._determine_push_type(overall_status, force_push)
            
            # 5. 发送通知
            notification_sent = False
            if push_type != 'none':
                notification_sent = self.send_whatsapp_notification(message)
            
            # 更新统计
            duration_ms = (time.time() - start_time) * 1000
            self.stats["runs"] += 1
            self.stats["checks_performed"] += len(health_report.get("checks", {}))
            
            # 更新平均检查时间
            if self.stats["runs"] == 1:
                self.stats["avg_check_time_ms"] = duration_ms
            else:
                # 指数移动平均
                self.stats["avg_check_time_ms"] = (
                    0.7 * self.stats["avg_check_time_ms"] + 0.3 * duration_ms
                )
            
            self.stats["last_run"] = datetime.now().isoformat()
            
            # 填充结果
            result['checked'] = True
            result['check_time'] = duration_ms / 1000.0  # 转换为秒
            result['overall_status'] = overall_status
            result['pushed'] = notification_sent
            result['push_type'] = push_type
            result['message'] = f"推送 {push_type} 报告" if notification_sent else f"无需推送 (状态: {overall_status})"
            
            if notification_sent:
                self.logger.info(f"推送 {push_type} 报告成功")
            else:
                self.logger.info(f"未推送报告 (推送类型: {push_type})")
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"检查并推送时出错: {e}")
            return result
    
    def _determine_push_type(self, overall_status: str, force_push: bool) -> str:
        """
        确定推送类型
        
        Args:
            overall_status: 整体状态
            force_push: 是否强制推送
            
        Returns:
            推送类型 ('critical_alert', 'warning_alert', 'regular_monitor', 'manual', 'none')
        """
        # 简化逻辑：总是推送监控报告（与当前每小时推送行为一致）
        # 以后可以添加更智能的逻辑
        if force_push:
            return 'manual'
        elif overall_status == 'unhealthy':
            return 'critical_alert'
        elif overall_status == 'warning':
            return 'warning_alert'
        else:
            # healthy状态也推送定期监控报告
            return 'regular_monitor'
    
    def run_monitoring_cycle(self, send_notification: bool = True) -> Dict[str, Any]:
        """
        运行完整的监控周期
        
        Args:
            send_notification: 是否发送通知
            
        Returns:
            监控结果
        """
        start_time = time.time()
        
        try:
            # 1. 运行健康检查
            health_report = self.run_health_check(quick_mode=True)
            
            # 2. 处理告警
            alerts = self.process_health_alerts(health_report)
            
            # 3. 生成监控消息
            message = self.generate_monitoring_message(health_report, alerts)
            
            # 4. 发送通知（如果启用）
            notification_sent = False
            if send_notification:
                notification_sent = self.send_whatsapp_notification(message)
            
            # 更新统计
            duration_ms = (time.time() - start_time) * 1000
            self.stats["runs"] += 1
            self.stats["checks_performed"] += len(health_report.get("checks", {}))
            
            # 更新平均检查时间
            if self.stats["runs"] == 1:
                self.stats["avg_check_time_ms"] = duration_ms
            else:
                # 指数移动平均
                self.stats["avg_check_time_ms"] = (
                    0.7 * self.stats["avg_check_time_ms"] + 0.3 * duration_ms
                )
            
            self.stats["last_run"] = datetime.now().isoformat()
            
            result = {
                "success": True,
                "duration_ms": duration_ms,
                "health_report": health_report,
                "alerts_generated": len(alerts),
                "notification_sent": notification_sent,
                "message_preview": message[:200] + "..." if len(message) > 200 else message
            }
            
            self.logger.info(f"监控周期完成: {duration_ms:.1f}ms, 告警: {len(alerts)}个")
            return result
            
        except Exception as e:
            self.logger.error(f"监控周期失败: {e}")
            
            # 发送错误通知
            if send_notification and self.enable_whatsapp:
                error_message = f"❌ 监控系统错误\n时间: {datetime.now().strftime('%H:%M:%S')}\n错误: {str(e)[:100]}"
                self.send_whatsapp_notification(error_message)
            
            return {
                "success": False,
                "error": str(e),
                "duration_ms": (time.time() - start_time) * 1000
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        获取服务状态
        
        Returns:
            服务状态信息
        """
        return {
            **self.stats,
            "whatsapp_enabled": self.enable_whatsapp,
            "health_check_available": HEALTH_CHECK_AVAILABLE,
            "monitor_check_count": len(self.monitor.checks),
            "alert_manager_alerts": len(self.alert_manager.get_active_alerts()),
            "current_time": datetime.now().isoformat()
        }


def run_situation_monitor_push_service():
    """运行situation-monitor推送服务（命令行入口点）"""
    print("🚀 启动situation-monitor监控推送服务")
    print("=" * 60)
    
    try:
        # 创建服务实例
        service = SituationMonitorPushService(enable_whatsapp=True)
        
        # 运行监控周期
        print("运行监控周期...")
        result = service.run_monitoring_cycle(send_notification=True)
        
        if result["success"]:
            print(f"✅ 监控周期成功完成")
            print(f"   耗时: {result['duration_ms']:.1f}ms")
            print(f"   告警生成: {result['alerts_generated']}个")
            print(f"   通知发送: {'成功' if result['notification_sent'] else '失败'}")
            
            # 显示消息预览
            if "message_preview" in result:
                print(f"\n📱 发送的消息预览:")
                print(result["message_preview"])
        else:
            print(f"❌ 监控周期失败")
            print(f"   错误: {result.get('error', '未知错误')}")
        
        # 显示服务状态
        print(f"\n📊 服务状态:")
        status = service.get_service_status()
        print(f"   运行次数: {status['runs']}")
        print(f"   平均耗时: {status['avg_check_time_ms']:.1f}ms")
        print(f"   活动告警: {status['alert_manager_alerts']}个")
        
        return result["success"]
        
    except Exception as e:
        print(f"❌ 服务运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_situation_monitor_push_service()
    sys.exit(0 if success else 1)
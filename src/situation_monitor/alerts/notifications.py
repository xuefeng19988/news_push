#!/usr/bin/env python3
"""
告警通知系统
提供多种告警通知渠道：控制台、文件、WhatsApp等
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

# 导入situation-monitor核心类型
from ..core.monitor import Alert, AlertLevel

# 尝试导入消息发送模块
try:
    from utils.message_sender import send_whatsapp_message
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False
    print("警告: WhatsApp消息发送模块不可用，WhatsApp通知将不可用")


@dataclass
class NotificationConfig:
    """通知配置"""
    enable_console: bool = True
    enable_file: bool = False
    enable_whatsapp: bool = True
    file_path: str = "alerts.log"
    whatsapp_recipient: Optional[str] = None
    min_severity_for_whatsapp: AlertLevel = AlertLevel.WARNING
    cooldown_seconds: int = 300  # 相同告警冷却时间（5分钟）


class AlertNotifier:
    """
    告警通知器
    提供多种通知渠道，支持冷却时间和严重性过滤
    """
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        """
        初始化告警通知器
        
        Args:
            config: 通知配置
        """
        self.config = config or NotificationConfig()
        
        # 告警冷却跟踪：alert_id -> 最后发送时间
        self.cooldown_tracker: Dict[str, datetime] = {}
        
        # 通知统计
        self.stats = {
            "notifications_sent": 0,
            "notifications_blocked_by_cooldown": 0,
            "notifications_blocked_by_severity": 0,
            "last_notification": None
        }
        
        # 自定义通知处理器
        self.custom_handlers: List[Callable[[Alert], None]] = []
    
    def should_send_notification(self, alert: Alert) -> bool:
        """
        检查是否应该发送通知
        
        Args:
            alert: 告警对象
            
        Returns:
            是否应该发送通知
        """
        # 检查冷却时间
        if alert.alert_id in self.cooldown_tracker:
            last_sent = self.cooldown_tracker[alert.alert_id]
            cooldown_delta = (datetime.now() - last_sent).total_seconds()
            
            if cooldown_delta < self.config.cooldown_seconds:
                self.stats["notifications_blocked_by_cooldown"] += 1
                return False
        
        # 检查WhatsApp最低严重性
        if self.config.enable_whatsapp:
            severity_order = {
                AlertLevel.INFO: 0,
                AlertLevel.WARNING: 1,
                AlertLevel.ERROR: 2,
                AlertLevel.CRITICAL: 3
            }
            
            min_severity_order = severity_order.get(self.config.min_severity_for_whatsapp, 0)
            alert_severity_order = severity_order.get(alert.level, 0)
            
            if alert_severity_order < min_severity_order:
                self.stats["notifications_blocked_by_severity"] += 1
                # 仍然可以发送到其他渠道
                pass
        
        return True
    
    def send_notification(self, alert: Alert) -> bool:
        """
        发送告警通知
        
        Args:
            alert: 告警对象
            
        Returns:
            是否成功发送
        """
        if not self.should_send_notification(alert):
            return False
        
        success = False
        
        # 发送到控制台
        if self.config.enable_console:
            console_success = self._send_to_console(alert)
            success = success or console_success
        
        # 发送到文件
        if self.config.enable_file:
            file_success = self._send_to_file(alert)
            success = success or file_success
        
        # 发送到WhatsApp
        if self.config.enable_whatsapp:
            whatsapp_success = self._send_to_whatsapp(alert)
            success = success or whatsapp_success
        
        # 调用自定义处理器
        for handler in self.custom_handlers:
            try:
                handler(alert)
                success = True
            except Exception as e:
                print(f"自定义通知处理器执行失败: {e}")
        
        # 更新冷却时间
        if success:
            self.cooldown_tracker[alert.alert_id] = datetime.now()
            self.stats["notifications_sent"] += 1
            self.stats["last_notification"] = datetime.now()
        
        return success
    
    def _send_to_console(self, alert: Alert) -> bool:
        """发送到控制台"""
        try:
            # 确定表情符号
            alert_emoji = "ℹ️"
            if alert.level == AlertLevel.WARNING:
                alert_emoji = "⚠️"
            elif alert.level == AlertLevel.ERROR:
                alert_emoji = "❌"
            elif alert.level == AlertLevel.CRITICAL:
                alert_emoji = "🔥"
            
            console_output = f"""
{alert_emoji} {alert.level.value.upper()} 告警通知
时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
来源: {alert.source}
标题: {alert.title}

{alert.message}
"""
            print(console_output.strip())
            return True
            
        except Exception as e:
            print(f"控制台通知失败: {e}")
            return False
    
    def _send_to_file(self, alert: Alert) -> bool:
        """发送到文件"""
        try:
            log_entry = {
                "timestamp": alert.timestamp.isoformat(),
                "alert_id": alert.alert_id,
                "level": alert.level.value,
                "source": alert.source,
                "title": alert.title,
                "message": alert.message,
                "context": alert.context
            }
            
            import json
            log_line = json.dumps(log_entry, ensure_ascii=False)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config.file_path), exist_ok=True)
            
            with open(self.config.file_path, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
            
            return True
            
        except Exception as e:
            print(f"文件通知失败: {e}")
            return False
    
    def _send_to_whatsapp(self, alert: Alert) -> bool:
        """发送到WhatsApp"""
        if not WHATSAPP_AVAILABLE:
            return False
        
        try:
            # 构建WhatsApp消息
            alert_emoji = "ℹ️"
            if alert.level == AlertLevel.WARNING:
                alert_emoji = "⚠️"
            elif alert.level == AlertLevel.ERROR:
                alert_emoji = "❌"
            elif alert.level == AlertLevel.CRITICAL:
                alert_emoji = "🔥"
            
            # 简化消息格式以适应WhatsApp限制
            whatsapp_message = f"""
{alert_emoji} 系统告警 {alert_emoji}

{alert.title}

级别: {alert.level.value.upper()}
来源: {alert.source}
时间: {alert.timestamp.strftime('%H:%M:%S')}

{alert.message[:200]}{'...' if len(alert.message) > 200 else ''}
"""
            # 发送消息
            recipient = self.config.whatsapp_recipient
            if not recipient:
                # 使用默认收件人
                recipient = os.getenv("WHATSAPP_NUMBER", "+8618966719971")  # 默认号码
            
            success = send_whatsapp_message(whatsapp_message.strip())
            return success
            
        except Exception as e:
            print(f"WhatsApp通知失败: {e}")
            return False
    
    def register_custom_handler(self, handler: Callable[[Alert], None]):
        """注册自定义通知处理器"""
        self.custom_handlers.append(handler)
    
    def clear_cooldown(self, alert_id: Optional[str] = None):
        """
        清除冷却时间
        
        Args:
            alert_id: 告警ID，如果为None则清除所有
        """
        if alert_id:
            if alert_id in self.cooldown_tracker:
                del self.cooldown_tracker[alert_id]
        else:
            self.cooldown_tracker.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取通知统计
        
        Returns:
            统计信息字典
        """
        return {
            **self.stats,
            "cooldown_tracker_size": len(self.cooldown_tracker),
            "custom_handlers_count": len(self.custom_handlers),
            "config": {
                "enable_console": self.config.enable_console,
                "enable_file": self.config.enable_file,
                "enable_whatsapp": self.config.enable_whatsapp,
                "min_severity_for_whatsapp": self.config.min_severity_for_whatsapp.value,
                "cooldown_seconds": self.config.cooldown_seconds
            }
        }
    
    def format_alert_for_display(self, alert: Alert, format_type: str = "compact") -> str:
        """
        格式化告警用于显示
        
        Args:
            alert: 告警对象
            format_type: 格式类型 ("compact", "detailed", "whatsapp")
            
        Returns:
            格式化后的字符串
        """
        if format_type == "compact":
            alert_emoji = "ℹ️"
            if alert.level == AlertLevel.WARNING:
                alert_emoji = "⚠️"
            elif alert.level == AlertLevel.ERROR:
                alert_emoji = "❌"
            elif alert.level == AlertLevel.CRITICAL:
                alert_emoji = "🔥"
            
            return f"{alert_emoji} {alert.source}: {alert.message[:50]}..."
        
        elif format_type == "detailed":
            alert_emoji = "ℹ️"
            if alert.level == AlertLevel.WARNING:
                alert_emoji = "⚠️"
            elif alert.level == AlertLevel.ERROR:
                alert_emoji = "❌"
            elif alert.level == AlertLevel.CRITICAL:
                alert_emoji = "🔥"
            
            return f"""
{alert_emoji} {alert.level.value.upper()} 告警详情
{"=" * 40}
ID: {alert.alert_id}
时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
来源: {alert.source}
标题: {alert.title}

消息:
{alert.message}

上下文:
{alert.context if alert.context else "无"}
{"=" * 40}
""".strip()
        
        elif format_type == "whatsapp":
            alert_emoji = "ℹ️"
            if alert.level == AlertLevel.WARNING:
                alert_emoji = "⚠️"
            elif alert.level == AlertLevel.ERROR:
                alert_emoji = "❌"
            elif alert.level == AlertLevel.CRITICAL:
                alert_emoji = "🔥"
            
            return f"""
{alert_emoji} 系统告警 {alert_emoji}

*{alert.title}*

级别: *{alert.level.value.upper()}*
来源: {alert.source}
时间: {alert.timestamp.strftime('%H:%M')}

{alert.message[:180]}{'...' if len(alert.message) > 180 else ''}
""".strip()
        
        else:
            return str(alert)


def create_default_notifier() -> AlertNotifier:
    """
    创建默认的告警通知器
    
    Returns:
        配置好的告警通知器实例
    """
    config = NotificationConfig(
        enable_console=True,
        enable_file=True,
        enable_whatsapp=True,
        file_path="./logs/alerts.log",
        whatsapp_recipient=os.getenv("WHATSAPP_NUMBER", "+8618966719971"),
        min_severity_for_whatsapp=AlertLevel.WARNING,  # 只发送warning及以上到WhatsApp
        cooldown_seconds=300  # 5分钟冷却
    )
    
    return AlertNotifier(config)


def test_alert_notifier():
    """测试告警通知器"""
    print("🧪 测试AlertNotifier")
    print("=" * 60)
    
    notifier = create_default_notifier()
    
    # 创建测试告警
    test_alert = Alert(
        alert_id="test_notification_1",
        level=AlertLevel.WARNING,
        title="测试告警通知",
        message="这是一个测试告警通知，用于验证通知系统功能。",
        source="test_component",
        timestamp=datetime.now(),
        context={"test": True, "priority": "medium"}
    )
    
    print("测试1: 发送通知")
    success = notifier.send_notification(test_alert)
    print(f"  通知发送结果: {'成功' if success else '失败'}")
    
    print("\n测试2: 冷却时间检查")
    success2 = notifier.send_notification(test_alert)
    print(f"  第二次发送结果: {'成功' if success2 else '失败'}")
    print(f"  预期: 失败（冷却时间生效）")
    
    print("\n测试3: 获取统计")
    stats = notifier.get_statistics()
    print(f"  发送通知数: {stats['notifications_sent']}")
    print(f"  冷却阻止数: {stats['notifications_blocked_by_cooldown']}")
    
    print("\n测试4: 格式化显示")
    formatted = notifier.format_alert_for_display(test_alert, "compact")
    print(f"  紧凑格式: {formatted}")
    
    print("\n✅ 告警通知器测试完成")


if __name__ == "__main__":
    test_alert_notifier()
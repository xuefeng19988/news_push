#!/usr/bin/env python3
"""
告警管理器
集成告警升级系统，协调告警生成、处理和通知
"""

import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass

# 导入situation-monitor核心类型
from ..core.monitor import Alert, AlertLevel
from .escalation import AlertEscalationManager, AlertRecord, AlertState


class AlertManager:
    """
    告警管理器
    负责协调告警的整个生命周期：生成、升级、通知和解决
    """
    
    def __init__(self, 
                 escalation_manager: Optional[AlertEscalationManager] = None,
                 enable_notifications: bool = True):
        """
        初始化告警管理器
        
        Args:
            escalation_manager: 告警升级管理器实例
            enable_notifications: 是否启用通知
        """
        self.escalation_manager = escalation_manager or AlertEscalationManager()
        self.enable_notifications = enable_notifications
        
        # 通知回调列表
        self.notification_callbacks: List[Callable[[Alert], None]] = []
        
        # 已静音的告警源
        self.muted_sources: Set[str] = set()
        
        # 告警统计
        self.stats = {
            "alerts_processed": 0,
            "alerts_escalated": 0,
            "notifications_sent": 0,
            "last_processed": None
        }
        
        # 告警过滤器
        self.alert_filters = []
    
    def register_notification_callback(self, callback: Callable[[Alert], None]):
        """
        注册通知回调
        
        Args:
            callback: 通知回调函数
        """
        if callback not in self.notification_callbacks:
            self.notification_callbacks.append(callback)
    
    def mute_source(self, source: str):
        """静音指定源的告警"""
        self.muted_sources.add(source)
    
    def unmute_source(self, source: str):
        """取消静音指定源的告警"""
        if source in self.muted_sources:
            self.muted_sources.remove(source)
    
    def process_alert(self, alert: Alert) -> AlertRecord:
        """
        处理告警（主要入口点）
        
        Args:
            alert: 原始告警对象
            
        Returns:
            处理后的告警记录
        """
        # 更新统计
        self.stats["alerts_processed"] += 1
        self.stats["last_processed"] = datetime.now()
        
        # 检查是否静音
        if alert.source in self.muted_sources:
            # 仍然记录，但不升级或通知
            alert_record, is_new = self.escalation_manager.process_alert(alert)
            return alert_record
        
        # 应用过滤器
        for alert_filter in self.alert_filters:
            if not alert_filter(alert):
                # 过滤器拒绝此告警
                return None
        
        # 处理告警升级
        alert_record, is_new = self.escalation_manager.process_alert(alert)
        
        # 检查是否需要升级
        if alert_record.escalation_level > 0:
            self.stats["alerts_escalated"] += 1
            
            # 生成升级后的告警
            escalated_alert = alert_record.to_situation_alert()
            
            # 发送通知
            if self.enable_notifications:
                self._send_notification(escalated_alert)
        
        # 如果是新告警并且级别较高，也发送通知
        elif is_new and alert_record.severity in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
            if self.enable_notifications:
                self._send_notification(alert)
        
        return alert_record
    
    def _send_notification(self, alert: Alert):
        """
        发送告警通知
        
        Args:
            alert: 告警对象
        """
        if not self.notification_callbacks:
            # 如果没有注册回调，使用默认处理
            self._default_notification(alert)
            return
        
        # 调用所有注册的回调
        for callback in self.notification_callbacks:
            try:
                callback(alert)
                self.stats["notifications_sent"] += 1
            except Exception as e:
                print(f"告警通知回调执行失败: {e}")
    
    def _default_notification(self, alert: Alert):
        """
        默认告警通知处理（打印到控制台）
        
        Args:
            alert: 告警对象
        """
        alert_emoji = "ℹ️"
        if alert.level == AlertLevel.WARNING:
            alert_emoji = "⚠️"
        elif alert.level == AlertLevel.ERROR:
            alert_emoji = "❌"
        elif alert.level == AlertLevel.CRITICAL:
            alert_emoji = "🔥"
        
        notification = f"""
{alert_emoji} 系统告警通知
====================
标题: {alert.title}
级别: {alert.level.value}
来源: {alert.source}
时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

{alert.message}
====================
        """
        
        print(notification.strip())
    
    def get_active_alerts(self) -> List[AlertRecord]:
        """
        获取所有活动告警
        
        Returns:
            活动告警列表
        """
        return self.escalation_manager.get_active_alerts()
    
    def get_escalated_alerts(self, min_level: int = 1) -> List[AlertRecord]:
        """
        获取已升级的告警
        
        Args:
            min_level: 最小升级级别
            
        Returns:
            已升级告警列表
        """
        return self.escalation_manager.get_escalated_alerts(min_level)
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        解决指定告警
        
        Args:
            alert_id: 告警ID
            
        Returns:
            是否成功解决
        """
        return self.escalation_manager.resolve_alert(alert_id)
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        确认指定告警
        
        Args:
            alert_id: 告警ID
            
        Returns:
            是否成功确认
        """
        return self.escalation_manager.acknowledge_alert(alert_id)
    
    def get_alert_summary(self) -> str:
        """
        获取告警摘要
        
        Returns:
            告警摘要文本
        """
        active_alerts = self.get_active_alerts()
        escalated_alerts = self.get_escalated_alerts(min_level=1)
        
        if not active_alerts:
            return "✅ 目前没有活动告警"
        
        summary = f"📊 告警摘要 ({len(active_alerts)}个活动告警)\n"
        summary += "=" * 40 + "\n"
        
        # 按严重性分组
        severity_groups = {}
        for alert in active_alerts:
            severity = alert.severity.value
            if severity not in severity_groups:
                severity_groups[severity] = []
            severity_groups[severity].append(alert)
        
        for severity, alerts in severity_groups.items():
            severity_emoji = "ℹ️"
            if severity == "warning":
                severity_emoji = "⚠️"
            elif severity == "error":
                severity_emoji = "❌"
            elif severity == "critical":
                severity_emoji = "🔥"
            
            summary += f"\n{severity_emoji} {severity.upper()} ({len(alerts)}个):\n"
            
            for alert in alerts[:3]:  # 只显示前3个
                duration_minutes = (datetime.now() - alert.first_seen).total_seconds() / 60
                summary += f"  • {alert.component}: {alert.message[:50]}"
                if len(alert.message) > 50:
                    summary += "..."
                
                if alert.escalation_level > 0:
                    summary += f" [升级级别: {alert.escalation_level}]"
                
                summary += f" ({duration_minutes:.1f}分钟)\n"
            
            if len(alerts) > 3:
                summary += f"  还有 {len(alerts) - 3} 个告警...\n"
        
        # 添加已升级告警信息
        if escalated_alerts:
            summary += f"\n🚨 已升级告警 ({len(escalated_alerts)}个):\n"
            for alert in escalated_alerts[:2]:
                summary += f"  • {alert.component} (级别{alert.escalation_level}): {alert.message[:40]}...\n"
        
        # 添加统计信息
        stats = self.escalation_manager.get_statistics()
        summary += f"\n📈 统计: "
        summary += f"总告警: {stats['total_alerts']}, "
        summary += f"活动: {stats['active_alerts']}, "
        summary += f"已升级: {stats['escalated_alerts']}"
        
        return summary
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取管理器统计信息
        
        Returns:
            统计信息字典
        """
        escalation_stats = self.escalation_manager.get_statistics()
        
        return {
            **self.stats,
            **escalation_stats,
            "muted_sources_count": len(self.muted_sources),
            "notification_callbacks_count": len(self.notification_callbacks),
            "alert_filters_count": len(self.alert_filters)
        }
    
    def register_filter(self, filter_func: Callable[[Alert], bool]):
        """
        注册告警过滤器
        
        Args:
            filter_func: 过滤器函数，返回True表示接受告警
        """
        self.alert_filters.append(filter_func)
    
    def add_simple_filter(self, 
                          min_severity: Optional[AlertLevel] = None,
                          excluded_sources: Optional[List[str]] = None):
        """
        添加简单过滤器
        
        Args:
            min_severity: 最小严重性级别（低于此级别的告警将被过滤）
            excluded_sources: 排除的告警源列表
        """
        def simple_filter(alert: Alert) -> bool:
            # 检查严重性
            if min_severity:
                severity_order = {
                    AlertLevel.INFO: 0,
                    AlertLevel.WARNING: 1,
                    AlertLevel.ERROR: 2,
                    AlertLevel.CRITICAL: 3
                }
                
                if severity_order.get(alert.level, 0) < severity_order[min_severity]:
                    return False
            
            # 检查排除源
            if excluded_sources and alert.source in excluded_sources:
                return False
            
            return True
        
        self.register_filter(simple_filter)
    
    def cleanup(self, days_to_keep: int = 30):
        """清理旧告警"""
        self.escalation_manager.cleanup_old_alerts(days_to_keep)


def create_default_alert_manager(storage_file: str = None) -> AlertManager:
    """
    创建默认的告警管理器
    
    Args:
        storage_file: 告警存储文件路径，如果为None则使用默认路径
        
    Returns:
        配置好的告警管理器实例
    """
    import os
    
    # 设置默认存储文件路径
    if storage_file is None:
        logs_dir = "./logs"
        os.makedirs(logs_dir, exist_ok=True)
        storage_file = os.path.join(logs_dir, "situation_alerts.json")
    
    # 创建告警升级管理器
    from .escalation import AlertEscalationManager
    escalation_manager = AlertEscalationManager(storage_file=storage_file)
    
    # 创建告警管理器
    manager = AlertManager(
        escalation_manager=escalation_manager,
        enable_notifications=True
    )
    
    # 添加默认过滤器：过滤info级别的微信未配置告警
    manager.add_simple_filter(
        min_severity=AlertLevel.WARNING,  # 只处理warning及以上级别
        excluded_sources=[]  # 可以添加要排除的源
    )
    
    return manager


def test_alert_manager():
    """测试告警管理器"""
    print("🧪 测试AlertManager")
    print("=" * 60)
    
    manager = create_default_alert_manager()
    
    # 测试1: 处理低级别告警（应该被过滤）
    info_alert = Alert(
        alert_id="test_info_1",
        level=AlertLevel.INFO,
        title="信息级别告警",
        message="这是一个信息级别告警",
        source="test_component",
        timestamp=datetime.now(),
        context={"test": True}
    )
    
    print("测试1: 处理信息级别告警")
    result = manager.process_alert(info_alert)
    if result:
        print(f"  ❌ 信息级别告警未被过滤")
    else:
        print(f"  ✅ 信息级别告警正确被过滤")
    
    # 测试2: 处理警告级别告警
    warning_alert = Alert(
        alert_id="test_warning_1",
        level=AlertLevel.WARNING,
        title="警告级别告警",
        message="这是一个警告级别告警",
        source="database",
        timestamp=datetime.now(),
        context={"component": "database", "error": "连接超时"}
    )
    
    print("\n测试2: 处理警告级别告警")
    result = manager.process_alert(warning_alert)
    if result:
        print(f"  ✅ 处理警告级别告警成功")
        print(f"    告警ID: {result.alert_id}")
        print(f"    组件: {result.component}")
        print(f"    升级级别: {result.escalation_level}")
    else:
        print(f"  ❌ 警告级别告警处理失败")
    
    # 测试3: 获取摘要
    print("\n测试3: 获取告警摘要")
    summary = manager.get_alert_summary()
    print(summary[:200] + "..." if len(summary) > 200 else summary)
    
    # 测试4: 获取统计
    print("\n测试4: 获取统计信息")
    stats = manager.get_statistics()
    print(f"  处理告警数: {stats['alerts_processed']}")
    print(f"  已升级告警: {stats['alerts_escalated']}")
    print(f"  活动告警数: {stats['active_alerts']}")
    
    print("\n✅ 告警管理器测试完成")


if __name__ == "__main__":
    test_alert_manager()
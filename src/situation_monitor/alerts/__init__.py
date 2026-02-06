"""
告警管理模块
基于situation-monitor架构的智能告警系统
"""

from .escalation import AlertState, AlertRecord, AlertEscalationManager
from .manager import AlertManager, create_default_alert_manager
from .notifications import AlertNotifier, NotificationConfig, create_default_notifier
from .integration import LegacyCompatibleAlertManager, HealthCheckAlertAdapter, create_legacy_compatible_manager

# 导出主要组件
__all__ = [
    'AlertState',
    'AlertRecord',
    'AlertEscalationManager',
    'AlertManager',
    'create_default_alert_manager',
    'AlertNotifier',
    'NotificationConfig',
    'create_default_notifier',
    'LegacyCompatibleAlertManager',
    'HealthCheckAlertAdapter',
    'create_legacy_compatible_manager',
]
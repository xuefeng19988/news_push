"""
集成模块
包含旧系统适配器和推送服务集成
"""

from .legacy_adapter import LegacyHealthChecker
from .push_service import SituationMonitorPushService, run_situation_monitor_push_service

# 导出主要组件
__all__ = [
    'LegacyHealthChecker',
    'SituationMonitorPushService',
    'run_situation_monitor_push_service',
]
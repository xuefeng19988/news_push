"""
Situation-Monitor 智能监控系统
基于情境感知的实时监控、智能告警和自动化修复系统
"""

__version__ = "1.0.0"
__author__ = "智能新闻推送系统团队"

from .core.monitor import SituationMonitor, Check, CheckResult, Alert, CheckStatus, AlertLevel

# 导出主要组件
__all__ = [
    'SituationMonitor',
    'Check',
    'CheckResult', 
    'Alert',
    'CheckStatus',
    'AlertLevel',
]
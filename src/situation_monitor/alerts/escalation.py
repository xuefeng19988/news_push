#!/usr/bin/env python3
"""
告警升级系统
基于situation-monitor架构的智能告警升级管理
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# 导入situation-monitor核心类型
from ..core.monitor import Alert, AlertLevel


class AlertState(Enum):
    """告警状态（保持与原有系统兼容）"""
    NEW = "new"          # 新告警
    ACKNOWLEDGED = "acknowledged"  # 已确认
    RESOLVED = "resolved"  # 已解决


@dataclass
class AlertRecord:
    """
    告警记录（增强版）
    用于跟踪告警历史、升级状态和解决情况
    """
    alert_id: str
    component: str
    severity: AlertLevel  # 使用situation-monitor的AlertLevel
    message: str
    first_seen: datetime
    last_seen: datetime
    state: AlertState
    escalation_level: int = 0  # 升级级别 (0=初始, 1=轻微升级, 2=中度升级, 3=严重升级)
    count: int = 1  # 出现次数
    context: Optional[Dict[str, Any]] = None  # 附加上下文信息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "alert_id": self.alert_id,
            "component": self.component,
            "severity": self.severity.value,
            "message": self.message,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "state": self.state.value,
            "escalation_level": self.escalation_level,
            "count": self.count,
            "context": self.context or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlertRecord':
        """从字典创建"""
        # 兼容性处理：将字符串转换为AlertLevel
        severity_str = data["severity"]
        if isinstance(severity_str, str):
            severity = AlertLevel(severity_str)
        else:
            severity = severity_str
        
        return cls(
            alert_id=data["alert_id"],
            component=data["component"],
            severity=severity,
            message=data["message"],
            first_seen=datetime.fromisoformat(data["first_seen"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
            state=AlertState(data["state"]),
            escalation_level=data.get("escalation_level", 0),
            count=data.get("count", 1),
            context=data.get("context", {})
        )
    
    def to_situation_alert(self) -> Alert:
        """转换为situation-monitor的Alert对象"""
        # 基于升级级别调整告警标题
        title_prefix = ""
        if self.escalation_level == 1:
            title_prefix = "⚠️ 轻微升级: "
        elif self.escalation_level == 2:
            title_prefix = "🚨 中度升级: "
        elif self.escalation_level >= 3:
            title_prefix = "🔥 严重升级: "
        
        title = f"{title_prefix}{self.component} - {self.message[:50]}{'...' if len(self.message) > 50 else ''}"
        
        # 创建详细的告警消息
        alert_message = f"""
{self.component} 告警
严重性: {self.severity.value}
消息: {self.message}
首次出现: {self.first_seen.strftime('%Y-%m-%d %H:%M:%S')}
持续时间: {self._calculate_duration()}
升级级别: {self.escalation_level}
出现次数: {self.count}
状态: {self.state.value}
        """
        
        return Alert(
            alert_id=self.alert_id,
            level=self.severity,
            title=title,
            message=alert_message.strip(),
            source=self.component,
            timestamp=self.last_seen,
            context=self.context or {}
        )
    
    def _calculate_duration(self) -> str:
        """计算告警持续时间"""
        duration = self.last_seen - self.first_seen
        total_seconds = duration.total_seconds()
        
        if total_seconds < 60:
            return f"{int(total_seconds)}秒"
        elif total_seconds < 3600:
            return f"{int(total_seconds // 60)}分钟"
        elif total_seconds < 86400:
            return f"{int(total_seconds // 3600)}小时"
        else:
            return f"{int(total_seconds // 86400)}天"


class AlertEscalationManager:
    """
    告警升级管理器
    根据告警持续时间自动提升告警级别，实现智能告警管理
    """
    
    def __init__(self, storage_file: str = "alert_history.json"):
        """
        初始化告警升级管理器
        
        Args:
            storage_file: 告警历史存储文件路径
        """
        self.storage_file = storage_file
        self.alerts: Dict[str, AlertRecord] = {}  # alert_id -> AlertRecord
        
        # 智能升级规则配置
        self.escalation_rules = {
            # (持续时间分钟, 最小严重性): 升级级别
            # 持续时间越长，升级级别越高
            (0, 15): 0,    # 0-15分钟: 级别0 (初始)
            (15, 60): 1,   # 15-60分钟: 级别1 (轻微升级)
            (60, 240): 2,  # 60-240分钟: 级别2 (中度升级)
            (240, float('inf')): 3  # 240+分钟: 级别3 (严重升级)
        }
        
        # 严重性映射到初始升级级别
        self.severity_to_base_level = {
            AlertLevel.INFO: 0,
            AlertLevel.WARNING: 0,
            AlertLevel.ERROR: 1,
            AlertLevel.CRITICAL: 2
        }
        
        # 加载历史告警
        self._load_alerts()
    
    def _load_alerts(self):
        """加载告警历史"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for alert_data in data.get("alerts", []):
                        try:
                            alert = AlertRecord.from_dict(alert_data)
                            self.alerts[alert.alert_id] = alert
                        except Exception as e:
                            print(f"警告: 加载告警记录失败: {e}")
        except Exception as e:
            print(f"警告: 加载告警文件失败: {e}")
    
    def _save_alerts(self):
        """保存告警历史"""
        try:
            alerts_data = [alert.to_dict() for alert in self.alerts.values()]
            data = {
                "version": "1.0.0",
                "saved_at": datetime.now().isoformat(),
                "alert_count": len(alerts_data),
                "alerts": alerts_data
            }
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"错误: 保存告警文件失败: {e}")
    
    def _calculate_escalation_level(self, severity: AlertLevel, duration_minutes: float) -> int:
        """
        计算告警升级级别
        
        Args:
            severity: 告警严重性
            duration_minutes: 持续时间（分钟）
            
        Returns:
            升级级别 (0-3)
        """
        # 基础级别基于严重性
        base_level = self.severity_to_base_level.get(severity, 0)
        
        # 基于持续时间增加升级级别
        for (min_dur, max_dur), level_addition in self.escalation_rules.items():
            if min_dur <= duration_minutes < max_dur:
                return min(base_level + level_addition, 3)  # 最大级别为3
        
        return min(base_level + 3, 3)  # 默认最高升级
    
    def process_alert(self, alert: Alert) -> Tuple[AlertRecord, bool]:
        """
        处理新告警
        
        Args:
            alert: situation-monitor告警对象
            
        Returns:
            (告警记录, 是否是新告警)
        """
        current_time = datetime.now()
        
        # 生成稳定的告警ID
        alert_id = alert.alert_id if alert.alert_id else f"alert_{alert.source}_{int(time.time())}"
        
        if alert_id in self.alerts:
            # 现有告警：更新信息
            existing_alert = self.alerts[alert_id]
            existing_alert.last_seen = current_time
            existing_alert.count += 1
            existing_alert.severity = alert.level  # 更新严重性（可能变化）
            
            # 重新计算升级级别
            duration_minutes = (current_time - existing_alert.first_seen).total_seconds() / 60
            existing_alert.escalation_level = self._calculate_escalation_level(
                alert.level, duration_minutes
            )
            
            self._save_alerts()
            return existing_alert, False
        else:
            # 新告警：创建记录
            new_alert = AlertRecord(
                alert_id=alert_id,
                component=alert.source or "unknown",
                severity=alert.level,
                message=alert.message,
                first_seen=current_time,
                last_seen=current_time,
                state=AlertState.NEW,
                escalation_level=self.severity_to_base_level.get(alert.level, 0),
                count=1,
                context=alert.context
            )
            
            self.alerts[alert_id] = new_alert
            self._save_alerts()
            return new_alert, True
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        解决告警
        
        Args:
            alert_id: 告警ID
            
        Returns:
            是否成功解决
        """
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.state = AlertState.RESOLVED
            alert.last_seen = datetime.now()
            self._save_alerts()
            return True
        return False
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        确认告警
        
        Args:
            alert_id: 告警ID
            
        Returns:
            是否成功确认
        """
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.state = AlertState.ACKNOWLEDGED
            alert.last_seen = datetime.now()
            self._save_alerts()
            return True
        return False
    
    def get_active_alerts(self) -> List[AlertRecord]:
        """
        获取活动中的告警（未解决）
        
        Returns:
            活动告警列表
        """
        return [
            alert for alert in self.alerts.values()
            if alert.state != AlertState.RESOLVED
        ]
    
    def get_escalated_alerts(self, min_level: int = 1) -> List[AlertRecord]:
        """
        获取已升级的告警
        
        Args:
            min_level: 最小升级级别
            
        Returns:
            已升级告警列表
        """
        return [
            alert for alert in self.alerts.values()
            if alert.escalation_level >= min_level and alert.state != AlertState.RESOLVED
        ]
    
    def get_alerts_by_component(self, component: str) -> List[AlertRecord]:
        """
        按组件获取告警
        
        Args:
            component: 组件名称
            
        Returns:
            组件相关告警列表
        """
        return [
            alert for alert in self.alerts.values()
            if alert.component == component
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取告警统计信息
        
        Returns:
            统计信息字典
        """
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())
        escalated_alerts = len(self.get_escalated_alerts(min_level=1))
        
        # 按严重性统计
        severity_counts = {
            AlertLevel.INFO.value: 0,
            AlertLevel.WARNING.value: 0,
            AlertLevel.ERROR.value: 0,
            AlertLevel.CRITICAL.value: 0
        }
        
        for alert in self.alerts.values():
            if alert.severity.value in severity_counts:
                severity_counts[alert.severity.value] += 1
        
        # 按组件统计
        component_counts = {}
        for alert in self.alerts.values():
            component = alert.component
            component_counts[component] = component_counts.get(component, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "escalated_alerts": escalated_alerts,
            "severity_counts": severity_counts,
            "top_components": dict(sorted(component_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            "last_updated": datetime.now().isoformat()
        }
    
    def cleanup_old_alerts(self, days_to_keep: int = 30):
        """
        清理旧的已解决告警
        
        Args:
            days_to_keep: 保留天数
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        alerts_to_remove = []
        for alert_id, alert in self.alerts.items():
            if alert.state == AlertState.RESOLVED and alert.last_seen < cutoff_date:
                alerts_to_remove.append(alert_id)
        
        for alert_id in alerts_to_remove:
            del self.alerts[alert_id]
        
        if alerts_to_remove:
            print(f"清理了 {len(alerts_to_remove)} 个旧告警")
            self._save_alerts()


def test_alert_escalation():
    """测试告警升级系统"""
    print("🧪 测试AlertEscalationManager")
    print("=" * 60)
    
    # 创建测试用的临时文件
    import tempfile
    import os
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    temp_file.close()
    
    try:
        manager = AlertEscalationManager(storage_file=temp_file.name)
        
        # 创建测试告警
        test_alert = Alert(
            alert_id="test_alert_1",
            level=AlertLevel.WARNING,
            title="测试告警",
            message="这是一个测试告警",
            source="test_component",
            timestamp=datetime.now(),
            context={"test": True}
        )
        
        # 处理告警
        alert_record, is_new = manager.process_alert(test_alert)
        print(f"处理告警结果:")
        print(f"  是新告警: {is_new}")
        print(f"  告警ID: {alert_record.alert_id}")
        print(f"  组件: {alert_record.component}")
        print(f"  严重性: {alert_record.severity.value}")
        print(f"  升级级别: {alert_record.escalation_level}")
        
        # 获取统计数据
        stats = manager.get_statistics()
        print(f"\n告警统计:")
        print(f"  总告警数: {stats['total_alerts']}")
        print(f"  活动告警: {stats['active_alerts']}")
        print(f"  已升级告警: {stats['escalated_alerts']}")
        
        # 转换为situation-alert
        situation_alert = alert_record.to_situation_alert()
        print(f"\n转换后的situation-alert:")
        print(f"  标题: {situation_alert.title}")
        print(f"  级别: {situation_alert.level.value}")
        
        print("\n✅ 告警升级系统测试完成")
        
    finally:
        # 清理临时文件
        os.unlink(temp_file.name)


if __name__ == "__main__":
    test_alert_escalation()
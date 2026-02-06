#!/usr/bin/env python3
"""
告警升级管理器
根据问题持续时间自动提升告警级别
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AlertSeverity(Enum):
    """告警严重性级别"""
    INFO = "info"        # 信息
    WARNING = "warning"  # 警告
    ERROR = "error"      # 错误
    CRITICAL = "critical"  # 严重


class AlertState(Enum):
    """告警状态"""
    NEW = "new"          # 新告警
    ACKNOWLEDGED = "acknowledged"  # 已确认
    RESOLVED = "resolved"  # 已解决


@dataclass
class AlertRecord:
    """告警记录"""
    alert_id: str
    component: str
    severity: AlertSeverity
    message: str
    first_seen: datetime
    last_seen: datetime
    state: AlertState
    escalation_level: int = 0  # 升级级别 (0=初始, 1=轻微升级, 2=中度升级, 3=严重升级)
    count: int = 1  # 出现次数
    
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
            "count": self.count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlertRecord':
        """从字典创建"""
        return cls(
            alert_id=data["alert_id"],
            component=data["component"],
            severity=AlertSeverity(data["severity"]),
            message=data["message"],
            first_seen=datetime.fromisoformat(data["first_seen"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
            state=AlertState(data["state"]),
            escalation_level=data.get("escalation_level", 0),
            count=data.get("count", 1)
        )


class AlertEscalationManager:
    """告警升级管理器"""
    
    def __init__(self, storage_file: str = "alert_history.json"):
        """
        初始化告警升级管理器
        
        Args:
            storage_file: 告警历史存储文件
        """
        self.storage_file = storage_file
        self.alerts: Dict[str, AlertRecord] = {}  # alert_id -> AlertRecord
        
        # 升级规则配置
        self.escalation_rules = {
            # (持续时间分钟, 升级级别)
            (0, 15): 0,    # 0-15分钟: 级别0 (初始)
            (15, 60): 1,   # 15-60分钟: 级别1 (轻微升级)
            (60, 240): 2,  # 60-240分钟: 级别2 (中度升级)
            (240, float('inf')): 3  # 240+分钟: 级别3 (严重升级)
        }
        
        # 加载历史告警
        self._load_alerts()
    
    def _load_alerts(self):
        """加载告警历史"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for alert_data in data.get("alerts", []):
                    try:
                        alert = AlertRecord.from_dict(alert_data)
                        self.alerts[alert.alert_id] = alert
                    except:
                        continue
                        
                print(f"📂 加载 {len(self.alerts)} 条告警记录")
                
            except Exception as e:
                print(f"❌ 加载告警历史失败: {e}")
    
    def _save_alerts(self):
        """保存告警历史"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "alerts": [alert.to_dict() for alert in self.alerts.values()]
            }
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ 保存告警历史失败: {e}")
    
    def process_health_report(self, report: Dict[str, Any]) -> List[AlertRecord]:
        """
        处理健康检查报告，生成或更新告警
        
        Args:
            report: 健康检查报告
            
        Returns:
            需要升级的告警列表
        """
        current_time = datetime.now()
        new_or_updated_alerts = []
        
        # 从报告中提取问题
        issues = self._extract_issues_from_report(report)
        
        for issue in issues:
            # 生成唯一的告警ID
            alert_id = self._generate_alert_id(issue)
            
            if alert_id in self.alerts:
                # 更新现有告警
                alert = self._update_existing_alert(alert_id, issue, current_time)
            else:
                # 创建新告警
                alert = self._create_new_alert(alert_id, issue, current_time)
            
            new_or_updated_alerts.append(alert)
        
        # 检查告警是否需要升级
        escalated_alerts = self._check_escalations(current_time)
        
        # 保存更新
        self._save_alerts()
        
        return escalated_alerts
    
    def _extract_issues_from_report(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从健康检查报告中提取问题"""
        issues = []
        checks = report.get("checks", {})
        
        for check_id, check_result in checks.items():
            status = check_result.get("status", "unknown")
            
            if status in ["warning", "unhealthy"]:
                component = check_result.get("component", check_id)
                details = check_result.get("details", {})
                
                if "error" in details:
                    issue = {
                        "component": component,
                        "message": details["error"],
                        "severity": AlertSeverity.ERROR if status == "unhealthy" else AlertSeverity.WARNING,
                        "details": details
                    }
                    issues.append(issue)
                elif "warnings" in details and details["warnings"]:
                    for warning in details["warnings"]:
                        issue = {
                            "component": component,
                            "message": warning,
                            "severity": AlertSeverity.WARNING,
                            "details": {"warning": warning}
                        }
                        issues.append(issue)
                else:
                    issue = {
                        "component": component,
                        "message": f"{component} 状态异常 ({status})",
                        "severity": AlertSeverity.WARNING,
                        "details": {"status": status}
                    }
                    issues.append(issue)
        
        return issues
    
    def _generate_alert_id(self, issue: Dict[str, Any]) -> str:
        """生成唯一的告警ID"""
        component = issue["component"]
        message_hash = hash(issue["message"]) % 10000
        return f"{component}_{abs(message_hash)}"
    
    def _create_new_alert(self, alert_id: str, issue: Dict[str, Any], current_time: datetime) -> AlertRecord:
        """创建新告警"""
        alert = AlertRecord(
            alert_id=alert_id,
            component=issue["component"],
            severity=issue["severity"],
            message=issue["message"],
            first_seen=current_time,
            last_seen=current_time,
            state=AlertState.NEW,
            escalation_level=0,
            count=1
        )
        
        self.alerts[alert_id] = alert
        print(f"🚨 新告警: {alert.component} - {alert.message}")
        
        return alert
    
    def _update_existing_alert(self, alert_id: str, issue: Dict[str, Any], current_time: datetime) -> AlertRecord:
        """更新现有告警"""
        alert = self.alerts[alert_id]
        
        # 更新最后出现时间
        alert.last_seen = current_time
        
        # 增加计数
        alert.count += 1
        
        # 如果状态是已解决，重新激活
        if alert.state == AlertState.RESOLVED:
            alert.state = AlertState.NEW
            print(f"🔄 告警重新激活: {alert.component}")
        
        return alert
    
    def _check_escalations(self, current_time: datetime) -> List[AlertRecord]:
        """检查告警是否需要升级"""
        escalated_alerts = []
        
        for alert_id, alert in self.alerts.items():
            if alert.state in [AlertState.RESOLVED, AlertState.ACKNOWLEDGED]:
                continue
            
            # 计算持续时间（分钟）
            duration_minutes = (current_time - alert.first_seen).total_seconds() / 60
            
            # 确定升级级别
            new_escalation_level = self._calculate_escalation_level(duration_minutes)
            
            # 检查是否需要升级
            if new_escalation_level > alert.escalation_level:
                alert.escalation_level = new_escalation_level
                escalated_alerts.append(alert)
                
                # 根据升级级别调整严重性
                if new_escalation_level >= 2 and alert.severity == AlertSeverity.WARNING:
                    alert.severity = AlertSeverity.ERROR
                    print(f"📈 告警升级: {alert.component} -> 级别{new_escalation_level} (ERROR)")
                elif new_escalation_level >= 3:
                    alert.severity = AlertSeverity.CRITICAL
                    print(f"📈 告警升级: {alert.component} -> 级别{new_escalation_level} (CRITICAL)")
                else:
                    print(f"📈 告警升级: {alert.component} -> 级别{new_escalation_level}")
        
        return escalated_alerts
    
    def _calculate_escalation_level(self, duration_minutes: float) -> int:
        """根据持续时间计算升级级别"""
        for (min_dur, max_dur), level in self.escalation_rules.items():
            if min_dur <= duration_minutes < max_dur:
                return level
        return 0
    
    def acknowledge_alert(self, alert_id: str):
        """确认告警（标记为已确认）"""
        if alert_id in self.alerts:
            self.alerts[alert_id].state = AlertState.ACKNOWLEDGED
            print(f"✅ 告警已确认: {alert_id}")
            self._save_alerts()
    
    def resolve_alert(self, alert_id: str):
        """解决告警（标记为已解决）"""
        if alert_id in self.alerts:
            self.alerts[alert_id].state = AlertState.RESOLVED
            print(f"✅ 告警已解决: {alert_id}")
            self._save_alerts()
    
    def get_active_alerts(self) -> List[AlertRecord]:
        """获取活动中的告警（未解决）"""
        return [
            alert for alert in self.alerts.values()
            if alert.state != AlertState.RESOLVED
        ]
    
    def get_escalated_alerts(self, min_level: int = 1) -> List[AlertRecord]:
        """获取已升级的告警"""
        return [
            alert for alert in self.alerts.values()
            if alert.escalation_level >= min_level and alert.state != AlertState.RESOLVED
        ]
    
    def cleanup_old_alerts(self, days_to_keep: int = 30):
        """清理旧的告警记录"""
        cutoff_time = datetime.now() - timedelta(days=days_to_keep)
        
        old_count = 0
        new_alerts = {}
        
        for alert_id, alert in self.alerts.items():
            if alert.last_seen >= cutoff_time:
                new_alerts[alert_id] = alert
            else:
                old_count += 1
        
        if old_count > 0:
            self.alerts = new_alerts
            print(f"🧹 清理 {old_count} 条旧告警记录")
            self._save_alerts()
    
    def generate_escalation_summary(self) -> str:
        """生成升级摘要"""
        active_alerts = self.get_active_alerts()
        escalated_alerts = self.get_escalated_alerts(min_level=1)
        
        if not active_alerts:
            return "📊 告警状态: 无活动告警"
        
        summary = f"📊 告警升级摘要\n"
        summary += f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"活动告警: {len(active_alerts)} 个\n"
        summary += f"已升级告警: {len(escalated_alerts)} 个\n\n"
        
        # 按严重性分组
        severity_counts = {}
        for alert in active_alerts:
            severity = alert.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        if severity_counts:
            summary += "严重性分布:\n"
            for severity, count in sorted(severity_counts.items()):
                summary += f"  • {severity}: {count}个\n"
        
        # 列出严重告警
        critical_alerts = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
        if critical_alerts:
            summary += "\n🛑 严重告警:\n"
            for alert in critical_alerts[:3]:  # 最多显示3个
                duration_hours = (datetime.now() - alert.first_seen).total_seconds() / 3600
                summary += f"  • {alert.component}: {alert.message[:50]}... ({duration_hours:.1f}小时)\n"
        
        return summary


def test_alert_escalation():
    """测试告警升级管理器"""
    print("🧪 测试告警升级管理器")
    print("=" * 60)
    
    # 创建管理器（使用临时文件）
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
    
    try:
        manager = AlertEscalationManager(temp_file)
        
        # 模拟健康检查报告
        test_report = {
            "checks": {
                "database": {
                    "status": "healthy",
                    "component": "数据库"
                },
                "message_platforms": {
                    "status": "warning",
                    "component": "消息平台",
                    "details": {"error": "微信推送未配置"}
                },
                "system_resources": {
                    "status": "warning",
                    "component": "系统资源",
                    "details": {"warnings": ["CPU使用率偏高: 85%"]}
                }
            }
        }
        
        print("1. 处理测试报告...")
        escalated = manager.process_health_report(test_report)
        print(f"   发现 {len(manager.get_active_alerts())} 个活动告警")
        print(f"   升级 {len(escalated)} 个告警")
        
        print("\n2. 生成摘要...")
        summary = manager.generate_escalation_summary()
        print(summary)
        
        print("\n3. 模拟告警持续存在（升级检查）...")
        # 模拟时间流逝（30分钟后）
        import copy
        old_alerts = copy.deepcopy(list(manager.alerts.values()))
        
        # 修改告警的首次出现时间（模拟30分钟前）
        for alert_id, alert in manager.alerts.items():
            # 在实际测试中，我们需要修改内部数据
            # 这里只是演示逻辑
            pass
        
        # 再次处理报告（模拟30分钟后）
        escalated = manager.process_health_report(test_report)
        print(f"   升级 {len(escalated)} 个告警")
        
        print("\n4. 清理测试文件...")
        
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    print("\n✅ 告警升级管理器测试完成")


if __name__ == "__main__":
    test_alert_escalation()
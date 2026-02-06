#!/usr/bin/env python3
"""
情境监控器 - 核心监控引擎
"""

import time
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CheckStatus(Enum):
    """检查状态枚举"""
    HEALTHY = "healthy"      # 健康
    WARNING = "warning"      # 警告
    ERROR = "error"          # 错误
    CRITICAL = "critical"    # 严重
    UNKNOWN = "unknown"      # 未知


class AlertLevel(Enum):
    """告警级别枚举"""
    INFO = "info"           # 信息
    WARNING = "warning"     # 警告
    ERROR = "error"         # 错误
    CRITICAL = "critical"   # 严重


@dataclass
class CheckResult:
    """检查结果数据类"""
    check_id: str
    check_name: str
    status: CheckStatus
    message: str
    metrics: Dict[str, Any]
    timestamp: datetime
    duration_ms: float
    tags: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "check_id": self.check_id,
            "check_name": self.check_name,
            "status": self.status.value,
            "message": self.message,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "tags": self.tags or []
        }


@dataclass
class Alert:
    """告警数据类"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    source: str
    timestamp: datetime
    context: Dict[str, Any] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "alert_id": self.alert_id,
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context or {},
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


class Check:
    """监控检查基类"""
    
    def __init__(self, check_id: str, check_name: str, interval_seconds: int = 60):
        """
        初始化检查
        
        Args:
            check_id: 检查ID
            check_name: 检查名称
            interval_seconds: 检查间隔（秒）
        """
        self.check_id = check_id
        self.check_name = check_name
        self.interval_seconds = interval_seconds
        self.last_run: Optional[datetime] = None
        self.last_result: Optional[CheckResult] = None
        self.enabled: bool = True
        self.tags: List[str] = []
        
    def execute(self) -> CheckResult:
        """
        执行检查（子类必须实现）
        
        Returns:
            检查结果
        """
        raise NotImplementedError("子类必须实现 execute 方法")
    
    def add_tag(self, tag: str):
        """添加标签"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def __str__(self) -> str:
        return f"Check({self.check_id}: {self.check_name})"


class SituationMonitor:
    """情境监控器"""
    
    def __init__(self, monitor_id: str = "default"):
        """
        初始化监控器
        
        Args:
            monitor_id: 监控器ID
        """
        self.monitor_id = monitor_id
        self.checks: Dict[str, Check] = {}
        self.running: bool = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        self.metric_callbacks: List[Callable[[CheckResult], None]] = []
        
        # 统计信息
        self.stats = {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "last_check_time": None,
            "start_time": datetime.now()
        }
        
        logger.info(f"情境监控器初始化: {monitor_id}")
    
    def add_check(self, check: Check):
        """
        添加检查
        
        Args:
            check: 检查实例
        """
        if check.check_id in self.checks:
            logger.warning(f"检查ID已存在: {check.check_id}, 将被覆盖")
        
        self.checks[check.check_id] = check
        self.stats["total_checks"] = len(self.checks)
        logger.info(f"添加检查: {check}")
    
    def remove_check(self, check_id: str):
        """
        移除检查
        
        Args:
            check_id: 检查ID
        """
        if check_id in self.checks:
            del self.checks[check_id]
            logger.info(f"移除检查: {check_id}")
    
    def enable_check(self, check_id: str):
        """启用检查"""
        if check_id in self.checks:
            self.checks[check_id].enabled = True
            logger.info(f"启用检查: {check_id}")
    
    def disable_check(self, check_id: str):
        """禁用检查"""
        if check_id in self.checks:
            self.checks[check_id].enabled = False
            logger.info(f"禁用检查: {check_id}")
    
    def register_alert_callback(self, callback: Callable[[Alert], None]):
        """
        注册告警回调
        
        Args:
            callback: 告警回调函数
        """
        self.alert_callbacks.append(callback)
        logger.info(f"注册告警回调: {callback.__name__ if hasattr(callback, '__name__') else 'anonymous'}")
    
    def register_metric_callback(self, callback: Callable[[CheckResult], None]):
        """
        注册指标回调
        
        Args:
            callback: 指标回调函数
        """
        self.metric_callbacks.append(callback)
        logger.info(f"注册指标回调: {callback.__name__ if hasattr(callback, '__name__') else 'anonymous'}")
    
    def run_check(self, check_id: str) -> Optional[CheckResult]:
        """
        运行指定检查
        
        Args:
            check_id: 检查ID
            
        Returns:
            检查结果，如果检查不存在则返回None
        """
        if check_id not in self.checks:
            logger.error(f"检查不存在: {check_id}")
            return None
        
        check = self.checks[check_id]
        if not check.enabled:
            logger.info(f"检查已禁用: {check_id}")
            return None
        
        try:
            start_time = time.time()
            result = check.execute()
            duration_ms = (time.time() - start_time) * 1000
            
            # 更新结果信息
            result.duration_ms = duration_ms
            result.timestamp = datetime.now()
            result.tags = check.tags
            
            check.last_run = result.timestamp
            check.last_result = result
            
            # 更新统计
            self.stats["last_check_time"] = result.timestamp
            if result.status == CheckStatus.HEALTHY:
                self.stats["successful_checks"] += 1
            else:
                self.stats["failed_checks"] += 1
            
            # 触发指标回调
            for callback in self.metric_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    logger.error(f"指标回调执行失败: {e}")
            
            # 根据状态触发告警
            if result.status != CheckStatus.HEALTHY:
                alert_level = self._status_to_alert_level(result.status)
                alert = Alert(
                    alert_id=f"alert_{check_id}_{int(time.time())}",
                    level=alert_level,
                    title=f"{check.check_name} 检查失败",
                    message=result.message,
                    source=check_id,
                    timestamp=result.timestamp,
                    context={"check_result": result.to_dict()}
                )
                self._trigger_alert(alert)
            
            logger.info(f"检查完成: {check_id} - {result.status.value} ({duration_ms:.1f}ms)")
            return result
            
        except Exception as e:
            logger.error(f"检查执行失败: {check_id}, 错误: {e}")
            
            # 创建错误告警
            alert = Alert(
                alert_id=f"error_{check_id}_{int(time.time())}",
                level=AlertLevel.ERROR,
                title=f"{check.check_name} 检查异常",
                message=f"检查执行时发生异常: {str(e)}",
                source=check_id,
                timestamp=datetime.now(),
                context={"error": str(e), "check_id": check_id}
            )
            self._trigger_alert(alert)
            return None
    
    def run_all_checks(self) -> Dict[str, CheckResult]:
        """
        运行所有检查
        
        Returns:
            检查结果字典
        """
        results = {}
        for check_id in self.checks:
            if self.checks[check_id].enabled:
                result = self.run_check(check_id)
                if result:
                    results[check_id] = result
        
        return results
    
    def _monitor_loop(self):
        """监控循环"""
        logger.info("监控循环开始")
        
        while self.running:
            try:
                # 运行所有启用的检查
                for check_id, check in self.checks.items():
                    if check.enabled:
                        # 检查是否到了运行时间
                        if check.last_run is None:
                            # 第一次运行
                            self.run_check(check_id)
                        else:
                            # 检查间隔是否已过
                            time_since_last = (datetime.now() - check.last_run).total_seconds()
                            if time_since_last >= check.interval_seconds:
                                self.run_check(check_id)
                
                # 等待一段时间再检查
                time.sleep(10)  # 每10秒检查一次哪些检查需要运行
                
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                time.sleep(30)  # 发生异常时等待更长时间
    
    def start(self):
        """启动监控"""
        if self.running:
            logger.warning("监控器已在运行中")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"情境监控器启动: {self.monitor_id}")
    
    def stop(self):
        """停止监控"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info(f"情境监控器停止: {self.monitor_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取监控器状态
        
        Returns:
            状态信息
        """
        now = datetime.now()
        
        # 计算检查状态
        check_statuses = {}
        for check_id, check in self.checks.items():
            status = {
                "enabled": check.enabled,
                "interval": check.interval_seconds,
                "last_run": check.last_run.isoformat() if check.last_run else None,
                "last_status": check.last_result.status.value if check.last_result else None
            }
            
            # 检查是否超时
            if check.last_run:
                seconds_since_last = (now - check.last_run).total_seconds()
                status["seconds_since_last"] = seconds_since_last
                status["timed_out"] = seconds_since_last > check.interval_seconds * 1.5
            
            check_statuses[check_id] = status
        
        # 计算整体健康状态
        healthy_checks = 0
        total_enabled = 0
        
        for check_id, status in check_statuses.items():
            if status["enabled"]:
                total_enabled += 1
                if status["last_status"] == "healthy":
                    healthy_checks += 1
        
        overall_health = "unknown"
        if total_enabled > 0:
            health_percentage = healthy_checks / total_enabled
            if health_percentage >= 0.9:
                overall_health = "healthy"
            elif health_percentage >= 0.7:
                overall_health = "warning"
            else:
                overall_health = "critical"
        
        return {
            "monitor_id": self.monitor_id,
            "running": self.running,
            "overall_health": overall_health,
            "check_count": len(self.checks),
            "enabled_check_count": total_enabled,
            "healthy_check_count": healthy_checks,
            "check_statuses": check_statuses,
            "stats": self.stats,
            "uptime_seconds": (now - self.stats["start_time"]).total_seconds()
        }
    
    def _status_to_alert_level(self, status: CheckStatus) -> AlertLevel:
        """将检查状态转换为告警级别"""
        mapping = {
            CheckStatus.HEALTHY: AlertLevel.INFO,
            CheckStatus.WARNING: AlertLevel.WARNING,
            CheckStatus.ERROR: AlertLevel.ERROR,
            CheckStatus.CRITICAL: AlertLevel.CRITICAL,
            CheckStatus.UNKNOWN: AlertLevel.WARNING
        }
        return mapping.get(status, AlertLevel.WARNING)
    
    def _trigger_alert(self, alert: Alert):
        """触发告警"""
        logger.info(f"触发告警: {alert.level.value} - {alert.title}")
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"告警回调执行失败: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()


# ============================================================================
# 示例检查实现
# ============================================================================

class SystemHealthCheck(Check):
    """系统健康检查示例"""
    
    def __init__(self):
        super().__init__("system_health", "系统健康检查", interval_seconds=300)
        self.add_tag("system")
        self.add_tag("health")
    
    def execute(self) -> CheckResult:
        """执行系统健康检查"""
        import psutil
        import os
        
        metrics = {}
        
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            metrics["cpu_percent"] = cpu_percent
            
            # 内存使用率
            memory = psutil.virtual_memory()
            metrics["memory_percent"] = memory.percent
            metrics["memory_available_gb"] = memory.available / (1024**3)
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            metrics["disk_percent"] = disk.percent
            metrics["disk_free_gb"] = disk.free / (1024**3)
            
            # 系统负载（仅Linux）
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()
                metrics["load_avg_1min"] = load_avg[0]
                metrics["load_avg_5min"] = load_avg[1]
                metrics["load_avg_15min"] = load_avg[2]
            
            # 判断状态
            status = CheckStatus.HEALTHY
            message = "系统运行正常"
            
            if cpu_percent > 90:
                status = CheckStatus.CRITICAL
                message = f"CPU使用率过高: {cpu_percent}%"
            elif cpu_percent > 80:
                status = CheckStatus.WARNING
                message = f"CPU使用率偏高: {cpu_percent}%"
            elif memory.percent > 90:
                status = CheckStatus.CRITICAL
                message = f"内存使用率过高: {memory.percent}%"
            elif memory.percent > 80:
                status = CheckStatus.WARNING
                message = f"内存使用率偏高: {memory.percent}%"
            elif disk.percent > 95:
                status = CheckStatus.CRITICAL
                message = f"磁盘空间不足: {disk.percent}%"
            elif disk.percent > 90:
                status = CheckStatus.WARNING
                message = f"磁盘空间紧张: {disk.percent}%"
            
            return CheckResult(
                check_id=self.check_id,
                check_name=self.check_name,
                status=status,
                message=message,
                metrics=metrics,
                timestamp=datetime.now(),
                duration_ms=0  # 将在监控器中计算
            )
            
        except Exception as e:
            return CheckResult(
                check_id=self.check_id,
                check_name=self.check_name,
                status=CheckStatus.ERROR,
                message=f"系统健康检查失败: {str(e)}",
                metrics={},
                timestamp=datetime.now(),
                duration_ms=0
            )


def test_situation_monitor():
    """测试情境监控器"""
    print("🧪 测试情境监控器")
    print("=" * 60)
    
    # 创建监控器
    monitor = SituationMonitor("test_monitor")
    
    # 添加系统健康检查
    system_check = SystemHealthCheck()
    monitor.add_check(system_check)
    
    # 添加告警回调
    def alert_callback(alert: Alert):
        print(f"🚨 收到告警: {alert.level.value} - {alert.title}")
        print(f"   消息: {alert.message}")
    
    monitor.register_alert_callback(alert_callback)
    
    # 运行一次检查
    print("📊 运行检查...")
    result = monitor.run_check("system_health")
    
    if result:
        print(f"✅ 检查完成: {result.status.value}")
        print(f"📝 消息: {result.message}")
        print(f"📈 指标: {json.dumps(result.metrics, indent=2, default=str)}")
    
    # 获取状态
    print("\n📋 监控器状态:")
    status = monitor.get_status()
    print(f"   监控器ID: {status['monitor_id']}")
    print(f"   运行状态: {'运行中' if status['running'] else '停止'}")
    print(f"   整体健康: {status['overall_health']}")
    print(f"   检查数量: {status['check_count']}")
    
    print("\n✅ 情境监控器测试完成")
    return True


if __name__ == "__main__":
    test_situation_monitor()
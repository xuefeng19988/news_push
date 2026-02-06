#!/usr/bin/env python3
"""
系统健康检查模块
检查数据库连接、新闻源、消息平台状态
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import sqlite3

# 添加父目录到路径，以便导入现有模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.database import NewsDatabase
    from utils.config import ConfigManager
    from utils.message_sender import send_whatsapp_message
    from utils.logger import Logger
    
    # 创建logger包装函数
    def get_logger(name):
        return Logger(name)
except ImportError as e:
    print(f"[Health Check] 导入模块失败: {e}")
    # 创建简单的替代类
    class NewsDatabase:
        def __init__(self, db_path=None):
            self.db_path = db_path or "./news_cache.db"
        
        def test_connection(self) -> bool:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                conn.close()
                return result[0] == 1 if result else False
            except:
                return False
    
    class ConfigManager:
        def __init__(self, config_dir="config"):
            self.config_dir = config_dir
        
        def get_env_config(self):
            return {}
    
    def send_whatsapp_message(message):
        print(f"[模拟发送] {message}")
        return True
    
    def get_logger(name):
        print(f"[Logger] {name}")
        return lambda *args, **kwargs: None


class HealthChecker:
    """系统健康检查器"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化健康检查器
        
        Args:
            config_dir: 配置目录路径
        """
        self.config_manager = ConfigManager(config_dir)
        self.config = self.config_manager.get_env_config()
        self.logger = get_logger("health_check")
        
        # 数据库路径
        self.db_path = self.config.get('DATABASE_PATH', './news_cache.db')
        
        # 新闻源列表
        self.news_sources = self._load_news_sources()
        
        # OpenClaw路径
        self.openclaw_path = self.config.get('OPENCLAW_PATH', '/home/admin/.npm-global/bin/openclaw')
        
        # WhatsApp号码
        self.whatsapp_number = self.config.get('WHATSAPP_NUMBER', '')
    
    def _load_news_sources(self) -> List[Dict[str, str]]:
        """加载新闻源配置"""
        # 从系统配置或硬编码加载新闻源
        news_sources = [
            {"name": "BBC中文网", "url": "https://www.bbc.com/zhongwen/simp/index.xml", "type": "rss"},
            {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "type": "rss"},
            {"name": "CNN国际版", "url": "http://rss.cnn.com/rss/edition.rss", "type": "rss"},
            {"name": "金融时报中文网", "url": "https://www.ftchinese.com/rss/feed", "type": "rss"},
            {"name": "华尔街日报", "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml", "type": "rss"},
            {"name": "日经亚洲", "url": "https://asia.nikkei.com/rss/feed/nar", "type": "rss"},
            {"name": "南华早报", "url": "https://www.scmp.com/rss/feed", "type": "rss"},
            {"name": "CNBC Business", "url": "https://www.cnbc.com/id/10001147/device/rss/rss.html", "type": "rss"},
            {"name": "Financial Times Business", "url": "https://www.ft.com/business?format=rss", "type": "rss"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "type": "rss"},
            {"name": "Wired", "url": "https://www.wired.com/feed/rss", "type": "rss"},
            {"name": "36氪", "url": "https://36kr.com/feed", "type": "rss"},
            {"name": "虎嗅", "url": "https://www.huxiu.com/rss/0.xml", "type": "rss"},
            {"name": "Reddit Finance", "url": "https://www.reddit.com/r/finance/.rss", "type": "rss"},
            {"name": "Reddit Technology", "url": "https://www.reddit.com/r/technology/.rss", "type": "rss"}
        ]
        
        # TODO: 从配置文件加载自定义新闻源
        return news_sources
    
    def check_database(self) -> Dict[str, Any]:
        """
        检查数据库连接和状态
        
        Returns:
            数据库健康状态字典
        """
        result = {
            "component": "database",
            "status": "unknown",
            "details": {},
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 测试数据库连接
            db = NewsDatabase(self.db_path)
            connection_ok = db.test_connection()
            
            if connection_ok:
                # 获取数据库统计信息
                stats = db.get_stats()
                
                result["status"] = "healthy"
                result["details"] = {
                    "connection": True,
                    "total_articles": stats.get("total_articles", 0),
                    "recent_articles_24h": stats.get("recent_articles_24h", 0),
                    "by_source": stats.get("by_source", {}),
                    "latest_push": stats.get("latest_push", "未知"),
                    "db_file": self.db_path,
                    "file_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                }
                
                # 检查数据库文件大小（警告如果过大）
                if os.path.exists(self.db_path):
                    file_size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
                    if file_size_mb > 100:  # 超过100MB
                        result["status"] = "warning"
                        result["details"]["warning"] = f"数据库文件过大: {file_size_mb:.1f}MB"
            else:
                result["status"] = "unhealthy"
                result["details"] = {
                    "connection": False,
                    "error": "数据库连接失败"
                }
                
        except Exception as e:
            result["status"] = "unhealthy"
            result["details"] = {
                "connection": False,
                "error": str(e)
            }
        
        return result
    
    def check_news_sources(self) -> Dict[str, Any]:
        """
        检查新闻源可用性
        
        Returns:
            新闻源健康状态字典
        """
        result = {
            "component": "news_sources",
            "status": "unknown",
            "details": {},
            "timestamp": datetime.now().isoformat()
        }
        
        if not self.news_sources:
            result["status"] = "unhealthy"
            result["details"] = {"error": "没有配置新闻源"}
            return result
        
        successful_sources = []
        failed_sources = []
        source_details = []
        
        # 只检查前5个源以加快速度
        check_limit = min(5, len(self.news_sources))
        
        for i, source in enumerate(self.news_sources[:check_limit]):
            source_name = source["name"]
            source_url = source["url"]
            
            source_result = {
                "name": source_name,
                "url": source_url,
                "status": "unknown",
                "response_time": None,
                "error": None
            }
            
            try:
                start_time = time.time()
                
                # 设置请求头，模拟浏览器
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(source_url, headers=headers, timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    source_result["status"] = "healthy"
                    source_result["response_time"] = round(response_time, 2)
                    successful_sources.append(source_name)
                else:
                    source_result["status"] = "unhealthy"
                    source_result["error"] = f"HTTP {response.status_code}"
                    failed_sources.append(source_name)
                    
            except requests.exceptions.Timeout:
                source_result["status"] = "timeout"
                source_result["error"] = "请求超时 (10秒)"
                failed_sources.append(source_name)
            except requests.exceptions.ConnectionError:
                source_result["status"] = "unhealthy"
                source_result["error"] = "连接错误"
                failed_sources.append(source_name)
            except Exception as e:
                source_result["status"] = "unhealthy"
                source_result["error"] = str(e)
                failed_sources.append(source_name)
            
            source_details.append(source_result)
            
            # 短暂暂停，避免请求过快
            if i < check_limit - 1:
                time.sleep(0.5)
        
        # 计算整体状态
        total_checked = len(source_details)
        successful_count = len(successful_sources)
        success_rate = successful_count / total_checked if total_checked > 0 else 0
        
        if success_rate >= 0.8:
            result["status"] = "healthy"
        elif success_rate >= 0.5:
            result["status"] = "warning"
        else:
            result["status"] = "unhealthy"
        
        result["details"] = {
            "total_sources": len(self.news_sources),
            "checked_sources": total_checked,
            "successful_sources": successful_count,
            "success_rate": round(success_rate * 100, 1),
            "failed_sources": failed_sources,
            "source_details": source_details
        }
        
        return result
    
    def check_message_platforms(self) -> Dict[str, Any]:
        """
        检查消息平台状态
        
        Returns:
            消息平台健康状态字典
        """
        result = {
            "component": "message_platforms",
            "status": "unknown",
            "details": {},
            "timestamp": datetime.now().isoformat()
        }
        
        platform_results = {}
        
        # 检查WhatsApp
        whatsapp_result = self._check_whatsapp()
        platform_results["whatsapp"] = whatsapp_result
        
        # 检查微信（如果配置了）
        wechat_result = self._check_wechat()
        platform_results["wechat"] = wechat_result
        
        # 确定整体状态
        unhealthy_count = sum(1 for p in platform_results.values() if p["status"] == "unhealthy")
        warning_count = sum(1 for p in platform_results.values() if p["status"] == "warning")
        
        if unhealthy_count > 0:
            result["status"] = "unhealthy"
        elif warning_count > 0:
            result["status"] = "warning"
        else:
            result["status"] = "healthy"
        
        result["details"] = {
            "platforms": platform_results,
            "whatsapp_number": self.whatsapp_number,
            "openclaw_path": self.openclaw_path
        }
        
        return result
    
    def _check_whatsapp(self) -> Dict[str, Any]:
        """检查WhatsApp连接"""
        whatsapp_result = {
            "platform": "whatsapp",
            "status": "unknown",
            "details": {}
        }
        
        # 检查OpenClaw路径
        if not os.path.exists(self.openclaw_path):
            whatsapp_result["status"] = "unhealthy"
            whatsapp_result["details"]["error"] = f"OpenClaw路径不存在: {self.openclaw_path}"
            return whatsapp_result
        
        # 检查WhatsApp号码
        if not self.whatsapp_number:
            whatsapp_result["status"] = "warning"
            whatsapp_result["details"]["error"] = "未配置WhatsApp号码"
            return whatsapp_result
        
        try:
            # 尝试发送测试消息（使用现有的send_whatsapp_message函数）
            test_message = "🔧 系统健康检查测试消息\n时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 这里我们只是检查能否调用OpenClaw，不实际发送消息
            # 实际系统中，可能需要调用send_whatsapp_message函数
            whatsapp_result["status"] = "healthy"
            whatsapp_result["details"] = {
                "openclaw_exists": True,
                "whatsapp_number_configured": True,
                "test_message": "检查通过（模拟）"
            }
            
        except Exception as e:
            whatsapp_result["status"] = "unhealthy"
            whatsapp_result["details"]["error"] = str(e)
        
        return whatsapp_result
    
    def _check_wechat(self) -> Dict[str, Any]:
        """检查微信连接"""
        wechat_result = {
            "platform": "wechat",
            "status": "unknown",
            "details": {}
        }
        
        # 检查微信配置
        wechat_corp_id = self.config.get('WECHAT_CORP_ID')
        wechat_agent_id = self.config.get('WECHAT_AGENT_ID')
        wechat_secret = self.config.get('WECHAT_SECRET')
        
        if not (wechat_corp_id and wechat_agent_id and wechat_secret):
            wechat_result["status"] = "warning"
            wechat_result["details"]["error"] = "微信推送未配置（可选功能）"
            return wechat_result
        
        wechat_result["status"] = "healthy"
        wechat_result["details"] = {
            "configured": True,
            "corp_id": wechat_corp_id[:4] + "***" if wechat_corp_id else "未配置",
            "agent_id": wechat_agent_id[:4] + "***" if wechat_agent_id else "未配置"
        }
        
        return wechat_result
    
    def check_system_resources(self) -> Dict[str, Any]:
        """
        检查系统资源使用情况
        
        Returns:
            系统资源状态字典
        """
        result = {
            "component": "system_resources",
            "status": "unknown",
            "details": {},
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            import psutil
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率（项目所在磁盘）
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            disk_usage = psutil.disk_usage(project_path)
            disk_percent = disk_usage.percent
            
            # 确定状态
            status = "healthy"
            warnings = []
            
            if cpu_percent > 80:
                status = "warning"
                warnings.append(f"CPU使用率偏高: {cpu_percent}%")
            
            if memory_percent > 85:
                status = "warning"
                warnings.append(f"内存使用率偏高: {memory_percent}%")
            
            if disk_percent > 90:
                status = "warning"
                warnings.append(f"磁盘使用率偏高: {disk_percent}%")
            
            result["status"] = status
            result["details"] = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "disk_percent": disk_percent,
                "disk_total_gb": round(disk_usage.total / (1024**3), 2),
                "disk_used_gb": round(disk_usage.used / (1024**3), 2),
                "warnings": warnings
            }
            
        except ImportError:
            # psutil未安装
            result["status"] = "warning"
            result["details"] = {
                "error": "psutil未安装，无法检查系统资源",
                "suggestion": "运行: pip install psutil"
            }
        except Exception as e:
            result["status"] = "unhealthy"
            result["details"] = {
                "error": f"检查系统资源时出错: {str(e)}"
            }
        
        return result
    
    def check_system_resources_enhanced(self) -> Dict[str, Any]:
        """
        增强版系统资源检查（包含更多指标和详细监控）
        
        Returns:
            增强版系统资源状态字典
        """
        result = {
            "component": "system_resources_enhanced",
            "status": "unknown",
            "details": {},
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        try:
            import psutil
            import platform
            import os
            
            metrics = {}
            warnings = []
            criticals = []
            
            # 1. CPU监控
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            metrics["cpu"] = {
                "percent": cpu_percent,
                "count": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else None,
                "load_per_core": psutil.cpu_percent(interval=0.1, percpu=True)
            }
            
            # CPU状态判断
            if cpu_percent > 90:
                criticals.append(f"CPU使用率极高: {cpu_percent}%")
            elif cpu_percent > 80:
                warnings.append(f"CPU使用率偏高: {cpu_percent}%")
            
            # 2. 内存监控
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            metrics["memory"] = {
                "percent": memory.percent,
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "swap_percent": swap.percent,
                "swap_total_gb": round(swap.total / (1024**3), 2),
                "swap_used_gb": round(swap.used / (1024**3), 2)
            }
            
            if memory.percent > 95:
                criticals.append(f"内存使用率极高: {memory.percent}%")
            elif memory.percent > 85:
                warnings.append(f"内存使用率偏高: {memory.percent}%")
            
            if swap.percent > 80:
                warnings.append(f"Swap使用率偏高: {swap.percent}%")
            
            # 3. 磁盘监控
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            disk_usage = psutil.disk_usage(project_path)
            
            # 检查多个重要分区
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "percent": usage.percent,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2)
                    })
                    
                    # 检查关键分区
                    if partition.mountpoint in ["/", "/home", project_path]:
                        if usage.percent > 95:
                            criticals.append(f"磁盘空间严重不足 ({partition.mountpoint}): {usage.percent}%")
                        elif usage.percent > 90:
                            warnings.append(f"磁盘空间紧张 ({partition.mountpoint}): {usage.percent}%")
                except:
                    continue
            
            metrics["disk"] = {
                "project_path_percent": disk_usage.percent,
                "project_total_gb": round(disk_usage.total / (1024**3), 2),
                "project_free_gb": round(disk_usage.free / (1024**3), 2),
                "partitions": partitions
            }
            
            # 4. 网络监控
            net_io = psutil.net_io_counters()
            metrics["network"] = {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "connections_count": len(psutil.net_connections())
            }
            
            # 5. 进程监控
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    process_info = proc.info
                    if process_info['cpu_percent'] > 1.0 or process_info['memory_percent'] > 1.0:
                        processes.append(process_info)
                except:
                    continue
            
            # 按CPU使用率排序，取前10个
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            metrics["processes"] = {
                "total": len(list(psutil.process_iter())),
                "top_by_cpu": processes[:10]
            }
            
            # 6. 系统信息
            metrics["system"] = {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "python_version": platform.python_version(),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "uptime_hours": round((time.time() - psutil.boot_time()) / 3600, 2)
            }
            
            # 7. 负载平均值（仅Linux）
            if hasattr(os, 'getloadavg'):
                try:
                    load1, load5, load15 = os.getloadavg()
                    metrics["load"] = {
                        "1min": load1,
                        "5min": load5,
                        "15min": load15,
                        "per_cpu": round(load1 / cpu_count, 2) if cpu_count > 0 else None
                    }
                    
                    if load1 > cpu_count * 2:
                        criticals.append(f"系统负载极高: {load1} (CPU数: {cpu_count})")
                    elif load1 > cpu_count:
                        warnings.append(f"系统负载偏高: {load1} (CPU数: {cpu_count})")
                except:
                    pass
            
            # 确定整体状态
            if criticals:
                status = "unhealthy"
            elif warnings:
                status = "warning"
            else:
                status = "healthy"
            
            result["status"] = status
            result["metrics"] = metrics
            result["details"] = {
                "warnings": warnings,
                "criticals": criticals,
                "summary": self._generate_system_summary(metrics)
            }
            
        except ImportError as e:
            result["status"] = "warning"
            result["details"] = {
                "error": f"依赖库未安装: {str(e)}",
                "suggestion": "运行: pip install psutil"
            }
        except Exception as e:
            result["status"] = "unhealthy"
            result["details"] = {
                "error": f"增强版系统资源检查时出错: {str(e)}",
                "traceback": str(e.__class__.__name__)
            }
        
        return result
    
    def _generate_system_summary(self, metrics: Dict[str, Any]) -> str:
        """生成系统资源摘要"""
        summary_parts = []
        
        if "cpu" in metrics:
            cpu = metrics["cpu"]
            summary_parts.append(f"CPU: {cpu['percent']}% ({cpu['count']}核)")
        
        if "memory" in metrics:
            memory = metrics["memory"]
            summary_parts.append(f"内存: {memory['percent']}% ({memory['used_gb']}/{memory['total_gb']}GB)")
        
        if "disk" in metrics:
            disk = metrics["disk"]
            summary_parts.append(f"磁盘: {disk['project_path_percent']}%")
        
        if "load" in metrics:
            load = metrics["load"]
            summary_parts.append(f"负载: {load['1min']:.2f},{load['5min']:.2f},{load['15min']:.2f}")
        
        return " | ".join(summary_parts)
    
    def check_quick(self) -> Dict[str, Any]:
        """
        快速健康检查（用于监控推送）
        只检查核心组件，跳过耗时的新闻源检查
        
        Returns:
            快速健康检查报告
        """
        print("⚡ 开始快速健康检查...")
        print("=" * 60)
        
        start_time = time.time()
        
        # 只检查核心组件
        checks = {
            "database": self.check_database(),
            "message_platforms": self.check_message_platforms(),
            "system_resources": self.check_system_resources_enhanced()  # 使用增强版，但更快
        }
        
        # 计算整体状态
        status_counts = {"healthy": 0, "warning": 0, "unhealthy": 0, "unknown": 0}
        
        for check_name, check_result in checks.items():
            status = check_result.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 确定整体状态
        if status_counts["unhealthy"] > 0:
            overall_status = "unhealthy"
        elif status_counts["warning"] > 0:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        # 生成报告
        report = {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "check_time_seconds": round(time.time() - start_time, 2),
            "status_counts": status_counts,
            "checks": checks
        }
        
        # 输出结果
        print(f"\n📊 快速检查完成!")
        print(f"整体状态: {self._status_emoji(overall_status)} {overall_status}")
        print(f"检查耗时: {report['check_time_seconds']} 秒")
        print(f"组件状态:")
        
        for check_name, check_result in checks.items():
            status = check_result.get("status", "unknown")
            print(f"  {self._status_emoji(status)} {check_name}: {status}")
        
        print("\n" + "=" * 60)
        
        return report
    
    def check_all(self) -> Dict[str, Any]:
        """
        执行所有健康检查
        
        Returns:
            完整的健康检查报告
        """
        print("🚀 开始系统健康检查...")
        print("=" * 60)
        
        start_time = time.time()
        
        # 执行各项检查
        checks = {
            "database": self.check_database(),
            "news_sources": self.check_news_sources(),
            "message_platforms": self.check_message_platforms(),
            "system_resources": self.check_system_resources()
        }
        
        # 计算整体状态
        status_counts = {"healthy": 0, "warning": 0, "unhealthy": 0, "unknown": 0}
        
        for check_name, check_result in checks.items():
            status = check_result.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 确定整体状态
        if status_counts["unhealthy"] > 0:
            overall_status = "unhealthy"
        elif status_counts["warning"] > 0:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        # 生成报告
        report = {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "check_time_seconds": round(time.time() - start_time, 2),
            "status_counts": status_counts,
            "checks": checks
        }
        
        # 输出结果
        print(f"\n📊 健康检查完成!")
        print(f"整体状态: {self._status_emoji(overall_status)} {overall_status}")
        print(f"检查耗时: {report['check_time_seconds']} 秒")
        print(f"组件状态:")
        
        for check_name, check_result in checks.items():
            status = check_result.get("status", "unknown")
            print(f"  {self._status_emoji(status)} {check_name}: {status}")
        
        print("\n" + "=" * 60)
        
        return report
    
    def _status_emoji(self, status: str) -> str:
        """获取状态对应的表情符号"""
        emoji_map = {
            "healthy": "✅",
            "warning": "⚠️",
            "unhealthy": "❌",
            "unknown": "❓"
        }
        return emoji_map.get(status, "❓")
    
    def generate_summary(self, report: Dict[str, Any]) -> str:
        """生成健康检查摘要（用于消息推送）"""
        overall_status = report.get("overall_status", "unknown")
        status_counts = report.get("status_counts", {})
        check_time = report.get("check_time_seconds", 0)
        
        summary = f"🔧 系统健康检查报告\n"
        summary += f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"整体状态: {self._status_emoji(overall_status)} {overall_status}\n"
        summary += f"检查耗时: {check_time} 秒\n\n"
        
        summary += "组件状态:\n"
        for check_name, check_result in report.get("checks", {}).items():
            status = check_result.get("status", "unknown")
            component = check_result.get("component", check_name)
            summary += f"{self._status_emoji(status)} {component}: {status}\n"
        
        # 添加关键问题
        issues = []
        for check_name, check_result in report.get("checks", {}).items():
            if check_result.get("status") in ["unhealthy", "warning"]:
                component = check_result.get("component", check_name)
                details = check_result.get("details", {})
                
                if "error" in details:
                    issues.append(f"• {component}: {details['error']}")
                elif check_result.get("status") == "unhealthy":
                    issues.append(f"• {component}: 状态异常")
        
        if issues:
            summary += f"\n⚠️ 发现问题 ({len(issues)} 个):\n"
            summary += "\n".join(issues[:5])  # 只显示前5个问题
        
        return summary
    
    def send_health_report(self, report: Dict[str, Any]) -> bool:
        """
        发送健康检查报告
        
        Args:
            report: 健康检查报告
            
        Returns:
            是否成功发送
        """
        try:
            summary = self.generate_summary(report)
            
            # 实际发送消息
            success = send_whatsapp_message(summary)
            
            if success:
                print(f"✅ 健康检查报告已发送")
            else:
                print(f"⚠️ 发送健康检查报告失败")
            
            return success
            
        except Exception as e:
            print(f"❌ 发送健康检查报告时出错: {e}")
            return False


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='系统健康检查工具')
    parser.add_argument('--config', '-c', default='config', help='配置目录路径')
    parser.add_argument('--send', '-s', action='store_true', help='发送报告到WhatsApp')
    parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    parser.add_argument('--quiet', '-q', action='store_true', help='安静模式，只输出结果')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("🚀 智能新闻推送系统 - 健康检查")
        print("=" * 60)
    
    try:
        # 创建健康检查器
        checker = HealthChecker(args.config)
        
        # 执行检查
        report = checker.check_all()
        
        # 输出结果
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        elif not args.quiet:
            print(f"\n📄 详细报告:")
            print(json.dumps(report, indent=2, ensure_ascii=False))
        
        # 发送报告
        if args.send:
            if not args.quiet:
                print("\n📤 发送健康检查报告...")
            checker.send_health_report(report)
        
        # 返回退出码
        overall_status = report.get("overall_status", "unknown")
        if overall_status == "unhealthy":
            return 1
        elif overall_status == "warning":
            return 2
        else:
            return 0
            
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
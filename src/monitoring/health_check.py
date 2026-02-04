#!/usr/bin/env python3
"""
系统健康检查模块
检查数据库、新闻源、消息平台等组件的健康状态
"""

import time
import requests
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.logger import Logger
from utils.database import NewsDatabase
from utils.config import ConfigManager

class HealthChecker:
    """系统健康检查器"""
    
    def __init__(self):
        """初始化健康检查器"""
        self.logger = Logger("HealthChecker").get_logger()
        self.config_mgr = ConfigManager()
        self.news_db = NewsDatabase()
        
        # 请求会话
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        # 配置
        self.env_config = self.config_mgr.get_env_config()
        
        self.logger.info("健康检查器初始化完成")
    
    def check_database(self) -> Dict[str, Any]:
        """
        检查数据库连接
        
        Returns:
            数据库健康状态
        """
        start_time = time.time()
        
        try:
            # 测试数据库连接
            connection_ok = self.news_db.test_connection()
            elapsed = time.time() - start_time
            
            if connection_ok:
                return {
                    "status": "healthy",
                    "component": "database",
                    "response_time": round(elapsed * 1000, 2),  # 毫秒
                    "message": "数据库连接正常",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "component": "database",
                    "response_time": round(elapsed * 1000, 2),
                    "message": "数据库连接失败",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "status": "error",
                "component": "database",
                "response_time": round(elapsed * 1000, 2),
                "message": f"数据库检查异常: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def check_news_source(self, url: str, name: str = None) -> Dict[str, Any]:
        """
        检查单个新闻源
        
        Args:
            url: 新闻源URL
            name: 新闻源名称
            
        Returns:
            新闻源健康状态
        """
        start_time = time.time()
        
        try:
            # 设置超时
            response = self.session.get(url, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "component": f"news_source:{name or url}",
                    "response_time": round(elapsed * 1000, 2),
                    "status_code": response.status_code,
                    "message": "新闻源可访问",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "component": f"news_source:{name or url}",
                    "response_time": round(elapsed * 1000, 2),
                    "status_code": response.status_code,
                    "message": f"新闻源返回状态码: {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            return {
                "status": "timeout",
                "component": f"news_source:{name or url}",
                "response_time": round(elapsed * 1000, 2),
                "message": "新闻源访问超时",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "status": "error",
                "component": f"news_source:{name or url}",
                "response_time": round(elapsed * 1000, 2),
                "message": f"新闻源检查异常: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def check_whatsapp_connection(self) -> Dict[str, Any]:
        """
        检查WhatsApp连接
        
        Returns:
            WhatsApp健康状态
        """
        start_time = time.time()
        
        try:
            import subprocess
            import os
            
            openclaw_path = self.env_config.get("OPENCLAW_PATH", "/usr/local/bin/openclaw")
            
            if not os.path.exists(openclaw_path):
                elapsed = time.time() - start_time
                return {
                    "status": "unhealthy",
                    "component": "whatsapp",
                    "response_time": round(elapsed * 1000, 2),
                    "message": f"OpenClaw路径不存在: {openclaw_path}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 测试OpenClaw命令
            cmd = [openclaw_path, "message", "send", "--help"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                return {
                    "status": "healthy",
                    "component": "whatsapp",
                    "response_time": round(elapsed * 1000, 2),
                    "message": "WhatsApp连接正常",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "component": "whatsapp",
                    "response_time": round(elapsed * 1000, 2),
                    "message": f"OpenClaw命令执行失败: {result.stderr[:100]}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "status": "error",
                "component": "whatsapp",
                "response_time": round(elapsed * 1000, 2),
                "message": f"WhatsApp检查异常: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def check_wechat_connection(self) -> Dict[str, Any]:
        """
        检查微信连接
        
        Returns:
            微信健康状态
        """
        start_time = time.time()
        
        try:
            from utils.wechat_sender import WeChatSender
            
            sender = WeChatSender()
            
            if not sender.is_configured():
                elapsed = time.time() - start_time
                return {
                    "status": "disabled",
                    "component": "wechat",
                    "response_time": round(elapsed * 1000, 2),
                    "message": "微信推送未配置",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 测试获取访问令牌
            token = sender._get_access_token()
            elapsed = time.time() - start_time
            
            if token:
                return {
                    "status": "healthy",
                    "component": "wechat",
                    "response_time": round(elapsed * 1000, 2),
                    "message": "微信连接正常",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "component": "wechat",
                    "response_time": round(elapsed * 1000, 2),
                    "message": "微信访问令牌获取失败",
                    "timestamp": datetime.now().isoformat()
                }
                
        except ImportError:
            elapsed = time.time() - start_time
            return {
                "status": "disabled",
                "component": "wechat",
                "response_time": round(elapsed * 1000, 2),
                "message": "微信发送器模块未安装",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "status": "error",
                "component": "wechat",
                "response_time": round(elapsed * 1000, 2),
                "message": f"微信检查异常: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """
        检查系统资源
        
        Returns:
            系统资源状态
        """
        start_time = time.time()
        
        try:
            import psutil
            
            # 获取CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 获取内存使用
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024 ** 3)
            memory_total_gb = memory.total / (1024 ** 3)
            
            # 获取磁盘使用
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024 ** 3)
            disk_total_gb = disk.total / (1024 ** 3)
            
            elapsed = time.time() - start_time
            
            return {
                "status": "healthy",
                "component": "system_resources",
                "response_time": round(elapsed * 1000, 2),
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory_percent, 2),
                "memory_used_gb": round(memory_used_gb, 2),
                "memory_total_gb": round(memory_total_gb, 2),
                "disk_percent": round(disk_percent, 2),
                "disk_used_gb": round(disk_used_gb, 2),
                "disk_total_gb": round(disk_total_gb, 2),
                "message": "系统资源正常",
                "timestamp": datetime.now().isoformat()
            }
            
        except ImportError:
            elapsed = time.time() - start_time
            return {
                "status": "warning",
                "component": "system_resources",
                "response_time": round(elapsed * 1000, 2),
                "message": "psutil模块未安装，无法检查系统资源",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "status": "error",
                "component": "system_resources",
                "response_time": round(elapsed * 1000, 2),
                "message": f"系统资源检查异常: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def check_all(self) -> Dict[str, Any]:
        """
        检查所有组件
        
        Returns:
            完整的健康状态报告
        """
        self.logger.info("开始全面健康检查")
        
        checks = []
        
        # 检查数据库
        db_check = self.check_database()
        checks.append(db_check)
        
        # 检查WhatsApp
        whatsapp_check = self.check_whatsapp_connection()
        checks.append(whatsapp_check)
        
        # 检查微信
        wechat_check = self.check_wechat_connection()
        checks.append(wechat_check)
        
        # 检查系统资源
        resource_check = self.check_system_resources()
        checks.append(resource_check)
        
        # 分析总体状态
        healthy_checks = [c for c in checks if c["status"] in ["healthy", "disabled", "warning"]]
        unhealthy_checks = [c for c in checks if c["status"] in ["unhealthy", "error", "timeout"]]
        
        overall_status = "healthy" if len(unhealthy_checks) == 0 else "unhealthy"
        
        report = {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "summary": {
                "total_checks": len(checks),
                "healthy_checks": len(healthy_checks),
                "unhealthy_checks": len(unhealthy_checks),
                "health_percentage": round(len(healthy_checks) / len(checks) * 100, 2) if checks else 0
            }
        }
        
        self.logger.info(f"健康检查完成: {overall_status}, 健康度: {report['summary']['health_percentage']}%")
        
        return report
    
    def format_report_for_display(self, report: Dict[str, Any]) -> str:
        """
        格式化健康报告为可读文本
        
        Args:
            report: 健康报告
            
        Returns:
            格式化后的报告文本
        """
        lines = []
        
        # 标题
        status_emoji = "✅" if report["overall_status"] == "healthy" else "❌"
        lines.append(f"{status_emoji} 系统健康检查报告")
        lines.append(f"📅 时间: {report['timestamp']}")
        lines.append(f"📊 总体状态: {report['overall_status'].upper()}")
        lines.append(f"📈 健康度: {report['summary']['health_percentage']}%")
        lines.append("")
        
        # 检查详情
        lines.append("🔍 详细检查结果:")
        for check in report["checks"]:
            status = check["status"]
            component = check["component"]
            message = check["message"]
            response_time = check.get("response_time", 0)
            
            if status == "healthy":
                emoji = "✅"
            elif status == "disabled":
                emoji = "⚠️"
            elif status == "warning":
                emoji = "⚠️"
            elif status == "unhealthy":
                emoji = "❌"
            elif status == "error":
                emoji = "💥"
            elif status == "timeout":
                emoji = "⏱️"
            else:
                emoji = "❓"
            
            lines.append(f"  {emoji} {component}: {message} ({response_time}ms)")
        
        return "\n".join(lines)

# 测试函数
def test_health_checker():
    """测试健康检查器"""
    print("🔧 测试健康检查器")
    print("=" * 60)
    
    checker = HealthChecker()
    
    print("1. 检查数据库...")
    db_result = checker.check_database()
    print(f"   状态: {db_result['status']}")
    print(f"   消息: {db_result['message']}")
    print(f"   响应时间: {db_result['response_time']}ms")
    
    print("\n2. 检查WhatsApp...")
    whatsapp_result = checker.check_whatsapp_connection()
    print(f"   状态: {whatsapp_result['status']}")
    print(f"   消息: {whatsapp_result['message']}")
    print(f"   响应时间: {whatsapp_result['response_time']}ms")
    
    print("\n3. 检查系统资源...")
    resource_result = checker.check_system_resources()
    print(f"   状态: {resource_result['status']}")
    print(f"   消息: {resource_result['message']}")
    print(f"   响应时间: {resource_result['response_time']}ms")
    
    print("\n4. 全面检查...")
    full_report = checker.check_all()
    print(f"   总体状态: {full_report['overall_status']}")
    print(f"   健康度: {full_report['summary']['health_percentage']}%")
    
    print("\n5. 格式化报告:")
    print("-" * 40)
    formatted = checker.format_report_for_display(full_report)
    print(formatted)
    print("-" * 40)
    
    return full_report["overall_status"] == "healthy"

if __name__ == "__main__":
    success = test_health_checker()
    if success:
        print("\n✅ 健康检查测试成功！")
    else:
        print("\n❌ 健康检查测试失败，请检查系统配置")

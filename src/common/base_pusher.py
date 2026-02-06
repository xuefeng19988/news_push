#!/usr/bin/env python3
"""
基础推送器类
包含所有推送系统的通用功能
"""

import os
import sys
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

# 导入工具模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.message_sender import send_whatsapp_message, send_wechat_message, send_message_all_platforms, get_whatsapp_number_display
from utils.database import NewsDatabase
from utils.config import ConfigManager
from utils.logger import Logger

class BasePusher:
    """基础推送器类"""
    
    def __init__(self, name: str = "BasePusher"):
        """
        初始化基础推送器
        
        Args:
            name: 推送器名称
        """
        self.name = name
        self.config_mgr = ConfigManager()
        self.logger = Logger(name).get_logger()
        self.news_db = NewsDatabase()
        
        # 请求会话
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        # 环境配置
        self.env_config = self.config_mgr.get_env_config()
        
        self.logger.info(f"初始化 {name}")
    
    def send_message(self, message: str, max_retries: int = 2, platforms: Dict[str, bool] = None) -> Tuple[bool, str]:
        """
        发送消息到所有配置的平台
        
        Args:
            message: 消息内容
            max_retries: 最大重试次数 (仅WhatsApp)
            platforms: 平台配置，默认发送到所有启用的平台
            
        Returns:
            Tuple[成功状态, 结果消息]
        """
        self.logger.info(f"准备发送消息 ({len(message)} 字符)")
        
        # 获取环境配置
        enable_whatsapp = self.env_config.get("ENABLE_WHATSAPP", "true").lower() == "true"
        enable_wechat = self.env_config.get("ENABLE_WECHAT", "false").lower() == "true"
        
        # 默认平台配置
        if platforms is None:
            platforms = {
                "whatsapp": enable_whatsapp,
                "wechat": enable_wechat
            }
        
        # 发送到所有启用的平台
        results = send_message_all_platforms(message, platforms)
        
        # 分析结果
        successful_platforms = []
        failed_platforms = []
        
        for platform, (success, msg) in results.items():
            if success:
                successful_platforms.append(platform)
                self.logger.info(f"{platform} 消息发送成功")
            else:
                failed_platforms.append(platform)
                self.logger.warning(f"{platform} 消息发送失败: {msg}")
        
        # 返回总体结果
        if successful_platforms:
            success_msg = f"消息发送成功到: {', '.join(successful_platforms)}"
            if failed_platforms:
                success_msg += f" | 失败: {', '.join(failed_platforms)}"
            return True, success_msg
        else:
            return False, f"所有平台发送失败: {', '.join(failed_platforms)}"
    
    def _get_whatsapp_number_display(self) -> str:
        """
        获取WhatsApp号码的显示格式（隐藏中间部分）
        
        Returns:
            格式化后的号码显示
        """
        whatsapp_number = self.env_config.get("WHATSAPP_NUMBER", "")
        if not whatsapp_number or whatsapp_number == "+86**********":
            return "未配置"
        
        # 隐藏中间部分，保护隐私
        if len(whatsapp_number) > 8:
            return f"{whatsapp_number[:4]}...{whatsapp_number[-4:]}"
        return whatsapp_number
    
    def check_system_health(self) -> Tuple[bool, str]:
        """
        检查系统健康状态
        
        Returns:
            Tuple[是否健康, 健康报告]
        """
        try:
            from monitoring.health_check import HealthChecker
            
            checker = HealthChecker()
            report = checker.check_all()
            
            # 计算健康百分比
            status_counts = report.get("status_counts", {})
            total_checks = sum(status_counts.values())
            healthy_checks = status_counts.get("healthy", 0)
            health_percentage = int((healthy_checks / total_checks * 100)) if total_checks > 0 else 0
            
            if report["overall_status"] == "healthy":
                return True, f"系统健康状态良好 ({health_percentage}%)"
            else:
                # 收集问题详情
                problems = []
                checks = report.get("checks", {})
                
                for check_name, check_result in checks.items():
                    status = check_result.get("status", "unknown")
                    if status != "healthy":
                        component = check_result.get("component", check_name)
                        details = check_result.get("details", {})
                        
                        if "error" in details:
                            problems.append(f"{component}: {details['error']}")
                        elif status == "unhealthy":
                            problems.append(f"{component}: 状态异常")
                        elif status == "warning":
                            problems.append(f"{component}: 警告状态")
                
                problem_msg = " | ".join(problems[:3])  # 只显示前3个问题
                if len(problems) > 3:
                    problem_msg += f" ... 还有{len(problems)-3}个问题"
                
                return False, f"系统健康状态有问题 ({health_percentage}%): {problem_msg}"
                
        except ImportError:
            self.logger.warning("健康检查模块未安装，跳过健康检查")
            return True, "健康检查模块未安装"
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return False, f"健康检查异常: {str(e)}"
    
    def is_within_push_hours(self, start_hour: int = 8, end_hour: int = 22) -> bool:
        """
        检查是否在推送时间范围内
        
        Args:
            start_hour: 开始小时
            end_hour: 结束小时
            
        Returns:
            是否在推送时间范围内
        """
        current_hour = datetime.now().hour
        return start_hour <= current_hour <= end_hour
    
    def should_push_stocks(self) -> bool:
        """
        是否应该推送股票信息
        
        Returns:
            是否应该推送股票
        """
        try:
            stock_start = int(self.env_config.get("STOCK_PUSH_START", "8"))
            stock_end = int(self.env_config.get("STOCK_PUSH_END", "18"))
            return self.is_within_push_hours(stock_start, stock_end)
        except ValueError:
            return self.is_within_push_hours(8, 18)
    
    def should_push_news(self) -> bool:
        """
        是否应该推送新闻信息
        
        Returns:
            是否应该推送新闻
        """
        try:
            news_start = int(self.env_config.get("NEWS_PUSH_START", "8"))
            news_end = int(self.env_config.get("NEWS_PUSH_END", "22"))
            return self.is_within_push_hours(news_start, news_end)
        except ValueError:
            return self.is_within_push_hours(8, 22)
    
    def fetch_url(self, url: str, timeout: int = 10, retries: int = 2) -> Optional[requests.Response]:
        """
        获取URL内容
        
        Args:
            url: URL地址
            timeout: 超时时间
            retries: 重试次数
            
        Returns:
            Response对象或None
        """
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                self.logger.debug(f"成功获取URL: {url}")
                return response
            except requests.exceptions.Timeout:
                self.logger.warning(f"获取URL超时 ({attempt+1}/{retries}): {url}")
                if attempt == retries - 1:
                    self.logger.error(f"获取URL失败: {url} - 超时")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"获取URL失败 ({attempt+1}/{retries}): {url} - {e}")
                if attempt == retries - 1:
                    return None
            except Exception as e:
                self.logger.error(f"获取URL异常: {url} - {e}")
                return None
            
            # 重试前等待
            if attempt < retries - 1:
                time.sleep(1)
        
        return None
    
    def save_to_file(self, content: str, filename: str, directory: str = "./logs") -> str:
        """
        保存内容到文件
        
        Args:
            content: 要保存的内容
            filename: 文件名
            directory: 目录
            
        Returns:
            文件路径
        """
        import os
        from pathlib import Path
        
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        
        file_path = dir_path / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"内容已保存到: {file_path}")
            return str(file_path)
        except Exception as e:
            self.logger.error(f"保存文件失败: {file_path} - {e}")
            return ""
    
    def generate_timestamp(self) -> str:
        """
        生成时间戳
        
        Returns:
            时间戳字符串
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def format_duration(self, seconds: float) -> str:
        """
        格式化持续时间
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化后的时间字符串
        """
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小时"
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态
        
        Returns:
            系统状态字典
        """
        status = {
            "pusher_name": self.name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "whatsapp_number": get_whatsapp_number_display(),
            "should_push_stocks": self.should_push_stocks(),
            "should_push_news": self.should_push_news(),
            "current_hour": datetime.now().hour,
            "database_stats": self.news_db.get_stats(),
            "config_status": {
                "whatsapp_configured": self.env_config["WHATSAPP_NUMBER"] != "+86**********",
                "openclaw_exists": os.path.exists(self.env_config["OPENCLAW_PATH"])
            }
        }
        return status
    
    def cleanup(self):
        """
        清理资源
        """
        self.logger.info(f"清理 {self.name} 资源")
        self.session.close()
        # 清理数据库旧记录
        deleted_count = self.news_db.cleanup_old_records(days=7)
        if deleted_count > 0:
            self.logger.info(f"清理了 {deleted_count} 条旧记录")

if __name__ == "__main__":
    # 测试代码
    print("🧪 基础推送器测试")
    print("=" * 50)
    
    pusher = BasePusher("TestPusher")
    
    # 测试状态检查
    status = pusher.get_system_status()
    print(f"推送器名称: {status['pusher_name']}")
    print(f"时间戳: {status['timestamp']}")
    print(f"WhatsApp号码: {status['whatsapp_number']}")
    print(f"应该推送股票: {status['should_push_stocks']}")
    print(f"应该推送新闻: {status['should_push_news']}")
    print(f"当前小时: {status['current_hour']}")
    
    # 测试URL获取
    print("\n测试URL获取...")
    response = pusher.fetch_url("https://httpbin.org/get", timeout=5)
    if response:
        print(f"✅ URL获取成功: {response.status_code}")
    else:
        print("❌ URL获取失败")
    
    # 测试文件保存
    print("\n测试文件保存...")
    test_content = "测试内容\n时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = pusher.save_to_file(test_content, "test_output.txt")
    if file_path:
        print(f"✅ 文件保存成功: {file_path}")
    
    # 清理
    pusher.cleanup()
    
    print("\n✅ 基础推送器测试完成")
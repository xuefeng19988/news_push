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
from utils.message_sender import send_whatsapp_message, get_whatsapp_number_display
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
    
    def send_message(self, message: str, max_retries: int = 2) -> Tuple[bool, str]:
        """
        发送消息
        
        Args:
            message: 消息内容
            max_retries: 最大重试次数
            
        Returns:
            Tuple[成功状态, 结果消息]
        """
        self.logger.info(f"准备发送消息 ({len(message)} 字符)")
        success, result = send_whatsapp_message(message, max_retries=max_retries)
        
        if success:
            self.logger.info("消息发送成功")
        else:
            self.logger.error(f"消息发送失败: {result}")
        
        return success, result
    
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
        return start_hour <= current_hour < end_hour
    
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
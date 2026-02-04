#!/usr/bin/env python3
"""
统一的配置管理工具
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "./config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置目录路径
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # 默认配置
        self.default_configs = {
            "alert_config.json": {
                "stocks": [
                    {"symbol": "BABA", "name": "阿里巴巴", "alert_threshold": 5.0},
                    {"symbol": "9988.HK", "name": "阿里巴巴(港股)", "alert_threshold": 5.0},
                    {"symbol": "1810.HK", "name": "小米集团", "alert_threshold": 5.0},
                    {"symbol": "1211.HK", "name": "比亚迪股份", "alert_threshold": 5.0}
                ],
                "price_alerts": {
                    "enabled": True,
                    "check_interval_minutes": 30,
                    "max_alerts_per_day": 10
                }
            },
            "social_config.json": {
                "sources": {
                    "weibo": {
                        "enabled": True,
                        "hot_searches_count": 10
                    },
                    "twitter": {
                        "enabled": True,
                        "trends_count": 10
                    },
                    "reddit": {
                        "enabled": True,
                        "subreddits": ["all", "news", "worldnews"],
                        "posts_per_subreddit": 5
                    },
                    "thepaper": {
                        "enabled": True,
                        "sections": ["news", "finance", "tech"]
                    }
                },
                "fetch_interval_minutes": 60,
                "max_articles_per_source": 5
            },
            "clawdbot_stock_config.json": {
                "stocks": [
                    {"symbol": "BABA", "name": "阿里巴巴", "currency": "USD"},
                    {"symbol": "9988.HK", "name": "阿里巴巴(港股)", "currency": "HKD"},
                    {"symbol": "1810.HK", "name": "小米集团", "currency": "HKD"},
                    {"symbol": "1211.HK", "name": "比亚迪股份", "currency": "HKD"},
                    {"symbol": "^HSI", "name": "恒生指数", "currency": "HKD"},
                    {"symbol": "0700.HK", "name": "腾讯控股", "currency": "HKD"}
                ],
                "monitoring": {
                    "enabled": True,
                    "interval_minutes": 60,
                    "trading_hours_only": True
                }
            }
        }
    
    def get_config(self, config_name: str, create_if_missing: bool = True) -> Dict[str, Any]:
        """
        获取配置
        
        Args:
            config_name: 配置文件名
            create_if_missing: 如果不存在是否创建
            
        Returns:
            配置字典
        """
        config_path = self.config_dir / config_name
        
        # 如果配置文件不存在且需要创建
        if not config_path.exists() and create_if_missing:
            if config_name in self.default_configs:
                self.save_config(config_name, self.default_configs[config_name])
                return self.default_configs[config_name]
            else:
                return {}
        
        # 读取配置文件
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            if create_if_missing:
                return {}
            raise
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]):
        """
        保存配置
        
        Args:
            config_name: 配置文件名
            config_data: 配置数据
        """
        config_path = self.config_dir / config_name
        
        # 确保目录存在
        config_path.parent.mkdir(exist_ok=True)
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    def update_config(self, config_name: str, updates: Dict[str, Any]):
        """
        更新配置（合并更新）
        
        Args:
            config_name: 配置文件名
            updates: 要更新的配置
        """
        current_config = self.get_config(config_name, create_if_missing=True)
        current_config.update(updates)
        self.save_config(config_name, current_config)
    
    def get_env_config(self) -> Dict[str, str]:
        """
        获取环境变量配置
        
        Returns:
            环境变量配置字典
        """
        env_config = {
            # 基础配置
            "WHATSAPP_NUMBER": os.getenv("WHATSAPP_NUMBER", "+86**********"),
            "OPENCLAW_PATH": os.getenv("OPENCLAW_PATH", "/home/admin/.npm-global/bin/openclaw"),
            "DATABASE_PATH": os.getenv("DATABASE_PATH", "./news_cache.db"),
            "STOCK_PUSH_START": os.getenv("STOCK_PUSH_START", "8"),
            "STOCK_PUSH_END": os.getenv("STOCK_PUSH_END", "18"),
            "NEWS_PUSH_START": os.getenv("NEWS_PUSH_START", "8"),
            "NEWS_PUSH_END": os.getenv("NEWS_PUSH_END", "22"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
            "LOG_DIR": os.getenv("LOG_DIR", "./logs"),
            
            # API密钥配置
            "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY", ""),
            "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET", ""),
            "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN", ""),
            "WEIBO_API_KEY": os.getenv("WEIBO_API_KEY", ""),
            "REDDIT_CLIENT_ID": os.getenv("REDDIT_CLIENT_ID", ""),
            "REDDIT_CLIENT_SECRET": os.getenv("REDDIT_CLIENT_SECRET", ""),
            "YAHOO_FINANCE_API_KEY": os.getenv("YAHOO_FINANCE_API_KEY", ""),
            "NEWS_API_KEY": os.getenv("NEWS_API_KEY", ""),
            
            # 代理配置
            "HTTP_PROXY": os.getenv("HTTP_PROXY", ""),
            "HTTPS_PROXY": os.getenv("HTTPS_PROXY", ""),
        }
        return env_config
    
    def validate_config(self, config_name: str) -> tuple[bool, list[str]]:
        """
        验证配置
        
        Args:
            config_name: 配置文件名
            
        Returns:
            Tuple[是否有效, 错误信息列表]
        """
        config = self.get_config(config_name, create_if_missing=False)
        errors = []
        
        if config_name == "alert_config.json":
            if "stocks" not in config:
                errors.append("缺少stocks配置")
            elif not isinstance(config["stocks"], list):
                errors.append("stocks应为列表")
        
        elif config_name == "social_config.json":
            if "sources" not in config:
                errors.append("缺少sources配置")
        
        elif config_name == "clawdbot_stock_config.json":
            if "stocks" not in config:
                errors.append("缺少stocks配置")
        
        return len(errors) == 0, errors

def load_env_config():
    """加载环境变量配置（兼容旧代码）"""
    return {
        "WHATSAPP_NUMBER": os.getenv("WHATSAPP_NUMBER", "+86**********"),
        "OPENCLAW_PATH": os.getenv("OPENCLAW_PATH", "/home/admin/.npm-global/bin/openclaw")
    }

if __name__ == "__main__":
    # 测试代码
    print("⚙️ 配置管理工具测试")
    print("=" * 50)
    
    config_mgr = ConfigManager()
    
    # 测试环境配置
    env_config = config_mgr.get_env_config()
    print("环境配置:")
    for key, value in env_config.items():
        print(f"  {key}: {value}")
    
    # 测试配置文件管理
    print("\n配置文件测试:")
    test_config = config_mgr.get_config("alert_config.json")
    print(f"  股票警报配置: {len(test_config.get('stocks', []))} 只股票")
    
    # 测试配置验证
    for config_file in ["alert_config.json", "social_config.json", "clawdbot_stock_config.json"]:
        valid, errors = config_mgr.validate_config(config_file)
        print(f"  {config_file}: {'✅ 有效' if valid else '❌ 无效'}")
        if errors:
            print(f"    错误: {errors}")
    
    print("\n✅ 配置管理工具测试完成")

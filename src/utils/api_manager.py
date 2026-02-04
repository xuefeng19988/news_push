#!/usr/bin/env python3
"""
API密钥管理器
统一管理所有API密钥，从环境变量读取
"""

import os
from typing import Dict, Optional, Any
from .config import ConfigManager

class APIManager:
    """API密钥管理器"""
    
    def __init__(self):
        """初始化API管理器"""
        self.config_mgr = ConfigManager()
        self.env_config = self.config_mgr.get_env_config()
        
        # API配置
        self.api_configs = {
            "twitter": {
                "api_key": self.env_config.get("TWITTER_API_KEY", ""),
                "api_secret": self.env_config.get("TWITTER_API_SECRET", ""),
                "bearer_token": self.env_config.get("TWITTER_BEARER_TOKEN", ""),
                "enabled": bool(self.env_config.get("TWITTER_API_KEY")),
                "base_url": "https://api.twitter.com/2",
                "headers": self._get_twitter_headers,
            },
            "weibo": {
                "api_key": self.env_config.get("WEIBO_API_KEY", ""),
                "enabled": bool(self.env_config.get("WEIBO_API_KEY")),
                "base_url": "https://api.weibo.com/2",
                "headers": self._get_weibo_headers,
            },
            "reddit": {
                "client_id": self.env_config.get("REDDIT_CLIENT_ID", ""),
                "client_secret": self.env_config.get("REDDIT_CLIENT_SECRET", ""),
                "enabled": bool(self.env_config.get("REDDIT_CLIENT_ID")),
                "base_url": "https://www.reddit.com",
                "headers": self._get_reddit_headers,
            },
            "yahoo_finance": {
                "api_key": self.env_config.get("YAHOO_FINANCE_API_KEY", ""),
                "enabled": bool(self.env_config.get("YAHOO_FINANCE_API_KEY")),
                "base_url": "https://yfapi.net",
                "headers": self._get_yahoo_headers,
            },
            "news_api": {
                "api_key": self.env_config.get("NEWS_API_KEY", ""),
                "enabled": bool(self.env_config.get("NEWS_API_KEY")),
                "base_url": "https://newsapi.org/v2",
                "headers": self._get_newsapi_headers,
            }
        }
    
    def _get_twitter_headers(self) -> Dict[str, str]:
        """获取Twitter API请求头"""
        bearer_token = self.api_configs["twitter"]["bearer_token"]
        if bearer_token:
            return {
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json",
            }
        return {}
    
    def _get_weibo_headers(self) -> Dict[str, str]:
        """获取微博API请求头"""
        api_key = self.api_configs["weibo"]["api_key"]
        if api_key:
            return {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        return {}
    
    def _get_reddit_headers(self) -> Dict[str, str]:
        """获取Reddit API请求头"""
        client_id = self.api_configs["reddit"]["client_id"]
        client_secret = self.api_configs["reddit"]["client_secret"]
        
        if client_id and client_secret:
            # Reddit需要OAuth2认证，这里返回基础头
            # 实际使用时需要获取访问令牌
            return {
                "User-Agent": "NewsPushSystem/0.0.1",
            }
        return {}
    
    def _get_yahoo_headers(self) -> Dict[str, str]:
        """获取Yahoo Finance API请求头"""
        api_key = self.api_configs["yahoo_finance"]["api_key"]
        if api_key:
            return {
                "X-API-KEY": api_key,
                "Content-Type": "application/json",
            }
        return {}
    
    def _get_newsapi_headers(self) -> Dict[str, str]:
        """获取NewsAPI请求头"""
        api_key = self.api_configs["news_api"]["api_key"]
        if api_key:
            return {
                "X-Api-Key": api_key,
                "Content-Type": "application/json",
            }
        return {}
    
    def get_api_config(self, api_name: str) -> Dict[str, Any]:
        """
        获取API配置
        
        Args:
            api_name: API名称 (twitter, weibo, reddit, yahoo_finance, news_api)
            
        Returns:
            API配置字典
        """
        return self.api_configs.get(api_name.lower(), {})
    
    def is_api_enabled(self, api_name: str) -> bool:
        """
        检查API是否启用
        
        Args:
            api_name: API名称
            
        Returns:
            是否启用
        """
        config = self.get_api_config(api_name)
        return config.get("enabled", False)
    
    def get_api_headers(self, api_name: str) -> Dict[str, str]:
        """
        获取API请求头
        
        Args:
            api_name: API名称
            
        Returns:
            请求头字典
        """
        config = self.get_api_config(api_name)
        headers_func = config.get("headers")
        if callable(headers_func):
            return headers_func()
        return {}
    
    def get_api_url(self, api_name: str, endpoint: str = "") -> str:
        """
        获取API完整URL
        
        Args:
            api_name: API名称
            endpoint: API端点
            
        Returns:
            完整URL
        """
        config = self.get_api_config(api_name)
        base_url = config.get("base_url", "")
        
        if base_url and endpoint:
            return f"{base_url}/{endpoint.lstrip('/')}"
        elif base_url:
            return base_url
        else:
            return endpoint
    
    def check_all_apis(self) -> Dict[str, Dict[str, Any]]:
        """
        检查所有API状态
        
        Returns:
            API状态字典
        """
        status = {}
        
        for api_name, config in self.api_configs.items():
            enabled = config.get("enabled", False)
            has_key = bool(config.get("api_key") or config.get("bearer_token") or 
                          config.get("client_id") or config.get("client_secret"))
            
            status[api_name] = {
                "enabled": enabled,
                "configured": has_key,
                "status": "✅ 已配置" if enabled else "❌ 未配置",
                "message": "API密钥已配置" if enabled else "请设置环境变量"
            }
        
        return status
    
    def get_proxy_config(self) -> Dict[str, str]:
        """
        获取代理配置
        
        Returns:
            代理配置字典
        """
        proxies = {}
        
        http_proxy = self.env_config.get("HTTP_PROXY")
        https_proxy = self.env_config.get("HTTPS_PROXY")
        
        if http_proxy:
            proxies["http"] = http_proxy
        if https_proxy:
            proxies["https"] = https_proxy
        
        return proxies

def get_api_manager() -> APIManager:
    """
    获取API管理器实例（单例模式）
    
    Returns:
        APIManager实例
    """
    if not hasattr(get_api_manager, "_instance"):
        get_api_manager._instance = APIManager()
    return get_api_manager._instance

if __name__ == "__main__":
    # 测试代码
    print("🔑 API密钥管理器测试")
    print("=" * 50)
    
    api_mgr = APIManager()
    
    # 检查所有API状态
    print("📊 API状态检查:")
    status = api_mgr.check_all_apis()
    
    for api_name, api_status in status.items():
        print(f"  {api_name}: {api_status['status']}")
        if not api_status['enabled']:
            print(f"     提示: {api_status['message']}")
    
    print()
    
    # 检查代理配置
    proxies = api_mgr.get_proxy_config()
    if proxies:
        print("🌐 代理配置:")
        for protocol, proxy_url in proxies.items():
            print(f"  {protocol}: {proxy_url}")
    else:
        print("🌐 代理配置: 未设置")
    
    print()
    
    # 测试获取API配置
    print("🔧 API配置示例:")
    twitter_config = api_mgr.get_api_config("twitter")
    print(f"  Twitter启用: {twitter_config.get('enabled', False)}")
    
    twitter_headers = api_mgr.get_api_headers("twitter")
    print(f"  Twitter请求头: {len(twitter_headers)} 个")
    
    print()
    print("✅ API管理器测试完成")
    print()
    print("💡 使用提示:")
    print("  1. 设置环境变量来配置API密钥")
    print("  2. 例如: export TWITTER_API_KEY='your_key_here'")
    print("  3. 在代码中使用: from utils.api_manager import get_api_manager")
    print("  4. api_mgr = get_api_manager()")
    print("  5. headers = api_mgr.get_api_headers('twitter')")
#!/usr/bin/env python3
"""
社交媒体监控模块
使用API管理器从环境变量读取API密钥
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..utils.api_manager import get_api_manager
from ..utils.logger import Logger

class SocialMediaMonitor:
    """社交媒体监控器"""
    
    def __init__(self):
        """初始化社交媒体监控器"""
        self.logger = Logger("SocialMediaMonitor").get_logger()
        self.api_mgr = get_api_manager()
        self.session = None
        
        # 检查API状态
        self.check_api_status()
    
    def check_api_status(self):
        """检查API状态"""
        status = self.api_mgr.check_all_apis()
        
        self.logger.info("社交媒体API状态:")
        for api_name, api_status in status.items():
            if api_name in ["twitter", "weibo", "reddit"]:
                status_emoji = "✅" if api_status["enabled"] else "❌"
                self.logger.info(f"  {status_emoji} {api_name}: {api_status['status']}")
    
    def fetch_twitter_trends(self, location_id: int = 1) -> List[Dict[str, Any]]:
        """
        获取Twitter趋势
        
        Args:
            location_id: 位置ID (1=全球)
            
        Returns:
            趋势列表
        """
        if not self.api_mgr.is_api_enabled("twitter"):
            self.logger.warning("Twitter API未启用，跳过获取趋势")
            return []
        
        try:
            import requests
            
            # 获取API配置
            headers = self.api_mgr.get_api_headers("twitter")
            url = self.api_mgr.get_api_url("twitter", f"trends/place.json?id={location_id}")
            
            if not headers.get("Authorization"):
                self.logger.error("Twitter Bearer Token未配置")
                return []
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                trends = []
                
                # 解析趋势数据
                for trend_data in data.get("trends", []):
                    trend = {
                        "name": trend_data.get("name", ""),
                        "url": trend_data.get("url", ""),
                        "tweet_volume": trend_data.get("tweet_volume", 0),
                        "source": "Twitter",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    trends.append(trend)
                
                self.logger.info(f"获取到 {len(trends)} 个Twitter趋势")
                return trends[:10]  # 返回前10个趋势
            else:
                self.logger.error(f"Twitter API请求失败: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"获取Twitter趋势失败: {e}")
            return []
    
    def fetch_weibo_hot_searches(self) -> List[Dict[str, Any]]:
        """
        获取微博热搜
        
        Returns:
            热搜列表
        """
        if not self.api_mgr.is_api_enabled("weibo"):
            self.logger.warning("微博API未启用，跳过获取热搜")
            return []
        
        try:
            import requests
            
            # 微博热搜API
            url = "https://weibo.com/ajax/side/hotSearch"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
            }
            
            # 如果有API密钥，添加到请求头
            weibo_headers = self.api_mgr.get_api_headers("weibo")
            headers.update(weibo_headers)
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                hot_searches = []
                
                # 解析热搜数据
                for item in data.get("data", {}).get("realtime", [])[:20]:
                    hot_search = {
                        "rank": item.get("rank", 0),
                        "keyword": item.get("word", ""),
                        "url": f"https://s.weibo.com/weibo?q={item.get('word', '')}",
                        "hot_value": item.get("num", 0),
                        "source": "微博",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    hot_searches.append(hot_search)
                
                self.logger.info(f"获取到 {len(hot_searches)} 个微博热搜")
                return hot_searches[:15]  # 返回前15个热搜
            else:
                self.logger.error(f"微博API请求失败: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"获取微博热搜失败: {e}")
            return []
    
    def fetch_reddit_hot_posts(self, subreddit: str = "all", limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取Reddit热门帖子
        
        Args:
            subreddit: 子版块名称
            limit: 帖子数量限制
            
        Returns:
            帖子列表
        """
        if not self.api_mgr.is_api_enabled("reddit"):
            self.logger.warning("Reddit API未启用，跳过获取热门帖子")
            return []
        
        try:
            import requests
            
            # Reddit API (需要OAuth2认证，这里使用公开API)
            url = f"https://www.reddit.com/r/{subreddit}/hot.json"
            params = {
                "limit": limit,
                "raw_json": 1
            }
            
            headers = {
                "User-Agent": "NewsPushSystem/0.0.1"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                # 解析帖子数据
                for post_data in data.get("data", {}).get("children", [])[:limit]:
                    post = post_data.get("data", {})
                    
                    reddit_post = {
                        "title": post.get("title", ""),
                        "url": f"https://reddit.com{post.get('permalink', '')}",
                        "score": post.get("score", 0),
                        "num_comments": post.get("num_comments", 0),
                        "subreddit": post.get("subreddit", ""),
                        "author": post.get("author", ""),
                        "created_utc": post.get("created_utc", 0),
                        "source": "Reddit",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    posts.append(reddit_post)
                
                self.logger.info(f"从 r/{subreddit} 获取到 {len(posts)} 个热门帖子")
                return posts
            else:
                self.logger.error(f"Reddit API请求失败: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"获取Reddit热门帖子失败: {e}")
            return []
    
    def generate_social_media_report(self) -> str:
        """
        生成社交媒体报告
        
        Returns:
            报告字符串
        """
        report_parts = ["📱 社交媒体动态", ""]
        
        # 获取微博热搜
        weibo_hot_searches = self.fetch_weibo_hot_searches()
        if weibo_hot_searches:
            report_parts.append("🔥 微博热搜:")
            for i, search in enumerate(weibo_hot_searches[:5], 1):
                report_parts.append(f"{i}. {search['keyword']} ({search['hot_value']} 热度)")
            report_parts.append("")
        
        # 获取Twitter趋势
        twitter_trends = self.fetch_twitter_trends()
        if twitter_trends:
            report_parts.append("🐦 Twitter趋势:")
            for i, trend in enumerate(twitter_trends[:5], 1):
                tweet_count = f" ({trend['tweet_volume']} 推文)" if trend.get('tweet_volume') else ""
                report_parts.append(f"{i}. {trend['name']}{tweet_count}")
            report_parts.append("")
        
        # 获取Reddit热门
        reddit_posts = self.fetch_reddit_hot_posts("all", 5)
        if reddit_posts:
            report_parts.append("📝 Reddit热门:")
            for i, post in enumerate(reddit_posts[:3], 1):
                report_parts.append(f"{i}. {post['title']}")
                report_parts.append(f"   👍 {post['score']} | 💬 {post['num_comments']} | r/{post['subreddit']}")
            report_parts.append("")
        
        if len(report_parts) <= 2:  # 只有标题和空行
            report_parts.append("暂时无法获取社交媒体数据")
            report_parts.append("请配置相应的API密钥以启用功能")
        
        return "\n".join(report_parts)
    
    def run(self) -> str:
        """
        运行社交媒体监控
        
        Returns:
            社交媒体报告
        """
        self.logger.info("开始社交媒体监控")
        
        start_time = time.time()
        report = self.generate_social_media_report()
        
        duration = time.time() - start_time
        self.logger.info(f"社交媒体监控完成，耗时: {duration:.1f}秒")
        
        return report

def main():
    """主函数"""
    print("=" * 60)
    print("📱 社交媒体监控系统")
    print("=" * 60)
    
    monitor = SocialMediaMonitor()
    
    # 生成报告
    report = monitor.run()
    
    print("\n" + report)
    print("\n" + "=" * 60)
    print("✅ 社交媒体监控完成")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
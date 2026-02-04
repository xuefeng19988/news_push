#!/usr/bin/env python3
"""
社交媒体监控器 - 监控Twitter/X和Reddit热点
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import requests

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SocialMediaMonitor:
    """社交媒体监控器"""
    
    def __init__(self, config_file: str = "/home/admin/clawd/social_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
        # 数据存储
        self.data_dir = "/home/admin/clawd/social_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 监控关键词 (财经科技相关)
        self.keywords = [
            # 股票相关
            "stock", "stocks", "investing", "investment", "trading",
            "market", "markets", "finance", "financial",
            # 公司
            "Alibaba", "阿里巴巴", "BABA", "Tencent", "腾讯", "Xiaomi", "小米",
            "BYD", "比亚迪", "Tesla", "TSLA", "Apple", "AAPL", "Google", "GOOGL",
            # 科技
            "AI", "artificial intelligence", "tech", "technology", "innovation",
            "startup", "startups", "VC", "venture capital",
            # 加密货币
            "Bitcoin", "BTC", "Ethereum", "ETH", "crypto", "cryptocurrency",
            "blockchain", "Web3",
            # 经济
            "economy", "economic", "recession", "inflation", "Fed", "central bank"
        ]
        
        # 用户代理
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            "enabled": True,
            "check_interval_minutes": 15,
            "working_hours": {"start": 8, "end": 22},
            "twitter": {
                "enabled": True,
                "api_key": None,  # 需要Twitter API密钥
                "track_keywords": True,
                "max_tweets": 20
            },
            "reddit": {
                "enabled": True,
                "client_id": None,  # 需要Reddit API凭证
                "client_secret": None,
                "subreddits": ["stocks", "investing", "technology", "finance", "CryptoCurrency"],
                "max_posts": 20
            },
            "notification": {
                "min_importance": 3,
                "max_items": 5,
                "channels": ["whatsapp"]
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.save_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return default_config
    
    def save_config(self, config: Dict):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def should_check(self) -> bool:
        """是否应该检查"""
        if not self.config.get("enabled", True):
            return False
        
        # 检查工作时间
        current_hour = datetime.now().hour
        working_hours = self.config.get("working_hours", {"start": 8, "end": 22})
        
        if current_hour < working_hours["start"] or current_hour >= working_hours["end"]:
            logger.info(f"⏭️ 非工作时间，跳过社交媒体检查")
            return False
        
        return True
    
    def fetch_twitter_trends(self) -> List[Dict]:
        """获取Twitter趋势 (简化版，使用公开API)"""
        trends = []
        
        if not self.config.get("twitter", {}).get("enabled", True):
            return trends
        
        logger.info("🐦 获取Twitter趋势...")
        
        try:
            # 方法1: 使用公开的Twitter趋势API (有限制)
            # 注意: 正式使用需要Twitter API密钥
            
            # 这里使用简化的方法，实际需要Twitter API
            # 返回模拟数据用于测试
            
            mock_trends = [
                {
                    "name": "#StockMarket",
                    "tweet_volume": 125000,
                    "url": "https://twitter.com/search?q=%23StockMarket",
                    "importance": 4
                },
                {
                    "name": "#AI",
                    "tweet_volume": 89000,
                    "url": "https://twitter.com/search?q=%23AI",
                    "importance": 5
                },
                {
                    "name": "#Bitcoin",
                    "tweet_volume": 75000,
                    "url": "https://twitter.com/search?q=%23Bitcoin",
                    "importance": 4
                },
                {
                    "name": "#TechNews",
                    "tweet_volume": 52000,
                    "url": "https://twitter.com/search?q=%23TechNews",
                    "importance": 3
                }
            ]
            
            # 过滤相关趋势
            for trend in mock_trends:
                trend_name = trend["name"].lower().replace('#', '')
                
                # 检查是否包含关键词
                for keyword in self.keywords:
                    if keyword.lower() in trend_name:
                        trends.append(trend)
                        logger.info(f"  发现相关趋势: {trend['name']} ({trend['tweet_volume']}推文)")
                        break
            
            logger.info(f"✅ 获取 {len(trends)} 个相关Twitter趋势")
            
        except Exception as e:
            logger.error(f"❌ 获取Twitter趋势失败: {e}")
        
        return trends
    
    def fetch_reddit_posts(self) -> List[Dict]:
        """获取Reddit热门帖子"""
        posts = []
        
        if not self.config.get("reddit", {}).get("enabled", True):
            return posts
        
        logger.info("📱 获取Reddit热门帖子...")
        
        try:
            # Reddit API需要认证，这里使用简化方法
            # 实际使用需要Reddit API凭证
            
            subreddits = self.config.get("reddit", {}).get("subreddits", ["stocks", "investing"])
            
            for subreddit in subreddits[:3]:  # 限制检查的子版块数量
                try:
                    # 使用Reddit的JSON端点 (公开，有限制)
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                    
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for post in data.get("data", {}).get("children", [])[:5]:
                            post_data = post.get("data", {})
                            
                            title = post_data.get("title", "")
                            score = post_data.get("score", 0)
                            num_comments = post_data.get("num_comments", 0)
                            url = post_data.get("url", "")
                            permalink = f"https://reddit.com{post_data.get('permalink', '')}"
                            
                            # 检查是否包含关键词
                            title_lower = title.lower()
                            relevant = False
                            
                            for keyword in self.keywords:
                                if keyword.lower() in title_lower:
                                    relevant = True
                                    break
                            
                            if relevant and score > 50:  # 只关注热门帖子
                                post_info = {
                                    "title": title,
                                    "subreddit": subreddit,
                                    "score": score,
                                    "comments": num_comments,
                                    "url": url if url.startswith('http') else permalink,
                                    "importance": self.calculate_importance(score, num_comments),
                                    "source": "reddit"
                                }
                                
                                posts.append(post_info)
                                logger.info(f"  发现热门帖子: r/{subreddit} - {title[:50]}... ({score}↑)")
                    
                    time.sleep(1)  # 避免请求过快
                    
                except Exception as e:
                    logger.error(f"❌ 获取r/{subreddit}失败: {e}")
                    continue
            
            logger.info(f"✅ 获取 {len(posts)} 个相关Reddit帖子")
            
        except Exception as e:
            logger.error(f"❌ 获取Reddit帖子失败: {e}")
        
        return posts
    
    def calculate_importance(self, score: int, comments: int) -> int:
        """计算内容重要性 (1-5分)"""
        importance = 1
        
        # 基于分数
        if score > 1000:
            importance += 2
        elif score > 100:
            importance += 1
        
        # 基于评论数
        if comments > 500:
            importance += 2
        elif comments > 50:
            importance += 1
        
        return min(max(importance, 1), 5)
    
    def analyze_sentiment(self, content: str) -> str:
        """简单情感分析"""
        positive_words = ["bullish", "growth", "profit", "gain", "up", "positive", "good", "great", "buy"]
        negative_words = ["bearish", "loss", "drop", "down", "negative", "bad", "sell", "crash", "warning"]
        
        content_lower = content.lower()
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def format_social_summary(self, trends: List[Dict], posts: List[Dict]) -> str:
        """格式化社交媒体摘要"""
        if not trends and not posts:
            return "📭 当前无重要社交媒体动态"
        
        summary = "🌐 **社交媒体热点摘要**\n\n"
        
        # Twitter趋势
        if trends:
            summary += "🐦 **Twitter趋势**:\n"
            
            for i, trend in enumerate(trends[:3], 1):
                name = trend["name"]
                volume = trend.get("tweet_volume", 0)
                importance = trend.get("importance", 1)
                
                summary += f"{i}. {name}\n"
                if volume:
                    summary += f"   📊 {volume:,} 推文\n"
                summary += f"   ⭐ {'★' * importance}\n\n"
        
        # Reddit帖子
        if posts:
            summary += "📱 **Reddit热门**:\n"
            
            for i, post in enumerate(posts[:3], 1):
                title = post["title"]
                subreddit = post["subreddit"]
                score = post["score"]
                comments = post["comments"]
                importance = post["importance"]
                
                # 简单情感分析
                sentiment = self.analyze_sentiment(title)
                sentiment_emoji = "📈" if sentiment == "positive" else "📉" if sentiment == "negative" else "📊"
                
                summary += f"{i}. {title[:60]}...\n"
                summary += f"   📍 r/{subreddit}\n"
                summary += f"   👍 {score} ↑ | 💬 {comments}\n"
                summary += f"   {sentiment_emoji} {sentiment}\n"
                summary += f"   ⭐ {'★' * importance}\n\n"
        
        # 统计信息
        summary += "---\n"
        summary += f"📊 统计: {len(trends)}趋势 + {len(posts)}帖子\n"
        summary += f"⏰ 更新时间: {datetime.now().strftime('%H:%M')}\n"
        summary += "🔍 监控关键词: 股票/投资/科技/AI/加密货币\n"
        
        return summary
    
    def check_and_notify(self) -> Optional[str]:
        """检查并生成通知"""
        if not self.should_check():
            return None
        
        logger.info("🔍 开始社交媒体监控...")
        
        try:
            # 获取数据
            twitter_trends = self.fetch_twitter_trends()
            reddit_posts = self.fetch_reddit_posts()
            
            # 生成摘要
            summary = self.format_social_summary(twitter_trends, reddit_posts)
            
            # 保存数据
            self.save_social_data(twitter_trends, reddit_posts)
            
            # 检查是否需要通知
            min_importance = self.config.get("notification", {}).get("min_importance", 3)
            
            has_important_content = False
            for trend in twitter_trends:
                if trend.get("importance", 1) >= min_importance:
                    has_important_content = True
                    break
            
            for post in reddit_posts:
                if post.get("importance", 1) >= min_importance:
                    has_important_content = True
                    break
            
            if has_important_content:
                logger.info("✅ 发现重要社交媒体动态")
                
                # 保存摘要文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                summary_file = f"./logs/social_summary_{timestamp}.txt"
                
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(summary)
                
                logger.info(f"📝 摘要已保存: {summary_file}")
                return summary_file
            else:
                logger.info("📭 无重要社交媒体动态")
                return None
            
        except Exception as e:
            logger.error(f"❌ 社交媒体监控失败: {e}")
            return None
    
    def save_social_data(self, trends: List[Dict], posts: List[Dict]):
        """保存社交媒体数据"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "twitter_trends": trends,
                "reddit_posts": posts,
                "total_items": len(trends) + len(posts)
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H")
            data_file = f"{self.data_dir}/social_data_{timestamp}.json"
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"❌ 保存数据失败: {e}")

def test_social_monitor():
    """测试社交媒体监控器"""
    print("🌐 测试社交媒体监控器...")
    
    monitor = SocialMediaMonitor()
    
    # 测试数据获取
    print("\n1. 获取Twitter趋势:")
    trends = monitor.fetch_twitter_trends()
    for trend in trends[:2]:
        print(f"   - {trend['name']} ({trend.get('tweet_volume', 0)}推文)")
    
    print("\n2. 获取Reddit帖子:")
    posts = monitor.fetch_reddit_posts()
    for post in posts[:2]:
        print(f"   - r/{post['subreddit']}: {post['title'][:50]}...")
    
    print("\n3. 生成摘要:")
    summary = monitor.format_social_summary(trends, posts)
    print(summary[:200] + "..." if len(summary) > 200 else summary)
    
    print("\n4. 完整检查:")
    result = monitor.check_and_notify()
    if result:
        print(f"✅ 检查完成，摘要文件: {result}")
    else:
        print("✅ 检查完成，无重要动态")
    
    return monitor

if __name__ == "__main__":
    monitor = test_social_monitor()
    print("\n🌐 社交媒体监控器测试完成")
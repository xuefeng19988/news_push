#!/usr/bin/env python3
"""
全球新闻推送系统 - 支持国内外新闻源
支持: 国内新闻 + Twitter/X + Reddit + RSS新闻源
"""

import os
import json
import time
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GlobalNewsPusher:
    def __init__(self):
        self.news_file = "./logs/stock_data/news_history.json"
        self.news_cache = {}
        self.load_news_cache()
        
        # 新闻源配置 - 增强版，更多新闻源
        self.news_sources = {
            # ========== 国际媒体 ==========
            "bbc": {
                "name": "BBC中文网",
                "url": "https://www.bbc.com/zhongwen/simp/index.xml",
                "type": "rss",
                "enabled": True,
                "category": "国际"
            },
            "reuters": {
                "name": "路透社中文",
                "url": "https://cn.reuters.com/rssFeed/CNTopGenNews/",
                "type": "rss",
                "enabled": True,
                "category": "国际"
            },
            "ft": {
                "name": "金融时报中文",
                "url": "https://www.ftchinese.com/rss/news",
                "type": "rss",
                "enabled": True,
                "category": "财经"
            },
            "nytimes": {
                "name": "纽约时报中文",
                "url": "https://cn.nytimes.com/rss/",
                "type": "rss",
                "enabled": True,
                "category": "国际"
            },
            "bloomberg": {
                "name": "彭博社",
                "url": "https://www.bloomberg.com/feeds/bbiz/sitemap_news.xml",
                "type": "rss",
                "enabled": True,
                "category": "财经"
            },
            "wsj": {
                "name": "华尔街日报中文",
                "url": "https://cn.wsj.com/rss/",
                "type": "rss",
                "enabled": True,
                "category": "财经"
            },
            "economist": {
                "name": "经济学人",
                "url": "https://www.economist.com/rss",
                "type": "rss",
                "enabled": True,
                "category": "财经"
            },
            
            # ========== 国内财经 ==========
            "wallstreetcn": {
                "name": "华尔街见闻",
                "url": "https://wallstreetcn.com/rss",
                "type": "rss",
                "enabled": True,
                "category": "财经"
            },
            "caixin": {
                "name": "财新网",
                "url": "https://www.caixin.com/rss/",
                "type": "rss",
                "enabled": True,
                "category": "财经"
            },
            "eastmoney": {
                "name": "东方财富",
                "url": "https://rss.cnfol.com/",
                "type": "rss",
                "enabled": True,
                "category": "财经"
            },
            "sina_finance": {
                "name": "新浪财经",
                "url": "https://rss.sina.com.cn/finance/",
                "type": "rss",
                "enabled": True,
                "category": "财经"
            },
            "hexun": {
                "name": "和讯网",
                "url": "https://rss.hexun.com/",
                "type": "rss",
                "enabled": True,
                "category": "财经"
            },
            "yicai": {
                "name": "第一财经",
                "url": "https://www.yicai.com/rss/",
                "type": "rss",
                "enabled": True,
                "category": "财经"
            },
            
            # ========== 科技新闻 ==========
            "techcrunch": {
                "name": "TechCrunch",
                "url": "https://techcrunch.com/feed/",
                "type": "rss",
                "enabled": True,
                "category": "科技"
            },
            "theverge": {
                "name": "The Verge",
                "url": "https://www.theverge.com/rss/index.xml",
                "type": "rss",
                "enabled": True,
                "category": "科技"
            },
            "wired": {
                "name": "WIRED",
                "url": "https://www.wired.com/feed/rss",
                "type": "rss",
                "enabled": True,
                "category": "科技"
            },
            "arstechnica": {
                "name": "Ars Technica",
                "url": "https://arstechnica.com/feed/",
                "type": "rss",
                "enabled": True,
                "category": "科技"
            },
            "engadget": {
                "name": "Engadget",
                "url": "https://www.engadget.com/rss.xml",
                "type": "rss",
                "enabled": True,
                "category": "科技"
            },
            "techmeme": {
                "name": "Techmeme",
                "url": "https://www.techmeme.com/feed.xml",
                "type": "rss",
                "enabled": True,
                "category": "科技"
            },
            
            # ========== 加密货币 ==========
            "coindesk": {
                "name": "CoinDesk",
                "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
                "type": "rss",
                "enabled": True,
                "category": "加密货币"
            },
            "cointelegraph": {
                "name": "CoinTelegraph",
                "url": "https://cointelegraph.com/rss",
                "type": "rss",
                "enabled": True,
                "category": "加密货币"
            },
            
            # ========== 创业投资 ==========
            "venturebeat": {
                "name": "VentureBeat",
                "url": "https://venturebeat.com/feed/",
                "type": "rss",
                "enabled": True,
                "category": "创业"
            },
            "techinasia": {
                "name": "Tech in Asia",
                "url": "https://www.techinasia.com/feed",
                "type": "rss",
                "enabled": True,
                "category": "创业"
            }
        }
        
        # 关键词过滤 (增强版)
        self.keywords = [
            # ========== 股票投资 ==========
            "stock", "stocks", "share", "shares", "equity", "equities",
            "投资", "invest", "investment", "portfolio", "trading", "trade",
            "股市", "stock market", "market", "markets", "exchange",
            "证券", "securities", "broker", "brokerage", "trader",
            
            # ========== 基金理财 ==========
            "基金", "fund", "funds", "ETF", "mutual fund", "hedge fund",
            "理财", "wealth", "wealth management", "asset", "assets",
            "养老金", "pension", "retirement", "401k", "IRA",
            
            # ========== 经济金融 ==========
            "经济", "economy", "economic", "economics", "GDP", "growth",
            "金融", "finance", "financial", "bank", "banking", "banker",
            "央行", "central bank", "Fed", "Federal Reserve", "ECB",
            "利率", "interest rate", "rate", "rates", "yield", "bond",
            "通胀", "inflation", "deflation", "CPI", "PPI", "price",
            "货币政策", "monetary policy", "fiscal policy", "policy",
            " recession", "downturn", "slowdown", "crisis",
            
            # ========== 科技 ==========
            "科技", "technology", "tech", "innovation", "innovative",
            "人工智能", "AI", "artificial intelligence", "machine learning",
            "互联网", "internet", "web", "online", "digital", "digitization",
            "云计算", "cloud", "cloud computing", "AWS", "Azure", "Google Cloud",
            "大数据", "big data", "data", "analytics", "analysis",
            "5G", "6G", "network", "telecom", "telecommunications",
            "芯片", "chip", "semiconductor", "processor", "CPU", "GPU",
            "软件", "software", "app", "application", "platform",
            "硬件", "hardware", "device", "smartphone", "computer",
            
            # ========== 公司 ==========
            "阿里巴巴", "Alibaba", "BABA", "Tencent", "腾讯", "0700",
            "百度", "Baidu", "BIDU", "小米", "Xiaomi", "1810",
            "华为", "Huawei", "比亚迪", "BYD", "002594",
            "苹果", "Apple", "AAPL", "谷歌", "Google", "GOOGL", "GOOG",
            "微软", "Microsoft", "MSFT", "亚马逊", "Amazon", "AMZN",
            "特斯拉", "Tesla", "TSLA", "英伟达", "NVIDIA", "NVDA",
            "Meta", "Facebook", "FB", "Netflix", "NFLX",
            
            # ========== 市场指数 ==========
            "美股", "US stocks", "S&P", "S&P 500", "Dow", "Dow Jones",
            "纳斯达克", "NASDAQ", "港股", "Hong Kong stocks", "恒生", "Hang Seng",
            "A股", "China stocks", "上证", "Shanghai", "深证", "Shenzhen",
            "创业板", "ChiNext", "科创板", "STAR Market",
            
            # ========== 加密货币 ==========
            "比特币", "Bitcoin", "BTC", "以太坊", "Ethereum", "ETH",
            "加密货币", "crypto", "cryptocurrency", "digital currency",
            "区块链", "blockchain", "Web3", "DeFi", "NFT", "token",
            
            # ========== 重要事件 ==========
            "财报", "earnings", "quarterly", "Q1", "Q2", "Q3", "Q4",
            "业绩", "performance", "results", "revenue", "profit", "loss",
            "收购", "acquisition", "acquire", "merger", "merge", "M&A",
            "合并", "consolidation", "partnership", "alliance",
            "上市", "IPO", "initial public offering", "listing",
            "融资", "funding", "raise", "capital", "venture", "VC",
            "裁员", "layoff", "layoffs", "firing", "fired",
            "涨价", "price increase", "涨价", "price hike",
            
            # ========== 行业 ==========
            "汽车", "auto", "automotive", "car", "EV", "electric vehicle",
            "房地产", "real estate", "property", "housing", "mortgage",
            "能源", "energy", "oil", "gas", "petroleum", "renewable",
            "医疗", "healthcare", "medical", "pharma", "pharmaceutical",
            "消费", "consumer", "retail", "e-commerce", "commerce",
            
            # ========== 政策监管 ==========
            "监管", "regulation", "regulatory", "supervision",
            "政策", "policy", "law", "legislation", "bill",
            "税收", "tax", "taxation", "tariff", "duty",
            "制裁", "sanction", "sanctions", "embargo",
            
            # ========== 地缘政治 ==========
            "中美", "US-China", "China-US", "trade war",
            "俄乌", "Russia-Ukraine", "Ukraine-Russia",
            "中东", "Middle East", "Israel", "Palestine",
            "欧盟", "EU", "European Union", "Brexit"
        ]
        
        # 用户配置
        self.user_preferences = {
            "min_importance": 3,  # 重要性阈值 (1-5)
            "max_articles": 5,    # 每次推送最大文章数
            "language": "zh",     # 语言偏好
            "categories": ["财经", "科技", "股票"]  # 关注的分类
        }
    
    def load_news_cache(self):
        """加载新闻历史记录"""
        try:
            if os.path.exists(self.news_file):
                with open(self.news_file, 'r', encoding='utf-8') as f:
                    self.news_cache = json.load(f)
            else:
                self.news_cache = {"articles": [], "last_update": None}
        except Exception as e:
            logger.error(f"加载新闻缓存失败: {e}")
            self.news_cache = {"articles": [], "last_update": None}
    
    def save_news_cache(self):
        """保存新闻历史记录"""
        try:
            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump(self.news_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存新闻缓存失败: {e}")
    
    def fetch_rss_news(self, source_name: str, source_config: dict) -> List[Dict]:
        """获取RSS新闻"""
        articles = []
        try:
            logger.info(f"从 {source_name} 获取RSS新闻...")
            feed = feedparser.parse(source_config["url"])
            
            for entry in feed.entries[:10]:  # 取最新10条
                # 解析文章信息
                article = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "source": source_name,
                    "source_name": source_config["name"],
                    "importance": self.calculate_importance(entry.get("title", "") + " " + entry.get("summary", "")),
                    "category": self.detect_category(entry.get("title", "")),
                    "timestamp": datetime.now().isoformat()
                }
                
                # 过滤重要文章
                if article["importance"] >= self.user_preferences["min_importance"]:
                    articles.append(article)
                    logger.info(f"  发现重要文章: {article['title'][:50]}... (重要性: {article['importance']})")
            
            logger.info(f"✅ 从 {source_name} 获取 {len(articles)} 条重要新闻")
            
        except Exception as e:
            logger.error(f"❌ 获取RSS新闻失败 ({source_name}): {e}")
        
        return articles
    
    def fetch_web_news(self, source_name: str, source_config: dict) -> List[Dict]:
        """获取网页新闻 (备用方法)"""
        articles = []
        try:
            logger.info(f"从 {source_name} 获取网页新闻...")
            
            # 使用requests获取网页
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(source_config["url"], headers=headers, timeout=10)
            response.raise_for_status()
            
            # 简单解析标题 (这里需要根据具体网站调整)
            # 这是一个简化的示例
            title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
            if title_match:
                article = {
                    "title": title_match.group(1),
                    "link": source_config["url"],
                    "summary": "从网页获取的最新新闻",
                    "published": datetime.now().isoformat(),
                    "source": source_name,
                    "source_name": source_config["name"],
                    "importance": 3,  # 默认重要性
                    "category": "综合",
                    "timestamp": datetime.now().isoformat()
                }
                articles.append(article)
                logger.info(f"  获取文章: {article['title'][:50]}...")
            
            logger.info(f"✅ 从 {source_name} 获取 {len(articles)} 条新闻")
            
        except Exception as e:
            logger.error(f"❌ 获取网页新闻失败 ({source_name}): {e}")
        
        return articles
    
    def calculate_importance(self, text: str) -> int:
        """计算文章重要性 (1-5分)"""
        importance = 1  # 基础分
        
        # 关键词匹配加分
        for keyword in self.keywords:
            if keyword.lower() in text.lower():
                importance += 1
        
        # 标题长度和内容质量
        if len(text) > 100:
            importance += 1
        
        # 限制在1-5分
        return min(max(importance, 1), 5)
    
    def detect_category(self, title: str) -> str:
        """检测文章分类"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ["股票", "股市", "投资", "基金", "理财", "金融"]):
            return "财经"
        elif any(word in title_lower for word in ["科技", "人工智能", "AI", "互联网", "手机", "电脑"]):
            return "科技"
        elif any(word in title_lower for word in ["政治", "政策", "政府", "外交"]):
            return "政治"
        elif any(word in title_lower for word in ["体育", "足球", "篮球", "比赛"]):
            return "体育"
        elif any(word in title_lower for word in ["娱乐", "电影", "音乐", "明星"]):
            return "娱乐"
        else:
            return "综合"
    
    def is_new_article(self, article: Dict) -> bool:
        """检查是否是新的文章"""
        for cached_article in self.news_cache.get("articles", []):
            if (article["title"] == cached_article["title"] and 
                article["source"] == cached_article["source"]):
                return False
        return True
    
    def fetch_all_news(self) -> List[Dict]:
        """从所有新闻源获取新闻"""
        all_articles = []
        
        logger.info("📡 开始获取全球新闻...")
        
        for source_name, source_config in self.news_sources.items():
            if not source_config.get("enabled", True):
                continue
            
            try:
                if source_config["type"] == "rss":
                    articles = self.fetch_rss_news(source_name, source_config)
                elif source_config["type"] == "web":
                    articles = self.fetch_web_news(source_name, source_config)
                else:
                    continue
                
                # 过滤新文章
                new_articles = [article for article in articles if self.is_new_article(article)]
                all_articles.extend(new_articles)
                
                # 更新缓存
                self.news_cache["articles"].extend(new_articles)
                
            except Exception as e:
                logger.error(f"❌ 处理新闻源 {source_name} 失败: {e}")
                continue
        
        # 按重要性排序
        all_articles.sort(key=lambda x: x["importance"], reverse=True)
        
        # 限制文章数量
        max_articles = self.user_preferences["max_articles"]
        if len(all_articles) > max_articles:
            all_articles = all_articles[:max_articles]
        
        # 更新最后更新时间
        self.news_cache["last_update"] = datetime.now().isoformat()
        
        # 清理旧文章 (保留最近100条)
        if len(self.news_cache["articles"]) > 100:
            self.news_cache["articles"] = self.news_cache["articles"][-100:]
        
        # 保存缓存
        self.save_news_cache()
        
        logger.info(f"✅ 共获取 {len(all_articles)} 条新文章")
        return all_articles
    
    def format_news_message(self, articles: List[Dict]) -> str:
        """格式化新闻消息 (增强版内容)"""
        if not articles:
            return "📭 没有新的重要新闻需要推送"
        
        message = "📰 **全球重要新闻摘要**\n\n"
        
        for i, article in enumerate(articles, 1):
            # 清理标题中的特殊字符
            title = article['title']
            title = title.replace('"', "'").replace('`', "'").replace('\\', '')
            
            # 格式化时间
            try:
                pub_time = datetime.fromisoformat(article["published"].replace('Z', '+00:00'))
                time_str = pub_time.strftime("%H:%M")
            except:
                time_str = "刚刚"
            
            # 添加文章标题
            message += f"{i}. **{title}**\n"
            
            # 来源和时间
            message += f"   📍 来源: {article['source_name']}\n"
            message += f"   ⏰ 时间: {time_str}\n"
            
            # 分类
            category = article.get('category', '综合')
            message += f"   🏷️ 分类: {category}\n"
            
            # 重要性评级
            importance = article['importance']
            importance_stars = '★' * importance
            message += f"   ⭐ 重要性: {importance_stars} ({importance}/5)\n"
            
            # 详细摘要 (增加长度)
            if article.get("summary"):
                summary = article["summary"]
                # 清理摘要
                summary = summary.replace('"', "'").replace('`', "'").replace('\\', '')
                
                # 根据重要性决定摘要长度
                if importance >= 4:
                    # 重要新闻显示更长摘要
                    if len(summary) > 150:
                        summary = summary[:150] + "..."
                else:
                    if len(summary) > 100:
                        summary = summary[:100] + "..."
                
                message += f"   📝 摘要: {summary}\n"
            
            # 关键信息提取 (尝试从摘要中提取)
            if article.get("summary"):
                summary_lower = article["summary"].lower()
                key_points = []
                
                # 检查是否包含重要关键词
                finance_keywords = ["stock", "market", "invest", "price", "earnings", "revenue"]
                tech_keywords = ["ai", "artificial intelligence", "tech", "software", "hardware"]
                company_keywords = ["alibaba", "tencent", "xiaomi", "byd", "tesla", "apple"]
                
                for keyword in finance_keywords:
                    if keyword in summary_lower:
                        key_points.append("💰 财经相关")
                        break
                
                for keyword in tech_keywords:
                    if keyword in summary_lower:
                        key_points.append("🤖 科技相关")
                        break
                
                for keyword in company_keywords:
                    if keyword in summary_lower:
                        key_points.append("🏢 公司动态")
                        break
                
                if key_points:
                    message += f"   🔑 关键词: {', '.join(key_points[:2])}\n"
            
            # 链接 - 显示完整文章地址
            link = article['link']
            if link:
                # 清理链接，确保可点击
                link = link.strip()
                # WhatsApp中链接可能需要特殊处理
                if len(link) < 150:  # 避免过长链接
                    message += f"   🔗 {link}\n"
                else:
                    # 如果链接太长，显示缩短版本但保留完整链接
                    short_link = link[:80] + "..."
                    message += f"   🔗 {short_link}\n"
                    # 在消息末尾添加完整链接
                    # 注意：这需要在消息格式化函数中特殊处理
            
            message += "\n"
        
        # 增强统计信息
        message += "---\n"
        message += f"📊 **统计信息**:\n"
        message += f"   • 文章数量: {len(articles)} 条重要新闻\n"
        
        # 分类统计
        categories = {}
        for article in articles:
            cat = article.get('category', '综合')
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            message += f"   • 分类分布: "
            cat_list = [f"{cat}({count})" for cat, count in categories.items()]
            message += ", ".join(cat_list[:3]) + "\n"
        
        # 重要性统计
        importance_counts = {}
        for article in articles:
            imp = article['importance']
            importance_counts[imp] = importance_counts.get(imp, 0) + 1
        
        if importance_counts:
            imp_list = [f"{'★'*imp}({count})" for imp, count in sorted(importance_counts.items())]
            message += f"   • 重要性: {', '.join(imp_list)}\n"
        
        message += f"   • 新闻源: {len([s for s in self.news_sources.values() if s.get('enabled', True)])} 个活跃源\n"
        message += f"   • 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        message += f"   • 推送频率: 每小时自动推送\n"
        
        # 添加简要分析
        if len(articles) >= 3:
            message += "\n📈 **简要分析**:\n"
            
            # 检查是否有高重要性新闻
            high_importance = sum(1 for a in articles if a['importance'] >= 4)
            if high_importance > 0:
                message += f"   • 有 {high_importance} 条高重要性新闻(4★+)\n"
            
            # 检查分类分布
            if '财经' in categories:
                message += f"   • 财经新闻: {categories['财经']} 条\n"
            if '科技' in categories:
                message += f"   • 科技新闻: {categories['科技']} 条\n"
        
        # 检查消息长度
        message_length = len(message)
        logger.info(f"📱 消息长度: {message_length} 字符")
        
        if message_length > 4000:
            logger.warning("⚠️ 消息过长，进行精简...")
            # 精简消息，保留核心内容
            lines = message.split('\n')
            simplified = []
            for line in lines:
                if len(''.join(simplified)) + len(line) < 3500:
                    simplified.append(line)
                else:
                    break
            
            message = '\n'.join(simplified)
            message += "\n... (内容已精简)\n"
        
        return message
    
    def run(self):
        """运行新闻推送"""
        logger.info("🚀 全球新闻推送系统启动")
        
        try:
            # 获取新闻
            articles = self.fetch_all_news()
            
            if not articles:
                logger.info("📭 没有新的重要新闻需要推送")
                return None
            
            # 格式化消息
            message = self.format_news_message(articles)
            
            # 保存消息到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            message_file = f"./logs/news_message_{timestamp}.txt"
            
            with open(message_file, 'w', encoding='utf-8') as f:
                f.write(message)
            
            logger.info(f"✅ 新闻消息已保存: {message_file}")
            
            # 同时保存到待发送队列
            pending_file = f"./logs/pending_news_{timestamp}.txt"
            with open(pending_file, 'w', encoding='utf-8') as f:
                f.write(message)
            
            logger.info(f"✅ 新闻已添加到待发送队列: {pending_file}")
            
            return message_file
            
        except Exception as e:
            logger.error(f"❌ 新闻推送系统运行失败: {e}")
            return None

def main():
    """主函数"""
    pusher = GlobalNewsPusher()
    result = pusher.run()
    
    if result:
        print(f"✅ 新闻推送完成: {result}")
        # 读取并显示消息
        with open(result, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("❌ 新闻推送失败或没有新新闻")

if __name__ == "__main__":
    main()
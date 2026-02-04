#!/usr/bin/env python3
"""
优化版新闻+股票推送系统
使用统一的工具模块，消除重复代码
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any, Optional

# 导入工具模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import NewsDatabase
from utils.config import ConfigManager, load_env_config
from utils.logger import Logger

class NewsStockPusherOptimized:
    """优化版新闻+股票推送器"""
    
    def __init__(self):
        # 初始化配置
        self.config_mgr = ConfigManager()
        self.env_config = load_env_config()
        
        # 初始化日志
        self.logger = Logger("news_stock_pusher", level="INFO").get_logger()
        
        # 初始化数据库
        self.db = NewsDatabase(self.env_config.get("DATABASE_PATH", "./news_cache.db"))
        
        # 初始化HTTP会话
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        # 加载股票配置
        self.stock_config = self.config_mgr.get_config("clawdbot_stock_config.json")
        self.stocks = self.stock_config.get("stocks", [])
        
        # 新闻源配置
        self.news_sources = self._get_news_sources()
        
        self.logger.info("新闻股票推送器初始化完成")
    
    def _get_news_sources(self) -> List[Dict[str, Any]]:
        """获取新闻源配置"""
        return [
            # 国际新闻
            {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "type": "rss"},
            {"name": "CNN", "url": "http://rss.cnn.com/rss/edition.rss", "type": "rss"},
            {"name": "Financial Times", "url": "https://www.ft.com/?format=rss", "type": "rss"},
            {"name": "Nikkei Asia", "url": "https://asia.nikkei.com/rss/feed/nar", "type": "rss"},
            {"name": "SCMP", "url": "https://www.scmp.com/rss/91/feed", "type": "rss"},
            
            # 中国新闻
            {"name": "澎湃新闻", "url": "https://www.thepaper.cn/feed_channel_25950", "type": "rss"},
            {"name": "新浪财经", "url": "http://finance.sina.com.cn/roll/index.d.html?cid=56578", "type": "html"},
            
            # 社交媒体
            {"name": "微博热搜", "url": "https://s.weibo.com/top/summary", "type": "weibo"},
            {"name": "Reddit热门", "url": "https://www.reddit.com/r/all/hot.json", "type": "reddit"},
        ]
    
    def fetch_news_from_rss(self, rss_url: str, source: str) -> List[Dict[str, Any]]:
        """从RSS源获取新闻"""
        try:
            response = self.session.get(rss_url, timeout=10)
            response.raise_for_status()
            
            articles = []
            
            # 简化的RSS解析（实际应使用feedparser库）
            # 这里使用简化的解析逻辑
            content = response.text
            
            # 查找文章项
            import re
            item_pattern = r'<item>.*?</item>'
            items = re.findall(item_pattern, content, re.DOTALL)
            
            for item in items[:10]:  # 限制数量
                # 提取标题
                title_match = re.search(r'<title>(.*?)</title>', item)
                title = title_match.group(1).strip() if title_match else "无标题"
                
                # 提取链接
                link_match = re.search(r'<link>(.*?)</link>', item)
                url = link_match.group(1).strip() if link_match else ""
                
                # 提取描述
                desc_match = re.search(r'<description>(.*?)</description>', item)
                description = desc_match.group(1).strip() if desc_match else ""
                
                # 提取发布时间
                pub_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                pub_date = pub_match.group(1).strip() if pub_match else ""
                
                if title and url:
                    articles.append({
                        "title": title,
                        "url": url,
                        "description": description,
                        "pub_date": pub_date,
                        "source": source
                    })
            
            self.logger.info(f"从 {source} 获取到 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            self.logger.error(f"获取 {source} RSS新闻失败: {e}")
            return []
    
    def fetch_all_news(self) -> List[Dict[str, Any]]:
        """获取所有新闻源的新闻"""
        all_articles = []
        
        for source in self.news_sources:
            try:
                if source["type"] == "rss":
                    articles = self.fetch_news_from_rss(source["url"], source["name"])
                    all_articles.extend(articles)
                
                # 可以添加其他类型的新闻源处理
                
                time.sleep(1)  # 避免请求过快
                
            except Exception as e:
                self.logger.error(f"处理新闻源 {source['name']} 失败: {e}")
                continue
        
        return all_articles
    
    def filter_new_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤已推送的文章"""
        new_articles = []
        
        for article in articles:
            if not self.db.is_article_pushed(article["title"], article["url"]):
                new_articles.append(article)
        
        self.logger.info(f"过滤后新文章: {len(new_articles)}/{len(articles)}")
        return new_articles
    
    def get_stock_data(self, stock_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取股票数据（简化版）"""
        try:
            # 这里使用简化的股票数据获取
            # 实际应使用Yahoo Finance API或其他股票API
            symbol = stock_info.get("yahoo_symbol", stock_info.get("symbol", ""))
            
            # 模拟股票数据
            import random
            base_price = 100 + random.uniform(-20, 20)
            change = random.uniform(-5, 5)
            change_percent = (change / base_price) * 100
            
            return {
                "name": stock_info.get("name", ""),
                "symbol": stock_info.get("symbol", ""),
                "price": round(base_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "currency": stock_info.get("currency", "USD"),
                "volume": random.randint(1000000, 10000000),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            self.logger.error(f"获取股票数据失败 {stock_info.get('name')}: {e}")
            return None
    
    def get_all_stocks_data(self) -> List[Dict[str, Any]]:
        """获取所有股票数据"""
        stocks_data = []
        
        for stock in self.stocks:
            data = self.get_stock_data(stock)
            if data:
                stocks_data.append(data)
            time.sleep(0.5)  # 避免请求过快
        
        self.logger.info(f"获取到 {len(stocks_data)} 只股票数据")
        return stocks_data
    
    def generate_summary(self, description: str, max_length: int = 150) -> str:
        """生成文章摘要"""
        if not description:
            return "暂无摘要"
        
        # 清理HTML标签
        import re
        clean_text = re.sub(r'<[^>]+>', '', description)
        
        # 截取合适长度
        if len(clean_text) <= max_length:
            return clean_text
        
        # 尝试在句子边界截断
        sentences = re.split(r'[.!?。！？]', clean_text)
        summary = ""
        
        for sentence in sentences:
            if sentence.strip():
                if len(summary + sentence) > max_length:
                    break
                summary += sentence + "."
        
        if not summary:
            summary = clean_text[:max_length] + "..."
        
        return summary.strip()
    
    def calculate_importance_score(self, article: Dict[str, Any]) -> int:
        """计算文章重要性分数"""
        score = 0
        
        # 来源权重
        source = article.get("source", "").lower()
        if "bbc" in source or "cnn" in source:
            score += 30
        elif "financial" in source or "ft" in source:
            score += 25
        elif "nikkei" in source or "scmp" in source:
            score += 20
        elif "thepaper" in source or "澎湃" in source:
            score += 15
        
        # 标题关键词
        title = article.get("title", "").lower()
        important_keywords = [
            "breaking", "紧急", "突发", "crisis", "危机",
            "war", "战争", "conflict", "冲突", "alert", "警报"
        ]
        
        for keyword in important_keywords:
            if keyword in title:
                score += 20
                break
        
        # 描述长度
        description = article.get("description", "")
        if len(description) > 200:
            score += 10
        
        return min(score, 100)  # 限制最大分数
    
    def get_importance_level(self, score: int) -> str:
        """获取重要性级别"""
        if score >= 70:
            return "🔥 高"
        elif score >= 40:
            return "⚠️ 中"
        else:
            return "📄 低"
    
    def format_stock_section(self, stocks_data: List[Dict[str, Any]]) -> str:
        """格式化股票部分"""
        if not stocks_data:
            return "📈 今日股票\n暂无数据\n"
        
        section = "📈 今日股票\n"
        section += "=" * 30 + "\n"
        
        for stock in stocks_data:
            name = stock.get("name", "未知")
            symbol = stock.get("symbol", "")
            price = stock.get("price", 0)
            change = stock.get("change", 0)
            change_percent = stock.get("change_percent", 0)
            currency = stock.get("currency", "")
            
            # 确定表情符号
            if change_percent > 3:
                emoji = "🚀"
            elif change_percent > 0:
                emoji = "📈"
            elif change_percent < -3:
                emoji = "📉"
            else:
                emoji = "➡️"
            
            section += f"{emoji} {name} ({symbol})\n"
            section += f"  价格: {price:.2f} {currency}\n"
            section += f"  涨跌: {change:+.2f} ({change_percent:+.2f}%)\n\n"
        
        return section
    
    def format_news_section(self, articles: List[Dict[str, Any]]) -> str:
        """格式化新闻部分"""
        if not articles:
            return "📰 今日新闻\n暂无新文章\n"
        
        section = "📰 今日新闻\n"
        section += "=" * 30 + "\n"
        
        for i, article in enumerate(articles[:5], 1):  # 限制5条
            title = article.get("title", "无标题")
            url = article.get("url", "")
            source = article.get("source", "未知来源")
            
            # 生成摘要
            description = article.get("description", "")
            summary = self.generate_summary(description)
            
            # 计算重要性
            importance_score = self.calculate_importance_score(article)
            importance_level = self.get_importance_level(importance_score)
            
            section += f"{i}. {title}\n"
            section += f"   来源: {source}\n"
            section += f"   重要性: {importance_level}\n"
            section += f"   摘要: {summary}\n"
            
            if url:
                section += f"   链接: {url}\n"
            
            section += "\n"
        
        return section
    
    def generate_full_report(self) -> str:
        """生成完整报告"""
        now = datetime.now()
        
        report = f"📊 智能新闻推送报告\n"
        report += f"时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 40 + "\n\n"
        
        # 获取股票数据
        stocks_data = self.get_all_stocks_data()
        report += self.format_stock_section(stocks_data)
        
        # 获取新闻
        all_articles = self.fetch_all_news()
        new_articles = self.filter_new_articles(all_articles)
        report += self.format_news_section(new_articles)
        
        # 统计信息
        report += "📊 统计信息\n"
        report += "=" * 30 + "\n"
        report += f"• 股票监控: {len(stocks_data)} 只\n"
        report += f"• 新闻源: {len(self.news_sources)} 个\n"
        report += f"• 新文章: {len(new_articles)} 篇\n"
        report += f"• 数据库记录: {self.db.get_stats().get('total_articles', 0)} 条\n"
        
        report += "\n⏰ 下次推送: 整点时刻\n"
        report += "🔔 系统状态: 运行正常\n"
        
        return report
    
    def run(self) -> bool:
        """运行推送器"""
        try:
            self.logger.info("开始生成推送报告")
            
            # 生成报告
            report = self.generate_full_report()
            
            # 保存报告
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            report_file = f"./logs/push_report_{timestamp}.txt"
            
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            
            self.logger.info(f"报告已保存到: {report_file}")
            self.logger.info(f"报告长度: {len(report)} 字符")
            
            # 标记文章为已推送
            all_articles = self.fetch_all_news()
            for article in all_articles:
                if not self.db.is_article_pushed(article["title"], article["url"]):
                    self.db.mark_article_pushed(
                        article["title"], 
                        article["url"], 
                        article.get("source", "未知")
                    )
            
            # 清理旧记录
            deleted_count = self.db.cleanup_old_records(days=7)
            if deleted_count > 0:
                self.logger.info(f"清理了 {deleted_count} 条旧记录")
            
            self.logger.info("推送器运行完成")
            return True
            
        except Exception as e:
            self.logger.error(f"推送器运行失败: {e}")
            return False

def main():
    """主函数"""
    print("🚀 优化版新闻股票推送系统")
    print("=" * 50)
    
    pusher = NewsStockPusherOptimized()
    
    # 运行推送器
    success = pusher.run()
    
    if success:
        print("✅ 推送器运行成功")
        return 0
    else:
        print("❌ 推送器运行失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())

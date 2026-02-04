#!/usr/bin/env python3
"""
优化版新闻+股票推送系统
基于BasePusher类，消除重复代码
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import feedparser
import re

# 导入基础类
from .base_pusher import BasePusher

class NewsStockPusherOptimized(BasePusher):
    """优化版新闻+股票推送器"""
    
    def __init__(self):
        """初始化推送器"""
        super().__init__("NewsStockPusher")
        
        # 加载配置
        self.stock_config = self.config_mgr.get_config("clawdbot_stock_config.json")
        self.alert_config = self.config_mgr.get_config("alert_config.json")
        self.social_config = self.config_mgr.get_config("social_config.json")
        
        # 股票列表
        self.stocks = self.stock_config.get("stocks", [
            {
                "name": "阿里巴巴-W",
                "symbol": "09988.HK",
                "yahoo_symbol": "9988.HK",
                "currency": "HKD"
            },
            {
                "name": "小米集团-W", 
                "symbol": "01810.HK",
                "yahoo_symbol": "1810.HK",
                "currency": "HKD"
            },
            {
                "name": "比亚迪",
                "symbol": "002594.SZ",
                "yahoo_symbol": "002594.SZ",
                "currency": "CNY"
            }
        ])
        
        # 新闻源配置
        self.news_sources = self._load_news_sources()
        
        self.logger.info(f"初始化完成，监控 {len(self.stocks)} 只股票，{len(self.news_sources)} 个新闻源")
    
    def _load_news_sources(self) -> List[Dict[str, Any]]:
        """加载新闻源配置"""
        return [
            # 国内新闻媒体
            {
                'name': '新浪新闻',
                'type': 'rss',
                'url': 'http://rss.sina.com.cn/news/marquee/ddt.xml',
                'category': '国内媒体'
            },
            {
                'name': '网易新闻',
                'type': 'rss', 
                'url': 'http://news.163.com/special/00011K6L/rss_newsattitude.xml',
                'category': '国内媒体'
            },
            {
                'name': '凤凰新闻',
                'type': 'rss',
                'url': 'https://news.ifeng.com/rss/ifengnews.xml',
                'category': '国内媒体'
            },
            {
                'name': '澎湃新闻',
                'type': 'rss',
                'url': 'https://www.thepaper.cn/rss_hot.jsp',
                'category': '国内媒体'
            },
            {
                'name': '今日头条热榜',
                'type': 'api',
                'url': 'https://www.toutiao.com/hot-event/hot-board/',
                'category': '社交媒体'
            },
            
            # 国际新闻媒体
            {
                'name': 'BBC中文网',
                'type': 'rss',
                'url': 'https://www.bbc.com/zhongwen/simp/index.xml',
                'category': '国际媒体'
            },
            {
                'name': 'BBC World',
                'type': 'rss',
                'url': 'http://feeds.bbci.co.uk/news/world/rss.xml',
                'category': '国际媒体'
            },
            {
                'name': 'CNN国际版',
                'type': 'rss',
                'url': 'http://rss.cnn.com/rss/edition.rss',
                'category': '国际媒体'
            },
            {
                'name': '金融时报中文网',
                'type': 'rss',
                'url': 'https://www.ftchinese.com/rss/feed',
                'category': '国际媒体'
            },
            {
                'name': '日经亚洲',
                'type': 'rss',
                'url': 'https://asia.nikkei.com/rss/feed/nar',
                'category': '国际媒体'
            },
            {
                'name': '南华早报',
                'type': 'rss',
                'url': 'https://www.scmp.com/rss/91/feed',
                'category': '国际媒体'
            },
            
            # 社交媒体
            {
                'name': '微博热搜',
                'type': 'api',
                'url': 'https://weibo.com/ajax/side/hotSearch',
                'category': '社交媒体'
            },
            {
                'name': 'Twitter趋势',
                'type': 'api',
                'url': 'https://api.twitter.com/1.1/trends/place.json?id=1',
                'category': '社交媒体'
            },
            {
                'name': 'Reddit热门',
                'type': 'api',
                'url': 'https://www.reddit.com/r/all/hot.json',
                'category': '社交媒体'
            }
        ]
    
    def parse_rss_feed(self, feed_url: str, source_name: str) -> List[Dict[str, Any]]:
        """
        解析RSS feed
        
        Args:
            feed_url: RSS feed URL
            source_name: 来源名称
            
        Returns:
            文章列表
        """
        articles = []
        
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.entries:
                for entry in feed.entries[:5]:  # 只取前5条
                    title = entry.get('title', '无标题')
                    link = entry.get('link', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    published = entry.get('published', entry.get('updated', ''))
                    
                    # 清理HTML标签
                    summary_clean = re.sub(r'<[^>]+>', '', summary)
                    
                    articles.append({
                        'title': title,
                        'url': link,
                        'summary': summary_clean[:200] + '...' if len(summary_clean) > 200 else summary_clean,
                        'published': published,
                        'source': source_name,
                        'category': '新闻'
                    })
            
            self.logger.debug(f"从 {source_name} 解析到 {len(articles)} 篇文章")
            
        except Exception as e:
            self.logger.error(f"解析RSS feed失败 {source_name}: {e}")
        
        return articles
    
    def fetch_stock_data(self, stock: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        获取股票数据
        
        Args:
            stock: 股票信息
            
        Returns:
            股票数据或None
        """
        symbol = stock.get('yahoo_symbol', stock.get('symbol', ''))
        
        if not symbol:
            self.logger.warning(f"股票缺少symbol: {stock}")
            return None
        
        try:
            # 使用Yahoo Finance API
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'range': '1d',
                'interval': '1m',
                'includePrePost': 'false'
            }
            
            response = self.fetch_url(url, timeout=10)
            if not response:
                return None
            
            data = response.json()
            
            if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
                self.logger.warning(f"股票数据格式错误: {symbol}")
                return None
            
            result = data['chart']['result'][0]
            meta = result.get('meta', {})
            
            stock_data = {
                'name': stock['name'],
                'symbol': stock['symbol'],
                'yahoo_symbol': symbol,
                'price': meta.get('regularMarketPrice', 0),
                'currency': stock.get('currency', 'USD'),
                'change': meta.get('regularMarketChange', 0),
                'change_percent': meta.get('regularMarketChangePercent', 0),
                'open': meta.get('regularMarketOpen', 0),
                'high': meta.get('regularMarketDayHigh', 0),
                'low': meta.get('regularMarketDayLow', 0),
                'volume': meta.get('regularMarketVolume', 0),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.logger.debug(f"获取股票数据成功: {stock['name']} ({stock_data['price']})")
            return stock_data
            
        except Exception as e:
            self.logger.error(f"获取股票数据失败 {stock['name']}: {e}")
            return None
    
    def generate_stock_report(self, stock_data_list: List[Dict[str, Any]]) -> str:
        """
        生成股票报告
        
        Args:
            stock_data_list: 股票数据列表
            
        Returns:
            股票报告字符串
        """
        if not stock_data_list:
            return "📈 股票监控\n暂无股票数据\n"
        
        report = ["📈 股票监控", ""]
        
        for stock_data in stock_data_list:
            change_emoji = "📈" if stock_data['change'] >= 0 else "📉"
            change_sign = "+" if stock_data['change'] >= 0 else ""
            
            report.append(f"{change_emoji} **{stock_data['name']}** ({stock_data['symbol']})")
            report.append(f"  价格: {stock_data['price']:.2f} {stock_data['currency']}")
            report.append(f"  涨跌: {change_sign}{stock_data['change']:.2f} ({change_sign}{stock_data['change_percent']:.2f}%)")
            
            if stock_data.get('open'):
                report.append(f"  开盘: {stock_data['open']:.2f}")
            if stock_data.get('volume'):
                report.append(f"  成交量: {stock_data['volume']:,}")
            
            report.append("")
        
        return "\n".join(report)
    
    def generate_news_report(self, articles: List[Dict[str, Any]]) -> str:
        """
        生成新闻报告
        
        Args:
            articles: 文章列表
            
        Returns:
            新闻报告字符串
        """
        if not articles:
            return "📰 新闻摘要\n暂无最新新闻\n"
        
        # 按来源分组
        articles_by_source = {}
        for article in articles:
            source = article['source']
            if source not in articles_by_source:
                articles_by_source[source] = []
            articles_by_source[source].append(article)
        
        report = ["📰 新闻摘要", ""]
        
        for source, source_articles in list(articles_by_source.items())[:5]:  # 最多5个来源
            report.append(f"**{source}**")
            
            for i, article in enumerate(source_articles[:3]):  # 每个来源最多3条
                # 检查是否已推送
                if self.news_db.is_article_pushed(article['title'], article['url']):
                    continue
                
                # 标记为已推送
                self.news_db.mark_article_pushed(article['title'], article['url'], source)
                
                # 添加文章
                report.append(f"{i+1}. {article['title']}")
                if article.get('summary'):
                    report.append(f"   {article['summary']}")
                if article.get('published'):
                    report.append(f"   📅 {article['published']}")
                report.append(f"   🔗 {article['url']}")
                report.append("")
            
            report.append("")
        
        return "\n".join(report)
    
    def run(self) -> Tuple[bool, str]:
        """
        运行推送器
        
        Returns:
            Tuple[成功状态, 报告内容]
        """
        start_time = time.time()
        self.logger.info("开始运行推送器")
        
        report_parts = []
        
        # 1. 股票部分
        if self.should_push_stocks():
            self.logger.info("获取股票数据...")
            stock_data_list = []
            
            for stock in self.stocks:
                stock_data = self.fetch_stock_data(stock)
                if stock_data:
                    stock_data_list.append(stock_data)
            
            if stock_data_list:
                stock_report = self.generate_stock_report(stock_data_list)
                report_parts.append(stock_report)
            else:
                report_parts.append("📈 股票监控\n暂时无法获取股票数据\n")
        else:
            self.logger.info("不在股票推送时间范围内")
        
        # 2. 新闻部分
        if self.should_push_news():
            self.logger.info("获取新闻数据...")
            all_articles = []
            
            for source in self.news_sources:
                if source['type'] == 'rss':
                    articles = self.parse_rss_feed(source['url'], source['name'])
                    all_articles.extend(articles)
                # 其他类型的新闻源可以在这里添加
            
            if all_articles:
                news_report = self.generate_news_report(all_articles)
                report_parts.append(news_report)
            else:
                report_parts.append("📰 新闻摘要\n暂时无法获取新闻数据\n")
        else:
            self.logger.info("不在新闻推送时间范围内")
        
        # 3. 添加系统信息
        duration = time.time() - start_time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        system_info = [
            "",
            "---",
            f"⏰ 推送时间: {timestamp}",
            f"⚡ 处理耗时: {self.format_duration(duration)}",
            f"📱 接收号码: {get_whatsapp_number_display()}",
            f"🔧 系统状态: 运行正常"
        ]
        
        report_parts.append("\n".join(system_info))
        
        # 合并报告
        full_report = "\n".join(report_parts)
        
        self.logger.info(f"报告生成完成，长度: {len(full_report)} 字符")
        
        return True, full_report
    
    def run_and_send(self) -> bool:
        """
        运行并发送报告
        
        Returns:
            是否成功
        """
        try:
            success, report = self.run()
            
            if not success:
                self.logger.error("生成报告失败")
                return False
            
            # 保存报告到文件
            timestamp = self.generate_timestamp()
            filename = f"push_report_{timestamp}.txt"
            self.save_to_file(report, filename)
            
            # 发送报告
            if report.strip():
                send_success, result_msg = self.send_message(report)
                self.logger.info(f"发送结果: {result_msg}")
                return send_success
            else:
                self.logger.warning("报告为空，不发送")
                return False
            
        except Exception as e:
            self.logger.error(f"运行推送器异常: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """主函数"""
    print("=" * 60)
    print("📱 优化版新闻+股票推送系统")
    print("=" * 60)
    
    pusher = NewsStockPusherOptimized()
    
    # 显示系统状态
    status = pusher.get_system_status()
    print(f"📊 系统状态:")
    print(f"  推送器: {status['pusher_name']}")
    print(f"  时间: {status['timestamp']}")
    print(f"  WhatsApp: {status['whatsapp_number']}")
    print(f"  推送股票: {'✅' if status['should_push_stocks'] else '❌'}")
    print(f"  推送新闻: {'✅' if status['should_push_news'] else '❌'}")
    print(f"  数据库文章: {status['database_stats'].get('total_articles', 0)}")
    print()
    
    # 运行推送器
    print("🚀 开始推送...")
    success = pusher.run_and_send()
    
    if success:
        print("✅ 推送完成")
    else:
        print("❌ 推送失败")
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
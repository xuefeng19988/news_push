#!/usr/bin/env python3
"""
新闻推送系统 - 每小时推送20-30条重要文章
避免重复，显示内容摘要
"""

import requests
from utils.database import NewsDatabase
import json
import time
import hashlib
from datetime import datetime, timedelta
import sqlite3
import os
from typing import List, Dict, Set
import re

class NewsPusher:
    """新闻推送器"""
    
    def __init__(self, db_path: str = "/home/admin/clawd/news_cache.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建已推送文章表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pushed_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_hash TEXT UNIQUE,
                title TEXT,
                source TEXT,
                url TEXT,
                pushed_at TIMESTAMP,
                category TEXT
            )
        ''')
        
        # 创建文章内容表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS article_contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_hash TEXT,
                content TEXT,
                summary TEXT,
                keywords TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_article_hash(self, title: str, url: str) -> str:
        """生成文章唯一哈希"""
        content = f"{title}|{url}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def is_article_pushed(self, article_hash: str) -> bool:
        """检查文章是否已推送"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM pushed_articles WHERE article_hash = ?",
            (article_hash,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def mark_article_pushed(self, article: Dict):
        """标记文章为已推送"""
        article_hash = self.get_article_hash(article['title'], article['url'])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO pushed_articles 
                (article_hash, title, source, url, pushed_at, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                article_hash,
                article['title'],
                article.get('source', '未知'),
                article['url'],
                datetime.now().isoformat(),
                article.get('category', '综合')
            ))
            
            conn.commit()
        except sqlite3.IntegrityError:
            # 文章已存在，忽略
            pass
        finally:
            conn.close()
    
    def fetch_news_from_rss(self, rss_url: str, source: str) -> List[Dict]:
        """从RSS源获取新闻"""
        articles = []
        try:
            response = self.session.get(rss_url, timeout=10)
            if response.status_code == 200:
                # 简单解析RSS（实际应该用xml解析库）
                content = response.text
                
                # 简单提取文章（实际项目应该用feedparser等库）
                # 这里使用简化版本
                import re
                
                # 查找item标签
                items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
                
                for item in items[:15]:  # 每个源取15条
                    # 提取标题
                    title_match = re.search(r'<title>(.*?)</title>', item)
                    title = title_match.group(1) if title_match else "无标题"
                    
                    # 提取链接
                    link_match = re.search(r'<link>(.*?)</link>', item)
                    url = link_match.group(1) if link_match else ""
                    
                    # 提取描述
                    desc_match = re.search(r'<description>(.*?)</description>', item)
                    description = desc_match.group(1) if desc_match else ""
                    
                    # 提取发布时间
                    pub_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                    pub_date = pub_match.group(1) if pub_match else ""
                    
                    if title and url:
                        articles.append({
                            'title': title.strip(),
                            'url': url.strip(),
                            'description': description.strip(),
                            'pub_date': pub_date.strip(),
                            'source': source,
                            'category': '综合'
                        })
            
            return articles
            
        except Exception as e:
            print(f"❌ 获取RSS新闻失败 ({source}): {e}")
            return []
    
    def fetch_news_from_api(self, api_url: str, source: str) -> List[Dict]:
        """从API获取新闻"""
        try:
            response = self.session.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                # 根据不同的API格式解析
                if isinstance(data, list):
                    for item in data[:15]:
                        articles.append({
                            'title': item.get('title', '无标题'),
                            'url': item.get('url', ''),
                            'description': item.get('description', ''),
                            'pub_date': item.get('pubDate', ''),
                            'source': source,
                            'category': item.get('category', '综合')
                        })
                
                return articles
                
        except Exception as e:
            print(f"❌ 获取API新闻失败 ({source}): {e}")
            return []
    
    def get_news_sources(self) -> List[Dict]:
        """获取新闻源配置"""
        return [
            {
                'name': '新浪新闻',
                'type': 'rss',
                'url': 'http://rss.sina.com.cn/news/marquee/ddt.xml',
                'category': '综合'
            },
            {
                'name': '网易新闻',
                'type': 'rss', 
                'url': 'http://news.163.com/special/00011K6L/rss_newsattitude.xml',
                'category': '综合'
            },
            {
                'name': '腾讯新闻',
                'type': 'rss',
                'url': 'http://news.qq.com/newsgn/rss_newsgn.xml',
                'category': '国内'
            },
            {
                'name': '凤凰新闻',
                'type': 'rss',
                'url': 'https://news.ifeng.com/rss/ifengnews.xml',
                'category': '综合'
            },
            {
                'name': '今日头条热榜',
                'type': 'api',
                'url': 'https://www.toutiao.com/hot-event/hot-board/',
                'category': '热点'
            }
        ]
    
    def fetch_all_news(self) -> List[Dict]:
        """获取所有新闻"""
        print("📡 开始获取新闻...")
        
        all_articles = []
        sources = self.get_news_sources()
        
        for source in sources:
            print(f"  从 {source['name']} 获取...")
            
            if source['type'] == 'rss':
                articles = self.fetch_news_from_rss(source['url'], source['name'])
            else:
                articles = self.fetch_news_from_api(source['url'], source['name'])
            
            # 添加分类信息
            for article in articles:
                article['category'] = source['category']
            
            all_articles.extend(articles)
            time.sleep(1)  # 避免请求过快
        
        print(f"✅ 共获取 {len(all_articles)} 条新闻")
        return all_articles
    
    def filter_new_articles(self, articles: List[Dict]) -> List[Dict]:
        """过滤出新文章（未推送过的）"""
        new_articles = []
        
        for article in articles:
            article_hash = self.get_article_hash(article['title'], article['url'])
            
            if not self.is_article_pushed(article_hash):
                new_articles.append(article)
        
        print(f"📊 过滤后新文章: {len(new_articles)}/{len(articles)} 条")
        return new_articles
    
    def generate_summary(self, description: str, max_length: int = 100) -> str:
        """生成文章摘要"""
        if not description:
            return "无内容摘要"
        
        # 清理HTML标签
        clean_text = re.sub(r'<[^>]+>', '', description)
        
        # 截取指定长度
        if len(clean_text) > max_length:
            return clean_text[:max_length] + "..."
        
        return clean_text
    
    def categorize_articles(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """按分类分组文章"""
        categories = {}
        
        for article in articles:
            category = article.get('category', '其他')
            if category not in categories:
                categories[category] = []
            categories[category].append(article)
        
        return categories
    
    def select_top_articles(self, articles: List[Dict], count: int = 25) -> List[Dict]:
        """选择最重要的文章"""
        # 简单策略：按来源权重和标题关键词排序
        source_weights = {
            '今日头条热榜': 3,
            '新浪新闻': 2,
            '腾讯新闻': 2,
            '网易新闻': 2,
            '凤凰新闻': 1
        }
        
        # 计算文章权重
        weighted_articles = []
        for article in articles:
            weight = source_weights.get(article['source'], 1)
            
            # 关键词加分
            title = article['title'].lower()
            keywords = ['重磅', '突发', '最新', '重要', '紧急', '独家']
            for keyword in keywords:
                if keyword in title:
                    weight += 1
            
            weighted_articles.append((weight, article))
        
        # 按权重排序
        weighted_articles.sort(key=lambda x: x[0], reverse=True)
        
        # 返回前N条
        return [article for _, article in weighted_articles[:count]]
    
    def format_article_message(self, article: Dict) -> str:
        """格式化单篇文章消息"""
        title = article['title']
        source = article['source']
        url = article['url']
        summary = self.generate_summary(article.get('description', ''))
        
        message = f"📰 **{title}**\n"
        message += f"📊 来源: {source}\n"
        
        if summary:
            message += f"📝 摘要: {summary}\n"
        
        if url:
            # 缩短URL显示
            if len(url) > 50:
                url_display = url[:47] + "..."
            else:
                url_display = url
            message += f"🔗 链接: {url_display}\n"
        
        return message
    
    def format_news_report(self, articles: List[Dict]) -> str:
        """格式化新闻报告"""
        timestamp = datetime.now().strftime('%H:%M')
        
        report = f"📰 **新闻推送报告** ({timestamp})\n\n"
        report += f"📊 本次推送: {len(articles)} 条重要新闻\n\n"
        
        # 按分类分组
        categories = self.categorize_articles(articles)
        
        for category, cat_articles in categories.items():
            report += f"## 📋 {category} ({len(cat_articles)}条)\n\n"
            
            for i, article in enumerate(cat_articles[:8], 1):  # 每类最多8条
                report += f"{i}. {self.format_article_message(article)}\n"
            
            report += "\n"
        
        # 添加统计信息
        sources = {}
        for article in articles:
            source = article['source']
            sources[source] = sources.get(source, 0) + 1
        
        report += "---\n"
        report += "📈 **来源统计**:\n"
        for source, count in sources.items():
            report += f"- {source}: {count}条\n"
        
        report += f"\n⏰ 下次推送: {(datetime.now() + timedelta(hours=1)).strftime('%H:%M')}\n"
        report += "🔄 推送频率: 每小时一次\n"
        report += "📱 避免重复: 已过滤已推送内容\n"
        
        return report
    
    def save_news_report(self, report: str):
        """保存新闻报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        report_file = f"./logs/news_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"💾 新闻报告已保存: {report_file}")
        return report_file
    
    def run(self) -> str:
        """运行新闻推送"""
        print(f"\n{'='*60}")
        print(f"🚀 新闻推送系统启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # 1. 获取所有新闻
        all_articles = self.fetch_all_news()
        
        if not all_articles:
            return "❌ 无法获取新闻数据"
        
        # 2. 过滤新文章
        new_articles = self.filter_new_articles(all_articles)
        
        if not new_articles:
            return "📭 没有新的重要新闻需要推送"
        
        # 3. 选择最重要的25条
        selected_articles = self.select_top_articles(new_articles, 25)
        
        # 4. 标记为已推送
        for article in selected_articles:
            self.mark_article_pushed(article)
        
        # 5. 生成报告
        report = self.format_news_report(selected_articles)
        
        # 6. 保存报告
        report_file = self.save_news_report(report)
        
        print(f"\n✅ 新闻推送完成!")
        print(f"   推送文章: {len(selected_articles)} 条")
        print(f"   报告文件: {report_file}")
        
        # 显示摘要
        categories = self.categorize_articles(selected_articles)
        print(f"\n📋 分类统计:")
        for category, articles in categories.items():
            print(f"  {category}: {len(articles)} 条")
        
        print(f"{'='*60}")
        
        return report

def send_whatsapp_news(news_report: str):
    """发送新闻到WhatsApp"""
    try:
        # 保存到待发送文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pending_file = f"./logs/pending_news_{timestamp}.txt"
        
        with open(pending_file, 'w', encoding='utf-8') as f:
            f.write(news_report)
        
        print(f"📤 新闻已保存到待发送队列: {pending_file}")
        
        # 显示预览
        preview = news_report[:300] + "..." if len(news_report) > 300 else news_report
        print(f"\n📄 新闻预览:")
        print("-"*40)
        print(preview)
        print("-"*40)
        
        return True
        
    except Exception as e:
        print(f"❌ 保存新闻失败: {e}")
        return False

def main():
    """主函数"""
    # 创建新闻推送器
    pusher = NewsPusher()
    
    # 运行新闻推送
    news_report = pusher.run()
    
    if news_report.startswith("❌") or news_report.startswith("📭"):
        print(f"\n{news_report}")
        return False
    
    # 发送到WhatsApp
    print("\n📤 准备发送新闻到WhatsApp...")
    if send_whatsapp_news(news_report):
        print("✅ 新闻推送准备完成")
        return True
    else:
        print("❌ 新闻推送失败")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
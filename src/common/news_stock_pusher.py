#!/usr/bin/env python3
"""
新闻+股票推送系统 - 集成版本
每小时推送新闻和股票信息到WhatsApp
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
import sqlite3
import hashlib
import re

class NewsStockPusher:
    """新闻+股票推送器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        # 数据库路径
        self.db_path = "/home/admin/clawd/news_cache.db"
        self.init_database()
        
        # 监控的股票
        self.stocks = [
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
        ]
        
        # 新闻源 - 国内+国际+社交媒体
        self.news_sources = [
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
                'url': 'http://rss.cnn.com/rss/edition_world.rss',
                'category': '国际媒体'
            },
            {
                'name': '金融时报中文',
                'type': 'rss',
                'url': 'https://www.ftchinese.com/rss/news',
                'category': '国际财经'
            },
            {
                'name': '日经亚洲',
                'type': 'rss',
                'url': 'https://asia.nikkei.com/rss',
                'category': '亚洲媒体'
            },
            {
                'name': '南华早报',
                'type': 'rss',
                'url': 'https://www.scmp.com/rss/91/feed',
                'category': '亚洲媒体'
            },
            
            # 社交媒体平台（需要API或特殊处理）
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
                pushed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                category TEXT
            )
        ''')
        
        # 创建索引以提高查询性能
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_article_hash ON pushed_articles(article_hash)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pushed_at ON pushed_articles(pushed_at)
        ''')
        
        # 自动清理7天前的旧记录
        seven_days_ago = datetime.now() - timedelta(days=7)
        cursor.execute(
            "DELETE FROM pushed_articles WHERE pushed_at < ?",
            (seven_days_ago.strftime('%Y-%m-%d %H:%M:%S'),)
        )
        
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            print(f"🗑️  自动清理了 {deleted_count} 条7天前的旧记录")
        
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
    
    def mark_article_pushed(self, article: dict):
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
    
    def cleanup_old_records(self, days_to_keep: int = 7):
        """清理指定天数前的旧记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cursor.execute(
            "DELETE FROM pushed_articles WHERE pushed_at < ?",
            (cutoff_date.strftime('%Y-%m-%d %H:%M:%S'),)
        )
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            print(f"🗑️  清理了 {deleted_count} 条{days_to_keep}天前的旧记录")
        
        return deleted_count
    
    def fetch_news_from_rss(self, rss_url: str, source: str) -> list:
        """从RSS源获取新闻（支持多种RSS格式）"""
        articles = []
        try:
            response = self.session.get(rss_url, timeout=15)
            if response.status_code == 200:
                content = response.text
                
                # 尝试多种RSS格式解析
                import re
                
                # 方法1: 标准RSS格式 <item>...</item>
                items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
                
                # 方法2: Atom格式 <entry>...</entry>
                if not items:
                    items = re.findall(r'<entry>(.*?)</entry>', content, re.DOTALL)
                
                # 方法3: 其他常见格式
                if not items:
                    # 尝试查找所有可能的条目
                    items = re.findall(r'<(?:item|entry)>(.*?)</(?:item|entry)>', content, re.DOTALL)
                
                for item in items[:8]:  # 每个源取8条
                    # 提取标题（尝试多种标签）
                    title = None
                    for tag in ['title', 'dc:title']:
                        match = re.search(f'<{tag}>(.*?)</{tag}>', item, re.DOTALL)
                        if match:
                            title = match.group(1).strip()
                            break
                    
                    if not title:
                        continue
                    
                    # 提取链接（尝试多种标签和属性）
                    url = None
                    
                    # 尝试 <link>标签
                    link_match = re.search(r'<link>(.*?)</link>', item)
                    if link_match:
                        url = link_match.group(1).strip()
                    else:
                        # 尝试 <link href="...">
                        link_match = re.search(r'<link[^>]*href=["\']([^"\']+)["\'][^>]*>', item)
                        if link_match:
                            url = link_match.group(1).strip()
                        else:
                            # 尝试 <guid>
                            guid_match = re.search(r'<guid[^>]*>(.*?)</guid>', item)
                            if guid_match and guid_match.group(1).startswith('http'):
                                url = guid_match.group(1).strip()
                    
                    if not url:
                        continue
                    
                    # 提取描述/内容（尝试多种标签）
                    description = ""
                    for tag in ['description', 'content:encoded', 'content', 'summary', 'dc:description']:
                        match = re.search(f'<{tag}>(.*?)</{tag}>', item, re.DOTALL)
                        if match:
                            description = match.group(1).strip()
                            break
                    
                    # 提取发布时间
                    pub_date = ""
                    for tag in ['pubDate', 'dc:date', 'published', 'updated']:
                        match = re.search(f'<{tag}>(.*?)</{tag}>', item)
                        if match:
                            pub_date = match.group(1).strip()
                            break
                    
                    # 清理标题中的CDATA和HTML标签
                    title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title)
                    title = re.sub(r'<[^>]+>', '', title)
                    
                    # 清理描述中的HTML标签
                    if description:
                        description = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', description)
                        description = re.sub(r'<[^>]+>', '', description)
                        description = re.sub(r'\s+', ' ', description).strip()
                    
                    articles.append({
                        'title': title[:200],  # 限制标题长度
                        'url': url,
                        'description': description[:300] if description else "",  # 限制描述长度
                        'pub_date': pub_date,
                        'source': source,
                        'category': '综合'  # 将在外部设置
                    })
            
            return articles
            
        except Exception as e:
            print(f"❌ 获取RSS新闻失败 ({source}): {e}")
            return []
    
    def fetch_news_from_api(self, api_url: str, source: str) -> list:
        """从API获取新闻和社交媒体内容"""
        articles = []
        try:
            headers = self.session.headers.copy()
            
            # 为不同平台设置特定的请求头
            if 'weibo' in api_url:
                headers.update({
                    'Referer': 'https://weibo.com/',
                    'Accept': 'application/json, text/plain, */*'
                })
            elif 'twitter' in api_url:
                # Twitter API需要认证，这里使用简化版本
                print(f"  ⚠️ Twitter API需要认证，跳过")
                return []
            elif 'reddit' in api_url:
                headers.update({
                    'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'
                })
            
            response = self.session.get(api_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # 根据不同的API格式解析
                if 'weibo' in api_url:
                    # 微博热搜榜格式
                    if 'data' in data and 'realtime' in data['data']:
                        for item in data['data']['realtime'][:10]:
                            word = item.get('word', '')
                            if word:
                                articles.append({
                                    'title': f"#{word}",
                                    'url': f"https://s.weibo.com/weibo?q={word}",
                                    'description': item.get('word_scheme', ''),
                                    'source': source,
                                    'category': '社交媒体'
                                })
                
                elif 'reddit' in api_url:
                    # Reddit热门帖子格式
                    if 'data' in data and 'children' in data['data']:
                        for child in data['data']['children'][:10]:
                            post = child.get('data', {})
                            title = post.get('title', '')
                            url = post.get('url', '')
                            
                            if title and url:
                                articles.append({
                                    'title': title[:150],
                                    'url': f"https://reddit.com{post.get('permalink', '')}",
                                    'description': f"👍 {post.get('ups', 0)} | 💬 {post.get('num_comments', 0)}",
                                    'source': source,
                                    'category': '社交媒体'
                                })
                
                elif 'toutiao' in api_url or '今日头条' in source:
                    # 今日头条热榜格式
                    if 'data' in data:
                        for item in data['data'][:10]:
                            title = item.get('Title', '')
                            url = item.get('Url', '')
                            
                            if title and url:
                                articles.append({
                                    'title': title.strip(),
                                    'url': url.strip(),
                                    'description': item.get('Description', ''),
                                    'source': source,
                                    'category': '社交媒体'
                                })
                
                return articles
            else:
                print(f"  ⚠️ API返回错误: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 获取API内容失败 ({source}): {e}")
            return []
    
    def fetch_all_news(self) -> list:
        """获取所有新闻"""
        print("📡 开始获取新闻...")
        
        all_articles = []
        total_sources = len(self.news_sources)
        
        for i, source in enumerate(self.news_sources, 1):
            print(f"  [{i}/{total_sources}] 从 {source['name']} 获取...")
            
            articles = []
            if source['type'] == 'rss':
                articles = self.fetch_news_from_rss(source['url'], source['name'])
            elif source['type'] == 'api':
                articles = self.fetch_news_from_api(source['url'], source['name'])
            
            # 添加分类信息
            for article in articles:
                article['category'] = source['category']
            
            all_articles.extend(articles)
            
            # 避免请求过快，但不同源之间等待时间不同
            if i < total_sources:
                time.sleep(0.3)  # 减少等待时间
        
        print(f"✅ 共获取 {len(all_articles)} 条新闻")
        
        # 按来源分类统计
        source_stats = {}
        for article in all_articles:
            source = article['source']
            source_stats[source] = source_stats.get(source, 0) + 1
        
        print("📊 新闻来源统计:")
        for source, count in source_stats.items():
            print(f"  {source}: {count}条")
        
        return all_articles
    
    def filter_new_articles(self, articles: list) -> list:
        """过滤出新文章（未推送过的）"""
        new_articles = []
        
        for article in articles:
            article_hash = self.get_article_hash(article['title'], article['url'])
            
            if not self.is_article_pushed(article_hash):
                new_articles.append(article)
        
        print(f"📊 过滤后新文章: {len(new_articles)}/{len(articles)} 条")
        return new_articles
    
    def get_stock_from_yahoo(self, stock_info: dict):
        """从Yahoo Finance获取股票数据"""
        try:
            symbol = stock_info["yahoo_symbol"]
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            
            params = {
                "interval": "1d",
                "range": "1d",
                "includePrePost": "false"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                chart_data = data.get("chart", {}).get("result", [{}])[0]
                meta = chart_data.get("meta", {})
                quotes = chart_data.get("indicators", {}).get("quote", [{}])[0]
                
                if meta and quotes:
                    closes = quotes.get("close", [])
                    if closes:
                        latest_price = closes[-1]
                        prev_price = closes[-2] if len(closes) > 1 else latest_price
                        
                        change = latest_price - prev_price
                        change_percent = (change / prev_price) * 100 if prev_price else 0
                        
                        return {
                            "symbol": stock_info["symbol"],
                            "name": stock_info["name"],
                            "price": latest_price,
                            "change": change,
                            "change_percent": change_percent,
                            "currency": stock_info["currency"],
                            "timestamp": datetime.now().isoformat()
                        }
            
            return None
                
        except Exception as e:
            print(f"❌ Yahoo API错误 ({stock_info['symbol']}): {e}")
            return None
    
    def get_all_stocks_data(self):
        """获取所有股票数据"""
        print("📈 开始获取股票数据...")
        
        all_data = []
        
        for stock in self.stocks:
            print(f"  获取 {stock['name']} ({stock['symbol']})...")
            data = self.get_stock_from_yahoo(stock)
            
            if data:
                all_data.append(data)
                print(f"    ✅ 成功: {data['price']} {data['currency']}")
            else:
                print(f"    ❌ 失败")
        
        return all_data
    
    def analyze_stock_sentiment(self, change_percent: float) -> str:
        """分析股票情绪"""
        if change_percent > 3:
            return "🚀 非常正面"
        elif change_percent > 1:
            return "📈 正面"
        elif change_percent > -1:
            return "➡️ 中性"
        elif change_percent > -3:
            return "📉 负面"
        else:
            return "🔻 非常负面"
    
    def generate_summary(self, description: str, max_length: int = 150) -> str:
        """生成详细文章摘要"""
        if not description or description.strip() == '':
            return "暂无详细内容摘要"
        
        # 清理HTML标签和特殊字符
        clean_text = re.sub(r'<[^>]+>', '', description)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # 移除常见的无用前缀
        prefixes = ['摘要：', '简介：', '内容：', '导读：', '【', '[']
        for prefix in prefixes:
            if clean_text.startswith(prefix):
                clean_text = clean_text[len(prefix):].strip()
        
        # 如果文本太短，直接返回
        if len(clean_text) <= 50:
            return clean_text
        
        # 尝试提取关键句子（第一句+最后一句）
        sentences = re.split(r'[。！？.!?]', clean_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) >= 2:
            # 取第一句和最后一句
            first_sentence = sentences[0]
            last_sentence = sentences[-1]
            
            # 如果第一句和最后一句相同或相似，只取第一句
            if first_sentence == last_sentence or last_sentence in first_sentence:
                summary = first_sentence
            else:
                summary = f"{first_sentence}...{last_sentence}"
        elif sentences:
            summary = sentences[0]
        else:
            summary = clean_text
        
        # 截取指定长度
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    def enhance_article_info(self, article: dict) -> dict:
        """增强文章信息（包含更新时间、重要性评级等）"""
        enhanced = article.copy()
        
        # 根据来源添加额外信息
        source = article.get('source', '')
        description = article.get('description', '')
        pub_date = article.get('pub_date', '')
        
        # 1. 提取关键信息标签
        extra_info_tags = []
        
        if '微博' in source:
            extra_info_tags.append("🔥 实时热点")
        elif 'Reddit' in source:
            extra_info_tags.append("👥 社区热议")
        elif 'BBC' in source or 'CNN' in source:
            extra_info_tags.append("🌍 国际权威")
        elif '金融时报' in source or '华尔街' in source:
            extra_info_tags.append("💼 财经深度")
        elif '澎湃' in source:
            extra_info_tags.append("📊 深度调查")
        elif '头条' in source:
            extra_info_tags.append("📱 平台热榜")
        
        # 2. 分析文章重要性
        importance_score = self.calculate_importance_score(article)
        importance_level = self.get_importance_level(importance_score)
        enhanced['importance'] = importance_level
        
        # 3. 处理更新时间
        update_time = self.parse_publication_time(pub_date)
        enhanced['update_time'] = update_time
        enhanced['time_recency'] = self.get_time_recency(update_time)
        
        # 4. 组合额外信息
        if extra_info_tags:
            enhanced['extra_info'] = " | ".join(extra_info_tags)
        
        # 5. 添加阅读时间估计
        title_len = len(article.get('title', ''))
        desc_len = len(description)
        total_chars = title_len + desc_len
        read_time = max(1, total_chars // 500)  # 按500字/分钟计算
        enhanced['read_time'] = f"⏱️ 阅读约{read_time}分钟"
        
        return enhanced
    
    def calculate_importance_score(self, article: dict) -> int:
        """计算文章重要性分数（0-100）"""
        score = 50  # 基础分
        
        # 来源权重
        source_weights = {
            'BBC中文网': 20, 'BBC World': 20, 'CNN国际版': 20,
            '金融时报中文': 18, '华尔街日报中文': 18,
            '澎湃新闻': 15, '新浪新闻': 12, '网易新闻': 12, '凤凰新闻': 12,
            '日经亚洲': 15, '南华早报': 15,
            '今日头条热榜': 10, '微博热搜': 8, 'Twitter趋势': 8, 'Reddit热门': 8
        }
        
        source = article.get('source', '')
        if source in source_weights:
            score += source_weights[source]
        
        # 标题关键词加分
        title = article.get('title', '').lower()
        important_keywords = [
            '突发', '紧急', '重磅', '独家', '最新', '重大', '突破', '首次',
            '危机', '战争', '地震', '疫情', '经济', '金融', '股市', '政策',
            '习近平', '拜登', '特朗普', '普京'
        ]
        
        for keyword in important_keywords:
            if keyword in title:
                score += 5
        
        # 描述长度加分（内容越详细可能越重要）
        description = article.get('description', '')
        if len(description) > 200:
            score += 10
        elif len(description) > 100:
            score += 5
        
        return min(100, max(0, score))  # 限制在0-100之间
    
    def get_importance_level(self, score: int) -> str:
        """根据分数获取重要性等级"""
        if score >= 80:
            return "🔴 非常重要"
        elif score >= 65:
            return "🟠 重要"
        elif score >= 50:
            return "🟡 中等"
        elif score >= 35:
            return "🟢 一般"
        else:
            return "⚪ 资讯"
    
    def parse_publication_time(self, pub_date: str) -> str:
        """解析发布时间"""
        if not pub_date:
            return "时间未知"
        
        # 尝试解析常见的时间格式
        import re
        from datetime import datetime
        
        try:
            # 移除时区信息
            clean_date = re.sub(r'[+-]\d{2}:?\d{2}$', '', pub_date).strip()
            
            # 尝试多种格式
            formats = [
                '%a, %d %b %Y %H:%M:%S',  # RFC 822格式
                '%Y-%m-%dT%H:%M:%S',      # ISO格式
                '%Y-%m-%d %H:%M:%S',      # 标准格式
                '%d %b %Y %H:%M:%S',      # 简写月份格式
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(clean_date, fmt)
                    return dt.strftime('%m-%d %H:%M')
                except ValueError:
                    continue
            
            # 如果都无法解析，返回原始字符串（截断）
            return pub_date[:16]
            
        except Exception:
            return "时间解析错误"
    
    def get_time_recency(self, time_str: str) -> str:
        """获取时间新鲜度"""
        if "时间未知" in time_str or "解析错误" in time_str:
            return "🕒 时间未知"
        
        try:
            from datetime import datetime
            
            # 尝试解析时间
            now = datetime.now()
            time_format = '%m-%d %H:%M'
            
            try:
                article_time = datetime.strptime(time_str, time_format)
                # 设置年份为当前年份
                article_time = article_time.replace(year=now.year)
                
                # 计算时间差
                time_diff = now - article_time
                hours_diff = time_diff.total_seconds() / 3600
                
                if hours_diff < 1:
                    return "🆕 刚刚更新"
                elif hours_diff < 3:
                    return "🆕 3小时内"
                elif hours_diff < 12:
                    return "🕒 半天内"
                elif hours_diff < 24:
                    return "🕒 今天"
                elif hours_diff < 48:
                    return "🕒 昨天"
                else:
                    days = int(hours_diff / 24)
                    return f"🕒 {days}天前"
                    
            except ValueError:
                return "🕒 " + time_str
                
        except Exception:
            return "🕒 " + time_str
    
    def format_stock_section(self, stocks_data: list) -> str:
        """格式化股票部分"""
        if not stocks_data:
            return "📭 暂时无法获取股票数据\n"
        
        section = "📈 **股票监控**\n\n"
        
        for stock in stocks_data:
            sentiment = self.analyze_stock_sentiment(stock['change_percent'])
            
            section += f"• **{stock['name']}** ({stock['symbol']})\n"
            section += f"  价格: {stock['price']:.2f} {stock['currency']}\n"
            section += f"  涨跌: {stock['change']:+.2f} ({stock['change_percent']:+.2f}%)\n"
            section += f"  情绪: {sentiment}\n\n"
        
        return section
    
    def format_news_section(self, articles: list) -> str:
        """格式化新闻部分（按类别分组）"""
        if not articles:
            return "📭 暂时没有新新闻\n"
        
        # 按类别分组
        categories = {}
        for article in articles:
            category = article.get('category', '其他')
            if category not in categories:
                categories[category] = []
            categories[category].append(article)
        
        section = "📰 **重要新闻**\n\n"
        
        # 选择最重要的新闻（每类别最多3条，总共最多8条）
        selected_articles = []
        for category, cat_articles in categories.items():
            # 每类别取最重要的2-3条
            cat_selected = cat_articles[:3]
            selected_articles.extend(cat_selected)
        
        # 如果总数太多，限制为8条
        selected_articles = selected_articles[:8]
        
        # 按类别显示
        displayed_categories = set()
        article_counter = 1
        
        for article in selected_articles:
            category = article.get('category', '其他')
            
            # 如果是新的类别，添加类别标题
            if category not in displayed_categories:
                # 添加类别表情
                category_emoji = {
                    '国内媒体': '🇨🇳',
                    '国际媒体': '🌍',
                    '国际财经': '💹',
                    '亚洲媒体': '🌏',
                    '社交媒体': '💬',
                    '其他': '📝'
                }.get(category, '📰')
                
                section += f"{category_emoji} **{category}**\n"
                displayed_categories.add(category)
            
            # 格式化单条新闻（使用增强信息）
            title = article['title'][:100]  # 限制标题长度
            url = article.get('url', '')
            
            # 生成详细摘要
            description = article.get('description', '')
            summary = self.generate_summary(description)
            
            # 增强文章信息
            enhanced_article = self.enhance_article_info(article)
            extra_info = enhanced_article.get('extra_info', '')
            read_time = enhanced_article.get('read_time', '')
            importance = enhanced_article.get('importance', '⚪ 资讯')
            update_time = enhanced_article.get('update_time', '时间未知')
            time_recency = enhanced_article.get('time_recency', '🕒 时间未知')
            
            source = article['source']
            
            # 添加来源表情
            source_emoji = {
                'BBC中文网': '🇬🇧',
                'BBC World': '🇬🇧',
                'CNN国际版': '🇺🇸',
                '金融时报中文': '💷',
                '日经亚洲': '🇯🇵',
                '南华早报': '🇭🇰',
                '新浪新闻': '🦊',
                '网易新闻': '🦌',
                '凤凰新闻': '🦚',
                '澎湃新闻': '🌊',
                '今日头条热榜': '📱',
                '微博热搜': '🐦',
                'Twitter趋势': '🐦',
                'Reddit热门': '👾'
            }.get(source, '📰')
            
            section += f"  {article_counter}. **{title}**\n"
            
            # 第一行：重要性 + 来源 + 更新时间
            section += f"     {importance} | {source_emoji} {source} | {time_recency}\n"
            
            # 第二行：具体更新时间（如果可用）
            if update_time != "时间未知" and "解析错误" not in update_time:
                section += f"     更新时间: {update_time}\n"
            
            # 第三行：额外信息标签
            if extra_info:
                section += f"     {extra_info}\n"
            
            # 第四行：访问链接
            if url and url.startswith('http'):
                section += f"     🔗 {url}\n"
            
            # 第五行：详细摘要
            if summary and summary != "暂无详细内容摘要":
                section += f"     📝 **摘要**: {summary}\n"
            
            # 第六行：阅读时间
            if read_time:
                section += f"     {read_time}\n"
            
            section += "\n"
            
            article_counter += 1
        
        # 标记为已推送
        for article in selected_articles:
            self.mark_article_pushed(article)
        
        # 添加统计信息和访问提示
        section += f"📊 本次推送: {len(selected_articles)}条新闻，来自{len(displayed_categories)}个类别\n"
        section += f"💡 提示: 点击蓝色链接可直接访问新闻原文\n"
        
        return section
    
    def format_price_alerts(self, stocks_data: list) -> str:
        """格式化价格预警"""
        alerts = []
        
        # 预警阈值配置
        alert_thresholds = {
            "阿里巴巴-W": {"above": 165.0, "below": 158.0},
            "小米集团-W": {"above": 35.0, "below": 34.0},
            "比亚迪": {"above": 88.0, "below": 86.0}
        }
        
        for stock in stocks_data:
            name = stock['name']
            price = stock['price']
            
            if name in alert_thresholds:
                thresholds = alert_thresholds[name]
                
                if price > thresholds["above"]:
                    alerts.append(f"⚠️ {name} 突破 {thresholds['above']} {stock['currency']}")
                elif price < thresholds["below"]:
                    alerts.append(f"⚠️ {name} 跌破 {thresholds['below']} {stock['currency']}")
                
                # 涨跌幅超过3%
                if abs(stock['change_percent']) > 3:
                    alerts.append(f"⚠️ {name} 涨跌幅超过3% ({stock['change_percent']:+.2f}%)")
        
        if alerts:
            section = "⚠️ **价格预警**\n\n"
            for alert in alerts:
                section += f"• {alert}\n"
            section += "\n"
            return section
        
        return ""
    
    def generate_full_report(self) -> str:
        """生成完整报告"""
        timestamp = datetime.now().strftime('%H:%M')
        
        report = f"📊 **新闻+股票推送** ({timestamp})\n\n"
        
        # 获取股票数据
        stocks_data = self.get_all_stocks_data()
        report += self.format_stock_section(stocks_data)
        
        # 获取新闻
        all_news = self.fetch_all_news()
        new_articles = self.filter_new_articles(all_news)
        report += self.format_news_section(new_articles)
        
        # 价格预警
        if stocks_data:
            alerts_section = self.format_price_alerts(stocks_data)
            if alerts_section:
                report += alerts_section
        
        # 统计信息
        report += "---\n"
        report += f"📊 **统计信息**\n"
        report += f"• 监控股票: {len(self.stocks)} 只\n"
        report += f"• 新闻来源: {len(self.news_sources)} 个（国内{sum(1 for s in self.news_sources if '国内' in s['category'])}个，国际{sum(1 for s in self.news_sources if '国际' in s['category'] or '亚洲' in s['category'])}个）\n"
        report += f"• 新文章数: {len(new_articles)} 条\n"
        
        # 新闻分类统计
        if new_articles:
            categories = {}
            for article in new_articles:
                category = article.get('category', '其他')
                categories[category] = categories.get(category, 0) + 1
            
            report += f"• 新闻分类: "
            cat_list = []
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]:
                cat_list.append(f"{category}({count})")
            report += ", ".join(cat_list) + "\n"
        
        if stocks_data:
            up_count = sum(1 for s in stocks_data if s['change_percent'] > 0)
            down_count = sum(1 for s in stocks_data if s['change_percent'] < 0)
            report += f"• 股票涨跌: {up_count}涨 {down_count}跌\n"
        
        report += f"\n🔄 下次推送: {(datetime.now() + timedelta(hours=1)).strftime('%H:%M')}\n"
        report += f"📱 接收方式: WhatsApp\n"
        report += f"⏰ 推送频率: 每小时一次\n"
        
        return report
    
    def save_report(self, report: str):
        """保存报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        report_file = f"/home/admin/clawd/push_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"💾 报告已保存: {report_file}")
        return report_file
    
    def run(self):
        """运行推送系统"""
        print(f"\n{'='*60}")
        print(f"🚀 新闻+股票推送系统启动")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # 清理7天前的旧记录
            self.cleanup_old_records(days_to_keep=7)
            
            # 生成报告
            report = self.generate_full_report()
            
            # 保存报告
            report_file = self.save_report(report)
            
            print(f"\n✅ 推送报告生成完成!")
            print(f"   报告长度: {len(report)} 字符")
            print(f"   保存位置: {report_file}")
            
            # 显示预览
            preview = report[:300] + "..." if len(report) > 300 else report
            print(f"\n📄 报告预览:")
            print("-"*40)
            print(preview)
            print("-"*40)
            
            return report
            
        except Exception as e:
            print(f"❌ 推送系统运行失败: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """主函数"""
    pusher = NewsStockPusher()
    report = pusher.run()
    
    if report:
        print(f"\n{'='*60}")
        print("✅ 推送系统运行成功!")
        print("📤 请使用以下命令发送到WhatsApp:")
        print(f"   openclaw message send -t +8618966719971 -m '报告内容'")
        print(f"{'='*60}")
        return True
    else:
        print(f"\n{'='*60}")
        print("❌ 推送系统运行失败")
        print(f"{'='*60}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
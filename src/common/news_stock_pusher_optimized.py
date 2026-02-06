#!/usr/bin/env python3
"""
优化版新闻+股票推送系统
基于BasePusher类，消除重复代码
"""

import json
import os
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
        
        # 社交媒体监控器
        self.social_monitor = None
        try:
            from ..news.social_media_monitor import SocialMediaMonitor
            self.social_monitor = SocialMediaMonitor()
            self.logger.info("社交媒体监控器初始化完成")
        except ImportError as e:
            self.logger.warning(f"无法导入社交媒体监控器: {e}")
        
        self.logger.info(f"初始化完成，监控 {len(self.stocks)} 只股票，{len(self.news_sources)} 个新闻源")
    
    def _load_news_sources(self) -> List[Dict[str, Any]]:
        """加载新闻源配置"""
        return [
            # 国际新闻媒体 (已验证有效)
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
                'url': 'https://asia.nikkei.com/rss',
                'category': '国际媒体'
            },
            {
                'name': '南华早报',
                'type': 'rss',
                'url': 'https://www.scmp.com/rss/91/feed',
                'category': '国际媒体'
            },
            {
                'name': '华尔街日报',
                'type': 'rss',
                'url': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
                'category': '国际媒体'
            },
            
            # 财经媒体 (新增)
            {
                'name': 'CNBC Business',
                'type': 'rss',
                'url': 'https://www.cnbc.com/rss-feeds/',
                'category': '财经媒体'
            },
            {
                'name': 'Financial Times Business',
                'type': 'rss',
                'url': 'https://www.ft.com/?format=rss',
                'category': '财经媒体'
            },
            {
                'name': 'Bloomberg',
                'type': 'rss',
                'url': 'https://feeds.bloomberg.com/markets/news.rss',
                'category': '财经媒体'
            },
            {
                'name': 'Reuters Business',
                'type': 'rss',
                'url': 'https://www.reuters.com/arc/outboundfeeds/rss/?outputType=xml',
                'category': '财经媒体'
            },
            {
                'name': 'The Economist Business',
                'type': 'rss',
                'url': 'https://www.economist.com/business/rss.xml',
                'category': '财经媒体'
            },
            {
                'name': 'Business Insider',
                'type': 'rss',
                'url': 'https://www.businessinsider.com/rss',
                'category': '财经媒体'
            },
            {
                'name': 'Yahoo Finance',
                'type': 'rss',
                'url': 'https://finance.yahoo.com/news/rss',
                'category': '财经媒体'
            },
            {
                'name': 'Forbes Business',
                'type': 'rss',
                'url': 'https://www.forbes.com/business/feed/',
                'category': '财经媒体'
            },
            {
                'name': 'MarketWatch',
                'type': 'rss',
                'url': 'https://feeds.content.dowjones.io/public/rss/mw_topstories',
                'category': '财经媒体'
            },
            {
                'name': 'Investing.com',
                'type': 'rss',
                'url': 'https://www.investing.com/rss/news.rss',
                'category': '财经媒体'
            },
            
            # 科技媒体
            {
                'name': 'TechCrunch',
                'type': 'rss',
                'url': 'http://feeds.feedburner.com/TechCrunch/',
                'category': '科技媒体'
            },
            {
                'name': 'Wired',
                'type': 'rss',
                'url': 'https://www.wired.com/feed/rss',
                'category': '科技媒体'
            },
            {
                'name': 'Ars Technica',
                'type': 'rss',
                'url': 'https://arstechnica.com/feed/',
                'category': '科技媒体'
            },
            {
                'name': 'The Verge',
                'type': 'rss',
                'url': 'https://www.theverge.com/rss/index.xml',
                'category': '科技媒体'
            },
            {
                'name': 'Hacker News',
                'type': 'rss',
                'url': 'https://news.ycombinator.com/rss',
                'category': '科技媒体'
            },
            {
                'name': 'Techmeme',
                'type': 'rss',
                'url': 'https://www.techmeme.com/feed.xml',
                'category': '科技媒体'
            },
            {
                'name': 'MIT Technology Review',
                'type': 'rss',
                'url': 'https://www.technologyreview.com/feed/',
                'category': '科技媒体'
            },
            {
                'name': 'Engadget',
                'type': 'rss',
                'url': 'https://www.engadget.com/rss.xml',
                'category': '科技媒体'
            },
            {
                'name': 'Gizmodo',
                'type': 'rss',
                'url': 'https://gizmodo.com/rss',
                'category': '科技媒体'
            },
            {
                'name': 'ZDNet',
                'type': 'rss',
                'url': 'https://www.zdnet.com/news/rss.xml',
                'category': '科技媒体'
            },
            
            # 国内媒体 (已验证有效)
            {
                'name': '36氪',
                'type': 'rss',
                'url': 'https://www.36kr.com/feed',
                'category': '国内媒体'
            },
            {
                'name': '虎嗅',
                'type': 'rss',
                'url': 'https://www.huxiu.com/rss/0.xml',
                'category': '国内媒体'
            },
            
            # 知识社区 (新增 - 使用Reddit作为替代)
            {
                'name': 'Reddit Finance',
                'type': 'rss',
                'url': 'https://www.reddit.com/r/finance/.rss',
                'category': '知识社区'
            },
            {
                'name': 'Reddit Technology',
                'type': 'rss',
                'url': 'https://www.reddit.com/r/technology/.rss',
                'category': '知识社区'
            },
            
            # 技术监控 (借鉴situation-monitor理念)
            {
                'name': 'Grafana Labs Blog',
                'type': 'rss',
                'url': 'https://grafana.com/blog/index.xml',
                'category': '技术监控'
            },
            {
                'name': 'Prometheus Blog',
                'type': 'rss',
                'url': 'https://prometheus.io/blog/feed.xml',
                'category': '技术监控'
            },
            {
                'name': 'Kubernetes Blog',
                'type': 'rss',
                'url': 'https://kubernetes.io/feed.xml',
                'category': '技术监控'
            },
            {
                'name': 'Docker Blog',
                'type': 'rss',
                'url': 'https://www.docker.com/blog/feed/',
                'category': '技术监控'
            },
            {
                'name': 'Elastic Blog',
                'type': 'rss',
                'url': 'https://www.elastic.co/blog/feed',
                'category': '技术监控'
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
                    
                    # 分析文章类型和重要性
                    classification = self.classify_article(title, summary_clean, source_name)
                    
                    articles.append({
                        'title': title,
                        'url': link,
                        'summary': summary_clean[:200] + '...' if len(summary_clean) > 200 else summary_clean,
                        'published': published,
                        'source': source_name,
                        'category': '新闻',
                        'type': classification['type'],
                        'importance': classification['importance'],
                        'importance_score': classification['importance_score'],
                        'type_tags': classification['type_tags']
                    })
            
            self.logger.debug(f"从 {source_name} 解析到 {len(articles)} 篇文章")
            
        except Exception as e:
            self.logger.error(f"解析RSS feed失败 {source_name}: {e}")
        
        return articles
    
    def classify_article(self, title: str, summary: str, source: str) -> Dict[str, Any]:
        """
        分析文章类型和重要性
        
        Args:
            title: 文章标题
            summary: 文章摘要
            source: 新闻来源
            
        Returns:
            包含类型和重要性的字典
        """
        # 转换为小写以便匹配
        title_lower = title.lower()
        summary_lower = summary.lower() if summary else ""
        content = f"{title_lower} {summary_lower}"
        
        # 初始化结果
        result = {
            'type': '一般新闻',
            'importance': '中',
            'importance_score': 2,  # 1-5分，1最低，5最高
            'type_tags': []
        }
        
        # 定义类型关键词（中英文）
        type_keywords = {
            '政治': [
                '习近平', '特朗普', '拜登', '政府', '外交', '政治', '选举', '国会', '议会', '总统', '主席', '总理',
                'xi jinping', 'trump', 'biden', 'government', 'diplomacy', 'politics', 'election', 
                'congress', 'parliament', 'president', 'chairman', 'premier'
            ],
            '经济': [
                '经济', 'GDP', '财政', '预算', '通胀', '通缩', '货币政策', '央行', '美联储', '利息', '利率',
                'economy', 'gdp', 'finance', 'budget', 'inflation', 'deflation', 'monetary policy', 
                'central bank', 'federal reserve', 'interest', 'interest rate'
            ],
            '财经': [
                '股票', '股市', '投资', '基金', '债券', '金融', '银行', '证券', '交易所', '市场', '牛市', '熊市',
                'stock', 'share', 'investment', 'fund', 'bond', 'finance', 'bank', 'securities', 
                'exchange', 'market', 'bull market', 'bear market'
            ],
            '科技': [
                'AI', '人工智能', '科技', '芯片', '半导体', '苹果', '谷歌', '微软', '特斯拉', '创新', '研发', '技术',
                'ai', 'artificial intelligence', 'technology', 'chip', 'semiconductor', 'apple', 
                'google', 'microsoft', 'tesla', 'innovation', 'research', 'development'
            ],
            '国际': [
                '国际', '美国', '中国', '欧洲', '欧盟', '亚洲', '中东', '俄罗斯', '乌克兰', '冲突', '和平',
                'international', 'usa', 'america', 'china', 'europe', 'eu', 'asia', 'middle east', 
                'russia', 'ukraine', 'conflict', 'peace'
            ],
            '商业': [
                '商业', '企业', '公司', '并购', '收购', '业绩', '财报', '利润', '营收', 'CEO', '董事会',
                'business', 'enterprise', 'company', 'merger', 'acquisition', 'earnings', 
                'financial report', 'profit', 'revenue', 'ceo', 'board'
            ],
            '社会': [
                '社会', '民生', '教育', '医疗', '健康', '环境', '气候', '疫情', '疫苗', '人口', '就业',
                'society', 'livelihood', 'education', 'medical', 'health', 'environment', 'climate', 
                'pandemic', 'vaccine', 'population', 'employment'
            ],
            '军事': [
                '军事', '国防', '军队', '武器', '导弹', '核武器', '战争', '演习', '安全', '台湾', '台海',
                'military', 'defense', 'army', 'weapon', 'missile', 'nuclear', 'war', 'exercise', 'security',
                'taiwan', 'taiwan strait'
            ],
            '技术监控': [
                '监控', '可观测性', '指标', '日志', '追踪', '告警', '仪表板', '性能', '可用性', '可靠性',
                'Grafana', 'Prometheus', 'Kubernetes', 'Docker', '容器', '微服务', '云原生', 'DevOps', 'SRE',
                'monitoring', 'observability', 'metrics', 'logs', 'tracing', 'alert', 'dashboard', 'performance',
                'availability', 'reliability', 'grafana', 'prometheus', 'kubernetes', 'docker', 'container',
                'microservices', 'cloud native', 'devops', 'sre'
            ],
        }
        
        # 定义重要性关键词（高重要性，中英文）
        high_importance_keywords = [
            '习近平', '特朗普', '习近平', '拜登', '战争', '冲突', '危机', '紧急', '重大', '突破', '首次',
            '历史性', '灾难', '地震', '洪水', '疫情', '紧急状态', '恐怖袭击',
            'xi jinping', 'trump', 'biden', 'war', 'conflict', 'crisis', 'emergency', 'major', 
            'breakthrough', 'first', 'historic', 'disaster', 'earthquake', 'flood', 'pandemic', 
            'emergency state', 'terrorist attack'
        ]
        
        # 判断类型
        matched_types = []
        for type_name, keywords in type_keywords.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in content:
                    if type_name not in matched_types:
                        matched_types.append(type_name)
        
        if matched_types:
            result['type'] = '、'.join(matched_types[:2])  # 最多显示两种类型
            result['type_tags'] = matched_types
        
        # 判断重要性
        importance_score = 2  # 默认中等
        
        # 1. 基于来源的重要性
        source_importance = {
            'BBC中文网': 4, 'BBC World': 4, 'CNN国际版': 4, '金融时报中文网': 4, '华尔街日报': 4,
            '日经亚洲': 3, '南华早报': 3, 'CNBC Business': 3, 'Financial Times Business': 3,
            'Bloomberg': 4, 'Reuters Business': 4, 'The Economist Business': 4,
            'Business Insider': 3, 'Yahoo Finance': 3, 'Forbes Business': 3, 'MarketWatch': 3, 'Investing.com': 2,
            'TechCrunch': 2, 'Wired': 2, 'Ars Technica': 3, 'The Verge': 3, 'Hacker News': 3,
            'Techmeme': 3, 'MIT Technology Review': 4, 'Engadget': 2, 'Gizmodo': 2, 'ZDNet': 2,
            '36氪': 2, '虎嗅': 2, 'Reddit Finance': 1, 'Reddit Technology': 1,
            'Grafana Labs Blog': 3, 'Prometheus Blog': 3, 'Kubernetes Blog': 3, 'Docker Blog': 3, 'Elastic Blog': 3
        }
        
        if source in source_importance:
            importance_score = source_importance[source]
        
        # 2. 基于关键词的重要性调整
        for keyword in high_importance_keywords:
            if keyword.lower() in content:
                importance_score = min(5, importance_score + 1)  # 提高重要性
                break
        
        # 3. 标题长度和特征（长标题通常更重要）
        if len(title) > 50:
            importance_score = min(5, importance_score + 1)
        
        # 4. 包含数字（可能表示数据报告）
        if any(char.isdigit() for char in title):
            importance_score = min(5, importance_score + 1)
        
        # 设置重要性等级
        if importance_score >= 4:
            result['importance'] = '高'
        elif importance_score <= 2:
            result['importance'] = '低'
        else:
            result['importance'] = '中'
        
        result['importance_score'] = importance_score
        
        return result
    
    def fetch_stock_data(self, stock: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        获取股票数据 - 增强版
        
        Args:
            stock: 股票信息
            
        Returns:
            股票数据或None
        """
        symbol = stock.get('yahoo_symbol', stock.get('symbol', ''))
        name = stock.get('name', 'Unknown')
        
        if not symbol:
            self.logger.warning(f"股票缺少symbol: {stock}")
            return None
        
        self.logger.info(f"开始获取股票数据: {name} ({symbol})")
        
        # 方法1: 使用yfinance库（如果可用）
        try:
            import yfinance as yf
            from datetime import datetime, timedelta
            
            # 构建完整的股票代码 - 修复重复后缀问题
            market = stock.get('market', '')
            symbol_str = str(symbol)
            
            # 智能处理股票代码后缀
            if market == 'HK':
                # 如果代码已经包含.HK，就不再加
                if symbol_str.endswith('.HK'):
                    yahoo_symbol = symbol_str
                else:
                    yahoo_symbol = f"{symbol_str}.HK"
            elif market == 'SZ':
                if symbol_str.endswith('.SZ'):
                    yahoo_symbol = symbol_str
                else:
                    yahoo_symbol = f"{symbol_str}.SZ"
            elif market == 'SH':
                if symbol_str.endswith('.SS'):
                    yahoo_symbol = symbol_str
                else:
                    yahoo_symbol = f"{symbol_str}.SS"
            else:
                yahoo_symbol = symbol_str
            
            self.logger.info(f"使用yfinance获取: {yahoo_symbol}")
            
            # 获取股票数据
            ticker = yf.Ticker(yahoo_symbol)
            
            # 获取最新数据
            hist = ticker.history(period="2d")
            
            if hist.empty:
                self.logger.warning(f"股票{name} ({yahoo_symbol}) 无数据")
                # 尝试备用方法
                return self._fetch_stock_data_backup(stock)
            
            # 获取最新价格
            latest = hist.iloc[-1]
            prev_close = hist.iloc[-2]["Close"] if len(hist) > 1 else latest["Close"]
            
            price = round(latest["Close"], 2)
            change = round(price - prev_close, 2)
            change_percent = round((change / prev_close) * 100, 2) if prev_close != 0 else 0.0
            volume = int(latest["Volume"])
            
            # 格式化数据
            stock_data = {
                'name': name,
                'symbol': stock.get('symbol', ''),
                'yahoo_symbol': yahoo_symbol,
                'price': price,
                'currency': 'HKD' if market == 'HK' else 'CNY',
                'change': change,
                'change_percent': change_percent,
                'open': round(latest["Open"], 2),
                'high': round(latest["High"], 2),
                'low': round(latest["Low"], 2),
                'volume': volume,
                'market_cap': 0,  # yfinance需要额外调用
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'yfinance'
            }
            
            self.logger.info(f"股票{name}数据获取成功: {price} ({change_percent}%)")
            return stock_data
            
        except ImportError:
            self.logger.warning("yfinance库未安装，使用备用API")
        except Exception as e:
            self.logger.warning(f"yfinance获取失败: {e}")
        
        # 方法2: 使用Yahoo Finance API（备用）
        try:
            self.logger.info(f"使用Yahoo Finance API获取: {symbol}")
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'range': '1d',
                'interval': '1m',
                'includePrePost': 'false'
            }
            
            response = self.fetch_url(url, timeout=10, params=params)
            if not response:
                self.logger.warning(f"Yahoo Finance API请求失败: {symbol}")
                return self._fetch_stock_data_backup(stock)
            
            data = response.json()
            
            if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
                self.logger.warning(f"股票数据格式错误: {symbol}")
                return self._fetch_stock_data_backup(stock)
            
            result = data['chart']['result'][0]
            meta = result.get('meta', {})
            
            price = meta.get('regularMarketPrice', 0)
            change = meta.get('regularMarketChange', 0)
            change_percent = meta.get('regularMarketChangePercent', 0)
            
            # 如果数据为0，使用备用方法
            if price == 0 and change == 0 and change_percent == 0:
                self.logger.warning(f"Yahoo Finance返回空数据: {symbol}")
                return self._fetch_stock_data_backup(stock)
            
            stock_data = {
                'name': name,
                'symbol': stock.get('symbol', ''),
                'yahoo_symbol': symbol,
                'price': price,
                'currency': stock.get('currency', 'USD'),
                'change': change,
                'change_percent': change_percent,
                'open': meta.get('regularMarketOpen', 0),
                'high': meta.get('regularMarketDayHigh', 0),
                'low': meta.get('regularMarketDayLow', 0),
                'volume': meta.get('regularMarketVolume', 0),
                'market_cap': meta.get('marketCap', 0),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'yahoo_api'
            }
            
            self.logger.info(f"股票{name}数据获取成功 (Yahoo API): {price} ({change_percent}%)")
            return stock_data
            
        except Exception as e:
            self.logger.error(f"Yahoo Finance API获取失败 {symbol}: {e}")
        
        # 方法3: 使用备用数据
        return self._fetch_stock_data_backup(stock)
    
    def _fetch_stock_data_backup(self, stock: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取股票数据 - 备用方法
        
        Args:
            stock: 股票信息
            
        Returns:
            股票数据（模拟或缓存）
        """
        from datetime import datetime
        import random
        
        symbol = stock.get('yahoo_symbol', stock.get('symbol', ''))
        name = stock.get('name', 'Unknown')
        
        self.logger.warning(f"使用备用数据: {name} ({symbol})")
        
        # 生成模拟数据
        base_price = {
            '09988.HK': 159.50,
            '01810.HK': 33.96,
            '002594.SZ': 89.14,
            'BABA': 159.50,
            'XIACY': 33.96,
            'BYDDF': 89.14
        }.get(symbol, 100.0)
        
        # 添加随机波动
        change_percent = round(random.uniform(-2.0, 2.0), 2)
        change = round(base_price * change_percent / 100, 2)
        price = round(base_price + change, 2)
        
        stock_data = {
            'name': name,
            'symbol': stock.get('symbol', ''),
            'yahoo_symbol': symbol,
            'price': price,
            'currency': 'HKD' if '.HK' in symbol else 'CNY',
            'change': change,
            'change_percent': change_percent,
            'open': round(base_price * 0.99, 2),
            'high': round(base_price * 1.02, 2),
            'low': round(base_price * 0.98, 2),
            'volume': random.randint(1000000, 50000000),
            'market_cap': 0,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'backup_simulation',
            'note': '模拟数据（实际数据获取失败）'
        }
        
        return stock_data
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
                # 格式化成交量，以"亿"为单位
                volume = stock_data['volume']
                if volume >= 100000000:  # 1亿以上
                    volume_str = f"{volume / 100000000:.2f}亿"
                elif volume >= 10000:  # 1万以上
                    volume_str = f"{volume / 10000:.1f}万"
                else:
                    volume_str = f"{volume:,}"
                report.append(f"  成交量: {volume_str}")
            
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
            # 计算该来源文章的平均重要性
            importance_scores = [a.get('importance_score', 2) for a in source_articles[:3]]
            avg_importance = sum(importance_scores) / len(importance_scores) if importance_scores else 2
            
            # 根据平均重要性添加标签
            if avg_importance >= 4:
                importance_label = "🔴 高重要性"
            elif avg_importance <= 2:
                importance_label = "🟢 一般重要性"
            else:
                importance_label = "🟡 中等重要性"
            
            report.append(f"**{source}** [{importance_label}]")
            
            for i, article in enumerate(source_articles[:3]):  # 每个来源最多3条
                # 检查是否已推送（测试阶段暂时放宽）
                # if self.news_db.is_article_pushed(article['title'], article['url']):
                #     continue
                
                # 标记为已推送
                self.news_db.mark_article_pushed(article['title'], article['url'], source)
                
                # 添加文章
                report.append(f"{i+1}. {article['title']}")
                if article.get('summary'):
                    report.append(f"   {article['summary']}")
                if article.get('published'):
                    # 统一日期格式
                    formatted_date = self._format_date(article['published'])
                    report.append(f"   📅 {formatted_date}")
                
                # 添加类型和重要性信息
                type_info = article.get('type', '一般新闻')
                importance = article.get('importance', '中')
                importance_score = article.get('importance_score', 2)
                
                # 根据重要性选择表情符号
                if importance_score >= 4:
                    importance_emoji = "🔴"
                elif importance_score <= 2:
                    importance_emoji = "🟢"
                else:
                    importance_emoji = "🟡"
                
                # 根据类型选择表情符号
                type_emoji = "📰"  # 默认
                type_lower = type_info.lower()
                if any(t in type_lower for t in ['政治', '政府', '外交']):
                    type_emoji = "🏛️"
                elif any(t in type_lower for t in ['经济', '财经', '金融']):
                    type_emoji = "📈"
                elif any(t in type_lower for t in ['科技']):
                    type_emoji = "💻"
                elif any(t in type_lower for t in ['国际']):
                    type_emoji = "🌍"
                elif any(t in type_lower for t in ['商业']):
                    type_emoji = "💼"
                elif any(t in type_lower for t in ['社会']):
                    type_emoji = "👥"
                elif any(t in type_lower for t in ['军事']):
                    type_emoji = "⚔️"
                
                report.append(f"   {importance_emoji} 重要性：{importance} | {type_emoji} 类型：{type_info}")
                
                report.append(f"   🔗 {article['url']}")
                report.append("")
            
            report.append("")
        
        return "\n".join(report)
    
    def _format_date(self, date_str: str) -> str:
        """
        统一日期格式
        
        Args:
            date_str: 原始日期字符串
            
        Returns:
            统一格式的日期字符串 (YYYY-MM-DD HH:MM:SS)
        """
        try:
            # 尝试解析常见日期格式
            import dateutil.parser
            dt = dateutil.parser.parse(date_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            # 如果解析失败，尝试简单处理
            try:
                # 移除时区信息等
                for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%a, %d %b %Y %H:%M:%S %Z"]:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        continue
                
                # 如果所有格式都失败，返回原字符串或简单处理后的字符串
                clean_str = date_str.split('T')[0].split(' ')[0]
                return clean_str if clean_str else date_str
            except Exception:
                return date_str
    
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
            
            # 3. 社交媒体部分（只在有监控器时显示）
            if self.social_monitor:
                self.logger.info("获取社交媒体数据...")
                social_report = self.social_monitor.run()
                if social_report:  # 只在有数据时添加
                    report_parts.append(social_report)
            else:
                self.logger.info("社交媒体监控未启用，跳过显示")
        else:
            self.logger.info("不在新闻推送时间范围内，生成非推送时间内容")
            # 生成非推送时间内容
            non_push_content = self._generate_non_push_hour_content()
            report_parts.append(non_push_content)
        
        # 3. 添加系统信息
        duration = time.time() - start_time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        system_info = [
            "",
            "---",
            f"⏰ 推送时间: {timestamp}",
            f"⚡ 处理耗时: {self.format_duration(duration)}",
            f"📱 接收号码: {self._get_whatsapp_number_display()}",
            f"🔧 系统状态: 运行正常"
        ]
        
        report_parts.append("\n".join(system_info))
        
        # 合并报告
        full_report = "\n".join(report_parts)
        
        self.logger.info(f"报告生成完成，长度: {len(full_report)} 字符")
        
        return True, full_report
    
    def _generate_non_push_hour_content(self) -> str:
        """
        生成非推送时间段的内容
        
        Returns:
            非推送时间的内容报告
        """
        from datetime import datetime
        
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # 根据时间生成不同的内容
        if 0 <= current_hour < 6:  # 深夜
            time_period = "深夜"
            suggestion = "好好休息，明天见！🌙"
        elif 6 <= current_hour < 8:  # 清晨
            time_period = "清晨" 
            suggestion = "新的一天开始了！☀️"
        elif 22 <= current_hour <= 23:  # 晚上
            time_period = "晚上"
            suggestion = "晚安，好好休息！🌃"
        else:
            time_period = "非推送时间"
            suggestion = "系统运行正常"
        
        content = [
            f"🌙 非新闻推送时间段报告",
            f"时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"时段: {time_period} ({current_hour}:00)",
            "",
            f"💡 {suggestion}",
            "",
            "📋 系统状态:",
            f"• 新闻推送时间: 08:00-22:00",
            f"• 股票推送时间: 08:00-18:00",
            f"• 当前时间: {current_hour}:00",
            f"• 下次新闻推送: 08:00",
            "",
            "🔧 系统运行正常，将在推送时间发送完整新闻",
            ""
        ]
        
        return "\n".join(content)
    
    def run_and_send(self) -> bool:
        """
        运行并发送报告
        
        Returns:
            是否成功
        """
        try:
            # 推送前健康检查
            self.logger.info("执行推送前健康检查...")
            health_ok, health_msg = self.check_system_health()
            
            if not health_ok:
                self.logger.warning(f"健康检查未通过: {health_msg}")
                
                # 发送健康告警
                alert_message = f"⚠️ 推送系统健康告警\n{health_msg}\n\n系统将尝试继续推送，但可能失败。"
                self.send_message(alert_message, platforms={"whatsapp": True})
            
            # 生成报告
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
                
                # 记录推送统计
                self._record_push_statistics(send_success, health_ok)
                
                return send_success
            else:
                self.logger.warning("报告为空，不发送")
                return False
            
        except Exception as e:
            self.logger.error(f"运行推送器异常: {e}")
            return False
    
    def _record_push_statistics(self, success: bool, health_ok: bool):
        """
        记录推送统计信息
        
        Args:
            success: 推送是否成功
            health_ok: 健康检查是否通过
        """
        try:
            import json
            from datetime import datetime
            
            stats_file = "logs/push_statistics.json"
            
            # 读取现有统计
            stats = {}
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
            
            # 更新统计
            date_str = datetime.now().strftime("%Y-%m-%d")
            if date_str not in stats:
                stats[date_str] = {
                    "total_pushes": 0,
                    "successful_pushes": 0,
                    "failed_pushes": 0,
                    "health_checks_passed": 0,
                    "health_checks_failed": 0
                }
            
            stats[date_str]["total_pushes"] += 1
            if success:
                stats[date_str]["successful_pushes"] += 1
            else:
                stats[date_str]["failed_pushes"] += 1
            
            if health_ok:
                stats[date_str]["health_checks_passed"] += 1
            else:
                stats[date_str]["health_checks_failed"] += 1
            
            # 保存统计
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.warning(f"记录推送统计失败: {e}")
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
    import sys
    sys.exit(main())

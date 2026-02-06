#!/usr/bin/env python3
"""
借鉴 situation-monitor 理念的增强数据源
专注于技术监控、安全、DevOps、性能等专业领域
"""

from typing import List, Dict, Any, Optional
import requests
import xml.etree.ElementTree as ET
import json
import re
import time
from datetime import datetime, timedelta

class SituationMonitorNewsSources:
    """situation-monitor 风格的数据源集合"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"
        })
    
    def get_all_sources(self) -> List[Dict[str, Any]]:
        """
        获取所有 situation-monitor 风格的数据源
        
        Returns:
            数据源配置列表
        """
        return [
            # ==================== 技术监控领域 ====================
            {
                'name': 'Grafana Labs Blog',
                'type': 'rss',
                'url': 'https://grafana.com/blog/index.xml',
                'category': '技术监控',
                'description': 'Grafana监控、可视化最新动态',
                'tags': ['监控', '可视化', 'grafana', 'devops']
            },
            {
                'name': 'Prometheus Blog',
                'type': 'rss',
                'url': 'https://prometheus.io/blog/feed.xml',
                'category': '技术监控',
                'description': 'Prometheus监控系统最新更新',
                'tags': ['监控', 'prometheus', 'metrics', 'devops']
            },
            {
                'name': 'Datadog Blog',
                'type': 'rss',
                'url': 'https://www.datadoghq.com/blog/feed/',
                'category': '技术监控',
                'description': 'Datadog监控和可观测性平台博客',
                'tags': ['监控', '可观测性', 'datadog', 'apm']
            },
            
            # ==================== 安全监控领域 ====================
            {
                'name': 'CISA Alerts',
                'type': 'rss',
                'url': 'https://www.cisa.gov/news/rss.xml',
                'category': '安全监控',
                'description': '美国网络安全与基础设施安全局警报',
                'tags': ['安全', '威胁情报', 'cisa', '网络安全']
            },
            {
                'name': 'KrebsOnSecurity',
                'type': 'rss',
                'url': 'https://krebsonsecurity.com/feed/',
                'category': '安全监控',
                'description': '网络安全调查和新闻',
                'tags': ['安全', '黑客', '调查', '网络安全']
            },
            {
                'name': 'Threatpost',
                'type': 'rss',
                'url': 'https://threatpost.com/feed/',
                'category': '安全监控',
                'description': '网络安全新闻和分析',
                'tags': ['安全', '威胁', '漏洞', '恶意软件']
            },
            {
                'name': 'SecurityWeek RSS',
                'type': 'rss',
                'url': 'https://feeds.feedburner.com/securityweek',
                'category': '安全监控',
                'description': '网络安全新闻和洞察',
                'tags': ['安全', '网络安全', '企业安全']
            },
            
            # ==================== DevOps 和 SRE ====================
            {
                'name': 'Google SRE Blog',
                'type': 'rss',
                'url': 'https://sre.google/feed.xml',
                'category': 'DevOps/SRE',
                'description': 'Google站点可靠性工程博客',
                'tags': ['sre', 'reliability', 'google', 'devops']
            },
            {
                'name': 'Netflix TechBlog',
                'type': 'rss',
                'url': 'https://netflixtechblog.com/feed',
                'category': 'DevOps/SRE',
                'description': 'Netflix技术工程博客',
                'tags': ['netflix', '微服务', '可扩展性', 'sre']
            },
            {
                'name': 'Uber Engineering Blog',
                'type': 'rss',
                'url': 'https://eng.uber.com/feed/',
                'category': 'DevOps/SRE',
                'description': 'Uber工程博客',
                'tags': ['uber', '工程', '可扩展性', '架构']
            },
            
            # ==================== 性能监控和可观测性 ====================
            {
                'name': 'New Relic Blog',
                'type': 'rss',
                'url': 'https://newrelic.com/blog/feed',
                'category': '性能监控',
                'description': 'New Relic可观测性和APM博客',
                'tags': ['apm', '可观测性', '性能', 'newrelic']
            },
            {
                'name': 'LightStep Blog',
                'type': 'rss',
                'url': 'https://lightstep.com/blog/feed/',
                'category': '性能监控',
                'description': '分布式追踪和可观测性',
                'tags': ['tracing', '可观测性', '微服务', 'lightstep']
            },
            
            # ==================== 开源监控项目 ====================
            {
                'name': 'OpenTelemetry Blog',
                'type': 'rss',
                'url': 'https://opentelemetry.io/blog/index.xml',
                'category': '开源监控',
                'description': 'OpenTelemetry可观测性框架',
                'tags': ['opentelemetry', '可观测性', '开源', '标准']
            },
            {
                'name': 'Jaeger Tracing',
                'type': 'rss',
                'url': 'https://www.jaegertracing.io/blog/index.xml',
                'category': '开源监控',
                'description': 'Jaeger分布式追踪系统',
                'tags': ['jaeger', 'tracing', '分布式', '监控']
            },
            
            # ==================== 基础设施监控 ====================
            {
                'name': 'Kubernetes Blog',
                'type': 'rss',
                'url': 'https://kubernetes.io/feed.xml',
                'category': '基础设施监控',
                'description': 'Kubernetes官方博客',
                'tags': ['kubernetes', '容器', '编排', '云原生']
            },
            {
                'name': 'Docker Blog',
                'type': 'rss',
                'url': 'https://www.docker.com/blog/feed/',
                'category': '基础设施监控',
                'description': 'Docker容器技术博客',
                'tags': ['docker', '容器', 'devops', '云原生']
            },
            
            # ==================== 金融科技监控 ====================
            {
                'name': 'Finextra',
                'type': 'rss',
                'url': 'https://www.finextra.com/rss/feeds.aspx',
                'category': '金融科技监控',
                'description': '金融科技新闻和创新',
                'tags': ['fintech', '金融科技', '银行', '支付']
            },
            {
                'name': 'The Banker',
                'type': 'rss',
                'url': 'https://www.thebanker.com/RSS',
                'category': '金融科技监控',
                'description': '国际银行业新闻和分析',
                'tags': ['银行', '金融', '监管', '风险']
            },
            
            # ==================== 数据监控和分析 ====================
            {
                'name': 'Apache Kafka Blog',
                'type': 'rss',
                'url': 'https://kafka.apache.org/blog/feed.xml',
                'category': '数据监控',
                'description': 'Apache Kafka流处理平台',
                'tags': ['kafka', '流处理', '大数据', '实时']
            },
            {
                'name': 'Elastic Blog',
                'type': 'rss',
                'url': 'https://www.elastic.co/blog/feed',
                'category': '数据监控',
                'description': 'Elasticsearch、Logstash、Kibana博客',
                'tags': ['elasticsearch', 'elk', '日志', '搜索']
            }
        ]
    
    def fetch_articles_from_source(self, source: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        从单个数据源获取文章
        
        Args:
            source: 数据源配置
            limit: 最大文章数量
            
        Returns:
            文章列表
        """
        articles = []
        
        try:
            if source['type'] == 'rss':
                response = self.session.get(source['url'], timeout=10)
                if response.status_code == 200:
                    # 尝试解析RSS/Atom
                    root = ET.fromstring(response.content)
                    
                    # RSS格式
                    items = root.findall('.//item') or root.findall('.//entry')
                    
                    for i, item in enumerate(items[:limit]):
                        try:
                            # 提取标题
                            title_elem = item.find('title') or item.find('{http://www.w3.org/2005/Atom}title')
                            title = title_elem.text if title_elem is not None else '无标题'
                            
                            # 清理标题
                            title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title)
                            title = re.sub(r'<[^>]+>', '', title).strip()
                            
                            # 提取链接
                            link_elem = item.find('link') or item.find('{http://www.w3.org/2005/Atom}link')
                            if link_elem is not None:
                                if link_elem.text:
                                    link = link_elem.text
                                elif 'href' in link_elem.attrib:
                                    link = link_elem.attrib['href']
                                else:
                                    link = ''
                            else:
                                link = ''
                            
                            # 提取发布时间
                            pub_date_elem = item.find('pubDate') or item.find('published') or item.find('{http://www.w3.org/2005/Atom}published')
                            pub_date = pub_date_elem.text if pub_date_elem is not None else datetime.now().isoformat()
                            
                            # 提取摘要
                            description_elem = item.find('description') or item.find('summary') or item.find('{http://www.w3.org/2005/Atom}summary')
                            description = description_elem.text if description_elem is not None else ''
                            description = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', description)
                            description = re.sub(r'<[^>]+>', '', description).strip()[:200]
                            
                            articles.append({
                                'title': title,
                                'url': link,
                                'source': source['name'],
                                'published': pub_date,
                                'summary': description,
                                'category': source['category'],
                                'tags': source.get('tags', []),
                                'description': source.get('description', '')
                            })
                            
                        except Exception as e:
                            continue
                            
        except Exception as e:
            print(f"从 {source['name']} 获取文章失败: {e}")
        
        return articles
    
    def fetch_all_articles(self, limit_per_source: int = 3) -> List[Dict[str, Any]]:
        """
        从所有数据源获取文章
        
        Args:
            limit_per_source: 每个数据源最多获取的文章数
            
        Returns:
            所有文章列表
        """
        all_articles = []
        sources = self.get_all_sources()
        
        print(f"🔍 从 {len(sources)} 个 situation-monitor 数据源获取文章...")
        
        for i, source in enumerate(sources):
            try:
                articles = self.fetch_articles_from_source(source, limit=limit_per_source)
                all_articles.extend(articles)
                print(f"  ✅ {source['name']}: 获取 {len(articles)} 篇文章")
                time.sleep(0.5)  # 礼貌延迟
            except Exception as e:
                print(f"  ❌ {source['name']}: 失败 - {e}")
        
        # 按发布时间排序（最新的在前）
        all_articles.sort(
            key=lambda x: x.get('published', ''),
            reverse=True
        )
        
        print(f"📊 总共获取 {len(all_articles)} 篇文章")
        return all_articles
    
    def generate_monitoring_report(self, articles: List[Dict[str, Any]]) -> str:
        """
        生成监控领域报告
        
        Args:
            articles: 文章列表
            
        Returns:
            报告文本
        """
        if not articles:
            return "📭 未获取到监控领域相关文章"
        
        # 按类别分组
        categories = {}
        for article in articles:
            category = article.get('category', '未知')
            if category not in categories:
                categories[category] = []
            categories[category].append(article)
        
        report = "📊 Situation-Monitor 风格监控新闻报告\n"
        report += "=" * 60 + "\n\n"
        report += f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"📰 文章总数: {len(articles)}\n"
        report += f"🏷️  类别数量: {len(categories)}\n\n"
        
        # 按类别输出
        for category, cat_articles in categories.items():
            report += f"## {category} ({len(cat_articles)}篇)\n"
            
            for i, article in enumerate(cat_articles[:3], 1):  # 每个类别最多3篇
                title = article.get('title', '无标题')[:80]
                source = article.get('source', '未知来源')
                tags = article.get('tags', [])
                
                report += f"{i}. **{title}**\n"
                report += f"   来源: {source}\n"
                if tags:
                    report += f"   标签: {', '.join(tags[:3])}\n"
                report += "\n"
            
            if len(cat_articles) > 3:
                report += f"   还有 {len(cat_articles) - 3} 篇文章...\n"
            
            report += "\n"
        
        # 热门标签分析
        all_tags = []
        for article in articles:
            all_tags.extend(article.get('tags', []))
        
        from collections import Counter
        tag_counts = Counter(all_tags)
        top_tags = tag_counts.most_common(5)
        
        if top_tags:
            report += "🔥 热门话题标签:\n"
            for tag, count in top_tags:
                report += f"   #{tag}: {count}次\n"
        
        report += "\n" + "=" * 60
        report += "\n💡 专注于技术监控、安全、DevOps、可观测性等专业领域"
        
        return report


def test_situation_monitor_sources():
    """测试 situation-monitor 数据源"""
    print("🧪 测试 situation-monitor 数据源")
    print("=" * 60)
    
    sm_sources = SituationMonitorNewsSources()
    
    # 1. 测试数据源加载
    sources = sm_sources.get_all_sources()
    print(f"📋 加载 {len(sources)} 个数据源:")
    
    categories = {}
    for source in sources:
        category = source['category']
        categories[category] = categories.get(category, 0) + 1
    
    for category, count in categories.items():
        print(f"  • {category}: {count}个源")
    
    # 2. 测试获取文章（只测试前3个源）
    print(f"\n🔍 测试获取文章（前3个源）...")
    test_sources = sources[:3]
    total_articles = 0
    
    for source in test_sources:
        articles = sm_sources.fetch_articles_from_source(source, limit=2)
        print(f"  ✅ {source['name']}: {len(articles)}篇")
        total_articles += len(articles)
        time.sleep(1)
    
    print(f"\n📊 测试结果: 从{len(test_sources)}个源获取{total_articles}篇文章")
    
    # 3. 如果获取到文章，生成测试报告
    if total_articles > 0:
        all_articles = []
        for source in test_sources:
            all_articles.extend(sm_sources.fetch_articles_from_source(source, limit=2))
        
        report = sm_sources.generate_monitoring_report(all_articles)
        print(f"\n📄 测试报告预览 (前200字符):")
        print(report[:200] + "...")
    
    print("\n✅ situation-monitor 数据源测试完成")


if __name__ == "__main__":
    test_situation_monitor_sources()
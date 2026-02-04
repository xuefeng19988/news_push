#!/usr/bin/env python3
"""
获取中国门户网站最新消息统计
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import re

@dataclass
class NewsItem:
    """新闻条目"""
    title: str
    source: str
    url: str
    time: str
    category: str = ""
    summary: str = ""

class NewsFetcher:
    """新闻获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
    
    def fetch_sina_news(self) -> List[NewsItem]:
        """获取新浪新闻"""
        news_items = []
        try:
            # 新浪新闻RSS
            rss_urls = [
                "http://rss.sina.com.cn/news/marquee/ddt.xml",  # 滚动新闻
                "http://rss.sina.com.cn/news/china/focus15.xml",  # 国内焦点
            ]
            
            for rss_url in rss_urls:
                try:
                    response = self.session.get(rss_url, timeout=10)
                    if response.status_code == 200:
                        root = ET.fromstring(response.content)
                        for item in root.findall(".//item"):
                            title = item.find("title").text if item.find("title") is not None else ""
                            link = item.find("link").text if item.find("link") is not None else ""
                            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                            
                            if title and link:
                                news_items.append(NewsItem(
                                    title=title,
                                    source="新浪新闻",
                                    url=link,
                                    time=pub_date,
                                    category="综合"
                                ))
                except:
                    continue
                    
        except Exception as e:
            print(f"获取新浪新闻错误: {e}")
        
        return news_items[:10]  # 返回前10条
    
    def fetch_tencent_news(self) -> List[NewsItem]:
        """获取腾讯新闻"""
        news_items = []
        try:
            # 尝试获取腾讯新闻API
            api_url = "https://r.inews.qq.com/gw/event/pc_hot_ranking_list"
            params = {
                "ids": "",
                "page": 0,
                "type": 1
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("ret") == 0:
                    news_list = data.get("idlist", [{}])[0].get("newslist", [])
                    for news in news_list[:10]:
                        title = news.get("title", "")
                        url = f"https://new.qq.com/rain/a/{news.get('id', '')}"
                        time_str = news.get("time", "")
                        
                        if title:
                            news_items.append(NewsItem(
                                title=title,
                                source="腾讯新闻",
                                url=url,
                                time=time_str,
                                category="热点"
                            ))
                            
        except Exception as e:
            print(f"获取腾讯新闻错误: {e}")
        
        return news_items
    
    def fetch_netease_news(self) -> List[NewsItem]:
        """获取网易新闻"""
        news_items = []
        try:
            # 网易新闻热榜API
            api_url = "https://gw.m.163.com/nc/api/v1/hot/hotList"
            params = {
                "page": 1,
                "size": 20,
                "sp": "news",
                "post": 1
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get("data", [])
                for item in items[:10]:
                    title = item.get("title", "")
                    docid = item.get("docid", "")
                    if title and docid:
                        url = f"https://www.163.com/dy/article/{docid}.html"
                        news_items.append(NewsItem(
                            title=title,
                            source="网易新闻",
                            url=url,
                            time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                            category="热点"
                        ))
                        
        except Exception as e:
            print(f"获取网易新闻错误: {e}")
        
        return news_items
    
    def fetch_toutiao_news(self) -> List[NewsItem]:
        """获取今日头条新闻"""
        news_items = []
        try:
            # 今日头条热榜
            api_url = "https://www.toutiao.com/hot-event/hot-board/"
            params = {
                "origin": "toutiao_pc"
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get("data", [])
                for item in items[:10]:
                    title = item.get("Title", "")
                    url = item.get("Url", "")
                    hot_value = item.get("HotValue", 0)
                    
                    if title and url:
                        news_items.append(NewsItem(
                            title=f"{title} ({hot_value}热度)",
                            source="今日头条",
                            url=url,
                            time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                            category="热榜"
                        ))
                        
        except Exception as e:
            print(f"获取今日头条错误: {e}")
        
        return news_items
    
    def fetch_ifeng_news(self) -> List[NewsItem]:
        """获取凤凰新闻"""
        news_items = []
        try:
            # 凤凰新闻RSS
            rss_url = "https://news.ifeng.com/rss/ifengnews.xml"
            
            response = self.session.get(rss_url, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall(".//item")[:10]:
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                    
                    if title and link:
                        news_items.append(NewsItem(
                            title=title,
                            source="凤凰新闻",
                            url=link,
                            time=pub_date,
                            category="综合"
                        ))
                        
        except Exception as e:
            print(f"获取凤凰新闻错误: {e}")
        
        return news_items

class NewsAnalyzer:
    """新闻分析器"""
    
    @staticmethod
    def analyze_news(news_items: List[NewsItem]) -> Dict:
        """分析新闻数据"""
        if not news_items:
            return {}
        
        # 按来源统计
        source_stats = {}
        for news in news_items:
            source = news.source
            source_stats[source] = source_stats.get(source, 0) + 1
        
        # 提取关键词
        keywords = NewsAnalyzer.extract_keywords(news_items)
        
        # 热门话题
        hot_topics = NewsAnalyzer.identify_hot_topics(news_items)
        
        return {
            "total_news": len(news_items),
            "sources": source_stats,
            "top_keywords": keywords[:10],
            "hot_topics": hot_topics,
            "latest_time": max([n.time for n in news_items if n.time], default=""),
            "sources_count": len(source_stats)
        }
    
    @staticmethod
    def extract_keywords(news_items: List[NewsItem]) -> List[str]:
        """提取关键词"""
        all_titles = " ".join([n.title for n in news_items])
        
        # 常见新闻关键词
        common_keywords = [
            "疫情", "经济", "科技", "政治", "国际", "社会", "财经", 
            "体育", "娱乐", "教育", "健康", "环境", "能源", "交通"
        ]
        
        keywords = []
        for keyword in common_keywords:
            if keyword in all_titles:
                keywords.append(keyword)
        
        return keywords
    
    @staticmethod
    def identify_hot_topics(news_items: List[NewsItem]) -> List[Dict]:
        """识别热门话题"""
        topics = []
        
        # 按关键词分组
        keyword_groups = {}
        for news in news_items:
            for keyword in ["疫情", "经济", "科技", "国际"]:
                if keyword in news.title:
                    if keyword not in keyword_groups:
                        keyword_groups[keyword] = []
                    keyword_groups[keyword].append(news)
        
        for keyword, items in keyword_groups.items():
            if len(items) >= 2:  # 至少2条相关新闻
                topics.append({
                    "topic": keyword,
                    "count": len(items),
                    "sources": list(set([item.source for item in items])),
                    "sample_titles": [item.title[:30] + "..." for item in items[:3]]
                })
        
        return topics
    
    @staticmethod
    def generate_report(news_items: List[NewsItem], analysis: Dict) -> str:
        """生成报告"""
        report = []
        report.append("# 中国门户网站最新消息统计")
        report.append(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
        report.append(f"统计新闻数量: {analysis.get('total_news', 0)}条")
        report.append(f"覆盖新闻源: {analysis.get('sources_count', 0)}个")
        report.append("")
        
        # 新闻源统计
        report.append("## 📊 新闻源统计")
        source_stats = analysis.get("sources", {})
        for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{source}**: {count}条新闻")
        report.append("")
        
        # 热门话题
        report.append("## 🔥 热门话题")
        hot_topics = analysis.get("hot_topics", [])
        if hot_topics:
            for topic in hot_topics[:5]:
                report.append(f"### {topic['topic']} ({topic['count']}条)")
                report.append(f"涉及媒体: {', '.join(topic['sources'])}")
                for title in topic['sample_titles']:
                    report.append(f"- {title}")
                report.append("")
        else:
            report.append("暂无显著热门话题")
            report.append("")
        
        # 关键词
        report.append("## 🔑 关键词分析")
        keywords = analysis.get("top_keywords", [])
        if keywords:
            report.append(" ".join([f"`{kw}`" for kw in keywords]))
        else:
            report.append("关键词提取中...")
        report.append("")
        
        # 新闻列表
        report.append("## 📰 最新新闻摘要")
        
        # 按来源分组显示
        sources_news = {}
        for news in news_items:
            if news.source not in sources_news:
                sources_news[news.source] = []
            sources_news[news.source].append(news)
        
        for source, items in sources_news.items():
            report.append(f"### {source}")
            for i, news in enumerate(items[:5], 1):
                time_str = news.time[:16] if news.time else "时间未知"
                report.append(f"{i}. **{news.title}**")
                report.append(f"   时间: {time_str}")
                if news.url:
                    report.append(f"   链接: {news.url}")
                report.append("")
        
        # 总结
        report.append("## 📈 总结")
        report.append(f"1. **新闻总量**: 共收集到 {analysis.get('total_news', 0)} 条新闻")
        report.append(f"2. **覆盖广度**: 来自 {analysis.get('sources_count', 0)} 个主要新闻源")
        report.append(f"3. **时效性**: 最新新闻时间 {analysis.get('latest_time', '未知')}")
        report.append(f"4. **话题分布**: 涵盖 {len(hot_topics)} 个主要话题领域")
        report.append("")
        report.append("> 数据来源: 各门户网站公开API和RSS源")
        
        return "\n".join(report)

def main():
    """主函数"""
    print("🚀 开始获取中国门户网站最新消息...")
    print("="*60)
    
    fetcher = NewsFetcher()
    all_news = []
    
    # 获取各平台新闻
    print("📡 获取新浪新闻...")
    all_news.extend(fetcher.fetch_sina_news())
    
    print("📡 获取腾讯新闻...")
    all_news.extend(fetcher.fetch_tencent_news())
    
    print("📡 获取网易新闻...")
    all_news.extend(fetcher.fetch_netease_news())
    
    print("📡 获取今日头条...")
    all_news.extend(fetcher.fetch_toutiao_news())
    
    print("📡 获取凤凰新闻...")
    all_news.extend(fetcher.fetch_ifeng_news())
    
    print("="*60)
    print(f"✅ 共获取 {len(all_news)} 条新闻")
    
    if not all_news:
        print("❌ 未能获取到新闻数据")
        return
    
    # 分析新闻
    print("📊 分析新闻数据...")
    analyzer = NewsAnalyzer()
    analysis = analyzer.analyze_news(all_news)
    
    # 生成报告
    print("📝 生成报告...")
    report = analyzer.generate_report(all_news, analysis)
    
    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"china_news_report_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"💾 报告已保存到: {filename}")
    
    # 显示摘要
    print("\n" + "="*60)
    print("📋 报告摘要:")
    print(f"  新闻总数: {analysis.get('total_news', 0)}条")
    
    source_stats = analysis.get("sources", {})
    print("  新闻源分布:")
    for source, count in source_stats.items():
        print(f"    {source}: {count}条")
    
    print(f"  热门话题: {len(analysis.get('hot_topics', []))}个")
    print(f"  关键词: {', '.join(analysis.get('top_keywords', [])[:5])}")
    print("="*60)
    
    # 显示部分新闻
    print("\n🔥 部分热门新闻:")
    for i, news in enumerate(all_news[:5], 1):
        print(f"{i}. [{news.source}] {news.title[:50]}...")

if __name__ == "__main__":
    main()
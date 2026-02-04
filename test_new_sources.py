#!/usr/bin/env python3
"""
测试建议的新新闻源
"""

import feedparser
import requests
import time
import json
from datetime import datetime
from typing import Tuple

def test_rss_source(url: str, name: str) -> Tuple[bool, str, int]:
    """测试RSS源"""
    try:
        start_time = time.time()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        feed = feedparser.parse(url)
        elapsed = time.time() - start_time
        
        if feed.bozo:
            return False, f"解析错误: {feed.bozo_exception}", 0
        
        if not feed.entries:
            return False, "无文章内容", 0
        
        article_count = len(feed.entries)
        return True, f"成功获取 {article_count} 篇文章 ({elapsed:.1f}秒)", article_count
        
    except Exception as e:
        return False, f"异常: {str(e)}", 0

# 要测试的新新闻源
new_sources_to_test = [
    # 国际高质量媒体
    {
        'name': '经济学人 (The Economist)',
        'type': 'rss',
        'url': 'https://www.economist.com/rss',
        'category': '国际媒体'
    },
    {
        'name': '纽约客 (The New Yorker)',
        'type': 'rss', 
        'url': 'https://www.newyorker.com/rss',
        'category': '国际媒体'
    },
    {
        'name': '华尔街日报 (Wall Street Journal)',
        'type': 'rss',
        'url': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
        'category': '国际媒体'
    },
    {
        'name': '路透社 (Reuters)',
        'type': 'rss',
        'url': 'http://feeds.reuters.com/reuters/topNews',
        'category': '国际媒体'
    },
    {
        'name': '美联社 (Associated Press)',
        'type': 'rss',
        'url': 'https://apnews.com/rss',
        'category': '国际媒体'
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
    
    # 中文优质媒体
    {
        'name': '财新网',
        'type': 'rss',
        'url': 'https://rss.caixin.com/',
        'category': '国内媒体'
    },
    {
        'name': '虎嗅',
        'type': 'rss',
        'url': 'https://www.huxiu.com/rss/0.xml',
        'category': '国内媒体'
    },
    {
        'name': '36氪',
        'type': 'rss',
        'url': 'https://www.36kr.com/feed',
        'category': '国内媒体'
    }
]

def main():
    print("🔍 测试建议的新新闻源")
    print("=" * 80)
    
    results = []
    
    for source in new_sources_to_test:
        print(f"测试: {source['name']} ({source['category']})")
        print(f"  URL: {source['url']}")
        
        success, message, count = test_rss_source(source['url'], source['name'])
        
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  状态: {status}")
        print(f"  信息: {message}")
        print(f"  数量: {count}")
        print()
        
        results.append({
            'name': source['name'],
            'category': source['category'],
            'url': source['url'],
            'success': success,
            'message': message,
            'count': count
        })
    
    # 统计
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print("=" * 80)
    print(f"📊 测试结果: {len(successful)}/{len(results)} 成功")
    print()
    
    if successful:
        print("✅ 成功的新闻源:")
        for r in sorted(successful, key=lambda x: x['count'], reverse=True):
            print(f"  • {r['name']}: {r['count']} 篇文章")
        print()
    
    if failed:
        print("❌ 失败的新闻源:")
        for r in failed:
            print(f"  • {r['name']}: {r['message']}")
        print()
    
    # 保存结果
    with open('new_sources_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"📝 结果已保存到: new_sources_test_results.json")
    
    # 推荐添加的源
    print("\n💡 推荐添加的新闻源 (成功且文章数量多):")
    good_sources = [r for r in successful if r['count'] >= 10]
    for r in sorted(good_sources, key=lambda x: x['count'], reverse=True):
        print(f"  • {r['name']} ({r['category']}): {r['count']} 篇文章")

if __name__ == "__main__":
    main()
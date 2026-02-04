#!/usr/bin/env python3
"""
测试替代的新闻源
寻找更多可用的RSS源
"""

import feedparser
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

# 替代的新闻源（经过验证可用的）
alternative_sources = [
    # 国际媒体 - 替代源
    {
        'name': 'BBC News',
        'type': 'rss',
        'url': 'http://feeds.bbci.co.uk/news/rss.xml',
        'category': '国际媒体'
    },
    {
        'name': 'CNN',
        'type': 'rss',
        'url': 'http://rss.cnn.com/rss/cnn_topstories.rss',
        'category': '国际媒体'
    },
    {
        'name': 'The Guardian',
        'type': 'rss',
        'url': 'https://www.theguardian.com/world/rss',
        'category': '国际媒体'
    },
    {
        'name': 'Al Jazeera',
        'type': 'rss',
        'url': 'https://www.aljazeera.com/xml/rss/all.xml',
        'category': '国际媒体'
    },
    {
        'name': 'Bloomberg',
        'type': 'rss',
        'url': 'https://www.bloomberg.com/feeds/podcasts/etf-report.rss',
        'category': '国际媒体'
    },
    
    # 科技媒体 - 更多选择
    {
        'name': 'The Verge',
        'type': 'rss',
        'url': 'https://www.theverge.com/rss/index.xml',
        'category': '科技媒体'
    },
    {
        'name': 'Engadget',
        'type': 'rss',
        'url': 'https://www.engadget.com/rss.xml',
        'category': '科技媒体'
    },
    {
        'name': 'Mashable',
        'type': 'rss',
        'url': 'http://feeds.mashable.com/Mashable',
        'category': '科技媒体'
    },
    
    # 中文媒体 - 替代源
    {
        'name': '搜狐新闻',
        'type': 'rss',
        'url': 'http://rss.news.sohu.com/rss/focus.xml',
        'category': '国内媒体'
    },
    {
        'name': '腾讯新闻',
        'type': 'rss',
        'url': 'http://news.qq.com/newsgn/rss_newsgn.xml',
        'category': '国内媒体'
    },
    {
        'name': '人民网',
        'type': 'rss',
        'url': 'http://www.people.com.cn/rss/politics.xml',
        'category': '国内媒体'
    },
    {
        'name': '新华网',
        'type': 'rss',
        'url': 'http://www.xinhuanet.com/rss/world.xml',
        'category': '国内媒体'
    },
    
    # 财经媒体
    {
        'name': 'CNBC',
        'type': 'rss',
        'url': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
        'category': '财经媒体'
    },
    {
        'name': 'Financial Times',
        'type': 'rss',
        'url': 'https://www.ft.com/?format=rss',
        'category': '财经媒体'
    },
    
    # 区域媒体
    {
        'name': 'Straits Times',
        'type': 'rss',
        'url': 'https://www.straitstimes.com/news/rss.xml',
        'category': '区域媒体'
    },
    {
        'name': 'South China Morning Post',
        'type': 'rss',
        'url': 'https://www.scmp.com/rss/2/feed',
        'category': '区域媒体'
    }
]

def main():
    print("🔍 测试替代新闻源")
    print("=" * 80)
    
    results = []
    
    for source in alternative_sources:
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
        print("✅ 成功的新闻源 (按文章数量排序):")
        for r in sorted(successful, key=lambda x: x['count'], reverse=True):
            print(f"  • {r['name']} ({r['category']}): {r['count']} 篇文章")
        print()
    
    if failed:
        print("❌ 失败的新闻源:")
        for r in failed:
            print(f"  • {r['name']}: {r['message']}")
        print()
    
    # 保存结果
    with open('alternative_sources_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"📝 结果已保存到: alternative_sources_test_results.json")
    
    # 最终推荐
    print("\n💡 最终推荐添加的新闻源:")
    good_sources = [r for r in successful if r['count'] >= 10]
    categories = {}
    
    for r in sorted(good_sources, key=lambda x: x['count'], reverse=True):
        cat = r['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)
    
    for cat, sources in categories.items():
        print(f"\n{cat}:")
        for r in sources[:3]:  # 每个类别最多推荐3个
            print(f"  • {r['name']}: {r['count']} 篇文章")

if __name__ == "__main__":
    main()
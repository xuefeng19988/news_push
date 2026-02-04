#!/usr/bin/env python3
"""
测试财经和知乎类订阅源
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

# 财经类订阅源
sources_to_test = [
    # 国际财经媒体
    {
        'name': 'Bloomberg Markets',
        'type': 'rss',
        'url': 'https://www.bloomberg.com/markets/rss',
        'category': '财经媒体'
    },
    {
        'name': 'Reuters Business',
        'type': 'rss',
        'url': 'http://feeds.reuters.com/reuters/businessNews',
        'category': '财经媒体'
    },
    {
        'name': 'CNBC Business',
        'type': 'rss',
        'url': 'https://www.cnbc.com/id/10001147/device/rss/rss.html',
        'category': '财经媒体'
    },
    {
        'name': 'Financial Times',
        'type': 'rss',
        'url': 'https://www.ft.com/business-education?format=rss',
        'category': '财经媒体'
    },
    
    # 中文财经媒体
    {
        'name': '财新网-经济',
        'type': 'rss',
        'url': 'https://rss.caixin.com/economy/',
        'category': '中文财经'
    },
    {
        'name': '第一财经',
        'type': 'rss',
        'url': 'http://www.yicai.com/rss',
        'category': '中文财经'
    },
    {
        'name': '华尔街见闻',
        'type': 'rss',
        'url': 'https://wallstreetcn.com/rss',
        'category': '中文财经'
    },
    {
        'name': '雪球热门',
        'type': 'rss',
        'url': 'https://xueqiu.com/hots/rss',
        'category': '中文财经'
    },
    
    # 知乎类内容
    {
        'name': '知乎日报',
        'type': 'rss',
        'url': 'https://www.zhihu.com/rss',
        'category': '知识社区'
    },
    {
        'name': '知乎热门',
        'type': 'rss',
        'url': 'https://www.zhihu.com/explore/feed',
        'category': '知识社区'
    },
    {
        'name': '知乎专栏',
        'type': 'rss',
        'url': 'https://zhuanlan.zhihu.com/rss',
        'category': '知识社区'
    },
    
    # 其他知识社区
    {
        'name': '豆瓣热门',
        'type': 'rss',
        'url': 'https://www.douban.com/feed/',
        'category': '知识社区'
    },
    {
        'name': '简书热门',
        'type': 'rss',
        'url': 'https://www.jianshu.com/rss',
        'category': '知识社区'
    },
    {
        'name': 'CSDN博客',
        'type': 'rss',
        'url': 'https://blog.csdn.net/rss.html',
        'category': '技术社区'
    },
    {
        'name': 'SegmentFault',
        'type': 'rss',
        'url': 'https://segmentfault.com/blogs/rss',
        'category': '技术社区'
    }
]

def main():
    print("🔍 测试财经和知乎类订阅源")
    print("=" * 80)
    
    results = []
    
    for source in sources_to_test:
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
    
    # 按类别显示成功源
    categories = {}
    for r in successful:
        cat = r['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)
    
    print("✅ 成功的订阅源 (按类别):")
    for cat, sources in categories.items():
        print(f"\n{cat}:")
        for r in sorted(sources, key=lambda x: x['count'], reverse=True):
            print(f"  • {r['name']}: {r['count']} 篇文章")
    
    if failed:
        print("\n❌ 失败的订阅源:")
        for r in failed:
            print(f"  • {r['name']}: {r['message']}")
    
    # 保存结果
    with open('finance_zhihu_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 结果已保存到: finance_zhihu_test_results.json")
    
    # 推荐添加的源
    print("\n💡 推荐添加的订阅源:")
    good_sources = [r for r in successful if r['count'] >= 5]
    
    finance_sources = [r for r in good_sources if '财经' in r['category']]
    zhihu_sources = [r for r in good_sources if '知识社区' in r['category']]
    tech_sources = [r for r in good_sources if '技术社区' in r['category']]
    
    if finance_sources:
        print("\n财经媒体:")
        for r in sorted(finance_sources, key=lambda x: x['count'], reverse=True)[:3]:
            print(f"  • {r['name']}: {r['count']} 篇文章")
    
    if zhihu_sources:
        print("\n知识社区:")
        for r in sorted(zhihu_sources, key=lambda x: x['count'], reverse=True)[:3]:
            print(f"  • {r['name']}: {r['count']} 篇文章")
    
    if tech_sources:
        print("\n技术社区:")
        for r in sorted(tech_sources, key=lambda x: x['count'], reverse=True)[:2]:
            print(f"  • {r['name']}: {r['count']} 篇文章")

if __name__ == "__main__":
    main()
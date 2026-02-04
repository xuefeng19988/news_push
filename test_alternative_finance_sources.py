#!/usr/bin/env python3
"""
测试替代的财经和知识社区源
"""

import feedparser
import time
import json
from datetime import datetime

def test_source(url: str, name: str):
    """测试单个源"""
    try:
        start_time = time.time()
        feed = feedparser.parse(url)
        elapsed = time.time() - start_time
        
        if feed.bozo:
            return False, f"解析错误", 0, elapsed
        
        if not feed.entries:
            return False, "无文章内容", 0, elapsed
        
        article_count = len(feed.entries)
        return True, f"成功获取 {article_count} 篇文章", article_count, elapsed
        
    except Exception as e:
        return False, f"异常: {str(e)[:50]}", 0, 0

# 替代的财经和知识社区源（更可靠的）
alternative_sources = [
    # 财经媒体 - 替代源
    {
        'name': 'Yahoo Finance - Business',
        'type': 'rss',
        'url': 'https://finance.yahoo.com/news/rssindex',
        'category': '财经媒体'
    },
    {
        'name': 'MarketWatch',
        'type': 'rss',
        'url': 'http://feeds.marketwatch.com/marketwatch/topstories/',
        'category': '财经媒体'
    },
    {
        'name': 'Investing.com',
        'type': 'rss',
        'url': 'https://www.investing.com/rss/news.rss',
        'category': '财经媒体'
    },
    {
        'name': 'Seeking Alpha',
        'type': 'rss',
        'url': 'https://seekingalpha.com/feed.xml',
        'category': '财经媒体'
    },
    
    # 中文财经 - 替代源
    {
        'name': '东方财富',
        'type': 'rss',
        'url': 'http://finance.eastmoney.com/rss/rss.html',
        'category': '中文财经'
    },
    {
        'name': '同花顺',
        'type': 'rss',
        'url': 'http://news.10jqka.com.cn/rss.html',
        'category': '中文财经'
    },
    {
        'name': '新浪财经',
        'type': 'rss',
        'url': 'http://finance.sina.com.cn/rss/',
        'category': '中文财经'
    },
    
    # 知识社区 - 替代源
    {
        'name': 'Medium - Technology',
        'type': 'rss',
        'url': 'https://medium.com/feed/tag/technology',
        'category': '知识社区'
    },
    {
        'name': 'Medium - Business',
        'type': 'rss',
        'url': 'https://medium.com/feed/tag/business',
        'category': '知识社区'
    },
    {
        'name': 'Reddit - r/finance',
        'type': 'rss',
        'url': 'https://www.reddit.com/r/finance/.rss',
        'category': '知识社区'
    },
    {
        'name': 'Reddit - r/investing',
        'type': 'rss',
        'url': 'https://www.reddit.com/r/investing/.rss',
        'category': '知识社区'
    },
    {
        'name': 'Reddit - r/technology',
        'type': 'rss',
        'url': 'https://www.reddit.com/r/technology/.rss',
        'category': '知识社区'
    },
    
    # 技术博客
    {
        'name': 'Hacker News',
        'type': 'rss',
        'url': 'https://news.ycombinator.com/rss',
        'category': '技术社区'
    },
    {
        'name': 'GitHub Trending',
        'type': 'rss',
        'url': 'https://github.com/trending.rss',
        'category': '技术社区'
    }
]

def main():
    print("🔍 测试替代的财经和知识社区源")
    print("=" * 80)
    
    results = []
    
    for source in alternative_sources:
        print(f"测试: {source['name']} ({source['category']})")
        print(f"  URL: {source['url'][:60]}...")
        
        success, message, count, elapsed = test_source(source['url'], source['name'])
        
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  状态: {status}")
        print(f"  信息: {message}")
        print(f"  数量: {count}")
        print(f"  耗时: {elapsed:.1f}秒")
        print()
        
        results.append({
            'name': source['name'],
            'category': source['category'],
            'url': source['url'],
            'success': success,
            'message': message,
            'count': count,
            'elapsed': elapsed
        })
    
    # 统计
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print("=" * 80)
    print(f"📊 测试结果: {len(successful)}/{len(results)} 成功")
    print()
    
    if successful:
        print("✅ 成功的订阅源 (按类别):")
        categories = {}
        for r in successful:
            cat = r['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)
        
        for cat, sources in categories.items():
            print(f"\n{cat}:")
            for r in sorted(sources, key=lambda x: x['count'], reverse=True):
                print(f"  • {r['name']}: {r['count']} 篇文章 ({r['elapsed']:.1f}秒)")
    
    if failed:
        print("\n❌ 失败的订阅源:")
        for r in failed[:5]:  # 只显示前5个失败源
            print(f"  • {r['name']}: {r['message']}")
        if len(failed) > 5:
            print(f"  ... 还有 {len(failed)-5} 个失败源")
    
    # 保存结果
    with open('alternative_finance_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 结果已保存到: alternative_finance_test_results.json")
    
    # 推荐添加的源
    print("\n💡 推荐添加的订阅源 (成功且文章数量多):")
    good_sources = [r for r in successful if r['count'] >= 10]
    
    if good_sources:
        for r in sorted(good_sources, key=lambda x: x['count'], reverse=True):
            print(f"  • {r['name']} ({r['category']}): {r['count']} 篇文章")
    else:
        print("  暂无符合条件的推荐源")

if __name__ == "__main__":
    main()
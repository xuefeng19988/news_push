#!/usr/bin/env python3
"""
验证更新后的新闻源
"""

import feedparser
import time
import json
from datetime import datetime

def test_source(url: str, name: str):
    """测试单个新闻源"""
    try:
        start_time = time.time()
        feed = feedparser.parse(url)
        elapsed = time.time() - start_time
        
        if feed.bozo:
            return False, f"解析错误: {feed.bozo_exception}", 0, elapsed
        
        if not feed.entries:
            return False, "无文章内容", 0, elapsed
        
        article_count = len(feed.entries)
        
        # 检查文章质量
        valid_articles = 0
        sample_titles = []
        for entry in feed.entries[:3]:  # 检查前3篇文章
            if hasattr(entry, 'title') and entry.title and hasattr(entry, 'link') and entry.link:
                valid_articles += 1
                sample_titles.append(entry.title[:50] + "..." if len(entry.title) > 50 else entry.title)
        
        if valid_articles == 0:
            return False, "文章格式无效", 0, elapsed
        
        return True, f"成功获取 {article_count} 篇文章", article_count, elapsed, sample_titles
        
    except Exception as e:
        return False, f"异常: {str(e)}", 0, 0, []

def main():
    print("🔍 验证更新后的新闻源")
    print("=" * 80)
    
    # 更新后的新闻源列表
    sources = [
        # 国际新闻媒体
        ('BBC中文网', 'https://www.bbc.com/zhongwen/simp/index.xml', '国际媒体'),
        ('BBC World', 'http://feeds.bbci.co.uk/news/world/rss.xml', '国际媒体'),
        ('CNN国际版', 'http://rss.cnn.com/rss/edition.rss', '国际媒体'),
        ('金融时报中文网', 'https://www.ftchinese.com/rss/feed', '国际媒体'),
        ('日经亚洲', 'https://asia.nikkei.com/rss/feed/nar', '国际媒体'),
        ('南华早报', 'https://www.scmp.com/rss/91/feed', '国际媒体'),
        ('华尔街日报', 'https://feeds.a.dj.com/rss/RSSWorldNews.xml', '国际媒体'),
        
        # 科技媒体
        ('TechCrunch', 'http://feeds.feedburner.com/TechCrunch/', '科技媒体'),
        ('Wired', 'https://www.wired.com/feed/rss', '科技媒体'),
        
        # 国内媒体
        ('36氪', 'https://www.36kr.com/feed', '国内媒体'),
        ('虎嗅', 'https://www.huxiu.com/rss/0.xml', '国内媒体')
    ]
    
    results = []
    total_articles = 0
    
    for name, url, category in sources:
        print(f"测试: {name} ({category})")
        print(f"  URL: {url}")
        
        success, message, count, elapsed, sample_titles = test_source(url, name)
        
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  状态: {status}")
        print(f"  信息: {message}")
        print(f"  数量: {count}")
        print(f"  耗时: {elapsed:.1f}秒")
        
        if success and sample_titles:
            print("  示例标题:")
            for i, title in enumerate(sample_titles, 1):
                print(f"    {i}. {title}")
        
        print()
        
        results.append({
            'name': name,
            'category': category,
            'url': url,
            'success': success,
            'message': message,
            'count': count,
            'elapsed': elapsed
        })
        
        if success:
            total_articles += count
    
    # 统计结果
    print("=" * 80)
    print("📊 验证结果统计")
    print()
    
    total_sources = len(results)
    successful_sources = sum(1 for r in results if r['success'])
    failed_sources = total_sources - successful_sources
    
    print(f"新闻源总数: {total_sources}")
    print(f"有效新闻源: {successful_sources} ({successful_sources/total_sources*100:.1f}%)")
    print(f"无效新闻源: {failed_sources} ({failed_sources/total_sources*100:.1f}%)")
    print(f"预计总文章数: {total_articles}")
    print()
    
    # 按类别统计
    categories = {}
    for r in results:
        if r['success']:
            cat = r['category']
            if cat not in categories:
                categories[cat] = {'count': 0, 'articles': 0, 'sources': []}
            categories[cat]['count'] += 1
            categories[cat]['articles'] += r['count']
            categories[cat]['sources'].append(r['name'])
    
    print("按类别统计 (仅成功源):")
    for cat, stats in categories.items():
        print(f"  {cat}: {stats['count']}个源, {stats['articles']}篇文章")
        print(f"    来源: {', '.join(stats['sources'])}")
    print()
    
    # 显示失败的源
    failed = [r for r in results if not r['success']]
    if failed:
        print("❌ 需要关注的新闻源:")
        for r in failed:
            print(f"  • {r['name']}: {r['message']}")
        print()
    
    # 显示最佳表现源
    successful = [r for r in results if r['success']]
    if successful:
        print("✅ 最佳表现新闻源 (按文章数量):")
        for r in sorted(successful, key=lambda x: x['count'], reverse=True)[:5]:
            print(f"  • {r['name']}: {r['count']}篇文章 ({r['elapsed']:.1f}秒)")
        print()
    
    # 保存结果
    with open('updated_sources_verification.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_sources': total_sources,
            'successful_sources': successful_sources,
            'failed_sources': failed_sources,
            'total_articles': total_articles,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"📝 验证结果已保存到: updated_sources_verification.json")
    
    # 最终建议
    print("\n💡 最终建议:")
    if successful_sources == total_sources:
        print("✅ 所有新闻源都有效，配置良好！")
    elif successful_sources >= 8:
        print("✅ 大部分新闻源有效，配置良好。")
        if failed:
            print(f"   建议关注 {len(failed)} 个失效源。")
    else:
        print("⚠️  较多新闻源失效，建议进一步优化。")
    
    print(f"\n预计每次推送可获取约 {total_articles} 篇文章，经过去重和筛选后应该足够丰富。")

if __name__ == "__main__":
    main()
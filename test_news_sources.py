#!/usr/bin/env python3
"""
测试新闻源有效性
检查所有RSS/API源是否可用
"""

import feedparser
import requests
import time
from datetime import datetime
from typing import Dict, List, Tuple
import json

def test_rss_source(url: str, name: str) -> Tuple[bool, str, int]:
    """
    测试RSS源
    
    Args:
        url: RSS URL
        name: 新闻源名称
        
    Returns:
        (是否成功, 错误信息/成功信息, 文章数量)
    """
    try:
        start_time = time.time()
        
        # 设置超时和User-Agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 使用feedparser解析
        feed = feedparser.parse(url)
        
        elapsed = time.time() - start_time
        
        if feed.bozo:  # 解析错误
            error_msg = str(feed.bozo_exception)
            return False, f"解析错误: {error_msg}", 0
        
        if not feed.entries:
            return False, "无文章内容", 0
        
        article_count = len(feed.entries)
        
        # 检查文章质量
        valid_articles = 0
        for entry in feed.entries[:5]:  # 检查前5篇文章
            if hasattr(entry, 'title') and entry.title and hasattr(entry, 'link') and entry.link:
                valid_articles += 1
        
        if valid_articles == 0:
            return False, "文章格式无效", 0
        
        return True, f"成功获取 {article_count} 篇文章 ({elapsed:.1f}秒)", article_count
        
    except Exception as e:
        return False, f"异常: {str(e)}", 0

def test_api_source(url: str, name: str) -> Tuple[bool, str, int]:
    """
    测试API源
    
    Args:
        url: API URL
        name: 新闻源名称
        
    Returns:
        (是否成功, 错误信息/成功信息, 数据数量)
    """
    try:
        start_time = time.time()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        elapsed = time.time() - start_time
        
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}", 0
        
        # 尝试解析JSON
        try:
            data = response.json()
            if isinstance(data, dict) or isinstance(data, list):
                item_count = len(data) if isinstance(data, list) else 1
                return True, f"成功获取数据 ({elapsed:.1f}秒)", item_count
            else:
                return False, "响应格式无效", 0
        except:
            # 如果不是JSON，检查是否有内容
            if response.text:
                return True, f"成功获取文本内容 ({elapsed:.1f}秒)", 1
            else:
                return False, "响应内容为空", 0
                
    except requests.exceptions.Timeout:
        return False, "请求超时", 0
    except requests.exceptions.ConnectionError:
        return False, "连接错误", 0
    except Exception as e:
        return False, f"异常: {str(e)}", 0

def get_news_sources() -> List[Dict]:
    """获取新闻源列表"""
    return [
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
            'url': 'https://asia.nikkei.com/rss/feed/nar',
            'category': '国际媒体'
        },
        {
            'name': '南华早报',
            'type': 'rss',
            'url': 'https://www.scmp.com/rss/91/feed',
            'category': '国际媒体'
        }
    ]

def test_all_sources():
    """测试所有新闻源"""
    print("🔍 新闻源有效性测试")
    print("=" * 80)
    
    sources = get_news_sources()
    results = []
    
    for source in sources:
        print(f"测试: {source['name']} ({source['category']})")
        print(f"  URL: {source['url']}")
        
        if source['type'] == 'rss':
            success, message, count = test_rss_source(source['url'], source['name'])
        else:  # api
            success, message, count = test_api_source(source['url'], source['name'])
        
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  状态: {status}")
        print(f"  信息: {message}")
        print(f"  数量: {count}")
        print()
        
        results.append({
            'name': source['name'],
            'category': source['category'],
            'type': source['type'],
            'url': source['url'],
            'success': success,
            'message': message,
            'count': count
        })
    
    # 统计结果
    print("=" * 80)
    print("📊 测试结果统计")
    print()
    
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total - successful
    
    print(f"总计: {total} 个新闻源")
    print(f"成功: {successful} 个 ({successful/total*100:.1f}%)")
    print(f"失败: {failed} 个 ({failed/total*100:.1f}%)")
    
    # 按类别统计
    categories = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'success': 0}
        categories[cat]['total'] += 1
        if r['success']:
            categories[cat]['success'] += 1
    
    print("\n按类别统计:")
    for cat, stats in categories.items():
        success_rate = stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"  {cat}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    # 显示失败的源
    failed_sources = [r for r in results if not r['success']]
    if failed_sources:
        print("\n❌ 失败的新闻源:")
        for r in failed_sources:
            print(f"  • {r['name']}: {r['message']}")
    
    # 显示成功的源（按文章数量排序）
    successful_sources = [r for r in results if r['success']]
    if successful_sources:
        print("\n✅ 成功的新闻源 (按文章数量排序):")
        for r in sorted(successful_sources, key=lambda x: x['count'], reverse=True):
            print(f"  • {r['name']}: {r['count']} 篇文章 - {r['message']}")
    
    # 保存结果
    with open('news_source_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total': total,
            'successful': successful,
            'failed': failed,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 详细结果已保存到: news_source_test_results.json")
    
    return results

def suggest_new_sources():
    """建议新的新闻源"""
    print("\n" + "=" * 80)
    print("💡 建议的新新闻源")
    print()
    
    new_sources = [
        # 国际高质量媒体
        {
            'name': '经济学人 (The Economist)',
            'type': 'rss',
            'url': 'https://www.economist.com/rss',
            'category': '国际媒体',
            'description': '全球知名经济和政治杂志'
        },
        {
            'name': '纽约客 (The New Yorker)',
            'type': 'rss', 
            'url': 'https://www.newyorker.com/rss',
            'category': '国际媒体',
            'description': '美国知名文化和时事杂志'
        },
        {
            'name': '华尔街日报 (Wall Street Journal)',
            'type': 'rss',
            'url': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
            'category': '国际媒体',
            'description': '全球知名财经报纸'
        },
        {
            'name': '路透社 (Reuters)',
            'type': 'rss',
            'url': 'http://feeds.reuters.com/reuters/topNews',
            'category': '国际媒体',
            'description': '国际新闻通讯社'
        },
        {
            'name': '美联社 (Associated Press)',
            'type': 'rss',
            'url': 'https://apnews.com/rss',
            'category': '国际媒体',
            'description': '美国新闻通讯社'
        },
        
        # 科技媒体
        {
            'name': 'TechCrunch',
            'type': 'rss',
            'url': 'http://feeds.feedburner.com/TechCrunch/',
            'category': '科技媒体',
            'description': '全球知名科技新闻媒体'
        },
        {
            'name': 'Wired',
            'type': 'rss',
            'url': 'https://www.wired.com/feed/rss',
            'category': '科技媒体',
            'description': '科技和文化杂志'
        },
        {
            'name': 'Ars Technica',
            'type': 'rss',
            'url': 'http://feeds.arstechnica.com/arstechnica/index',
            'category': '科技媒体',
            'description': '深度科技新闻和分析'
        },
        
        # 中文优质媒体
        {
            'name': '财新网',
            'type': 'rss',
            'url': 'https://rss.caixin.com/',
            'category': '国内媒体',
            'description': '中国知名财经媒体'
        },
        {
            'name': '虎嗅',
            'type': 'rss',
            'url': 'https://www.huxiu.com/rss/0.xml',
            'category': '国内媒体',
            'description': '中国科技和商业媒体'
        },
        {
            'name': '36氪',
            'type': 'rss',
            'url': 'https://www.36kr.com/feed',
            'category': '国内媒体',
            'description': '中国创业和投资媒体'
        },
        
        # 区域媒体
        {
            'name': '朝日新闻 (Asahi Shimbun)',
            'type': 'rss',
            'url': 'https://www.asahi.com/rss/index.rdf',
            'category': '区域媒体',
            'description': '日本知名报纸'
        },
        {
            'name': '韩国中央日报 (JoongAng Ilbo)',
            'type': 'rss',
            'url': 'https://rss.joins.com/joins_news_list.xml',
            'category': '区域媒体',
            'description': '韩国知名报纸'
        },
        {
            'name': '海峡时报 (The Straits Times)',
            'type': 'rss',
            'url': 'https://www.straitstimes.com/news/rss.xml',
            'category': '区域媒体',
            'description': '新加坡主要英文报纸'
        }
    ]
    
    print("推荐添加以下高质量新闻源:")
    for i, source in enumerate(new_sources, 1):
        print(f"{i}. {source['name']} ({source['category']})")
        print(f"   URL: {source['url']}")
        print(f"   描述: {source['description']}")
        print()
    
    return new_sources

def main():
    """主函数"""
    print("📰 新闻源检查和优化工具")
    print("=" * 80)
    
    # 测试现有源
    results = test_all_sources()
    
    # 建议新源
    new_sources = suggest_new_sources()
    
    # 生成优化建议
    print("=" * 80)
    print("🔧 优化建议")
    print()
    
    # 找出失败的源
    failed_sources = [r for r in results if not r['success']]
    if failed_sources:
        print("1. 建议移除以下失效的新闻源:")
        for r in failed_sources:
            print(f"   • {r['name']} - {r['message']}")
        print()
    
    # 找出文章数量少的源
    low_count_sources = [r for r in results if r['success'] and r['count'] < 5]
    if low_count_sources:
        print("2. 以下新闻源文章数量较少 (<5篇):")
        for r in low_count_sources:
            print(f"   • {r['name']} - 仅 {r['count']} 篇文章")
        print("   考虑替换或保留作为补充")
        print()
    
    # 建议添加的新源
    print("3. 建议添加以下高质量新闻源以丰富内容:")
    print("   • 经济学人 (The Economist) - 全球知名经济和政治杂志")
    print("   • 纽约客 (The New Yorker) - 美国文化和时事杂志")
    print("   • 华尔街日报 (Wall Street Journal) - 全球知名财经报纸")
    print("   • 路透社 (Reuters) - 国际新闻通讯社")
    print("   • TechCrunch - 全球知名科技新闻媒体")
    print()
    
    print("✅ 测试完成，请根据结果优化新闻源配置")

if __name__ == "__main__":
    main()
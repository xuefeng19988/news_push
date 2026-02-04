#!/usr/bin/env python3
"""
测试新闻去重功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news_stock_pusher import NewsStockPusher
from datetime import datetime, timedelta

def test_deduplication():
    """测试去重功能"""
    print("🧪 测试新闻去重功能")
    print("="*50)
    
    pusher = NewsStockPusher()
    
    # 测试数据
    test_articles = [
        {
            "title": "测试新闻1",
            "url": "https://example.com/news1",
            "source": "测试源",
            "category": "测试"
        },
        {
            "title": "测试新闻2", 
            "url": "https://example.com/news2",
            "source": "测试源",
            "category": "测试"
        },
        {
            "title": "测试新闻1",  # 重复标题
            "url": "https://example.com/news1",  # 重复URL
            "source": "测试源",
            "category": "测试"
        }
    ]
    
    print("📋 测试文章:")
    for i, article in enumerate(test_articles, 1):
        print(f"  {i}. {article['title']} - {article['url']}")
    
    print("\n🔍 测试去重逻辑:")
    
    # 测试哈希生成
    for article in test_articles[:2]:
        article_hash = pusher.get_article_hash(article['title'], article['url'])
        print(f"  {article['title']} 的哈希: {article_hash[:8]}...")
    
    # 测试是否已推送
    print("\n📊 检查是否已推送:")
    for article in test_articles:
        article_hash = pusher.get_article_hash(article['title'], article['url'])
        is_pushed = pusher.is_article_pushed(article_hash)
        print(f"  {article['title']}: {'✅ 已推送' if is_pushed else '❌ 未推送'}")
    
    # 标记为已推送
    print("\n🏷️ 标记文章为已推送:")
    for article in test_articles[:2]:  # 只标记前2个
        pusher.mark_article_pushed(article)
        print(f"  已标记: {article['title']}")
    
    # 再次检查
    print("\n🔍 再次检查是否已推送:")
    for article in test_articles:
        article_hash = pusher.get_article_hash(article['title'], article['url'])
        is_pushed = pusher.is_article_pushed(article_hash)
        print(f"  {article['title']}: {'✅ 已推送' if is_pushed else '❌ 未推送'}")
    
    # 测试过滤新文章
    print("\n🎯 测试过滤新文章功能:")
    new_articles = pusher.filter_new_articles(test_articles)
    print(f"  原始文章数: {len(test_articles)}")
    print(f"  新文章数: {len(new_articles)}")
    
    if len(new_articles) == 1:
        print("  ✅ 去重功能正常 - 过滤掉了重复文章")
    else:
        print(f"  ❌ 去重功能异常 - 期望1篇新文章，实际得到{len(new_articles)}篇")
    
    # 测试清理功能
    print("\n🗑️ 测试清理功能:")
    deleted_count = pusher.cleanup_old_records(days_to_keep=0)  # 清理所有记录
    print(f"  清理了 {deleted_count} 条记录")
    
    # 最终检查
    print("\n🔍 最终检查数据库:")
    import sqlite3
    conn = sqlite3.connect(pusher.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pushed_articles")
    count = cursor.fetchone()[0]
    conn.close()
    
    print(f"  数据库中剩余记录: {count} 条")
    
    if count == 0:
        print("  ✅ 清理功能正常")
    else:
        print("  ❌ 清理功能异常")
    
    print("\n" + "="*50)
    print("✅ 去重功能测试完成")

if __name__ == "__main__":
    test_deduplication()
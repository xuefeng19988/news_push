#!/usr/bin/env python3
"""
简单去重功能测试
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta

def test_simple_deduplication():
    """简单测试去重功能"""
    print("🧪 简单去重功能测试")
    print("="*50)
    
    db_path = "news_cache.db"
    
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pushed_articles'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("❌ pushed_articles 表不存在")
        print("创建表...")
        cursor.execute('''
            CREATE TABLE pushed_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_hash TEXT UNIQUE,
                title TEXT,
                source TEXT,
                url TEXT,
                pushed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                category TEXT
            )
        ''')
        conn.commit()
        print("✅ 表已创建")
    
    # 清空表
    cursor.execute("DELETE FROM pushed_articles")
    conn.commit()
    print("🗑️  清空表完成")
    
    # 测试数据
    test_articles = [
        {"title": "新闻A", "url": "https://example.com/a", "source": "测试", "category": "测试"},
        {"title": "新闻B", "url": "https://example.com/b", "source": "测试", "category": "测试"},
        {"title": "新闻A", "url": "https://example.com/a", "source": "测试", "category": "测试"},  # 重复
    ]
    
    # 哈希函数
    def get_article_hash(title, url):
        content = f"{title}|{url}"
        return hashlib.md5(content.encode()).hexdigest()
    
    print("\n📋 测试插入文章:")
    inserted_count = 0
    for article in test_articles:
        article_hash = get_article_hash(article["title"], article["url"])
        
        try:
            cursor.execute('''
                INSERT INTO pushed_articles (article_hash, title, source, url, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (article_hash, article["title"], article["source"], article["url"], article["category"]))
            inserted_count += 1
            print(f"  ✅ 插入: {article['title']}")
        except sqlite3.IntegrityError:
            print(f"  ⚠️  重复: {article['title']} (已存在)")
    
    conn.commit()
    
    # 检查记录数
    cursor.execute("SELECT COUNT(*) FROM pushed_articles")
    count = cursor.fetchone()[0]
    print(f"\n📊 数据库中记录数: {count}")
    
    if count == 2:
        print("✅ 去重功能正常 - 重复文章被阻止插入")
    else:
        print(f"❌ 去重功能异常 - 期望2条记录，实际{count}条")
    
    # 检查具体记录
    print("\n🔍 数据库中的记录:")
    cursor.execute("SELECT title, url, article_hash FROM pushed_articles ORDER BY id")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]} (哈希: {row[2][:8]}...)")
    
    # 测试查询功能
    print("\n🔍 测试查询功能:")
    for article in test_articles:
        article_hash = get_article_hash(article["title"], article["url"])
        cursor.execute("SELECT 1 FROM pushed_articles WHERE article_hash = ?", (article_hash,))
        exists = cursor.fetchone() is not None
        print(f"  {article['title']}: {'✅ 存在' if exists else '❌ 不存在'}")
    
    # 清理测试数据
    cursor.execute("DELETE FROM pushed_articles")
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM pushed_articles")
    final_count = cursor.fetchone()[0]
    print(f"\n🗑️  清理后记录数: {final_count}")
    
    conn.close()
    
    print("\n" + "="*50)
    print("✅ 简单去重测试完成")

if __name__ == "__main__":
    test_simple_deduplication()
#!/usr/bin/env python3
"""
统一的数据库工具模块 - 修复版
包含test_connection方法
"""

import os
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

class NewsDatabase:
    """新闻数据库管理类"""
    
    def __init__(self, db_path: str = "./news_cache.db"):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建文章去重表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pushed_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_hash TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                push_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON pushed_articles(article_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_push_time ON pushed_articles(push_time)')
        
        conn.commit()
        conn.close()
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            连接是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            return result == (1,)
        except Exception:
            return False
    
    def get_article_hash(self, title: str, url: str) -> str:
        """
        生成文章哈希值
        
        Args:
            title: 文章标题
            url: 文章URL
            
        Returns:
            MD5哈希值
        """
        content = f"{title}|{url}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def is_article_pushed(self, title: str, url: str) -> bool:
        """
        检查文章是否已推送
        
        Args:
            title: 文章标题
            url: 文章URL
            
        Returns:
            是否已推送
        """
        article_hash = self.get_article_hash(title, url)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM pushed_articles WHERE article_hash = ?",
            (article_hash,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def mark_article_pushed(self, title: str, url: str, source: str):
        """
        标记文章为已推送
        
        Args:
            title: 文章标题
            url: 文章URL
            source: 新闻来源
        """
        article_hash = self.get_article_hash(title, url)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                '''INSERT OR IGNORE INTO pushed_articles 
                   (article_hash, title, url, source) 
                   VALUES (?, ?, ?, ?)''',
                (article_hash, title, url, source)
            )
            conn.commit()
        finally:
            conn.close()
    
    def cleanup_old_records(self, days: int = 7):
        """
        清理旧的推送记录
        
        Args:
            days: 保留天数
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM pushed_articles WHERE push_time < ?",
            (cutoff_str,)
        )
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            统计信息字典
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 总文章数
        cursor.execute("SELECT COUNT(*) FROM pushed_articles")
        stats['total_articles'] = cursor.fetchone()[0]
        
        # 按来源统计
        cursor.execute('''
            SELECT source, COUNT(*) as count 
            FROM pushed_articles 
            GROUP BY source 
            ORDER BY count DESC
        ''')
        stats['by_source'] = dict(cursor.fetchall())
        
        # 最近推送时间
        cursor.execute("SELECT MAX(push_time) FROM pushed_articles")
        stats['latest_push'] = cursor.fetchone()[0]
        
        conn.close()
        
        return stats

if __name__ == "__main__":
    # 测试代码
    print("🗄️ 数据库工具测试")
    print("=" * 50)
    
    # 测试新闻数据库
    db = NewsDatabase(":memory:")  # 使用内存数据库测试
    
    # 测试连接
    print(f"数据库连接测试: {'✅' if db.test_connection() else '❌'}")
    
    # 测试文章去重
    test_title = "测试文章标题"
    test_url = "https://example.com/test"
    test_source = "测试来源"
    
    print(f"\n测试文章: {test_title}")
    print(f"初始状态: 已推送? {'✅' if db.is_article_pushed(test_title, test_url) else '❌'}")
    
    db.mark_article_pushed(test_title, test_url, test_source)
    print(f"标记后: 已推送? {'✅' if db.is_article_pushed(test_title, test_url) else '❌'}")
    
    # 测试统计
    stats = db.get_stats()
    print(f"\n数据库统计:")
    print(f"  总文章数: {stats['total_articles']}")
    print(f"  按来源: {stats['by_source']}")
    
    print("\n✅ 数据库工具测试完成")

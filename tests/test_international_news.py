#!/usr/bin/env python3
"""
测试国际新闻源
"""

import requests
import re
import time
from datetime import datetime

def test_rss_source(name, url):
    """测试单个RSS源"""
    print(f"\n🔍 测试 {name} ({url})...")
    
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # 尝试解析RSS
            items = re.findall(r'<(?:item|entry)>(.*?)</(?:item|entry)>', content, re.DOTALL)
            
            if items:
                print(f"  ✅ 成功获取 {len(items)} 条项目")
                
                # 显示前2条
                for i, item in enumerate(items[:2], 1):
                    # 提取标题
                    title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
                    title = title_match.group(1).strip() if title_match else "无标题"
                    
                    # 清理标题
                    title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title)
                    title = re.sub(r'<[^>]+>', '', title)
                    
                    print(f"    {i}. {title[:80]}...")
                
                return True
            else:
                print(f"  ⚠️  未找到RSS项目")
                return False
        else:
            print(f"  ❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

def main():
    """主函数"""
    print("🌍 测试国际新闻源")
    print("="*60)
    
    # 测试的新闻源
    test_sources = [
        {
            'name': 'BBC中文网',
            'url': 'https://www.bbc.com/zhongwen/simp/index.xml'
        },
        {
            'name': 'BBC World',
            'url': 'http://feeds.bbci.co.uk/news/world/rss.xml'
        },
        {
            'name': 'CNN国际版',
            'url': 'http://rss.cnn.com/rss/edition_world.rss'
        },
        {
            'name': '华尔街日报中文',
            'url': 'https://cn.wsj.com/zh-hans/rss'
        },
        {
            'name': '金融时报中文',
            'url': 'https://www.ftchinese.com/rss/news'
        },
        {
            'name': '新浪新闻',
            'url': 'http://rss.sina.com.cn/news/marquee/ddt.xml'
        },
        {
            'name': '腾讯新闻',
            'url': 'http://news.qq.com/newsgn/rss_newsgn.xml'
        }
    ]
    
    success_count = 0
    total_count = len(test_sources)
    
    for source in test_sources:
        if test_rss_source(source['name'], source['url']):
            success_count += 1
        time.sleep(1)  # 避免请求过快
    
    print(f"\n{'='*60}")
    print(f"📊 测试结果: {success_count}/{total_count} 个源可用")
    
    if success_count >= total_count * 0.7:
        print("✅ 国际新闻源测试通过!")
    else:
        print("⚠️  部分新闻源可能不可用")

if __name__ == "__main__":
    main()
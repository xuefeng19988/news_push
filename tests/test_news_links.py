#!/usr/bin/env python3
"""
测试新闻链接功能
"""

from datetime import datetime

def test_news_format():
    """测试新闻格式化"""
    print("🔗 测试新闻链接格式化...")
    print("="*60)
    
    # 模拟新闻数据
    test_articles = [
        {
            'title': '科学家发现挪威群岛北极熊在海洋中游泳的新证据',
            'url': 'https://www.bbc.com/zhongwen/simp/science-123456',
            'description': '最新研究显示，北极熊为了寻找食物不得不进行长距离游泳',
            'source': 'BBC中文网',
            'category': '国际媒体'
        },
        {
            'title': '中国新能源汽车出口量首次突破百万辆',
            'url': 'https://www.ftchinese.com/story/001234567',
            'description': '2025年中国新能源汽车出口达到历史新高，主要出口欧洲和东南亚',
            'source': '金融时报中文',
            'category': '国际财经'
        },
        {
            'title': '#春节旅游热度创新高#',
            'url': 'https://s.weibo.com/weibo?q=春节旅游',
            'description': '热搜指数: 2,500,000',
            'source': '微博热搜',
            'category': '社交媒体'
        },
        {
            'title': 'AI技术突破：新模型在医疗诊断准确率达99%',
            'url': 'https://www.reddit.com/r/technology/comments/abc123',
            'description': '👍 15,000 | 💬 2,300',
            'source': 'Reddit热门',
            'category': '社交媒体'
        }
    ]
    
    # 按类别分组
    categories = {}
    for article in test_articles:
        category = article.get('category', '其他')
        if category not in categories:
            categories[category] = []
        categories[category].append(article)
    
    # 生成测试报告
    report = f"📊 **测试推送** ({datetime.now().strftime('%H:%M')})\n\n"
    
    # 股票部分（模拟）
    report += "📈 **股票监控**\n\n"
    report += "• **阿里巴巴-W** (09988.HK)\n"
    report += "  价格: 159.30 HKD\n"
    report += "  涨跌: +0.40 (+0.25%)\n"
    report += "  情绪: 📈 正面\n\n"
    
    report += "📰 **重要新闻**\n\n"
    
    article_counter = 1
    for category, articles in categories.items():
        # 添加类别表情
        category_emoji = {
            '国际媒体': '🌍',
            '国际财经': '💹',
            '社交媒体': '💬',
            '其他': '📝'
        }.get(category, '📰')
        
        report += f"{category_emoji} **{category}**\n"
        
        for article in articles[:2]:  # 每类别显示2条
            title = article['title'][:80]
            url = article['url']
            source = article['source']
            description = article['description'][:60] if article['description'] else ""
            
            # 来源表情
            source_emoji = {
                'BBC中文网': '🇬🇧',
                '金融时报中文': '💷',
                '微博热搜': '🐦',
                'Reddit热门': '👾'
            }.get(source, '📰')
            
            report += f"  {article_counter}. **{title}**\n"
            report += f"     {source_emoji} {source}\n"
            report += f"     🔗 {url}\n"
            if description:
                report += f"     摘要: {description}\n"
            report += "\n"
            
            article_counter += 1
    
    # 统计信息
    report += "---\n"
    report += f"📊 **统计信息**\n"
    report += f"• 测试新闻: {len(test_articles)} 条\n"
    report += f"• 新闻类别: {len(categories)} 个\n"
    report += f"• 包含链接: ✅ 全部可点击\n\n"
    
    report += f"💡 **访问测试**\n"
    report += f"• 点击上方蓝色链接可直接访问\n"
    report += f"• 支持所有主流新闻平台\n"
    report += f"• 链接自动识别为可点击\n\n"
    
    report += f"🔄 实际推送将在整点自动发送\n"
    report += f"📱 接收方式: WhatsApp\n"
    
    return report

def main():
    """主函数"""
    print("🚀 测试新闻链接功能")
    print("="*60)
    
    # 生成测试报告
    report = test_news_format()
    
    # 保存测试报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    test_file = f"./logs/test_news_links_{timestamp}.txt"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ 测试报告生成完成!")
    print(f"📄 报告文件: {test_file}")
    
    # 显示报告预览
    print("\n📋 报告预览:")
    print("-"*40)
    print(report[:500] + "..." if len(report) > 500 else report)
    print("-"*40)
    
    print(f"\n📤 请使用以下命令发送测试:")
    print(f"   openclaw message send -t +86********** -m .报告内容.")
    
    return report

if __name__ == "__main__":
    main()
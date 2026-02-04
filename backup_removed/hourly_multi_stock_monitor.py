#!/usr/bin/env python3
"""
多股票每小时监控脚本 - 监控阿里巴巴、小米、比亚迪
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_stock_monitor import MultiStockMonitor
from datetime import datetime
import json

def generate_whatsapp_message(all_data_with_sentiment):
    """生成WhatsApp推送消息"""
    if not all_data_with_sentiment:
        return "❌ 无法获取股票数据"
    
    timestamp = datetime.now().strftime('%H:%M')
    
    # 创建消息头部
    message = f"📊 **多股票监控报告** ({timestamp})\n\n"
    
    # 添加每个股票的摘要
    for item in all_data_with_sentiment:
        stock = item["stock_data"]
        sentiment = item["sentiment_analysis"]
        
        # 情绪表情
        emoji_map = {
            "非常正面": "🚀",
            "正面": "📈", 
            "中性": "➡️",
            "负面": "📉",
            "非常负面": "🔻"
        }
        
        emoji = emoji_map.get(sentiment["sentiment"], "❓")
        
        message += f"{emoji} **{stock['name']}** ({stock['symbol']})\n"
        message += f"💰 {stock['price']:.2f} {stock['currency']}\n"
        message += f"📊 {stock['change_percent']:+.2f}% | {sentiment['sentiment']}\n"
        message += f"📈 区间: {stock.get('low', stock['price']):.2f}-{stock.get('high', stock['price']):.2f}\n"
        message += f"📊 成交量: {stock.get('volume', 0):,.0f}\n\n"
    
    # 添加市场总体分析
    message += "---\n"
    message += "🎯 **市场总体**: "
    
    # 统计情绪
    sentiment_counts = {}
    for item in all_data_with_sentiment:
        sentiment = item["sentiment_analysis"]["sentiment"]
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
    
    # 总体判断
    if sentiment_counts.get("非常正面", 0) >= 2:
        message += "积极乐观，多数股票表现强劲\n"
        message += "💡 **建议**: 可考虑增加仓位"
    elif sentiment_counts.get("正面", 0) >= 2:
        message += "偏乐观，整体趋势向好\n"
        message += "💡 **建议**: 可选择性布局"
    elif sentiment_counts.get("负面", 0) >= 2 or sentiment_counts.get("非常负面", 0) >= 2:
        message += "偏谨慎，多数股票承压\n"
        message += "⚠️ **建议**: 控制风险，谨慎操作"
    else:
        message += "分化明显，个股表现不一\n"
        message += "🤔 **建议**: 精选个股，分散投资"
    
    # 添加底部信息
    message += f"\n\n---\n"
    message += f"⏰ 下次更新: {(datetime.now().timestamp() + 3600):.0f}\n"
    message += f"📁 详细报告: multi_stock_report_*.md\n"
    message += f"🔄 监控状态: ✅ 正常运行"
    
    return message

def save_notification(message):
    """保存通知到文件"""
    try:
        notification_file = f"/home/admin/clawd/latest_multi_stock_notification_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(notification_file, 'w', encoding='utf-8') as f:
            f.write(message)
        
        print(f"✅ 通知已保存到: {notification_file}")
        return notification_file
    except Exception as e:
        print(f"❌ 保存通知失败: {e}")
        return None

def main():
    """主监控函数"""
    print(f"\n{'='*60}")
    print(f"🕐 多股票每小时监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"监控股票: 阿里巴巴(09988.HK)、小米(01810.HK)、比亚迪(002594.SZ)")
    print(f"{'='*60}")
    
    # 创建监控器
    monitor = MultiStockMonitor()
    
    # 获取所有股票数据
    print("📡 获取股票数据...")
    all_stocks_data = monitor.get_all_stocks_data()
    
    if not all_stocks_data:
        error_msg = "❌ 无法获取股票数据"
        print(error_msg)
        save_notification(error_msg)
        return False
    
    print(f"✅ 成功获取 {len(all_stocks_data)}/{len(monitor.stocks)} 只股票")
    
    # 分析每个股票的情绪
    all_data_with_sentiment = []
    for stock_data in all_stocks_data:
        sentiment_analysis = monitor.analyze_sentiment(stock_data)
        all_data_with_sentiment.append({
            "stock_data": stock_data,
            "sentiment_analysis": sentiment_analysis
        })
    
    # 生成综合报告
    print("📝 生成综合报告...")
    comprehensive_report = monitor.generate_comprehensive_report(all_data_with_sentiment)
    
    # 保存报告
    report_file, data_file = monitor.save_reports(all_data_with_sentiment, comprehensive_report)
    
    # 生成WhatsApp消息
    print("📤 生成推送消息...")
    whatsapp_message = generate_whatsapp_message(all_data_with_sentiment)
    
    # 保存通知
    notification_file = save_notification(whatsapp_message)
    
    # 输出摘要
    print(f"\n✅ 监控完成!")
    print(f"   综合报告: {report_file}")
    print(f"   原始数据: {data_file}")
    if notification_file:
        print(f"   通知文件: {notification_file}")
    
    print(f"\n📋 股票摘要:")
    for item in all_data_with_sentiment:
        stock = item["stock_data"]
        sentiment = item["sentiment_analysis"]
        print(f"  {stock['name']}: {stock['price']:.2f} {stock['currency']} ({stock['change_percent']:+.2f}%) - {sentiment['sentiment']}")
    
    print(f"{'='*60}")
    
    # 显示消息预览
    print("\n📄 推送消息预览:")
    print("-"*40)
    print(whatsapp_message[:300] + "..." if len(whatsapp_message) > 300 else whatsapp_message)
    print("-"*40)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
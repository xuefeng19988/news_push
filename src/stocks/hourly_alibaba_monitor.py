#!/usr/bin/env python3
"""
阿里巴巴港股每小时监控脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_stock_monitor import SimpleStockMonitor
from datetime import datetime
import json

def send_whatsapp_notification(message):
    """通过Clawdbot发送WhatsApp通知"""
    try:
        # 这里可以集成Clawdbot的message工具
        # 暂时先保存到文件，由外部cron触发推送
        notification_file = f"/home/admin/clawd/latest_notification_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(notification_file, 'w', encoding='utf-8') as f:
            f.write(message)
        
        print(f"✅ 通知已保存到: {notification_file}")
        return True
    except Exception as e:
        print(f"❌ 发送通知失败: {e}")
        return False

def main():
    """主监控函数"""
    print(f"\n{'='*60}")
    print(f"🕐 阿里巴巴港股每小时监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 创建监控器
    monitor = SimpleStockMonitor()
    
    # 获取数据
    stock_data = monitor.get_stock_data()
    
    if not stock_data:
        error_msg = "❌ 无法获取阿里巴巴港股数据"
        print(error_msg)
        send_whatsapp_notification(error_msg)
        return
    
    # 分析情绪
    sentiment_analysis = monitor.analyze_sentiment(stock_data)
    
    # 生成报告
    report = monitor.generate_report(stock_data, sentiment_analysis)
    
    # 保存报告
    report_file, data_file = monitor.save_report(report, stock_data, sentiment_analysis)
    
    # 创建推送消息
    price = stock_data.get('price', 0)
    change = stock_data.get('change', 0)
    change_percent = stock_data.get('change_percent', 0)
    sentiment = sentiment_analysis.get('sentiment', '未知')
    
    notification = f"""📈 阿里巴巴港股监控报告 ({datetime.now().strftime('%H:%M')})

💰 当前价格: {price:.2f} HKD
📊 今日涨跌: {change:+.2f} HKD ({change_percent:+.2f}%)
🎯 市场情绪: {sentiment}

📋 摘要:
- 最高价: {stock_data.get('high', 0):.2f} HKD
- 最低价: {stock_data.get('low', 0):.2f} HKD  
- 成交量: {stock_data.get('volume', 0):,.0f} 手
- 数据来源: {stock_data.get('source', '未知')}

💡 建议: {sentiment_analysis.get('reason', '数据不足')}

📁 详细报告: {report_file}
🔄 下次更新: {(datetime.now().timestamp() + 3600):.0f}
"""
    
    # 发送通知
    print("\n📤 准备发送通知...")
    send_whatsapp_notification(notification)
    
    # 输出摘要
    print(f"\n✅ 监控完成!")
    print(f"   价格: {price:.2f} HKD")
    print(f"   涨跌: {change:+.2f} ({change_percent:+.2f}%)")
    print(f"   情绪: {sentiment}")
    print(f"   报告: {report_file}")
    print(f"{'='*60}")
    
    # 返回成功
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

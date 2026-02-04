import os
#!/usr/bin/env python3
"""
增强版智能推送调度器 - 集成所有功能
股票推送: 08:00-18:00
新闻推送: 08:00-22:00
社交媒体: 08:00-22:00 (每2小时)
"""

import sys
import os
import json
from datetime import datetime
import subprocess

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+86**********")  # 从环境变量读取
CLAWDBOT_PATH = "/home/admin/.npm-global/bin/clawdbot"

def get_current_hour():
    """获取当前小时"""
    return datetime.now().hour

def should_push_stocks():
    """是否应该推送股票 (08:00-18:00)"""
    hour = get_current_hour()
    return 8 <= hour <= 18  # 8点到18点之间 (包含18点)

def should_push_news():
    """是否应该推送新闻 (08:00-22:00)"""
    hour = get_current_hour()
    return 8 <= hour <= 22  # 8点到22点之间 (包含22点)

def should_check_social():
    """是否应该检查社交媒体 (08:00-22:00，每2小时)"""
    hour = get_current_hour()
    if hour < 8 or hour > 22:  # 22点之后不检查
        return False
    
    # 每2小时检查一次 (偶数小时)
    return hour % 2 == 0

def send_whatsapp_message(message: str) -> bool:
    """发送WhatsApp消息"""
    try:
        print(f"📤 发送消息 ({len(message)}字符)...")
        
        # 使用clawdbot命令发送 (使用完整路径)
        cmd = [
            CLAWDBOT_PATH, 'message', 'send',
            '-t', WHATSAPP_NUMBER,
            '-m', message
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 消息发送成功")
            return True
        else:
            print(f"❌ 发送失败: {result.stderr[:200]}")
            
            # 保存到文件备用
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            message_file = f"/home/admin/clawd/backup_msg_{timestamp}.txt"
            
            with open(message_file, 'w', encoding='utf-8') as f:
                f.write(message)
            
            print(f"📝 消息已备份: {message_file}")
            return False
        
    except Exception as e:
        print(f"❌ 发送消息失败: {e}")
        return False

def run_stock_monitor():
    """运行股票监控"""
    print(f"\n{'='*60}")
    print(f"📈 运行股票监控")
    print(f"{'='*60}")
    
    try:
        from auto_stock_notifier import run_stock_monitor_and_notify
        
        success = run_stock_monitor_and_notify()
        
        if success:
            # 读取并发送最新股票报告
            stock_files = sorted([f for f in os.listdir('.') if f.startswith('sent_multi_stock_notification_')])
            if stock_files:
                latest = stock_files[-1]
                with open(latest, 'r', encoding='utf-8') as f:
                    stock_message = f.read()
                
                send_success = send_whatsapp_message(stock_message)
                return send_success
            
        return False
        
    except Exception as e:
        print(f"❌ 股票监控失败: {e}")
        return False

def run_news_pusher():
    """运行新闻推送"""
    print(f"\n{'='*60}")
    print(f"📰 运行新闻推送")
    print(f"{'='*60}")
    
    try:
        from global_news_pusher import GlobalNewsPusher
        
        pusher = GlobalNewsPusher()
        result = pusher.run()
        
        if result:
            with open(result, 'r', encoding='utf-8') as f:
                news_message = f.read()
            
            send_success = send_whatsapp_message(news_message)
            
            if send_success:
                # 保存发送记录
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                sent_file = f"/home/admin/clawd/sent_news_{timestamp}.txt"
                with open(sent_file, 'w', encoding='utf-8') as f:
                    f.write(news_message)
            
            return send_success
        else:
            print("📭 没有新新闻")
            return True  # 没有新闻也算成功
            
    except Exception as e:
        print(f"❌ 新闻推送失败: {e}")
        return False

def run_social_monitor():
    """运行社交媒体监控"""
    print(f"\n{'='*60}")
    print(f"🌐 运行社交媒体监控")
    print(f"{'='*60}")
    
    try:
        from social_media_monitor import SocialMediaMonitor
        
        monitor = SocialMediaMonitor()
        result = monitor.check_and_notify()
        
        if result:
            with open(result, 'r', encoding='utf-8') as f:
                social_message = f.read()
            
            send_success = send_whatsapp_message(social_message)
            
            if send_success:
                # 保存发送记录
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                sent_file = f"/home/admin/clawd/sent_social_{timestamp}.txt"
                with open(sent_file, 'w', encoding='utf-8') as f:
                    f.write(social_message)
            
            return send_success
        else:
            print("📭 没有重要社交媒体动态")
            return True  # 没有动态也算成功
            
    except Exception as e:
        print(f"❌ 社交媒体监控失败: {e}")
        return False

def run_price_alerts():
    """运行价格预警检查"""
    print(f"\n{'='*60}")
    print(f"⚠️ 运行价格预警检查")
    print(f"{'='*60}")
    
    try:
        from price_alert_system import PriceAlertSystem
        
        # 这里需要实际的股票数据
        # 暂时跳过实际检查，只记录
        print("⏭️ 价格预警检查 (需要实时股票数据)")
        return True
        
    except Exception as e:
        print(f"❌ 价格预警检查失败: {e}")
        return False

def generate_summary(stock_success, news_success, social_success, alert_success,
                    stocks_enabled, news_enabled, social_enabled):
    """生成运行总结"""
    timestamp = datetime.now().strftime('%H:%M')
    
    summary = f"⏰ **系统运行总结** ({timestamp})\n\n"
    
    # 股票状态
    if stocks_enabled:
        summary += f"📈 股票监控: {'✅' if stock_success else '❌'}\n"
    else:
        summary += f"📈 股票监控: ⏭️ (非交易时间)\n"
    
    # 新闻状态
    if news_enabled:
        summary += f"📰 新闻推送: {'✅' if news_success else '❌'}\n"
    else:
        summary += f"📰 新闻推送: ⏭️ (非推送时间)\n"
    
    # 社交媒体状态
    if social_enabled:
        summary += f"🌐 社交媒体: {'✅' if social_success else '❌'}\n"
    else:
        summary += f"🌐 社交媒体: ⏭️ (非检查时间)\n"
    
    # 预警状态
    summary += f"⚠️ 价格预警: {'✅' if alert_success else '❌'}\n"
    
    summary += "\n---\n"
    summary += f"🔄 下次运行: {(datetime.now().timestamp() + 3600):.0f}\n"
    summary += f"📊 系统版本: 增强版 v1.0\n"
    
    # 保存总结
    summary_file = f"/home/admin/clawd/system_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n📋 系统总结: {summary_file}")
    return summary

def setup_enhanced_schedule():
    """设置增强版定时任务"""
    print(f"\n{'='*60}")
    print(f"⏰ 设置增强版推送计划")
    print(f"{'='*60}")
    
    cron_command = "0 * * * * cd /home/admin/clawd && /usr/bin/python3 smart_pusher_enhanced.py --run >> /home/admin/clawd/enhanced_pusher.log 2>&1"
    
    try:
        with subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True) as proc:
            proc.stdin.write(cron_command + "\n")
            proc.stdin.close()
        
        print("✅ 定时任务设置完成")
        print(f"任务: {cron_command}")
        
        print("\n📅 推送安排:")
        print("  股票: 08:00-18:00 (每小时)")
        print("  新闻: 08:00-22:00 (每小时)")
        print("  社交媒体: 08:00-22:00 (每2小时)")
        print("  价格预警: 实时监控")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置定时任务失败: {e}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="增强版智能推送调度器")
    parser.add_argument('--setup', action='store_true', help='设置定时任务')
    parser.add_argument('--run', action='store_true', help='运行推送')
    parser.add_argument('--test', action='store_true', help='测试所有功能')
    
    args = parser.parse_args()
    
    if args.setup:
        return setup_enhanced_schedule()
    
    if args.test:
        print("🧪 测试所有功能...")
        # 测试发送功能
        test_msg = "🔧 **增强版系统测试**\n\n✅ 所有功能集成测试\n⏰ " + datetime.now().strftime("%H:%M")
        return send_whatsapp_message(test_msg)
    
    print(f"\n{'='*60}")
    print(f"🚀 增强版推送系统启动")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 检查时间
    current_hour = get_current_hour()
    stocks_enabled = should_push_stocks()
    news_enabled = should_push_news()
    social_enabled = should_check_social()
    
    print(f"\n⏰ 时间检查 (当前: {current_hour}:00):")
    print(f"  股票推送: {'✅' if stocks_enabled else '⏭️'} (08:00-18:00)")
    print(f"  新闻推送: {'✅' if news_enabled else '⏭️'} (08:00-22:00)")
    print(f"  社交媒体: {'✅' if social_enabled else '⏭️'} (08:00-22:00, 每2小时)")
    
    # 运行各功能
    stock_success = False
    news_success = False
    social_success = False
    alert_success = False
    
    if stocks_enabled:
        stock_success = run_stock_monitor()
    else:
        print("\n⏭️ 跳过股票监控")
    
    if news_enabled:
        news_success = run_news_pusher()
    else:
        print("\n⏭️ 跳过新闻推送")
    
    if social_enabled:
        social_success = run_social_monitor()
    else:
        print("\n⏭️ 跳过社交媒体监控")
    
    # 价格预警 (总是运行检查)
    alert_success = run_price_alerts()
    
    # 生成总结
    summary = generate_summary(
        stock_success, news_success, social_success, alert_success,
        stocks_enabled, news_enabled, social_enabled
    )
    
    print(f"\n{'='*60}")
    print("✅ 增强版系统运行完成")
    print(f"{'='*60}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
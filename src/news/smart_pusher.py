#!/usr/bin/env python3
"""
智能推送调度器 - 根据时间决定推送内容
股票推送: 08:00-18:00
新闻推送: 08:00-22:00
"""

import sys
import os
from datetime import datetime
import subprocess

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_current_hour():
    """获取当前小时"""
    return datetime.now().hour

def should_push_stocks():
    """是否应该推送股票 (08:00-18:00)"""
    hour = get_current_hour()
    return 8 <= hour < 18  # 8点到18点之间

def should_push_news():
    """是否应该推送新闻 (08:00-22:00)"""
    hour = get_current_hour()
    return 8 <= hour < 22  # 8点到22点之间

def run_stock_monitor():
    """运行股票监控"""
    print(f"\n{'='*60}")
    print(f"📈 运行股票监控 - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        # 导入股票监控模块
        from auto_stock_notifier import run_stock_monitor_and_notify
        
        success = run_stock_monitor_and_notify()
        
        if success:
            print("✅ 股票监控完成")
            return True
        else:
            print("❌ 股票监控失败")
            return False
            
    except ImportError as e:
        print(f"❌ 导入股票监控模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 运行股票监控失败: {e}")
        return False

def run_news_pusher():
    """运行新闻推送"""
    print(f"\n{'='*60}")
    print(f"📰 运行新闻推送 - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        # 导入全球新闻推送模块
        from global_news_pusher import GlobalNewsPusher
        
        pusher = GlobalNewsPusher()
        result = pusher.run()
        
        if result:
            print("✅ 全球新闻推送完成")
            
            # 读取新闻消息
            with open(result, 'r', encoding='utf-8') as f:
                news_message = f.read()
            
            # 保存到待发送队列
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            pending_file = f"/home/admin/clawd/pending_news_{timestamp}.txt"
            with open(pending_file, 'w', encoding='utf-8') as f:
                f.write(news_message)
            
            print(f"✅ 新闻已添加到待发送队列: {pending_file}")
            return True
        else:
            print("❌ 新闻推送失败或没有新新闻")
            return False
            
    except ImportError as e:
        print(f"❌ 导入新闻推送模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 运行新闻推送失败: {e}")
        return False

def send_summary_notification(stock_success: bool, news_success: bool, stocks_enabled: bool, news_enabled: bool):
    """发送推送总结通知"""
    timestamp = datetime.now().strftime('%H:%M')
    current_hour = get_current_hour()
    
    summary = f"⏰ **智能推送总结** ({timestamp})\n\n"
    
    # 股票推送状态
    if stocks_enabled:
        if stock_success:
            summary += "✅ **股票监控**: 已完成\n"
            summary += "   - 监控股票: 阿里巴巴、小米、比亚迪\n"
            summary += "   - 数据获取: 实时价格+情绪分析\n"
            summary += "   - 推送状态: WhatsApp消息已准备\n"
        else:
            summary += "❌ **股票监控**: 失败\n"
    else:
        summary += "⏭️ **股票监控**: 已跳过 (非交易时间)\n"
        summary += f"   - 股票推送时间: 08:00-18:00\n"
        summary += f"   - 当前时间: {current_hour}:00\n"
    
    summary += "\n"
    
    # 新闻推送状态
    if news_enabled:
        if news_success:
            summary += "✅ **新闻推送**: 已完成\n"
            summary += "   - 新闻源: 7个全球媒体\n"
            summary += "   - 文章数量: 重要新闻摘要\n"
            summary += "   - 内容过滤: 智能重要性评分\n"
        else:
            summary += "❌ **新闻推送**: 失败\n"
    else:
        summary += "⏭️ **新闻推送**: 已跳过 (非推送时间)\n"
        summary += f"   - 新闻推送时间: 08:00-22:00\n"
        summary += f"   - 当前时间: {current_hour}:00\n"
    
    summary += "\n---\n"
    summary += "📊 **系统状态**:\n"
    summary += f"- 运行时间: {timestamp}\n"
    summary += f"- 当前小时: {current_hour}:00\n"
    summary += f"- 下次推送: {(datetime.now().timestamp() + 3600):.0f}\n"
    summary += "- 日志文件: hourly_pusher.log\n"
    summary += "- 推送频率: 每小时一次\n"
    summary += f"- 股票推送: {'✅ 启用' if stocks_enabled else '⏭️ 暂停'} (08:00-18:00)\n"
    summary += f"- 新闻推送: {'✅ 启用' if news_enabled else '⏭️ 暂停'} (08:00-22:00)\n"
    
    # 保存总结
    summary_file = f"/home/admin/clawd/push_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n📋 推送总结已保存: {summary_file}")
    print(f"\n📄 总结内容:")
    print("-"*40)
    print(summary)
    print("-"*40)
    
    return summary

def setup_smart_schedule():
    """设置智能定时任务"""
    print(f"\n{'='*60}")
    print(f"⏰ 设置智能推送计划 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 创建定时任务命令 (每小时运行一次)
    cron_command = "0 * * * * cd /home/admin/clawd && /usr/bin/python3 smart_pusher.py >> /home/admin/clawd/smart_pusher.log 2>&1"
    
    try:
        # 获取现有crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_crontab = result.stdout
        
        # 移除旧的推送任务
        lines = current_crontab.split('\n')
        new_lines = []
        
        for line in lines:
            if 'hourly_pusher' not in line and 'smart_pusher' not in line:
                new_lines.append(line)
        
        # 添加新任务
        new_lines.append(cron_command)
        new_crontab = '\n'.join(filter(None, new_lines))
        
        # 写入新crontab
        with subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True) as proc:
            proc.stdin.write(new_crontab)
            proc.stdin.close()
        
        print("✅ 智能推送计划设置完成")
        print(f"任务内容: {cron_command}")
        print("\n📅 推送时间安排:")
        print("  - 股票推送: 08:00-18:00 (每小时)")
        print("  - 新闻推送: 08:00-22:00 (每小时)")
        print("  - 其他时间: 仅运行检查，不推送")
        
        # 创建日志文件
        log_file = "/home/admin/clawd/smart_pusher.log"
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"智能推送系统启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
        
        print(f"📝 系统日志: {log_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置定时任务失败: {e}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="智能推送调度器")
    parser.add_argument('--setup', action='store_true', help='设置定时任务')
    parser.add_argument('--run', action='store_true', help='运行推送')
    parser.add_argument('--force-stocks', action='store_true', help='强制运行股票监控')
    parser.add_argument('--force-news', action='store_true', help='强制运行新闻推送')
    
    args = parser.parse_args()
    
    if args.setup:
        return setup_smart_schedule()
    
    print(f"\n{'='*60}")
    print(f"🤖 智能推送系统启动")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 检查当前时间
    current_hour = get_current_hour()
    stocks_enabled = should_push_stocks() or args.force_stocks
    news_enabled = should_push_news() or args.force_news
    
    print(f"\n⏰ 时间检查:")
    print(f"  当前小时: {current_hour}:00")
    print(f"  股票推送: {'✅ 启用' if stocks_enabled else '⏭️ 暂停'} (08:00-18:00)")
    print(f"  新闻推送: {'✅ 启用' if news_enabled else '⏭️ 暂停'} (08:00-22:00)")
    
    stock_success = False
    news_success = False
    
    # 运行股票监控
    if stocks_enabled:
        stock_success = run_stock_monitor()
    else:
        print("\n⏭️  跳过股票监控 (非交易时间)")
    
    # 运行新闻推送
    if news_enabled:
        news_success = run_news_pusher()
    else:
        print("\n⏭️  跳过新闻推送 (非推送时间)")
    
    # 发送总结
    summary = send_summary_notification(stock_success, news_success, stocks_enabled, news_enabled)
    
    # 总体结果
    if (stocks_enabled and stock_success) or (news_enabled and news_success) or (not stocks_enabled and not news_enabled):
        print(f"\n✅ 智能推送系统运行完成")
        return True
    else:
        print(f"\n❌ 智能推送系统运行失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
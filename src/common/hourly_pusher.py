#!/usr/bin/env python3
"""
每小时推送系统 - 整合股票监控和新闻推送
"""

import sys
import os
from datetime import datetime
import subprocess

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
        # 导入新的全球新闻推送模块
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
            pending_file = f"./logs/pending_news_{timestamp}.txt"
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

def setup_hourly_schedule():
    """设置每小时定时任务"""
    print(f"\n{'='*60}")
    print(f"⏰ 设置定时推送计划 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 创建定时任务命令
    cron_command = "0 * * * * cd /home/admin/clawd && /usr/bin/python3 hourly_pusher.py >> /home/admin/clawd/hourly_pusher.log 2>&1"
    
    try:
        # 获取现有crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_crontab = result.stdout
        
        # 移除旧的推送任务
        lines = current_crontab.split('\n')
        new_lines = []
        
        for line in lines:
            if 'auto_stock_notifier' not in line and 'hourly_pusher' not in line:
                new_lines.append(line)
        
        # 添加新任务
        new_lines.append(cron_command)
        new_crontab = '\n'.join(filter(None, new_lines))
        
        # 写入新crontab
        with subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True) as proc:
            proc.stdin.write(new_crontab)
            proc.stdin.close()
        
        print("✅ 定时推送计划设置完成")
        print(f"任务内容: {cron_command}")
        
        # 创建日志文件
        log_file = "./logs/hourly_pusher.log"
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"每小时推送系统启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
        
        print(f"📝 系统日志: {log_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置定时任务失败: {e}")
        return False

def send_summary_notification(stock_success: bool, news_success: bool):
    """发送推送总结通知"""
    timestamp = datetime.now().strftime('%H:%M')
    
    summary = f"⏰ **每小时推送总结** ({timestamp})\n\n"
    
    if stock_success:
        summary += "✅ **股票监控**: 已完成\n"
        summary += "   - 监控股票: 阿里巴巴、小米、比亚迪\n"
        summary += "   - 数据获取: 实时价格+情绪分析\n"
        summary += "   - 推送状态: WhatsApp消息已准备\n"
    else:
        summary += "❌ **股票监控**: 失败\n"
    
    summary += "\n"
    
    if news_success:
        summary += "✅ **新闻推送**: 已完成\n"
        summary += "   - 文章数量: 20-30条重要新闻\n"
        summary += "   - 内容过滤: 避免重复推送\n"
        summary += "   - 分类整理: 按类别分组显示\n"
    else:
        summary += "❌ **新闻推送**: 失败\n"
    
    summary += "\n---\n"
    summary += "📊 **系统状态**:\n"
    summary += f"- 运行时间: {timestamp}\n"
    summary += f"- 下次推送: {(datetime.now().timestamp() + 3600):.0f}\n"
    summary += "- 日志文件: hourly_pusher.log\n"
    summary += "- 监控频率: 每小时一次\n"
    
    # 保存总结
    summary_file = f"./logs/push_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n📋 推送总结已保存: {summary_file}")
    print(f"\n📄 总结内容:")
    print("-"*40)
    print(summary)
    print("-"*40)
    
    return summary

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="每小时推送系统")
    parser.add_argument('--setup', action='store_true', help='设置定时任务')
    parser.add_argument('--run', action='store_true', help='运行推送')
    parser.add_argument('--stocks-only', action='store_true', help='只运行股票监控')
    parser.add_argument('--news-only', action='store_true', help='只运行新闻推送')
    
    args = parser.parse_args()
    
    if args.setup:
        return setup_hourly_schedule()
    
    print(f"\n{'='*60}")
    print(f"🚀 每小时推送系统启动")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    stock_success = False
    news_success = False
    
    # 运行股票监控
    if not args.news_only:
        stock_success = run_stock_monitor()
    else:
        print("⏭️  跳过股票监控 (news-only模式)")
    
    # 运行新闻推送
    if not args.stocks_only:
        news_success = run_news_pusher()
    else:
        print("⏭️  跳过新闻推送 (stocks-only模式)")
    
    # 发送总结
    summary = send_summary_notification(stock_success, news_success)
    
    # 总体结果
    if (args.stocks_only and stock_success) or \
       (args.news_only and news_success) or \
       (not args.stocks_only and not args.news_only and (stock_success or news_success)):
        print(f"\n✅ 推送系统运行完成")
        return True
    else:
        print(f"\n❌ 推送系统运行失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
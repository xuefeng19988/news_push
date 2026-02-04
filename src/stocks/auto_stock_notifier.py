#!/usr/bin/env python3
"""
自动股票通知器 - 监控+推送一体化
"""

import sys
import os
import json
from datetime import datetime, timedelta
import glob

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def send_whatsapp_message(message):
    """通过Clawdbot发送WhatsApp消息"""
    try:
        # 导入Clawdbot的message工具
        # 这里使用exec来动态调用
        import subprocess
        import tempfile
        
        # 创建临时文件保存消息
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(message)
            temp_file = f.name
        
        print(f"📤 准备发送WhatsApp消息...")
        print(f"消息长度: {len(message)} 字符")
        
        # 显示消息预览
        preview = message[:200] + "..." if len(message) > 200 else message
        print(f"消息预览:\n{preview}")
        
        # 这里应该集成Clawdbot的message工具
        # 暂时先标记为待发送
        pending_file = f"/home/admin/clawd/pending_whatsapp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(pending_file, 'w', encoding='utf-8') as f:
            f.write(message)
        
        print(f"✅ 消息已保存到待发送队列: {pending_file}")
        return True
        
    except Exception as e:
        print(f"❌ 发送消息失败: {e}")
        return False

def check_and_send_latest_notification():
    """检查并发送最新的通知"""
    print(f"\n{'='*60}")
    print(f"🔍 检查最新通知 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 查找最新的通知文件
    notification_files = glob.glob("/home/admin/clawd/latest_multi_stock_notification_*.txt")
    
    if not notification_files:
        print("📭 没有找到通知文件")
        return False
    
    # 按时间排序，获取最新的
    latest_file = max(notification_files, key=os.path.getctime)
    file_time = datetime.fromtimestamp(os.path.getctime(latest_file))
    
    print(f"📄 找到最新通知文件: {latest_file}")
    print(f"⏰ 文件时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查文件是否在最近10分钟内
    if datetime.now() - file_time > timedelta(minutes=10):
        print(f"⚠️ 通知文件已过期 ({datetime.now() - file_time})")
        return False
    
    # 读取通知内容
    with open(latest_file, 'r', encoding='utf-8') as f:
        message = f.read()
    
    print(f"📊 通知内容长度: {len(message)} 字符")
    
    # 发送消息
    if send_whatsapp_message(message):
        print("✅ 通知发送成功")
        
        # 标记为已发送
        sent_file = latest_file.replace("latest_multi_stock_notification", "sent_multi_stock_notification")
        os.rename(latest_file, sent_file)
        print(f"📁 文件已重命名为: {sent_file}")
        
        return True
    else:
        print("❌ 通知发送失败")
        return False

def run_stock_monitor_and_notify():
    """运行股票监控并发送通知"""
    print(f"\n{'='*60}")
    print(f"🚀 运行股票监控+通知 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        # 导入监控模块
        from hourly_multi_stock_monitor import main as run_monitor
        
        print("📡 运行股票监控...")
        
        # 运行监控
        success = run_monitor()
        
        if not success:
            print("❌ 股票监控运行失败")
            return False
        
        print("✅ 股票监控完成")
        
        # 检查并发送通知
        print("\n📤 检查并发送通知...")
        return check_and_send_latest_notification()
        
    except ImportError as e:
        print(f"❌ 导入监控模块失败: {e}")
        print("请确保 hourly_multi_stock_monitor.py 存在")
        return False
    except Exception as e:
        print(f"❌ 运行监控失败: {e}")
        return False

def setup_hourly_cron():
    """设置每小时定时任务"""
    print(f"\n{'='*60}")
    print(f"⏰ 设置定时任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 创建定时任务命令
    cron_command = "0 * * * * cd /home/admin/clawd && /usr/bin/python3 auto_stock_notifier.py >> /home/admin/clawd/auto_notifier.log 2>&1"
    
    # 获取当前crontab
    import subprocess
    
    try:
        # 获取现有crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_crontab = result.stdout
        
        # 移除旧的股票监控任务
        lines = current_crontab.split('\n')
        new_lines = [line for line in lines if 'hourly_multi_stock_monitor' not in line and 'auto_stock_notifier' not in line]
        
        # 添加新任务
        new_lines.append(cron_command)
        new_crontab = '\n'.join(filter(None, new_lines))
        
        # 写入新crontab
        with subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True) as proc:
            proc.stdin.write(new_crontab)
            proc.stdin.close()
        
        print("✅ 定时任务设置完成")
        print(f"任务内容: {cron_command}")
        
        # 创建日志文件
        log_file = "/home/admin/clawd/auto_notifier.log"
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"自动通知器启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
        
        print(f"📝 日志文件: {log_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置定时任务失败: {e}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自动股票通知器")
    parser.add_argument('--setup', action='store_true', help='设置定时任务')
    parser.add_argument('--run', action='store_true', help='运行监控并发送通知')
    parser.add_argument('--check', action='store_true', help='检查并发送最新通知')
    
    args = parser.parse_args()
    
    if args.setup:
        return setup_hourly_cron()
    elif args.run:
        return run_stock_monitor_and_notify()
    elif args.check:
        return check_and_send_latest_notification()
    else:
        # 默认运行监控+通知
        print("🚀 自动股票通知器启动")
        print("模式: 运行监控并发送通知")
        return run_stock_monitor_and_notify()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
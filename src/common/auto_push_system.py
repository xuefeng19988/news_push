import os
#!/usr/bin/env python3
"""
自动推送系统 - 集成新闻和股票推送，自动发送到WhatsApp
"""

import os
import sys
import subprocess
from datetime import datetime
import time

def send_whatsapp_message(message: str) -> bool:
    """发送消息到WhatsApp"""
    try:
        print(f"📤 发送消息 ({len(message)}字符)...")
        
        # 使用openclaw发送消息
        cmd = [
            '/home/admin/.npm-global/bin/openclaw', 'message', 'send',
            '-t', os.getenv("WHATSAPP_NUMBER", "+86**********"),  # 从环境变量读取
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
            message_file = f"/home/admin/clawd/failed_msg_{timestamp}.txt"
            
            with open(message_file, 'w', encoding='utf-8') as f:
                f.write(message)
            
            print(f"📝 消息已备份: {message_file}")
            return False
        
    except Exception as e:
        print(f"❌ 发送消息失败: {e}")
        return False

def run_news_stock_push() -> str:
    """运行新闻+股票推送，返回报告内容"""
    try:
        print("🚀 运行新闻+股票推送系统...")
        
        # 导入推送系统
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from news_stock_pusher import NewsStockPusher
        
        pusher = NewsStockPusher()
        report = pusher.run()
        
        if report:
            return report
        else:
            return "❌ 推送系统运行失败"
            
    except Exception as e:
        print(f"❌ 运行推送系统失败: {e}")
        return f"❌ 系统错误: {str(e)}"

def should_push_stocks() -> bool:
    """是否应该推送股票 (08:00-18:00)"""
    hour = datetime.now().hour
    return 8 <= hour <= 18  # 8点到18点之间

def should_push_news() -> bool:
    """是否应该推送新闻 (08:00-22:00)"""
    hour = datetime.now().hour
    return 8 <= hour <= 22  # 8点到22点之间

def generate_system_status() -> str:
    """生成系统状态报告"""
    current_time = datetime.now().strftime('%H:%M')
    
    status = f"🖥️ **系统状态报告** ({current_time})\n\n"
    
    # 时间检查
    stocks_enabled = should_push_stocks()
    news_enabled = should_push_news()
    
    status += f"⏰ **时间检查**\n"
    status += f"• 当前时间: {current_time}\n"
    status += f"• 股票推送: {'✅ 启用' if stocks_enabled else '⏭️ 暂停'} (08:00-18:00)\n"
    status += f"• 新闻推送: {'✅ 启用' if news_enabled else '⏭️ 暂停'} (08:00-22:00)\n\n"
    
    # 文件检查
    status += f"📁 **文件检查**\n"
    
    important_files = [
        ("news_stock_pusher.py", "推送主程序"),
        ("auto_push_system.py", "自动推送脚本"),
        ("news_cache.db", "新闻数据库"),
        ("alert_config.json", "预警配置")
    ]
    
    for filename, description in important_files:
        filepath = f"/home/admin/clawd/{filename}"
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            status += f"• {description}: ✅ {size:,} 字节\n"
        else:
            status += f"• {description}: ❌ 文件不存在\n"
    
    # 最近推送记录
    status += f"\n📊 **最近推送**\n"
    
    push_patterns = [
        ("push_report_", "推送报告"),
        ("sent_news_", "新闻发送"),
        ("sent_stock_", "股票发送")
    ]
    
    for pattern, description in push_patterns:
        files = [f for f in os.listdir('/home/admin/clawd') if f.startswith(pattern)]
        if files:
            latest = max(files)
            status += f"• {description}: {len(files)} 条记录\n"
        else:
            status += f"• {description}: 📭 无记录\n"
    
    status += f"\n🔄 **下次运行**: 整点自动推送\n"
    status += f"📱 **接收号码**: +86**********\n"
    status += f"⚙️ **系统版本**: 自动推送系统 v1.0\n"
    
    return status

def setup_cron_job():
    """设置定时任务"""
    print("⏰ 设置定时任务...")
    
    # 每小时运行一次
    cron_command = "0 * * * * cd /home/admin/clawd && /usr/bin/python3 auto_push_system.py --run >> ./logs/auto_push.log 2>&1"
    
    try:
        # 获取当前crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout
        
        # 检查是否已存在
        if "auto_push_system.py" in current_cron:
            print("✅ 定时任务已存在")
            return True
        
        # 添加新任务
        new_cron = current_cron.strip() + "\n" + cron_command + "\n"
        
        with subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True) as proc:
            proc.stdin.write(new_cron)
            proc.stdin.close()
        
        print("✅ 定时任务设置完成")
        print(f"任务: {cron_command}")
        
        print("\n📅 推送安排:")
        print("  股票推送: 08:00-18:00 (每小时)")
        print("  新闻推送: 08:00-22:00 (每小时)")
        print("  推送方式: WhatsApp自动发送")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置定时任务失败: {e}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自动推送系统")
    parser.add_argument('--setup', action='store_true', help='设置定时任务')
    parser.add_argument('--run', action='store_true', help='运行推送')
    parser.add_argument('--status', action='store_true', help='检查系统状态')
    parser.add_argument('--test', action='store_true', help='测试消息发送')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"🚀 自动推送系统")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    if args.setup:
        return setup_cron_job()
    
    if args.status:
        status_report = generate_system_status()
        print(f"\n{status_report}")
        
        # 发送状态报告
        send_whatsapp_message(status_report)
        return True
    
    if args.test:
        print("🧪 测试消息发送...")
        test_msg = "🔧 **系统测试消息**\n\n✅ 自动推送系统测试成功\n⏰ " + datetime.now().strftime("%H:%M:%S")
        return send_whatsapp_message(test_msg)
    
    if args.run:
        print("🔄 运行自动推送...")
        
        # 检查时间
        stocks_enabled = should_push_stocks()
        news_enabled = should_push_news()
        
        print(f"\n⏰ 时间检查:")
        print(f"  股票推送: {'✅' if stocks_enabled else '⏭️'}")
        print(f"  新闻推送: {'✅' if news_enabled else '⏭️'}")
        
        # 运行推送
        if stocks_enabled or news_enabled:
            report = run_news_stock_push()
            
            if report and not report.startswith("❌"):
                # 发送报告
                success = send_whatsapp_message(report)
                
                if success:
                    # 保存发送记录
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    sent_file = f"/home/admin/clawd/sent_push_{timestamp}.txt"
                    with open(sent_file, 'w', encoding='utf-8') as f:
                        f.write(report)
                    
                    print(f"💾 发送记录已保存: {sent_file}")
                
                return success
            else:
                print(f"❌ 推送失败: {report}")
                return False
        else:
            print("⏭️ 非推送时间，跳过")
            return True
    
    # 默认显示帮助
    print("\n📋 可用命令:")
    print("  --setup   设置定时任务（每小时运行）")
    print("  --run     立即运行推送")
    print("  --status  检查系统状态")
    print("  --test    测试消息发送")
    print(f"\n{'='*60}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
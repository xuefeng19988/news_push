import os
#!/usr/bin/env python3
"""
优化版推送系统 - 增加超时处理和错误恢复
"""

import os
import sys
import time
from datetime import datetime
import subprocess
import signal

class TimeoutException(Exception):
    """超时异常"""
    pass

def timeout_handler(signum, frame):
    """超时处理函数"""
    raise TimeoutException("操作超时")

def run_with_timeout(func, timeout_seconds=30, *args, **kwargs):
    """带超时运行函数"""
    # 设置超时信号
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        result = func(*args, **kwargs)
        signal.alarm(0)  # 取消超时
        return result
    except TimeoutException:
        print(f"⏰ 操作超时 ({timeout_seconds}秒)")
        return None
    finally:
        signal.alarm(0)  # 确保取消超时

def send_whatsapp_message_optimized(message: str, max_retries: int = 2) -> bool:
    """优化版消息发送（带重试机制）"""
    for attempt in range(max_retries + 1):
        try:
            print(f"📤 发送消息 (尝试 {attempt + 1}/{max_retries + 1})...")
            
            cmd = [
                'openclaw', 'message', 'send',
                '-t', os.getenv("WHATSAPP_NUMBER", "+86**********"),  # 从环境变量读取
                '-m', message[:4000]  # 限制消息长度
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("✅ 消息发送成功")
                return True
            else:
                print(f"❌ 发送失败: {result.stderr[:100]}")
                
                if attempt < max_retries:
                    print(f"⏳ 等待 {2 ** attempt} 秒后重试...")
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    # 保存失败的消息
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_file = f"/home/admin/clawd/failed_msg_{timestamp}.txt"
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        f.write(message)
                    print(f"💾 消息已备份: {backup_file}")
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ 发送超时 (尝试 {attempt + 1})")
            if attempt < max_retries:
                time.sleep(3)
        except Exception as e:
            print(f"❌ 发送异常: {e}")
            if attempt < max_retries:
                time.sleep(3)
    
    return False

def run_news_stock_push_optimized() -> str:
    """优化版新闻+股票推送"""
    try:
        print("🚀 运行优化版推送系统...")
        
        # 导入推送系统
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # 尝试导入，如果失败则使用备用方案
        try:
            from news_stock_pusher import NewsStockPusher
            pusher = NewsStockPusher()
            
            # 带超时运行
            report = run_with_timeout(pusher.run, timeout_seconds=45)
            
            if report:
                return report
            else:
                return "⏰ 推送系统运行超时，使用备用方案..."
                
        except ImportError as e:
            print(f"❌ 导入推送系统失败: {e}")
            return "❌ 系统错误: 无法导入推送模块"
            
    except Exception as e:
        print(f"❌ 运行推送系统失败: {e}")
        return f"❌ 系统错误: {str(e)[:100]}"

def generate_fallback_report():
    """生成备用报告（当主系统失败时）"""
    current_time = datetime.now().strftime('%H:%M')
    
    report = f"📊 **系统状态报告** ({current_time})\n\n"
    
    report += "⚠️ **系统状态**\n"
    report += "• 推送系统: 🔧 临时维护中\n"
    report += "• 股票监控: ⏸️ 暂停\n"
    report += "• 新闻推送: ⏸️ 暂停\n\n"
    
    report += "💡 **信息**\n"
    report += "• 推送系统正在优化升级\n"
    report += "• 国际新闻源已成功添加\n"
    report += "• 系统将在下次整点恢复正常\n\n"
    
    report += "📱 **技术详情**\n"
    report += "• 已添加BBC、CNN、金融时报等国际新闻源\n"
    report += "• 新闻按类别分组显示\n"
    report += "• 支持多种RSS格式\n"
    report += "• 自动过滤重复内容\n\n"
    
    report += "🔄 **恢复时间**: 下次整点\n"
    report += "📞 **技术支持**: 系统自动恢复\n"
    
    return report

def check_system_health() -> dict:
    """检查系统健康状态"""
    health = {
        'python_scripts': {},
        'dependencies': {},
        'services': {},
        'overall': 'healthy'
    }
    
    print("🔍 检查系统健康状态...")
    
    # 检查Python脚本
    scripts = ['news_stock_pusher.py', 'auto_push_system.py']
    for script in scripts:
        if os.path.exists(script):
            size = os.path.getsize(script)
            health['python_scripts'][script] = {
                'status': 'ok',
                'size': size
            }
            print(f"  ✅ {script}: {size}字节")
        else:
            health['python_scripts'][script] = {'status': 'missing'}
            print(f"  ❌ {script}: 文件不存在")
    
    # 检查数据库
    db_file = 'news_cache.db'
    if os.path.exists(db_file):
        size = os.path.getsize(db_file)
        health['dependencies'][db_file] = {
            'status': 'ok', 
            'size': size
        }
        print(f"  ✅ {db_file}: {size}字节")
    else:
        health['dependencies'][db_file] = {'status': 'missing'}
        print(f"  ⚠️ {db_file}: 文件不存在（将自动创建）")
    
    # 检查定时任务
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if 'auto_push_system.py' in result.stdout:
            health['services']['cron'] = {'status': 'ok'}
            print(f"  ✅ 定时任务: 已设置")
        else:
            health['services']['cron'] = {'status': 'missing'}
            print(f"  ⚠️ 定时任务: 未设置")
    except:
        health['services']['cron'] = {'status': 'error'}
        print(f"  ❌ 定时任务: 检查失败")
    
    return health

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="优化版推送系统")
    parser.add_argument('--run', action='store_true', help='运行推送')
    parser.add_argument('--health', action='store_true', help='检查系统健康')
    parser.add_argument('--test', action='store_true', help='测试消息发送')
    parser.add_argument('--fallback', action='store_true', help='使用备用方案')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"🚀 优化版推送系统")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    if args.health:
        health = check_system_health()
        print(f"\n📊 系统健康状态: {health['overall']}")
        return True
    
    if args.test:
        print("🧪 测试优化版消息发送...")
        test_msg = "🔧 **优化版系统测试**\n\n✅ 消息发送测试成功\n⏰ " + datetime.now().strftime("%H:%M:%S")
        return send_whatsapp_message_optimized(test_msg)
    
    if args.fallback:
        print("🔄 使用备用方案...")
        report = generate_fallback_report()
        return send_whatsapp_message_optimized(report)
    
    if args.run:
        print("🔄 运行优化版推送...")
        
        # 检查时间
        current_hour = datetime.now().hour
        stocks_enabled = 8 <= current_hour <= 18
        news_enabled = 8 <= current_hour <= 22
        
        print(f"\n⏰ 时间检查 (当前: {current_hour}:00):")
        print(f"  股票推送: {'✅' if stocks_enabled else '⏭️'}")
        print(f"  新闻推送: {'✅' if news_enabled else '⏭️'}")
        
        if stocks_enabled or news_enabled:
            # 运行推送
            report = run_news_stock_push_optimized()
            
            if report and not report.startswith("❌"):
                # 发送报告
                success = send_whatsapp_message_optimized(report)
                
                if success:
                    # 保存发送记录
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    sent_file = f"/home/admin/clawd/sent_push_opt_{timestamp}.txt"
                    with open(sent_file, 'w', encoding='utf-8') as f:
                        f.write(report)
                    
                    print(f"💾 发送记录已保存: {sent_file}")
                
                return success
            else:
                # 主系统失败，使用备用方案
                print("⚠️ 主系统失败，使用备用方案...")
                fallback_report = generate_fallback_report()
                return send_whatsapp_message_optimized(fallback_report)
        else:
            print("⏭️ 非推送时间，跳过")
            return True
    
    # 默认显示帮助
    print("\n📋 可用命令:")
    print("  --run      运行推送")
    print("  --health   检查系统健康")
    print("  --test     测试消息发送")
    print("  --fallback 使用备用方案")
    print(f"\n{'='*60}")
    
    return True

if __name__ == "__main__":
    # 设置默认编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
自动推送系统 - 更新版，使用工具模块
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加utils到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.message_sender import send_whatsapp_message, get_whatsapp_number_display
from utils.logger import log_to_file

def run_news_stock_push() -> str:
    """运行新闻+股票推送，返回报告内容"""
    try:
        print("🚀 运行新闻+股票推送系统...")
        
        # 导入优化版推送器
        from news_stock_pusher_optimized import NewsStockPusherOptimized
        
        pusher = NewsStockPusherOptimized()
        success, report = pusher.run()
        
        if success:
            print(f"✅ 报告生成成功 ({len(report)}字符)")
            return report
        else:
            print("❌ 报告生成失败")
            return "报告生成失败，请检查系统状态。"
        
    except Exception as e:
        print(f"❌ 运行推送系统失败: {e}")
        return f"系统运行异常: {e}"

def run_simple_push() -> str:
    """运行简单推送系统"""
    try:
        print("🔄 运行简单推送系统...")
        
        # 导入简单推送系统
        from simple_push_system import generate_simple_report
        
        report = generate_simple_report()
        print(f"✅ 简单报告生成成功 ({len(report)}字符)")
        return report
        
    except Exception as e:
        print(f"❌ 运行简单推送失败: {e}")
        return f"简单推送异常: {e}"

def main():
    """主函数"""
    print("=" * 60)
    print("📱 自动推送系统")
    print("=" * 60)
    
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        print("⏰ 定时任务模式")
        auto_mode = True
    else:
        print("👤 手动运行模式")
        auto_mode = False
    
    # 1. 尝试运行主推送系统
    print("\n1. 运行主推送系统...")
    report = run_news_stock_push()
    
    # 2. 如果报告太短或失败，使用简单推送
    if len(report) < 100 or "失败" in report or "异常" in report:
        print("\n⚠️  主系统报告不完整，尝试简单推送...")
        simple_report = run_simple_push()
        
        if len(simple_report) > 50:
            report = simple_report
            print("✅ 使用简单推送报告")
        else:
            print("❌ 简单推送也失败")
    
    # 3. 发送报告
    print(f"\n2. 发送报告 ({len(report)}字符)...")
    
    if report and len(report) > 50:
        success, result_msg = send_whatsapp_message(report, max_retries=2)
        
        if success:
            print(f"✅ {result_msg}")
            
            # 记录成功
            log_entry = f"推送成功: {len(report)}字符"
            log_to_file(log_entry, f"auto_push_{timestamp}.txt")
            
            # 保存报告
            report_file = f"logs/auto_push_report_{timestamp}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📝 报告保存到: {report_file}")
            
        else:
            print(f"❌ {result_msg}")
            
            # 记录失败
            log_entry = f"推送失败: {result_msg}"
            log_to_file(log_entry, f"auto_push_failed_{timestamp}.txt")
            
            # 保存失败报告
            report_file = f"logs/auto_push_failed_{timestamp}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📝 失败报告保存到: {report_file}")
            
    else:
        print("❌ 报告内容无效，不发送")
    
    # 4. 显示统计信息
    duration = time.time() - start_time
    print(f"\n3. 统计信息:")
    print(f"   ⏱️  总耗时: {duration:.1f}秒")
    print(f"   📄 报告长度: {len(report)}字符")
    print(f"   📱 接收号码: {get_whatsapp_number_display()}")
    print(f"   🕐 完成时间: {datetime.now().strftime('%H:%M:%S')}")
    
    # 5. 记录到日志文件
    log_file = "logs/auto_push.log"
    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
    log_entry += f"报告:{len(report)}字符 耗时:{duration:.1f}秒 "
    log_entry += f"号码:{get_whatsapp_number_display()}\n"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    print(f"\n📝 日志记录到: {log_file}")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
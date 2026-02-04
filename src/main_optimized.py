#!/usr/bin/env python3
"""
优化版主入口文件
统一管理所有推送系统
"""

import os
import sys
import argparse
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.news_stock_pusher_optimized import NewsStockPusherOptimized
from common.auto_push_system import main as auto_push_main
from common.simple_push_system import main as simple_push_main
from common.optimized_push_system import main as optimized_push_main
from utils.config import ConfigManager
from utils.logger import Logger

def run_news_stock_pusher():
    """运行新闻+股票推送器"""
    print("🚀 运行新闻+股票推送器")
    print("=" * 50)
    
    pusher = NewsStockPusherOptimized()
    return pusher.run_and_send()

def run_auto_push_system():
    """运行自动推送系统"""
    print("🚀 运行自动推送系统")
    print("=" * 50)
    
    # 解析命令行参数
    sys.argv = ["auto_push_system.py", "--run"]
    return auto_push_main()

def run_simple_push_system():
    """运行简单推送系统"""
    print("🚀 运行简单推送系统")
    print("=" * 50)
    
    # 解析命令行参数
    sys.argv = ["simple_push_system.py", "--run"]
    return simple_push_main()

def run_optimized_push_system():
    """运行优化推送系统"""
    print("🚀 运行优化推送系统")
    print("=" * 50)
    
    # 解析命令行参数
    sys.argv = ["optimized_push_system.py", "--run"]
    return optimized_push_main()

def show_system_status():
    """显示系统状态"""
    print("📊 系统状态概览")
    print("=" * 50)
    
    config_mgr = ConfigManager()
    env_config = config_mgr.get_env_config()
    
    print("🔧 环境配置:")
    for key, value in env_config.items():
        print(f"  {key}: {value}")
    
    print("\n📁 配置文件:")
    config_files = ["alert_config.json", "social_config.json", "clawdbot_stock_config.json"]
    for config_file in config_files:
        valid, errors = config_mgr.validate_config(config_file)
        status = "✅ 有效" if valid else "❌ 无效"
        print(f"  {config_file}: {status}")
        if errors:
            print(f"    错误: {', '.join(errors)}")
    
    print(f"\n⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📱 WhatsApp号码: {env_config['WHATSAPP_NUMBER'][:6]}******")
    
    # 检查推送时间
    current_hour = datetime.now().hour
    stock_start = int(env_config.get("STOCK_PUSH_START", "8"))
    stock_end = int(env_config.get("STOCK_PUSH_END", "18"))
    news_start = int(env_config.get("NEWS_PUSH_START", "8"))
    news_end = int(env_config.get("NEWS_PUSH_END", "22"))
    
    print(f"\n⏰ 推送时间:")
    print(f"  股票推送: {stock_start:02d}:00 - {stock_end:02d}:00")
    print(f"  新闻推送: {news_start:02d}:00 - {news_end:02d}:00")
    print(f"  当前小时: {current_hour:02d}:00")
    print(f"  应该推送股票: {'✅' if stock_start <= current_hour < stock_end else '❌'}")
    print(f"  应该推送新闻: {'✅' if news_start <= current_hour < news_end else '❌'}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="优化版新闻推送系统")
    parser.add_argument("--mode", choices=["news-stock", "auto", "simple", "optimized", "status"], 
                       default="news-stock", help="运行模式")
    parser.add_argument("--test", action="store_true", help="测试模式")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📱 优化版新闻推送系统")
    print("=" * 60)
    
    if args.mode == "status":
        show_system_status()
        return 0
    
    if args.test:
        print("🧪 测试模式")
        print("=" * 50)
        
        # 运行所有系统进行测试
        results = []
        
        print("\n1. 测试新闻+股票推送器...")
        results.append(("新闻+股票推送器", run_news_stock_pusher()))
        
        print("\n2. 测试自动推送系统...")
        results.append(("自动推送系统", run_auto_push_system()))
        
        print("\n3. 测试简单推送系统...")
        results.append(("简单推送系统", run_simple_push_system()))
        
        print("\n4. 测试优化推送系统...")
        results.append(("优化推送系统", run_optimized_push_system()))
        
        print("\n📊 测试结果:")
        print("=" * 50)
        for name, success in results:
            status = "✅ 成功" if success else "❌ 失败"
            print(f"{name}: {status}")
        
        return 0
    
    # 正常模式
    if args.mode == "news-stock":
        return 0 if run_news_stock_pusher() else 1
    elif args.mode == "auto":
        return run_auto_push_system()
    elif args.mode == "simple":
        return run_simple_push_system()
    elif args.mode == "optimized":
        return run_optimized_push_system()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
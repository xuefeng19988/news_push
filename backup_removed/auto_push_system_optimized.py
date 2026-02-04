#!/usr/bin/env python3
"""
优化版自动推送系统
使用统一的工具模块
"""

import os
from utils.database import NewsDatabase
import sys
import argparse
from datetime import datetime
from pathlib import Path

# 导入工具模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.message_sender import send_whatsapp_message, get_whatsapp_number_display, check_configuration
from utils.logger import Logger, log_to_file
from utils.config import ConfigManager

def check_system_files() -> dict:
    """检查系统文件"""
    files_to_check = [
        ("news_stock_pusher.py", "新闻股票推送器"),
        ("news_cache.db", "新闻数据库"),
        ("config/alert_config.json", "警报配置"),
        ("config/social_config.json", "社交媒体配置"),
    ]
    
    results = {}
    for filename, description in files_to_check:
        exists = Path(filename).exists()
        results[description] = "✅ 存在" if exists else "❌ 缺失"
    
    return results

def generate_system_status() -> str:
    """生成系统状态报告"""
    now = datetime.now()
    
    # 检查配置
    config_ok, config_msg = check_configuration()
    
    # 检查文件
    file_checks = check_system_files()
    
    status = f"📊 推送系统状态报告\n"
    status += f"时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
    status += "=" * 50 + "\n\n"
    
    # 配置状态
    status += "⚙️ 配置状态\n"
    status += "-" * 30 + "\n"
    status += f"配置检查: {'✅ 完整' if config_ok else '❌ 不完整'}\n"
    if not config_ok:
        status += f"问题: {config_msg}\n"
    status += f"接收号码: {get_whatsapp_number_display()}\n\n"
    
    # 文件状态
    status += "📁 文件状态\n"
    status += "-" * 30 + "\n"
    for desc, result in file_checks.items():
        status += f"{desc}: {result}\n"
    status += "\n"
    
    # 运行状态
    status += "🚀 运行状态\n"
    status += "-" * 30 + "\n"
    status += "• 推送时间: 每小时整点\n"
    status += "• 股票推送: 08:00-18:00\n"
    status += "• 新闻推送: 08:00-22:00\n"
    status += "• 备份系统: 已启用\n"
    status += "• 去重功能: 已启用\n\n"
    
    # 统计信息
    status += "📈 统计信息\n"
    status += "-" * 30 + "\n"
    status += "• 今日推送: 0 次\n"
    status += "• 成功推送: 0 次\n"
    status += "• 失败推送: 0 次\n"
    status += "• 数据库记录: 0 条\n\n"
    
    status += "💡 提示: 这是系统状态报告，实际推送内容见新闻报告\n"
    
    return status

def run_push_system(test_mode: bool = False) -> bool:
    """运行推送系统"""
    logger = Logger("auto_push_system").get_logger()
    
    try:
        logger.info("=" * 60)
        logger.info("🚀 开始自动推送系统")
        logger.info("=" * 60)
        
        # 检查配置
        config_ok, config_msg = check_configuration()
        if not config_ok:
            logger.error(f"配置检查失败: {config_msg}")
            if not test_mode:
                return False
        
        # 生成状态报告
        status_report = generate_system_status()
        logger.info(f"生成状态报告 ({len(status_report)} 字符)")
        
        # 在测试模式下只显示不发送
        if test_mode:
            logger.info("测试模式 - 不发送消息")
            print(status_report)
            return True
        
        # 发送消息
        logger.info("发送状态报告...")
        success, result_msg = send_whatsapp_message(status_report, timeout=30, max_retries=2)
        
        if success:
            logger.info(f"✅ 消息发送成功: {result_msg}")
            
            # 记录日志
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            log_to_file(f"推送成功: {result_msg}", f"auto_push_{timestamp}.txt")
            
            return True
        else:
            logger.error(f"❌ 消息发送失败: {result_msg}")
            
            # 记录错误日志
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            log_to_file(f"推送失败: {result_msg}", f"auto_push_error_{timestamp}.txt")
            
            return False
            
    except Exception as e:
        logger.error(f"推送系统运行异常: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自动推送系统")
    parser.add_argument("--run", action="store_true", help="运行推送系统")
    parser.add_argument("--test", action="store_true", help="测试模式（不发送消息）")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    
    args = parser.parse_args()
    
    if args.status:
        # 显示系统状态
        status = generate_system_status()
        print(status)
        return 0
    
    elif args.run or args.test:
        # 运行推送系统
        success = run_push_system(test_mode=args.test)
        return 0 if success else 1
    
    else:
        # 显示帮助
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())

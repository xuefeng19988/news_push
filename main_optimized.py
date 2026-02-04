#!/usr/bin/env python3
"""
统一的主程序 - 新闻推送系统
整合所有功能，消除重复代码
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.message_sender import send_whatsapp_message, get_whatsapp_number_display, check_configuration
from utils.logger import Logger, setup_logger
from utils.config import ConfigManager
from utils.database import NewsDatabase
from common.news_stock_pusher_optimized import NewsStockPusherOptimized

class UnifiedNewsSystem:
    """统一的新闻系统"""
    
    def __init__(self):
        self.logger = setup_logger("unified_news_system")
        self.config_mgr = ConfigManager()
        self.db = NewsDatabase()
        
        self.logger.info("统一新闻系统初始化完成")
    
    def run_news_push(self) -> bool:
        """运行新闻推送"""
        try:
            self.logger.info("开始新闻推送")
            
            # 创建推送器
            pusher = NewsStockPusherOptimized()
            
            # 生成报告
            report = pusher.generate_full_report()
            self.logger.info(f"生成报告 ({len(report)} 字符)")
            
            # 发送报告
            success, result_msg = send_whatsapp_message(report, timeout=30, max_retries=2)
            
            if success:
                self.logger.info(f"✅ 新闻推送成功: {result_msg}")
                
                # 保存报告
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                report_file = f"./logs/news_report_{timestamp}.txt"
                
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(report)
                
                self.logger.info(f"报告已保存: {report_file}")
                return True
            else:
                self.logger.error(f"❌ 新闻推送失败: {result_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"新闻推送异常: {e}")
            return False
    
    def run_stock_push(self) -> bool:
        """运行股票推送"""
        try:
            self.logger.info("开始股票推送")
            
            # 创建推送器
            pusher = NewsStockPusherOptimized()
            
            # 获取股票数据
            stocks_data = pusher.get_all_stocks_data()
            
            # 生成股票报告
            stock_report = pusher.format_stock_section(stocks_data)
            
            # 添加标题和时间
            now = datetime.now()
            full_report = f"📈 股票推送报告\n时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n{stock_report}"
            
            self.logger.info(f"生成股票报告 ({len(full_report)} 字符)")
            
            # 发送报告
            success, result_msg = send_whatsapp_message(full_report, timeout=30, max_retries=2)
            
            if success:
                self.logger.info(f"✅ 股票推送成功: {result_msg}")
                return True
            else:
                self.logger.error(f"❌ 股票推送失败: {result_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"股票推送异常: {e}")
            return False
    
    def run_simple_push(self) -> bool:
        """运行简单推送（备份系统）"""
        try:
            self.logger.info("开始简单推送")
            
            now = datetime.now()
            
            # 生成简单报告
            report = f"""📊 新闻推送系统 - 备份报告
时间: {now.strftime('%Y-%m-%d %H:%M:%S')}

📱 状态: 备份系统运行正常
⚡ 功能: 确保每小时都有推送
🔧 系统: 简单推送保障

📝 说明:
这是备份系统的测试消息，确保推送通道正常工作。
主系统可能暂时不可用，但推送服务仍在运行。

⏰ 下次推送: 整点时刻
📈 监控: 系统持续运行中

---
💡 提示: 这是自动生成的备份消息
"""
            
            self.logger.info(f"生成简单报告 ({len(report)} 字符)")
            
            # 发送报告
            success, result_msg = send_whatsapp_message(report, timeout=30, max_retries=2)
            
            if success:
                self.logger.info(f"✅ 简单推送成功: {result_msg}")
                return True
            else:
                self.logger.error(f"❌ 简单推送失败: {result_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"简单推送异常: {e}")
            return False
    
    def show_system_status(self):
        """显示系统状态"""
        now = datetime.now()
        
        # 检查配置
        config_ok, config_msg = check_configuration()
        
        # 获取数据库统计
        db_stats = self.db.get_stats()
        
        status = f"📊 统一新闻系统状态\n"
        status += f"时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        status += "=" * 60 + "\n\n"
        
        # 系统信息
        status += "🏗️ 系统信息\n"
        status += "-" * 30 + "\n"
        status += f"• 版本: 统一优化版 v1.0\n"
        status += f"• 模式: 整合所有功能\n"
        status += f"• 配置: {'✅ 完整' if config_ok else '❌ 不完整'}\n"
        if not config_ok:
            status += f"  问题: {config_msg}\n"
        status += f"• 接收号码: {get_whatsapp_number_display()}\n\n"
        
        # 数据库信息
        status += "🗄️ 数据库信息\n"
        status += "-" * 30 + "\n"
        status += f"• 总文章数: {db_stats.get('total_articles', 0)}\n"
        status += f"• 24小时内: {db_stats.get('last_24h', 0)}\n"
        
        sources = db_stats.get('by_source', {})
        if sources:
            status += f"• 来源分布:\n"
            for source, count in list(sources.items())[:5]:  # 显示前5个
                status += f"  - {source}: {count}\n"
        status += "\n"
        
        # 功能状态
        status += "⚡ 功能状态\n"
        status += "-" * 30 + "\n"
        status += "• 新闻推送: ✅ 可用\n"
        status += "• 股票推送: ✅ 可用\n"
        status += "• 简单推送: ✅ 可用\n"
        status += "• 去重功能: ✅ 启用\n"
        status += "• 自动清理: ✅ 启用\n\n"
        
        # 推送计划
        status += "⏰ 推送计划\n"
        status += "-" * 30 + "\n"
        status += "• 新闻推送: 08:00-22:00 每小时\n"
        status += "• 股票推送: 08:00-18:00 每小时\n"
        status += "• 备份推送: 全天每小时\n\n"
        
        status += "🚀 使用命令:\n"
        status += "  python main_optimized.py --news     # 运行新闻推送\n"
        status += "  python main_optimized.py --stock    # 运行股票推送\n"
        status += "  python main_optimized.py --simple   # 运行简单推送\n"
        status += "  python main_optimized.py --status   # 显示系统状态\n"
        
        return status

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="统一新闻推送系统")
    parser.add_argument("--news", action="store_true", help="运行新闻推送")
    parser.add_argument("--stock", action="store_true", help="运行股票推送")
    parser.add_argument("--simple", action="store_true", help="运行简单推送（备份）")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    parser.add_argument("--test", action="store_true", help="测试模式（不发送消息）")
    
    args = parser.parse_args()
    
    # 创建系统实例
    system = UnifiedNewsSystem()
    
    if args.status:
        # 显示系统状态
        status = system.show_system_status()
        print(status)
        return 0
    
    elif args.news:
        # 运行新闻推送
        success = system.run_news_push()
        return 0 if success else 1
    
    elif args.stock:
        # 运行股票推送
        success = system.run_stock_push()
        return 0 if success else 1
    
    elif args.simple:
        # 运行简单推送
        success = system.run_simple_push()
        return 0 if success else 1
    
    else:
        # 显示帮助
        parser.print_help()
        print("\n📋 系统状态:")
        status = system.show_system_status()
        print(status[:500] + "..." if len(status) > 500 else status)
        return 0

if __name__ == "__main__":
    sys.exit(main())

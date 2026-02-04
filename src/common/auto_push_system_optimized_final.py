#!/usr/bin/env python3
"""
优化版自动推送系统
使用工具模块消除重复代码
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 导入工具模块
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.config import ConfigManager, load_env_config
from utils.logger import Logger, log_to_file
from utils.database import NewsDatabase
from .base_pusher import BasePusher
from .news_stock_pusher_optimized import NewsStockPusherOptimized

class AutoPushSystemOptimized(BasePusher):
    """优化版自动推送系统"""
    
    def __init__(self):
        """初始化推送系统"""
        super().__init__("AutoPushSystem")
        
        # 加载配置
        self.config_mgr = ConfigManager()
        self.env_config = load_env_config()
        
        # 初始化新闻股票推送器
        self.news_stock_pusher = NewsStockPusherOptimized()
        
        # 文件路径
        self.log_dir = Path("./logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger.info("优化版自动推送系统初始化完成")
    
    def check_system_status(self) -> dict:
        """
        检查系统状态
        
        Returns:
            系统状态字典
        """
        status = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system": "优化版新闻推送系统",
            "status": "运行正常",
            "components": {}
        }
        
        # 检查数据库
        try:
            db = NewsDatabase()
            stats = db.get_stats()
            status["components"]["database"] = {
                "status": "正常",
                "articles": stats.get("total_articles", 0),
                "last_24h": stats.get("last_24h", 0)
            }
        except Exception as e:
            status["components"]["database"] = {
                "status": "异常",
                "error": str(e)
            }
        
        # 检查配置
        env_config = self.env_config
        status["components"]["config"] = {
            "whatsapp_configured": env_config["WHATSAPP_NUMBER"] != "+86**********",
            "openclaw_exists": os.path.exists(env_config["OPENCLAW_PATH"]),
            "push_hours": {
                "stocks": f"{env_config.get('STOCK_PUSH_START', '8')}:00-{env_config.get('STOCK_PUSH_END', '18')}:00",
                "news": f"{env_config.get('NEWS_PUSH_START', '8')}:00-{env_config.get('NEWS_PUSH_END', '22')}:00"
            }
        }
        
        # 检查推送时间
        status["components"]["schedule"] = {
            "should_push_stocks": self.should_push_stocks(),
            "should_push_news": self.should_push_news(),
            "current_hour": datetime.now().hour
        }
        
        return status
    
    def generate_status_report(self) -> str:
        """
        生成状态报告
        
        Returns:
            状态报告字符串
        """
        status = self.check_system_status()
        
        report = [
            "📊 系统状态报告",
            "=" * 40,
            f"时间: {status['timestamp']}",
            f"系统: {status['system']}",
            f"状态: {status['status']}",
            "",
            "🔧 组件状态:"
        ]
        
        # 数据库状态
        db_status = status["components"]["database"]
        if db_status["status"] == "正常":
            report.append(f"  🗄️ 数据库: ✅ 正常 ({db_status['articles']}篇文章, 最近24小时: {db_status['last_24h']})")
        else:
            report.append(f"  🗄️ 数据库: ❌ 异常 ({db_status.get('error', '未知错误')})")
        
        # 配置状态
        config_status = status["components"]["config"]
        report.append(f"  ⚙️ 配置:")
        report.append(f"    • WhatsApp: {'✅ 已配置' if config_status['whatsapp_configured'] else '❌ 未配置'}")
        report.append(f"    • OpenClaw: {'✅ 存在' if config_status['openclaw_exists'] else '❌ 不存在'}")
        report.append(f"    • 股票推送: {config_status['push_hours']['stocks']}")
        report.append(f"    • 新闻推送: {config_status['push_hours']['news']}")
        
        # 推送状态
        schedule_status = status["components"]["schedule"]
        report.append(f"  ⏰ 推送状态:")
        report.append(f"    • 当前小时: {schedule_status['current_hour']}:00")
        report.append(f"    • 推送股票: {'✅ 是' if schedule_status['should_push_stocks'] else '❌ 否'}")
        report.append(f"    • 推送新闻: {'✅ 是' if schedule_status['should_push_news'] else '❌ 否'}")
        
        report.append("")
        report.append("💡 提示: 系统每小时自动运行一次")
        
        return "\n".join(report)
    
    def run_push(self) -> tuple[bool, str]:
        """
        运行推送
        
        Returns:
            Tuple[是否成功, 结果消息]
        """
        start_time = time.time()
        self.logger.info("开始运行推送")
        
        try:
            # 运行新闻股票推送器
            success = self.news_stock_pusher.run_and_send()
            
            duration = time.time() - start_time
            result_msg = f"推送{'成功' if success else '失败'}, 耗时: {self.format_duration(duration)}"
            
            self.logger.info(result_msg)
            return success, result_msg
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"推送异常: {e}, 耗时: {self.format_duration(duration)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def run_test(self) -> bool:
        """
        运行测试
        
        Returns:
            测试是否成功
        """
        self.logger.info("运行系统测试")
        
        # 生成状态报告
        status_report = self.generate_status_report()
        print(status_report)
        
        # 保存状态报告
        timestamp = self.generate_timestamp()
        status_file = self.log_dir / f"system_status_{timestamp}.txt"
        self.save_to_file(status_report, str(status_file))
        
        # 测试消息发送
        test_message = f"🔧 系统测试消息\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n状态: 测试运行中"
        
        self.logger.info("发送测试消息...")
        success, result_msg = self.send_message(test_message)
        
        if success:
            self.logger.info("测试消息发送成功")
            print("✅ 系统测试完成")
            return True
        else:
            self.logger.error(f"测试消息发送失败: {result_msg}")
            print(f"❌ 系统测试失败: {result_msg}")
            return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="优化版自动推送系统")
    parser.add_argument("--run", action="store_true", help="运行推送")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    parser.add_argument("--test", action="store_true", help="运行测试")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 优化版自动推送系统")
    print("=" * 60)
    
    system = AutoPushSystemOptimized()
    
    if args.status:
        # 显示状态
        report = system.generate_status_report()
        print(report)
        
        # 保存状态报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        system.save_to_file(report, f"system_status_{timestamp}.txt")
        
        return 0
    
    elif args.test:
        # 运行测试
        success = system.run_test()
        return 0 if success else 1
    
    elif args.run:
        # 运行推送
        print("开始推送...")
        success, result_msg = system.run_push()
        
        print(f"\n推送结果: {'✅ 成功' if success else '❌ 失败'}")
        print(f"详细信息: {result_msg}")
        
        # 记录结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_entry = f"[{timestamp}] 推送{'成功' if success else '失败'}: {result_msg}\n"
        log_to_file(log_entry, "auto_push.log")
        
        return 0 if success else 1
    
    else:
        # 默认显示帮助
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
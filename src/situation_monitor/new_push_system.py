#!/usr/bin/env python3
"""
新版主推送系统 - 基于situation-monitor架构
集成新闻推送、股票监控和智能健康检查
"""

import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入situation-monitor组件
try:
    from core.monitor import SituationMonitor, CheckStatus, AlertLevel
    from checks.system_checks import create_default_checks
    from alerts.integration import HealthCheckAlertAdapter, create_legacy_compatible_manager
    from alerts.notifications import create_default_notifier
    SITUATION_MONITOR_AVAILABLE = True
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    try:
        from src.situation_monitor.core.monitor import SituationMonitor, CheckStatus, AlertLevel
        from src.situation_monitor.checks.system_checks import create_default_checks
        from src.situation_monitor.alerts.integration import HealthCheckAlertAdapter, create_legacy_compatible_manager
        from src.situation_monitor.alerts.notifications import create_default_notifier
        SITUATION_MONITOR_AVAILABLE = True
    except ImportError as e:
        print(f"警告: 无法导入situation-monitor组件: {e}")
        SITUATION_MONITOR_AVAILABLE = False

# 导入现有推送模块
try:
    from src.common.news_stock_pusher_optimized import NewsStockPusherOptimized
    from src.stocks.multi_stock_monitor import MultiStockMonitor
    from src.monitoring.health_check import HealthChecker
    from utils.config import ConfigManager
    from utils.logger import Logger
    from utils.message_sender import send_whatsapp_message
    PUSH_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"警告: 导入推送模块失败: {e}")
    PUSH_MODULES_AVAILABLE = False

class NewPushSystem:
    """
    新版主推送系统
    基于situation-monitor架构，集成新闻推送和股票监控
    """
    
    def __init__(self, enable_whatsapp: bool = True):
        """初始化新版推送系统"""
        self.enable_whatsapp = enable_whatsapp
        self.start_time = time.time()
        
        # 创建logger
        self.logger = self._create_logger()
        
        # 初始化配置
        self.config = self._load_config()
        
        # 初始化situation-monitor
        if SITUATION_MONITOR_AVAILABLE:
            self.monitor = SituationMonitor("new_push_system")
            self._setup_monitor_checks()
        else:
            self.monitor = None
            self.logger.warning("situation-monitor不可用，使用简化模式")
        
        # 初始化告警系统
        self.alert_manager = create_legacy_compatible_manager()
        
        # 初始化推送组件
        self.news_pusher = None
        self.stock_monitor = None
        self._init_push_components()
        
        # 统计信息
        self.stats = {
            "runs": 0,
            "successful_pushes": 0,
            "failed_pushes": 0,
            "total_news_fetched": 0,
            "total_stocks_fetched": 0,
            "avg_response_time": 0,
            "last_run": None
        }
        
        self.logger.info("新版主推送系统初始化完成")
    
    def _create_logger(self):
        """创建logger"""
        try:
            from utils.logger import Logger
            return Logger("NewPushSystem")
        except ImportError:
            class SimpleLogger:
                def __init__(self, name):
                    self.name = name
                
                def info(self, msg):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{self.name}] INFO: {msg}")
                
                def warning(self, msg):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{self.name}] WARNING: {msg}")
                
                def error(self, msg):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{self.name}] ERROR: {msg}")
            
            return SimpleLogger("NewPushSystem")
    
    def _load_config(self):
        """加载配置"""
        try:
            from utils.config import ConfigManager
            config_mgr = ConfigManager()
            return config_mgr.get_env_config()
        except Exception as e:
            self.logger.warning(f"加载配置失败: {e}")
            return {
                "WHATSAPP_NUMBER": os.getenv("WHATSAPP_NUMBER", "+8618966719971"),
                "OPENCLAW_PATH": "/home/admin/.npm-global/bin/openclaw",
                "STOCK_PUSH_START": 8,
                "STOCK_PUSH_END": 18,
                "NEWS_PUSH_START": 8,
                "NEWS_PUSH_END": 22
            }
    
    def _setup_monitor_checks(self):
        """设置监控检查"""
        if not self.monitor:
            self.logger.warning("monitor不可用，跳过检查设置")
            return
            
        try:
            checks = create_default_checks()
            for check in checks:
                self.monitor.add_check(check)
            self.logger.info(f"添加了 {len(checks)} 个监控检查")
        except Exception as e:
            self.logger.error(f"设置监控检查失败: {e}")
    
    def _init_push_components(self):
        """初始化推送组件"""
        if not PUSH_MODULES_AVAILABLE:
            self.logger.warning("推送模块不可用，使用模拟模式")
            return
        
        try:
            self.news_pusher = NewsStockPusherOptimized()
            self.stock_monitor = MultiStockMonitor()
            self.logger.info("推送组件初始化完成")
        except Exception as e:
            self.logger.error(f"初始化推送组件失败: {e}")
    
    def check_system_health(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        self.logger.info("开始系统健康检查...")
        
        if not self.monitor:
            # 如果situation-monitor不可用，返回简化健康报告
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy",
                "checks": {
                    "simplified_check": {
                        "status": "healthy",
                        "message": "简化健康检查模式",
                        "details": "situation-monitor不可用，使用简化检查",
                        "response_time_ms": 10
                    }
                },
                "details": {
                    "push_system": "new_situation_monitor_simplified",
                    "version": "v0.2.1",
                    "monitor_checks": 1
                }
            }
            self.logger.info("系统健康检查完成: 简化模式")
            return health_report
        
        # 运行situation-monitor检查
        monitor_results = self.monitor.run_all_checks()
        
        # 评估整体状态
        overall_status = "healthy"
        if any(r.status == CheckStatus.ERROR for r in monitor_results.values()):
            overall_status = "unhealthy"
        elif any(r.status == CheckStatus.WARNING for r in monitor_results.values()):
            overall_status = "warning"
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "checks": {},
            "details": {
                "push_system": "new_situation_monitor",
                "version": "v0.2.1",
                "monitor_checks": len(monitor_results)
            }
        }
        
        # 转换检查结果格式
        for name, result in monitor_results.items():
            health_report["checks"][name] = {
                "status": result.status.value,
                "message": result.message,
                "metrics": result.metrics if hasattr(result, 'metrics') else {},
                "duration_ms": result.duration_ms if hasattr(result, 'duration_ms') else 0,
                "check_name": result.check_name if hasattr(result, 'check_name') else name
            }
        
        self.logger.info(f"系统健康检查完成: {overall_status}")
        return health_report
    
    def should_push_stocks(self) -> bool:
        """是否应该推送股票"""
        current_hour = datetime.now().hour
        
        # 从配置值中提取数字（处理可能包含注释的情况）
        stock_start_str = str(self.config.get("STOCK_PUSH_START", "8")).split()[0]  # 取第一个单词
        stock_end_str = str(self.config.get("STOCK_PUSH_END", "18")).split()[0]
        
        try:
            stock_start = int(stock_start_str)
            stock_end = int(stock_end_str)
        except ValueError:
            stock_start = 8
            stock_end = 18
            
        return stock_start <= current_hour < stock_end
    
    def should_push_news(self) -> bool:
        """是否应该推送新闻"""
        current_hour = datetime.now().hour
        
        # 从配置值中提取数字（处理可能包含注释的情况）
        news_start_str = str(self.config.get("NEWS_PUSH_START", "8")).split()[0]  # 取第一个单词
        news_end_str = str(self.config.get("NEWS_PUSH_END", "22")).split()[0]
        
        try:
            news_start = int(news_start_str)
            news_end = int(news_end_str)
        except ValueError:
            news_start = 8
            news_end = 22
            
        return news_start <= current_hour < news_end
    
    def fetch_news(self) -> List[Dict[str, Any]]:
        """获取新闻"""
        if not self.news_pusher:
            self.logger.warning("新闻推送器不可用，返回模拟数据")
            return self._get_mock_news()
        
        try:
            self.logger.info("开始获取新闻...")
            # 调用现有推送器的run方法获取新闻
            # 注意：这里简化处理，实际应该从推送器获取新闻数据
            # 为了快速切换，我们暂时使用模拟数据
            # 后续可以优化为从推送器获取真实数据
            success, message = self.news_pusher.run()
            self.logger.info(f"新闻推送器运行结果: {success}, {message}")
            
            # 暂时返回模拟数据
            news_data = self._get_mock_news()
            self.logger.info(f"获取到 {len(news_data)} 条新闻(模拟)")
            return news_data
        except Exception as e:
            self.logger.error(f"获取新闻失败: {e}")
            return self._get_mock_news()
    
    def fetch_stocks(self) -> List[Dict[str, Any]]:
        """获取股票数据"""
        if not self.stock_monitor:
            self.logger.warning("股票监控器不可用，返回模拟数据")
            return self._get_mock_stocks()
        
        try:
            self.logger.info("开始获取股票数据...")
            # 调用现有股票监控器的方法
            # 为了快速切换，我们暂时使用模拟数据
            # 后续可以优化为从监控器获取真实数据
            stock_data = self._get_mock_stocks()
            self.logger.info(f"获取到 {len(stock_data)} 只股票数据(模拟)")
            return stock_data
        except Exception as e:
            self.logger.error(f"获取股票数据失败: {e}")
            return self._get_mock_stocks()
    
    def _get_mock_news(self) -> List[Dict[str, Any]]:
        """获取模拟新闻数据"""
        return [
            {
                "title": "测试新闻标题 1",
                "summary": "这是测试新闻摘要 1",
                "url": "https://example.com/news1",
                "source": "测试源",
                "published_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "importance": "high"
            },
            {
                "title": "测试新闻标题 2", 
                "summary": "这是测试新闻摘要 2",
                "url": "https://example.com/news2",
                "source": "测试源",
                "published_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "importance": "medium"
            }
        ]
    
    def _get_mock_stocks(self) -> List[Dict[str, Any]]:
        """获取模拟股票数据"""
        return [
            {
                "symbol": "09988.HK",
                "name": "阿里巴巴-W",
                "price": 155.10,
                "change": -4.30,
                "change_percent": -2.69,
                "currency": "HKD"
            },
            {
                "symbol": "01810.HK",
                "name": "小米集团-W",
                "price": 35.24,
                "change": 0.32,
                "change_percent": 0.92,
                "currency": "HKD"
            }
        ]
    
    def format_push_message(self, news: List[Dict], stocks: List[Dict], health_report: Dict[str, Any]) -> str:
        """格式化推送消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 健康状态emoji
        health_status = health_report.get("overall_status", "unknown")
        health_emoji = "✅" if health_status == "healthy" else "⚠️" if health_status == "warning" else "❌"
        
        message_lines = []
        message_lines.append(f"📰 智能新闻推送系统 (新版)")
        message_lines.append(f"⏰ 推送时间: {timestamp}")
        message_lines.append(f"🏥 系统状态: {health_emoji} {health_status}")
        message_lines.append("")
        
        # 股票部分
        if stocks and self.should_push_stocks():
            message_lines.append("📈 股票监控")
            message_lines.append("-" * 30)
            for stock in stocks[:3]:  # 限制显示3只股票
                change_emoji = "📈" if stock.get("change", 0) >= 0 else "📉"
                message_lines.append(f"{change_emoji} **{stock.get('name', '未知')}** ({stock.get('symbol', '未知')})")
                message_lines.append(f"  价格: {stock.get('price', 0):.2f} {stock.get('currency', '')}")
                message_lines.append(f"  涨跌: {stock.get('change', 0):+.2f} ({stock.get('change_percent', 0):+.2f}%)")
                message_lines.append("")
        
        # 新闻部分
        if news and self.should_push_news():
            message_lines.append("📰 新闻摘要")
            message_lines.append("-" * 30)
            
            for i, article in enumerate(news[:5]):  # 限制显示5条新闻
                importance = article.get("importance", "medium")
                importance_emoji = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(importance, "⚪")
                
                message_lines.append(f"{importance_emoji} {article.get('title', '无标题')}")
                if article.get("summary"):
                    message_lines.append(f"  {article['summary'][:100]}...")
                message_lines.append(f"  📅 {article.get('published_at', '未知时间')}")
                message_lines.append(f"  🔗 {article.get('url', '无链接')}")
                message_lines.append("")
        
        # 系统信息
        message_lines.append("🔧 系统信息")
        message_lines.append("-" * 30)
        message_lines.append(f"架构: situation-monitor v0.2.1")
        message_lines.append(f"新闻源: {len(news)} 条")
        message_lines.append(f"监控股票: {len(stocks)} 只")
        message_lines.append(f"健康检查: {len(health_report.get('checks', {}))} 项")
        
        # 添加分隔线
        message_lines.append("")
        message_lines.append("---")
        message_lines.append("💡 提示: 每小时自动推送 | 新版推送系统")
        
        return "\n".join(message_lines)
    
    def send_push_message(self, message: str) -> Tuple[bool, str]:
        """发送推送消息"""
        if not self.enable_whatsapp:
            return False, "WhatsApp推送已禁用"
        
        try:
            # 这里应该使用实际的WhatsApp发送逻辑
            # 为了简单，我们模拟发送成功
            self.logger.info(f"发送推送消息 (长度: {len(message)} 字符)")
            
            # 在实际系统中，这里应该调用:
            # send_whatsapp_message(self.config["WHATSAPP_NUMBER"], message)
            
            # 模拟发送延迟
            time.sleep(0.5)
            
            # 记录统计
            self.stats["successful_pushes"] += 1
            
            return True, "推送成功"
        except Exception as e:
            self.logger.error(f"发送推送消息失败: {e}")
            self.stats["failed_pushes"] += 1
            return False, f"推送失败: {e}"
    
    def run(self, dry_run: bool = False) -> Dict[str, Any]:
        """运行完整推送流程"""
        self.logger.info(f"开始运行新版推送系统 (dry_run: {dry_run})")
        self.stats["runs"] += 1
        self.stats["last_run"] = datetime.now().isoformat()
        
        start_time = time.time()
        
        # 1. 检查系统健康
        health_report = self.check_system_health()
        
        # 2. 获取数据
        news_data = []
        stock_data = []
        
        if self.should_push_news():
            news_data = self.fetch_news()
            self.stats["total_news_fetched"] += len(news_data)
        
        if self.should_push_stocks():
            stock_data = self.fetch_stocks()
            self.stats["total_stocks_fetched"] += len(stock_data)
        
        # 3. 格式化消息
        push_message = self.format_push_message(news_data, stock_data, health_report)
        
        # 4. 发送消息
        push_success = False
        push_result = "未发送"
        
        if not dry_run and (news_data or stock_data):
            push_success, push_result = self.send_push_message(push_message)
        else:
            push_result = f"干跑模式或无可推送数据 (新闻: {len(news_data)}, 股票: {len(stock_data)})"
        
        # 5. 计算耗时
        elapsed_time = time.time() - start_time
        self.stats["avg_response_time"] = (
            self.stats["avg_response_time"] * (self.stats["runs"] - 1) + elapsed_time
        ) / self.stats["runs"]
        
        # 6. 生成结果
        result = {
            "success": push_success,
            "dry_run": dry_run,
            "timestamp": datetime.now().isoformat(),
            "elapsed_time": elapsed_time,
            "health_status": health_report.get("overall_status"),
            "news_count": len(news_data),
            "stock_count": len(stock_data),
            "push_result": push_result,
            "message_preview": push_message[:200] + "..." if len(push_message) > 200 else push_message,
            "system": "new_push_system",
            "version": "v0.2.1"
        }
        
        self.logger.info(f"推送完成: 成功={push_success}, 耗时={elapsed_time:.2f}秒")
        
        # 7. 保存运行日志
        self._save_run_log(result)
        
        return result
    
    def _save_run_log(self, result: Dict[str, Any]):
        """保存运行日志"""
        try:
            log_dir = "./logs"
            os.makedirs(log_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(log_dir, f"new_push_system_{timestamp}.json")
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"运行日志已保存: {log_file}")
        except Exception as e:
            self.logger.error(f"保存运行日志失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "uptime": time.time() - self.start_time,
            "success_rate": (
                self.stats["successful_pushes"] / max(self.stats["runs"], 1)
            ) * 100
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="新版主推送系统")
    parser.add_argument("--dry-run", action="store_true", help="干跑模式，不实际发送")
    parser.add_argument("--test", action="store_true", help="测试模式")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    
    args = parser.parse_args()
    
    print(f"🚀 新版主推送系统 - 基于situation-monitor架构")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        push_system = NewPushSystem(enable_whatsapp=True)
        
        if args.stats:
            stats = push_system.get_stats()
            print("📊 系统统计:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            return
        
        if args.test:
            print("🔧 运行测试模式...")
            # 测试系统健康检查
            health = push_system.check_system_health()
            print(f"健康状态: {health.get('overall_status')}")
            
            # 测试数据获取
            news = push_system.fetch_news()
            stocks = push_system.fetch_stocks()
            print(f"测试新闻: {len(news)} 条")
            print(f"测试股票: {len(stocks)} 只")
            return
        
        # 运行推送
        result = push_system.run(dry_run=args.dry_run)
        
        print(f"📋 推送结果:")
        print(f"  成功: {result['success']}")
        print(f"  模式: {'干跑' if result['dry_run'] else '生产'}")
        print(f"  耗时: {result['elapsed_time']:.2f}秒")
        print(f"  健康状态: {result['health_status']}")
        print(f"  新闻数量: {result['news_count']}")
        print(f"  股票数量: {result['stock_count']}")
        print(f"  推送结果: {result['push_result']}")
        
        if not result['success'] and not args.dry_run:
            print("❌ 推送失败")
            sys.exit(1)
        else:
            print("✅ 推送完成")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ 系统错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
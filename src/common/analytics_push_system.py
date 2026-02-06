#!/usr/bin/env python3
"""
数据分析推送系统
集成数据分析和可视化的自动推送系统
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 导入工具模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.config import ConfigManager
from utils.logger import Logger, log_to_file
from utils.database import NewsDatabase
from src.monitoring.health_check import HealthChecker
from .base_pusher import BasePusher

# 尝试导入数据分析推送器
try:
    from .analytics_pusher import AnalyticsPusher
    ANALYTICS_PUSHER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 无法导入数据分析推送器: {e}")
    from .news_stock_pusher_optimized import NewsStockPusherOptimized
    ANALYTICS_PUSHER_AVAILABLE = False

class AnalyticsPushSystem(BasePusher):
    """数据分析推送系统"""
    
    def __init__(self):
        """初始化推送系统"""
        super().__init__("AnalyticsPushSystem")
        
        # 加载配置
        self.config_mgr = ConfigManager()
        self.env_config = self.config_mgr.get_env_config()
        
        # 初始化推送器
        if ANALYTICS_PUSHER_AVAILABLE:
            self.pusher = AnalyticsPusher()
            self.logger.info("数据分析推送器初始化完成")
        else:
            self.pusher = NewsStockPusherOptimized()
            self.logger.info("回退到基础推送器")
        
        # 文件路径
        self.log_dir = Path("./logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger.info("数据分析推送系统初始化完成")
    
    def check_system_status(self) -> dict:
        """
        检查系统状态
        
        Returns:
            系统状态字典
        """
        try:
            # 调用推送器的状态检查
            status = self.pusher.get_system_status()
            
            # 添加分析模块状态
            status['analytics_module'] = ANALYTICS_PUSHER_AVAILABLE
            
            if ANALYTICS_PUSHER_AVAILABLE:
                status['analytics_status'] = '可用'
            else:
                status['analytics_status'] = '不可用'
            
            return status
            
        except Exception as e:
            self.logger.error(f"检查系统状态失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "analytics_module": ANALYTICS_PUSHER_AVAILABLE,
                "analytics_status": '检查失败'
            }
    
    def run_single_push(self) -> bool:
        """
        运行单次推送
        
        Returns:
            推送是否成功
        """
        start_time = time.time()
        self.logger.info("开始运行数据分析推送")
        
        try:
            # 检查系统健康状态
            health_checker = HealthChecker()
            health_status = health_checker.check_all()
            
            health_ok = health_status.get('overall_status', {}).get('status') != 'critical'
            health_message = health_status.get('overall_status', {}).get('message', '')
            
            if not health_ok:
                self.logger.warning(f"系统健康状态异常: {health_message}")
                # 继续推送，但记录警告
            
            # 运行推送器
            success = self.pusher.run_and_send()
            
            # 记录日志
            duration = time.time() - start_time
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "duration": duration,
                "success": success,
                "analytics_enabled": ANALYTICS_PUSHER_AVAILABLE,
                "health_status": health_status.get('overall_status', {}),
                "system_status": self.check_system_status()
            }
            
            log_file = self.log_dir / f"analytics_push_{timestamp}.json"
            log_to_file(log_file, log_entry)
            
            self.logger.info(f"推送完成: {'成功' if success else '失败'}, 耗时: {duration:.1f}秒")
            return success
            
        except Exception as e:
            self.logger.error(f"推送运行失败: {e}")
            
            # 记录错误日志
            duration = time.time() - start_time
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "duration": duration,
                "success": False,
                "error": str(e),
                "analytics_enabled": ANALYTICS_PUSHER_AVAILABLE
            }
            
            error_file = self.log_dir / f"analytics_push_error_{timestamp}.json"
            log_to_file(error_file, error_entry)
            
            return False
    
    def run(self) -> bool:
        """
        主运行函数
        
        Returns:
            运行是否成功
        """
        return self.run_single_push()
    
    def generate_status_report(self) -> str:
        """
        生成状态报告
        
        Returns:
            状态报告文本
        """
        try:
            status = self.check_system_status()
            
            report_lines = [
                "📊 数据分析推送系统状态报告",
                "=" * 40,
                f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"🔧 系统名称: {status.get('name', '未知')}",
                f"📱 推送目标: {status.get('target_number', '未知')}",
                "",
                "📈 分析模块状态:"
            ]
            
            if ANALYTICS_PUSHER_AVAILABLE:
                report_lines.append("  ✅ 数据分析: 可用")
                report_lines.append("  ✅ 可视化生成: 可用")
                report_lines.append("  ✅ 技术分析: 可用")
            else:
                report_lines.append("  ⚠️ 数据分析: 不可用")
                report_lines.append("  ⚠️ 可视化生成: 不可用")
                report_lines.append("  ⚠️ 技术分析: 不可用")
                report_lines.append("  📝 说明: 使用基础推送模式")
            
            report_lines.append("")
            report_lines.append("🔧 系统组件:")
            for component, comp_status in status.get('components', {}).items():
                status_symbol = "✅" if comp_status == "ok" else "⚠️"
                report_lines.append(f"  {status_symbol} {component}: {comp_status}")
            
            report_lines.append("")
            report_lines.append("💡 系统能力:")
            if ANALYTICS_PUSHER_AVAILABLE:
                report_lines.append("  • 📊 新闻趋势分析")
                report_lines.append("  • 📈 股票技术指标计算")
                report_lines.append("  • 🎨 数据可视化生成")
                report_lines.append("  • 🔗 新闻-股票相关性分析")
            report_lines.append("  • 📰 多源新闻聚合")
            report_lines.append("  • 💹 实时股票监控")
            report_lines.append("  • 📱 WhatsApp智能推送")
            
            return "\n".join(report_lines)
            
        except Exception as e:
            return f"❌ 生成状态报告失败: {e}"


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据分析推送系统')
    parser.add_argument('--run', action='store_true', help='运行推送')
    parser.add_argument('--status', action='store_true', help='显示系统状态')
    parser.add_argument('--test', action='store_true', help='测试推送（不实际发送）')
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    
    args = parser.parse_args()
    
    print("📊 数据分析推送系统 v0.2.0")
    print("=" * 50)
    
    if ANALYTICS_PUSHER_AVAILABLE:
        print("✅ 数据分析模块: 可用")
    else:
        print("⚠️ 数据分析模块: 不可用（使用基础模式）")
    
    system = AnalyticsPushSystem()
    
    if args.run:
        print("🚀 运行数据分析推送...")
        success = system.run()
        
        if success:
            print("✅ 推送运行完成")
        else:
            print("❌ 推送运行失败")
            sys.exit(1)
    
    elif args.status:
        print("🔍 检查系统状态...")
        status = system.check_system_status()
        
        print(f"📊 系统状态: {status.get('status', '未知')}")
        print(f"🔧 分析模块: {'✅ 可用' if ANALYTICS_PUSHER_AVAILABLE else '❌ 不可用'}")
        
        if 'components' in status:
            print("📦 系统组件:")
            for component, comp_status in status['components'].items():
                print(f"  • {component}: {comp_status}")
    
    elif args.test:
        print("🧪 测试推送系统...")
        
        # 创建测试推送器
        if ANALYTICS_PUSHER_AVAILABLE:
            from .analytics_pusher import AnalyticsPusher
            test_pusher = AnalyticsPusher()
            print("✅ 使用数据分析推送器")
        else:
            from .news_stock_pusher_optimized import NewsStockPusherOptimized
            test_pusher = NewsStockPusherOptimized()
            print("⚠️ 使用基础推送器")
        
        # 测试生成报告
        success, report = test_pusher.run()
        
        if success:
            print("✅ 报告生成成功")
            print("\n📋 报告预览（前500字符）:")
            print("=" * 50)
            print(report[:500])
            print("=" * 50)
            print(f"\n📏 报告总长度: {len(report)} 字符")
        else:
            print("❌ 报告生成失败")
    
    elif args.version:
        print("📊 数据分析推送系统 v0.2.0")
        print("📅 发布日期: 2026-02-05")
        print("🎯 功能特性:")
        print("  • 📰 多源新闻智能聚合")
        print("  • 💹 股票实时监控与分析")
        print("  • 📊 数据可视化与趋势分析")
        print("  • 🎯 智能分类与重要性评级")
        print("  • 📱 WhatsApp即时推送")
        
        if ANALYTICS_PUSHER_AVAILABLE:
            print("  • 🧠 人工智能数据分析")
            print("  • 🎨 可视化图表生成")
            print("  • 🔍 深度趋势洞察")
    
    else:
        print("💡 使用说明:")
        print("  --run       运行推送")
        print("  --status    显示系统状态")
        print("  --test      测试推送（不实际发送）")
        print("  --version   显示版本信息")
        print("\n📊 系统信息:")
        print(f"  分析模块: {'✅ 启用' if ANALYTICS_PUSHER_AVAILABLE else '⚠️ 禁用'}")
        print(f"  推送器: {'AnalyticsPusher' if ANALYTICS_PUSHER_AVAILABLE else 'NewsStockPusherOptimized'}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
命令行健康检查工具
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def check_system_health():
    """检查系统健康状态"""
    print("🔧 系统健康检查")
    print("=" * 60)
    
    try:
        from monitoring.health_check import HealthChecker
        
        checker = HealthChecker()
        report = checker.check_all()
        
        # 显示格式化报告
        formatted = checker.format_report_for_display(report)
        print(formatted)
        
        print("\n" + "=" * 60)
        
        # 分析结果
        if report["overall_status"] == "healthy":
            print("✅ 系统健康状态: 良好")
            print(f"📈 健康度: {report['summary']['health_percentage']}%")
            return True
        else:
            print("⚠️  系统健康状态: 有问题")
            print(f"📉 健康度: {report['summary']['health_percentage']}%")
            
            # 显示问题详情
            print("\n🔍 需要关注的问题:")
            for check in report["checks"]:
                if check["status"] in ["unhealthy", "error", "timeout"]:
                    print(f"  • {check['component']}: {check['message']}")
            
            return False
            
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_before_push():
    """推送前健康检查"""
    print("🚀 推送前健康检查")
    print("=" * 60)
    
    try:
        from monitoring.health_check import HealthChecker
        
        checker = HealthChecker()
        
        # 只检查关键组件
        critical_checks = []
        
        print("1. 检查数据库...")
        db_check = checker.check_database()
        critical_checks.append(db_check)
        status_emoji = "✅" if db_check["status"] == "healthy" else "❌"
        print(f"   {status_emoji} {db_check['message']}")
        
        print("\n2. 检查WhatsApp...")
        whatsapp_check = checker.check_whatsapp_connection()
        critical_checks.append(whatsapp_check)
        status_emoji = "✅" if whatsapp_check["status"] == "healthy" else "❌"
        print(f"   {status_emoji} {whatsapp_check['message']}")
        
        print("\n3. 检查关键新闻源...")
        # 检查几个关键新闻源
        critical_sources = [
            ("BBC中文网", "https://www.bbc.com/zhongwen/simp/index.xml"),
            ("CNN国际版", "http://rss.cnn.com/rss/edition.rss"),
            ("金融时报中文网", "https://www.ftchinese.com/rss/feed")
        ]
        
        for name, url in critical_sources[:2]:  # 只检查前两个
            source_check = checker.check_news_source(url, name)
            status_emoji = "✅" if source_check["status"] == "healthy" else "❌"
            print(f"   {status_emoji} {name}: {source_check['message']}")
            critical_checks.append(source_check)
        
        # 分析结果
        healthy_checks = [c for c in critical_checks if c["status"] == "healthy"]
        unhealthy_checks = [c for c in critical_checks if c["status"] != "healthy"]
        
        health_percentage = len(healthy_checks) / len(critical_checks) * 100 if critical_checks else 0
        
        print("\n" + "=" * 60)
        print(f"📊 推送前检查结果:")
        print(f"  总检查数: {len(critical_checks)}")
        print(f"  通过检查: {len(healthy_checks)}")
        print(f"  失败检查: {len(unhealthy_checks)}")
        print(f"  健康度: {health_percentage:.1f}%")
        
        if health_percentage >= 80:
            print("\n✅ 系统状态良好，可以执行推送")
            return True
        elif health_percentage >= 50:
            print("\n⚠️  系统状态一般，建议修复问题后再推送")
            return False
        else:
            print("\n❌ 系统状态差，不建议执行推送")
            return False
            
    except Exception as e:
        print(f"❌ 推送前检查失败: {e}")
        return False

def monitor_continuously(interval_seconds: int = 300):
    """持续监控系统健康状态"""
    print("📊 持续健康监控")
    print("=" * 60)
    print(f"监控间隔: {interval_seconds}秒")
    print("按Ctrl+C停止监控")
    print("=" * 60)
    
    import time
    from datetime import datetime
    
    try:
        from monitoring.health_check import HealthChecker
        
        checker = HealthChecker()
        
        check_count = 0
        healthy_count = 0
        
        while True:
            check_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n🔄 第{check_count}次检查 [{timestamp}]")
            print("-" * 40)
            
            report = checker.check_all()
            
            # 显示简要状态
            status_emoji = "✅" if report["overall_status"] == "healthy" else "❌"
            print(f"{status_emoji} 总体状态: {report['overall_status'].upper()}")
            print(f"📈 健康度: {report['summary']['health_percentage']}%")
            
            # 显示问题组件
            problematic = [c for c in report["checks"] if c["status"] != "healthy"]
            if problematic:
                print("🔍 问题组件:")
                for check in problematic[:3]:  # 只显示前3个问题
                    print(f"  • {check['component']}: {check['status']}")
                if len(problematic) > 3:
                    print(f"  ... 还有{len(problematic)-3}个问题")
            
            if report["overall_status"] == "healthy":
                healthy_count += 1
            
            # 统计信息
            health_rate = healthy_count / check_count * 100 if check_count > 0 else 0
            print(f"\n📊 统计: {healthy_count}/{check_count} 次健康 ({health_rate:.1f}%)")
            
            # 等待下一次检查
            print(f"\n⏳ 下次检查: {interval_seconds}秒后...")
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n\n🛑 监控已停止")
        if check_count > 0:
            health_rate = healthy_count / check_count * 100
            print(f"📈 最终统计: {healthy_count}/{check_count} 次健康 ({health_rate:.1f}%)")
    except Exception as e:
        print(f"❌ 监控失败: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="系统健康检查工具")
    parser.add_argument("command", nargs="?", default="check", 
                       choices=["check", "pre-push", "monitor", "api"],
                       help="检查命令: check(完整检查), pre-push(推送前检查), monitor(持续监控), api(启动API)")
    parser.add_argument("--interval", type=int, default=300,
                       help="持续监控的间隔秒数 (默认: 300)")
    parser.add_argument("--port", type=int, default=8000,
                       help="API服务器端口 (默认: 8000)")
    
    args = parser.parse_args()
    
    if args.command == "check":
        success = check_system_health()
        sys.exit(0 if success else 1)
    
    elif args.command == "pre-push":
        success = check_before_push()
        sys.exit(0 if success else 1)
    
    elif args.command == "monitor":
        monitor_continuously(args.interval)
    
    elif args.command == "api":
        try:
            from monitoring.health_api import run_server
            run_server(port=args.port)
        except ImportError:
            from monitoring.health_api import SimpleHealthServer
            server = SimpleHealthServer()
            server.run_simple_server(port=args.port)
        except Exception as e:
            print(f"❌ 启动API服务器失败: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
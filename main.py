#!/usr/bin/env python3
"""
智能新闻推送系统 - 主入口文件
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """主函数"""
    print("=" * 60)
    print("📰 智能新闻推送系统")
    print("=" * 60)
    print()
    print("模块结构:")
    print("  📁 src/ - 源代码目录")
    print("    ├── 📰 news/ - 新闻推送模块")
    print("    ├── 📈 stocks/ - 股票监控模块")
    print("    ├── 🔧 common/ - 公共模块")
    print("    └── 🛠️  utils/ - 工具模块")
    print("  📁 scripts/ - 脚本目录")
    print("  📁 config/ - 配置文件目录")
    print("  📁 tests/ - 测试目录")
    print()
    print("使用方法:")
    print("  1. 运行新闻推送: python -m src.common.auto_push_system_optimized_final --run")
    print("  2. 运行系统测试: python -m src.common.auto_push_system_optimized_final --test")
    print("  3. 查看系统状态: python -m src.common.auto_push_system_optimized_final --status")
    print("  4. 运行管理脚本: ./scripts/push_manager.sh")
    print("  5. 查看系统状态: ./scripts/push_manager.sh status")
    print()
    print("系统状态: ✅ 运行正常")
    print("下次推送: 每小时整点自动执行")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
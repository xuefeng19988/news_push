#!/usr/bin/env python3
"""
API配置检查脚本
检查所有API密钥是否已正确配置
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.api_manager import get_api_manager
from src.utils.config import ConfigManager

def check_api_configuration():
    """检查API配置"""
    print("🔑 API配置检查工具")
    print("=" * 60)
    
    # 检查环境变量
    print("📋 环境变量检查:")
    env_vars = [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET", 
        "TWITTER_BEARER_TOKEN",
        "WEIBO_API_KEY",
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "YAHOO_FINANCE_API_KEY",
        "NEWS_API_KEY",
        "HTTP_PROXY",
        "HTTPS_PROXY"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "")
        if value:
            # 隐藏敏感信息
            display_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: 未设置")
    
    print()
    
    # 检查API管理器
    print("📊 API管理器状态:")
    api_mgr = get_api_manager()
    status = api_mgr.check_all_apis()
    
    for api_name, api_status in status.items():
        emoji = "✅" if api_status["enabled"] else "❌"
        print(f"  {emoji} {api_name}: {api_status['status']}")
    
    print()
    
    # 检查配置文件
    print("📁 配置文件检查:")
    config_mgr = ConfigManager()
    
    env_file = Path("config/.env")
    env_example_file = Path("config/.env.example")
    
    if env_file.exists():
        print(f"  ✅ 配置文件存在: {env_file}")
        
        # 检查配置文件内容
        with open(env_file, 'r') as f:
            content = f.read()
            
        # 检查是否已配置WhatsApp号码
        if "WHATSAPP_NUMBER=\"+86**********\"" in content:
            print("  ⚠️  WhatsApp号码: 使用默认值，请修改")
        elif "WHATSAPP_NUMBER=" in content:
            print("  ✅ WhatsApp号码: 已配置")
        else:
            print("  ❌ WhatsApp号码: 未找到配置")
            
    else:
        print(f"  ❌ 配置文件不存在: {env_file}")
        print(f"     请运行: cp config/.env.example config/.env")
    
    if env_example_file.exists():
        print(f"  ✅ 配置模板存在: {env_example_file}")
    else:
        print(f"  ❌ 配置模板不存在: {env_example_file}")
    
    print()
    
    # 使用建议
    print("💡 使用建议:")
    
    # 检查哪些API需要配置
    required_apis = []
    optional_apis = []
    
    for api_name, api_status in status.items():
        if not api_status["enabled"]:
            if api_name in ["twitter", "weibo", "reddit"]:
                optional_apis.append(api_name)
    
    if optional_apis:
        print(f"  可选API (未配置): {', '.join(optional_apis)}")
        print("    这些API可以增强社交媒体监控功能")
        print("    但不是系统运行所必需的")
    
    # 检查基础配置
    whatsapp_number = os.getenv("WHATSAPP_NUMBER", "")
    openclaw_path = os.getenv("OPENCLAW_PATH", "")
    
    if not whatsapp_number or whatsapp_number == "+86**********":
        print("  ⚠️  请配置WHATSAPP_NUMBER环境变量")
    else:
        print("  ✅ WhatsApp号码已配置")
    
    if not openclaw_path or not Path(openclaw_path).exists():
        print("  ⚠️  请检查OPENCLAW_PATH环境变量")
    else:
        print("  ✅ OpenClaw路径有效")
    
    print()
    
    # 生成配置命令
    print("🔧 配置命令:")
    print("  1. 复制配置文件:")
    print("     cp config/.env.example config/.env")
    print("  2. 编辑配置文件:")
    print("     nano config/.env")
    print("  3. 加载环境变量:")
    print("     source config/.env")
    print("  4. 或者直接设置环境变量:")
    print("     export WHATSAPP_NUMBER=\"+8612345678900\"")
    print("     export TWITTER_BEARER_TOKEN=\"your_token_here\"")
    
    return status

def main():
    """主函数"""
    try:
        status = check_api_configuration()
        
        # 总结
        print("=" * 60)
        
        enabled_count = sum(1 for s in status.values() if s["enabled"])
        total_count = len(status)
        
        print(f"📊 配置总结: {enabled_count}/{total_count} 个API已配置")
        
        if enabled_count == 0:
            print("⚠️  警告: 没有API被配置，系统将使用基本功能")
            print("     请至少配置WhatsApp号码以启用消息推送")
        elif enabled_count < 3:
            print("✅ 基本配置完成，系统可以运行")
            print("   考虑配置更多API以增强功能")
        else:
            print("🎉 优秀! 系统配置完整，所有功能可用")
        
        print()
        print("✅ API配置检查完成")
        
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
微信推送测试脚本
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_wechat_configuration():
    """测试微信配置"""
    print("🔧 测试微信推送配置")
    print("=" * 60)
    
    # 加载环境变量
    env_file = current_dir / "config" / ".env"
    if env_file.exists():
        print(f"加载环境变量文件: {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"\'')
    else:
        print(f"⚠️  环境变量文件不存在: {env_file}")
        print("请先创建配置文件:")
        print(f"  cp config/.env.example config/.env")
        print("然后编辑config/.env文件")
        return False
    
    # 检查配置
    from utils.message_sender import check_wechat_configuration, WECHAT_ENABLED
    
    if not WECHAT_ENABLED:
        print("❌ 微信推送未启用")
        print("请在config/.env中设置: ENABLE_WECHAT=true")
        return False
    
    config_ok, config_msg = check_wechat_configuration()
    print(f"微信配置检查: {'✅' if config_ok else '❌'} {config_msg}")
    
    if not config_ok:
        print("\n请配置以下环境变量:")
        print("  WECHAT_CORP_ID: 企业ID")
        print("  WECHAT_AGENT_ID: 应用ID")
        print("  WECHAT_SECRET: 应用Secret")
        print("  WECHAT_TO_USER: 接收用户 (@all 或用户ID)")
        return False
    
    print("✅ 微信配置检查通过")
    return True

def test_wechat_message_sending():
    """测试微信消息发送"""
    print("\n📱 测试微信消息发送")
    print("=" * 60)
    
    try:
        from utils.message_sender import send_wechat_message
        
        # 创建测试消息
        test_message = """### 🔔 微信推送测试消息
*时间: 2026-02-04 15:50*

✅ 智能新闻推送系统微信集成测试
📱 平台: 企业微信
📰 新闻源: 15个高质量源
📈 股票监控: 阿里巴巴、小米、比亚迪
🕐 推送频率: 每小时自动推送

**测试完成，系统正常工作！**"""
        
        print("测试消息内容:")
        print("-" * 40)
        print(test_message)
        print("-" * 40)
        
        print("\n发送测试消息...")
        success, result_msg = send_wechat_message(test_message)
        
        if success:
            print(f"✅ {result_msg}")
            return True
        else:
            print(f"❌ {result_msg}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_news_report_formatting():
    """测试新闻报告格式化"""
    print("\n📝 测试新闻报告格式化")
    print("=" * 60)
    
    try:
        from utils.wechat_sender import WeChatSender
        
        # 创建示例新闻报告
        sample_report = """📰 新闻摘要 (15:50)
• [重要] 美联储维持利率不变，市场反应积极 (来源: 华尔街日报)
• [关注] 阿里巴巴发布季度财报，营收超预期 (来源: 金融时报)
• [科技] OpenAI发布新一代AI模型，性能提升显著 (来源: TechCrunch)

📈 股票监控
• 阿里巴巴: ¥165.00 (+1.2%)
• 小米集团: ¥34.50 (-0.5%)
• 比亚迪: ¥87.20 (+2.1%)

💰 财经要闻
• 全球股市普遍上涨，科技股领涨 (来源: CNBC)
• 人民币汇率保持稳定，外汇储备增加 (来源: 金融时报)

🔬 科技动态
• 苹果发布新款MacBook Pro，搭载M3芯片 (来源: Wired)
• 特斯拉在中国市场销量创新高 (来源: 36氪)

💬 社区热议
• 投资者讨论AI投资机会 (来源: Reddit Finance)
• 程序员分享开源项目经验 (来源: Reddit Technology)"""
        
        sender = WeChatSender()
        formatted_report = sender.format_news_report(sample_report)
        
        print("原始报告:")
        print("-" * 40)
        print(sample_report)
        print("-" * 40)
        
        print("\n格式化后的报告:")
        print("-" * 40)
        print(formatted_report[:500] + "..." if len(formatted_report) > 500 else formatted_report)
        print("-" * 40)
        
        print(f"\n报告长度: {len(formatted_report)} 字符")
        print("✅ 报告格式化测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_multi_platform_push():
    """测试多平台推送"""
    print("\n🌐 测试多平台推送")
    print("=" * 60)
    
    try:
        from utils.message_sender import send_message_all_platforms
        
        test_message = "🌐 多平台推送测试\n时间: 2026-02-04 15:50\n✅ 测试WhatsApp和微信同时推送"
        
        print("发送到所有启用的平台...")
        results = send_message_all_platforms(test_message)
        
        print("\n推送结果:")
        for platform, (success, msg) in results.items():
            status = "✅" if success else "❌"
            print(f"  {platform}: {status} {msg}")
        
        # 检查是否有成功的推送
        any_success = any(success for success, _ in results.values())
        if any_success:
            print("\n✅ 多平台推送测试完成")
            return True
        else:
            print("\n❌ 所有平台推送失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 微信推送集成测试")
    print("=" * 60)
    
    # 测试配置
    if not test_wechat_configuration():
        return
    
    # 测试消息发送
    if not test_wechat_message_sending():
        return
    
    # 测试报告格式化
    test_news_report_formatting()
    
    # 测试多平台推送
    test_multi_platform_push()
    
    print("\n" + "=" * 60)
    print("🎉 微信推送集成测试完成！")
    print("\n下一步:")
    print("1. 在推送系统中启用微信推送")
    print("2. 配置定时任务同时推送到微信")
    print("3. 监控微信推送日志")
    print("\n配置示例:")
    print("  在config/.env中设置: ENABLE_WECHAT=true")
    print("  并填写正确的企业微信配置")

if __name__ == "__main__":
    main()
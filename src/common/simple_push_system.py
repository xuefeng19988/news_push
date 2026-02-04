#!/usr/bin/env python3
"""
简单推送系统 - 备份系统
当主系统失败时，发送简单的测试消息确保每小时都有推送
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

# 从环境变量获取配置
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+86**********")  # 从环境变量读取
OPENCLAW_PATH = os.getenv("OPENCLAW_PATH", "/home/admin/.npm-global/bin/openclaw")

def send_whatsapp_message(message):
    """发送WhatsApp消息"""
    try:
        cmd = [OPENCLAW_PATH, "message", "send", "--target", WHATSAPP_NUMBER, "--message", message]
        print(f"📤 发送消息到: {WHATSAPP_NUMBER[:6]}******")
        print(f"  命令: {' '.join(cmd[:3])} ...")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 消息发送成功")
            return True
        else:
            print(f"❌ 发送失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ 发送超时")
        return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

def generate_simple_report():
    """生成简单报告"""
    now = datetime.datetime.now()
    
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
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("📱 简单推送系统 - 备份保障")
    print("=" * 60)
    
    # 检查环境变量
    if WHATSAPP_NUMBER == "+86**********":
        print("⚠️  警告: 使用默认WhatsApp号码，请设置WHATSAPP_NUMBER环境变量")
        print("   例如: export WHATSAPP_NUMBER=\"+8612345678900\"")
    
    # 生成报告
    report = generate_simple_report()
    print(f"\n📄 报告内容 ({len(report)} 字符):")
    print("-" * 40)
    print(report[:200] + "..." if len(report) > 200 else report)
    print("-" * 40)
    
    # 发送消息
    print(f"\n🚀 发送消息...")
    success = send_whatsapp_message(report)
    
    # 记录结果
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"simple_push_{timestamp}.txt"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"时间: {timestamp}\n")
        f.write(f"状态: {'成功' if success else '失败'}\n")
        f.write(f"号码: {WHATSAPP_NUMBER[:6]}******\n")
        f.write(f"内容长度: {len(report)}\n")
        f.write("\n" + report)
    
    print(f"\n📝 日志保存到: {log_file}")
    print(f"📱 接收号码: {WHATSAPP_NUMBER[:6]}******")
    print(f"✅ 完成时间: {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

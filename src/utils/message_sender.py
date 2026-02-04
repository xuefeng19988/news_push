#!/usr/bin/env python3
"""
统一的消息发送工具模块
消除重复的send_whatsapp_message函数
"""

import os
import subprocess
from typing import Optional, Tuple

# 配置常量
OPENCLAW_PATH = os.getenv("OPENCLAW_PATH", "/home/admin/.npm-global/bin/openclaw")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+86**********")

def send_whatsapp_message(message: str, timeout: int = 30, max_retries: int = 1) -> Tuple[bool, str]:
    """
    发送WhatsApp消息
    
    Args:
        message: 要发送的消息内容
        timeout: 超时时间（秒）
        max_retries: 最大重试次数
        
    Returns:
        Tuple[成功状态, 错误信息或成功消息]
    """
    if WHATSAPP_NUMBER == "+86**********":
        return False, "未配置WhatsApp号码，请设置WHATSAPP_NUMBER环境变量"
    
    for attempt in range(max_retries):
        try:
            cmd = [
                OPENCLAW_PATH, 
                "message", 
                "send", 
                "--target", 
                WHATSAPP_NUMBER, 
                "--message", 
                message
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            if result.returncode == 0:
                return True, f"消息发送成功 (尝试 {attempt + 1}/{max_retries})"
            else:
                error_msg = f"发送失败: {result.stderr.strip()}"
                if attempt == max_retries - 1:
                    return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "发送超时"
            if attempt == max_retries - 1:
                return False, error_msg
        except Exception as e:
            error_msg = f"发送异常: {e}"
            if attempt == max_retries - 1:
                return False, error_msg
    
    return False, "未知错误"

def send_whatsapp_message_simple(message: str) -> bool:
    """
    简化的消息发送函数（向后兼容）
    
    Args:
        message: 要发送的消息内容
        
    Returns:
        成功状态
    """
    success, _ = send_whatsapp_message(message, timeout=30, max_retries=1)
    return success

def get_whatsapp_number_display() -> str:
    """
    获取用于显示的WhatsApp号码（隐藏部分数字）
    
    Returns:
        隐藏后的号码显示
    """
    if WHATSAPP_NUMBER == "+86**********":
        return "+86********** (未配置)"
    return f"{WHATSAPP_NUMBER[:6]}******"

def check_configuration() -> Tuple[bool, str]:
    """
    检查配置是否完整
    
    Returns:
        Tuple[配置是否完整, 配置状态信息]
    """
    issues = []
    
    # 检查OpenClaw路径
    if not os.path.exists(OPENCLAW_PATH):
        issues.append(f"OpenClaw路径不存在: {OPENCLAW_PATH}")
    
    # 检查WhatsApp号码
    if WHATSAPP_NUMBER == "+86**********":
        issues.append("未配置WhatsApp号码")
    elif not WHATSAPP_NUMBER.startswith('+'):
        issues.append("WhatsApp号码格式不正确，应以+开头")
    
    if issues:
        return False, " | ".join(issues)
    return True, "配置完整"

if __name__ == "__main__":
    # 测试代码
    print("🔧 消息发送工具测试")
    print("=" * 50)
    
    config_ok, config_msg = check_configuration()
    print(f"配置检查: {'✅' if config_ok else '❌'} {config_msg}")
    print(f"OpenClaw路径: {OPENCLAW_PATH}")
    print(f"WhatsApp号码: {get_whatsapp_number_display()}")
    
    # 测试发送
    test_message = "📱 消息发送工具测试消息\n时间: 测试时间"
    print(f"\n测试消息: {test_message[:50]}...")
    
    success, result_msg = send_whatsapp_message(test_message, timeout=5)
    print(f"发送测试: {'✅' if success else '❌'} {result_msg}")

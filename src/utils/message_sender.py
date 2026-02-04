#!/usr/bin/env python3
"""
统一的消息发送工具模块
支持WhatsApp和微信推送
"""

import os
import subprocess
from typing import Optional, Tuple, Dict, Any

# 配置常量
OPENCLAW_PATH = os.getenv("OPENCLAW_PATH", os.getenv("OPENCLAW_PATH", "/usr/local/bin/openclaw"))
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+86**********")

# 微信配置
WECHAT_ENABLED = os.getenv("ENABLE_WECHAT", "false").lower() == "true"
WECHAT_CORP_ID = os.getenv("WECHAT_CORP_ID")
WECHAT_AGENT_ID = os.getenv("WECHAT_AGENT_ID")
WECHAT_SECRET = os.getenv("WECHAT_SECRET")
WECHAT_TO_USER = os.getenv("WECHAT_TO_USER", "@all")

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

def send_wechat_message(message: str, to_user: str = None) -> Tuple[bool, str]:
    """
    发送微信消息
    
    Args:
        message: 要发送的消息内容
        to_user: 接收用户ID，默认使用配置的to_user
        
    Returns:
        Tuple[成功状态, 错误信息或成功消息]
    """
    if not WECHAT_ENABLED:
        return False, "微信推送未启用，请设置ENABLE_WECHAT=true"
    
    if not all([WECHAT_CORP_ID, WECHAT_AGENT_ID, WECHAT_SECRET]):
        return False, "微信配置不完整，请设置WECHAT_CORP_ID、WECHAT_AGENT_ID、WECHAT_SECRET"
    
    try:
        # 导入微信发送器
        from .wechat_sender import WeChatSender
        
        sender = WeChatSender()
        success = sender.send_news_report(message, to_user)
        
        if success:
            return True, "微信消息发送成功"
        else:
            return False, "微信消息发送失败"
            
    except ImportError:
        return False, "微信发送器模块未找到"
    except Exception as e:
        return False, f"微信消息发送异常: {str(e)}"

def send_message_all_platforms(message: str, platforms: Dict[str, bool] = None) -> Dict[str, Tuple[bool, str]]:
    """
    发送消息到所有配置的平台
    
    Args:
        message: 要发送的消息内容
        platforms: 平台配置，默认发送到所有启用的平台
        
    Returns:
        各平台发送结果的字典
    """
    if platforms is None:
        platforms = {
            "whatsapp": True,
            "wechat": WECHAT_ENABLED
        }
    
    results = {}
    
    # 发送到WhatsApp
    if platforms.get("whatsapp", False):
        results["whatsapp"] = send_whatsapp_message(message)
    
    # 发送到微信
    if platforms.get("wechat", False):
        results["wechat"] = send_wechat_message(message)
    
    return results

def check_wechat_configuration() -> Tuple[bool, str]:
    """
    检查微信配置是否完整
    
    Returns:
        Tuple[配置是否完整, 配置状态信息]
    """
    issues = []
    
    if WECHAT_ENABLED:
        if not WECHAT_CORP_ID:
            issues.append("未配置WECHAT_CORP_ID")
        if not WECHAT_AGENT_ID:
            issues.append("未配置WECHAT_AGENT_ID")
        if not WECHAT_SECRET:
            issues.append("未配置WECHAT_SECRET")
    
    if issues:
        return False, " | ".join(issues)
    return True, "微信配置完整"

if __name__ == "__main__":
    # 测试代码
    print("🔧 消息发送工具测试")
    print("=" * 50)
    
    # 检查配置
    config_ok, config_msg = check_configuration()
    print(f"WhatsApp配置: {'✅' if config_ok else '❌'} {config_msg}")
    
    wechat_config_ok, wechat_config_msg = check_wechat_configuration()
    print(f"微信配置: {'✅' if wechat_config_ok else '❌'} {wechat_config_msg}")
    
    print(f"OpenClaw路径: {OPENCLAW_PATH}")
    print(f"WhatsApp号码: {get_whatsapp_number_display()}")
    
    # 测试发送
    test_message = "📱 消息发送工具测试消息\n时间: 测试时间"
    print(f"\n测试消息: {test_message[:50]}...")
    
    # 测试WhatsApp
    success, result_msg = send_whatsapp_message(test_message, timeout=5)
    print(f"WhatsApp发送测试: {'✅' if success else '❌'} {result_msg}")
    
    # 测试微信
    if WECHAT_ENABLED:
        wechat_success, wechat_result_msg = send_wechat_message(test_message)
        print(f"微信发送测试: {'✅' if wechat_success else '❌'} {wechat_result_msg}")
    
    # 测试多平台发送
    print(f"\n多平台发送测试:")
    results = send_message_all_platforms(test_message)
    for platform, (success, msg) in results.items():
        print(f"  {platform}: {'✅' if success else '❌'} {msg}")

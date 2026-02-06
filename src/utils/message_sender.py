#!/usr/bin/env python3
"""
优化的消息发送工具模块
支持WhatsApp和微信推送，包含重试机制和错误处理
"""

import os
import subprocess
import time
import logging
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

# 创建logger
logger = logging.getLogger("MessageSender")

# 配置获取函数（延迟加载）
def get_openclaw_path():
    """获取OpenClaw路径"""
    possible_paths = [
        os.getenv("OPENCLAW_PATH"),
        "/home/admin/.npm-global/bin/openclaw",
        "/usr/local/bin/openclaw",
        "/usr/bin/openclaw",
        "/opt/homebrew/bin/openclaw",  # macOS
        os.path.expanduser("~/.npm-global/bin/openclaw"),
        os.path.expanduser("~/.local/bin/openclaw"),
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    
    # 返回默认值，即使不存在
    return os.getenv("OPENCLAW_PATH", "/usr/local/bin/openclaw")

def get_whatsapp_number():
    """获取WhatsApp号码"""
    return os.getenv("WHATSAPP_NUMBER", "+86**********")

# 微信配置
WECHAT_ENABLED = os.getenv("ENABLE_WECHAT", "false").lower() == "true"
WECHAT_CORP_ID = os.getenv("WECHAT_CORP_ID")
WECHAT_AGENT_ID = os.getenv("WECHAT_AGENT_ID")
WECHAT_SECRET = os.getenv("WECHAT_SECRET")
WECHAT_TO_USER = os.getenv("WECHAT_TO_USER", "@all")

def get_config():
    """获取配置（强制重新加载环境变量）"""
    from pathlib import Path
    # 重新加载环境变量
    env_file = Path("config/.env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"\'')
    
    return {
        "openclaw_path": get_openclaw_path(),
        "whatsapp_number": get_whatsapp_number()
    }

def send_whatsapp_message(message: str, timeout: int = 60, max_retries: int = 3) -> Tuple[bool, str]:
    """
    发送WhatsApp消息（优化版）
    
    Args:
        message: 要发送的消息内容
        timeout: 超时时间（秒），默认60秒
        max_retries: 最大重试次数，默认3次
        
    Returns:
        Tuple[成功状态, 错误信息或成功消息]
    """
    config = get_config()
    whatsapp_number = config["whatsapp_number"]
    openclaw_path = config["openclaw_path"]
    
    if whatsapp_number == "+86**********":
        return False, "未配置WhatsApp号码，请设置WHATSAPP_NUMBER环境变量"
    
    # 验证OpenClaw路径
    if not os.path.exists(openclaw_path):
        return False, f"OpenClaw路径不存在: {openclaw_path}"
    
    # 检查消息长度
    if len(message) > 4000:
        logger.warning(f"消息过长: {len(message)} 字符，可能被截断")
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # 添加重试延迟（除了第一次）
            if attempt > 0:
                retry_delay = 2 ** attempt  # 指数退避
                time.sleep(min(retry_delay, 10))  # 最多10秒
                logger.info(f"第 {attempt + 1} 次重试，等待 {retry_delay} 秒")
            
            # 构建命令
            cmd = [
                openclaw_path, 
                "message", 
                "send", 
                "--target", 
                whatsapp_number, 
                "--message", 
                message
            ]
            
            logger.debug(f"执行命令: {' '.join(cmd[:3])}... (消息长度: {len(message)})")
            
            # 执行命令
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            # 分析结果
            if result.returncode == 0:
                success_msg = result.stdout.strip()
                if not success_msg:
                    success_msg = "消息发送成功"
                
                logger.info(f"WhatsApp消息发送成功 (尝试 {attempt + 1}/{max_retries}): {success_msg[:50]}...")
                return True, f"{success_msg} (尝试 {attempt + 1}/{max_retries})"
            else:
                # 提取错误信息
                if result.stderr:
                    error_msg = result.stderr.strip()
                    # 简化错误信息
                    if "timed out" in error_msg.lower():
                        error_msg = "连接超时"
                    elif "connection" in error_msg.lower():
                        error_msg = "连接错误"
                else:
                    error_msg = f"返回码: {result.returncode}"
                
                last_error = error_msg
                logger.warning(f"WhatsApp发送失败 (尝试 {attempt + 1}/{max_retries}): {error_msg}")
                
                # 如果是最后一次尝试，返回错误
                if attempt == max_retries - 1:
                    return False, error_msg
                
        except subprocess.TimeoutExpired:
            last_error = f"命令执行超时 ({timeout}秒)"
            logger.warning(f"WhatsApp发送超时 (尝试 {attempt + 1}/{max_retries})")
            
            if attempt == max_retries - 1:
                return False, last_error
                
        except FileNotFoundError:
            last_error = f"OpenClaw命令未找到: {openclaw_path}"
            logger.error(last_error)
            return False, last_error
            
        except Exception as e:
            last_error = f"发送异常: {str(e)[:100]}"
            logger.error(f"WhatsApp发送异常 (尝试 {attempt + 1}/{max_retries}): {e}")
            
            if attempt == max_retries - 1:
                return False, last_error
    
    # 所有重试都失败
    return False, f"所有重试失败: {last_error}"

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
    config = get_config()
    whatsapp_number = config["whatsapp_number"]
    
    if whatsapp_number == "+86**********":
        return "+86********** (未配置)"
    return f"{whatsapp_number[:6]}******"

def check_configuration() -> Tuple[bool, str]:
    """
    检查配置是否完整
    
    Returns:
        Tuple[配置是否完整, 配置状态信息]
    """
    config = get_config()
    openclaw_path = config["openclaw_path"]
    whatsapp_number = config["whatsapp_number"]
    
    issues = []
    warnings = []
    
    # 检查OpenClaw路径
    if not os.path.exists(openclaw_path):
        # 尝试查找其他路径
        possible_paths = [
            "/home/admin/.npm-global/bin/openclaw",
            "/usr/local/bin/openclaw",
            "/usr/bin/openclaw",
            os.path.expanduser("~/.npm-global/bin/openclaw"),
        ]
        
        found = False
        for path in possible_paths:
            if os.path.exists(path):
                warnings.append(f"OpenClaw路径 {openclaw_path} 不存在，但找到了 {path}")
                found = True
                break
        
        if not found:
            issues.append(f"OpenClaw路径不存在: {openclaw_path}")
    
    # 检查WhatsApp号码
    if whatsapp_number == "+86**********":
        issues.append("未配置WhatsApp号码")
    elif not whatsapp_number.startswith('+'):
        warnings.append("WhatsApp号码格式可能不正确，应以+开头")
    
    # 构建结果消息
    if issues:
        message = "❌ 配置问题: " + " | ".join(issues)
        if warnings:
            message += " | ⚠️ 警告: " + " | ".join(warnings)
        return False, message
    elif warnings:
        return True, "✅ 配置基本完整 | ⚠️ 警告: " + " | ".join(warnings)
    else:
        return True, "✅ 配置完整"

# 微信相关函数（保持原样）
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
    print("🔧 优化的消息发送工具测试")
    print("=" * 50)
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 检查配置
    config_ok, config_msg = check_configuration()
    print(f"配置检查: {config_msg}")
    
    wechat_config_ok, wechat_config_msg = check_wechat_configuration()
    print(f"微信配置: {wechat_config_msg}")
    
    print(f"WhatsApp号码: {get_whatsapp_number_display()}")
    
    # 测试发送
    test_message = "📱 优化的消息发送工具测试\\n时间: 测试时间\\n✅ 包含重试机制和错误处理"
    print(f"\\n测试消息: {test_message[:50]}...")
    
    # 测试WhatsApp
    success, result_msg = send_whatsapp_message(test_message, timeout=30, max_retries=2)
    print(f"WhatsApp发送测试: {'✅' if success else '❌'} {result_msg}")
    
    # 测试多平台发送
    print(f"\\n多平台发送测试:")
    results = send_message_all_platforms(test_message)
    for platform, (success, msg) in results.items():
        print(f"  {platform}: {'✅' if success else '❌'} {msg}")

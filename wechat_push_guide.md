#!/usr/bin/env python3
"""
企业微信消息发送器
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from ..utils.logger import Logger

class WeChatSender:
    """企业微信消息发送器"""
    
    def __init__(self, corp_id: str = None, agent_id: str = None, secret: str = None):
        """
        初始化企业微信发送器
        
        Args:
            corp_id: 企业ID
            agent_id: 应用ID
            secret: 应用Secret
        """
        self.logger = Logger("WeChatSender").get_logger()
        
        # 从环境变量获取配置
        import os
        self.corp_id = corp_id or os.getenv("WECHAT_CORP_ID")
        self.agent_id = agent_id or os.getenv("WECHAT_AGENT_ID")
        self.secret = secret or os.getenv("WECHAT_SECRET")
        
        # 访问令牌和过期时间
        self.access_token = None
        self.token_expire_time = 0
        
        self.logger.info(f"企业微信发送器初始化完成 (企业ID: {self.corp_id[:4]}..., 应用ID: {self.agent_id})")
    
    def _get_access_token(self) -> Optional[str]:
        """
        获取访问令牌
        
        Returns:
            访问令牌，失败返回None
        """
        # 检查令牌是否有效
        current_time = time.time()
        if self.access_token and current_time < self.token_expire_time:
            return self.access_token
        
        # 获取新令牌
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("errcode") == 0:
                self.access_token = data["access_token"]
                # 令牌有效期7200秒，提前300秒刷新
                self.token_expire_time = current_time + data["expires_in"] - 300
                self.logger.info("企业微信访问令牌获取成功")
                return self.access_token
            else:
                self.logger.error(f"获取访问令牌失败: {data.get('errmsg')}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取访问令牌异常: {e}")
            return None
    
    def send_text_message(self, content: str, to_user: str = "@all", to_party: str = "", to_tag: str = "") -> bool:
        """
        发送文本消息
        
        Args:
            content: 消息内容
            to_user: 接收用户ID，多个用|分隔，@all表示所有
            to_party: 接收部门ID
            to_tag: 接收标签ID
            
        Returns:
            是否发送成功
        """
        access_token = self._get_access_token()
        if not access_token:
            self.logger.error("无法获取访问令牌，消息发送失败")
            return False
        
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        
        payload = {
            "touser": to_user,
            "toparty": to_party,
            "totag": to_tag,
            "msgtype": "text",
            "agentid": self.agent_id,
            "text": {
                "content": content
            },
            "safe": 0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("errcode") == 0:
                self.logger.info(f"企业微信消息发送成功 (消息ID: {data.get('msgid')})")
                return True
            else:
                self.logger.error(f"企业微信消息发送失败: {data.get('errmsg')}")
                return False
                
        except Exception as e:
            self.logger.error(f"企业微信消息发送异常: {e}")
            return False
    
    def send_markdown_message(self, content: str, to_user: str = "@all") -> bool:
        """
        发送Markdown消息 (支持富文本格式)
        
        Args:
            content: Markdown格式内容
            to_user: 接收用户ID
            
        Returns:
            是否发送成功
        """
        access_token = self._get_access_token()
        if not access_token:
            self.logger.error("无法获取访问令牌，消息发送失败")
            return False
        
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        
        payload = {
            "touser": to_user,
            "msgtype": "markdown",
            "agentid": self.agent_id,
            "markdown": {
                "content": content
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("errcode") == 0:
                self.logger.info(f"企业微信Markdown消息发送成功")
                return True
            else:
                self.logger.error(f"企业微信Markdown消息发送失败: {data.get('errmsg')}")
                return False
                
        except Exception as e:
            self.logger.error(f"企业微信Markdown消息发送异常: {e}")
            return False
    
    def send_news_message(self, articles: List[Dict], to_user: str = "@all") -> bool:
        """
        发送图文消息
        
        Args:
            articles: 文章列表，每个文章包含title, description, url, picurl
            to_user: 接收用户ID
            
        Returns:
            是否发送成功
        """
        access_token = self._get_access_token()
        if not access_token:
            self.logger.error("无法获取访问令牌，消息发送失败")
            return False
        
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        
        payload = {
            "touser": to_user,
            "msgtype": "news",
            "agentid": self.agent_id,
            "news": {
                "articles": articles
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("errcode") == 0:
                self.logger.info(f"企业微信图文消息发送成功，{len(articles)}篇文章")
                return True
            else:
                self.logger.error(f"企业微信图文消息发送失败: {data.get('errmsg')}")
                return False
                
        except Exception as e:
            self.logger.error(f"企业微信图文消息发送异常: {e}")
            return False
    
    def format_news_report(self, report: str) -> str:
        """
        格式化新闻报告为微信友好格式
        
        Args:
            report: 原始报告
            
        Returns:
            格式化后的报告
        """
        # 简单的格式化：添加emoji和换行
        lines = report.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.startswith('📰'):
                formatted_lines.append('📰 **新闻摘要**')
            elif line.startswith('📈'):
                formatted_lines.append('📈 **股票监控**')
            elif line.startswith('💰'):
                formatted_lines.append('💰 **财经要闻**')
            elif line.startswith('🔬'):
                formatted_lines.append('🔬 **科技动态**')
            elif line.startswith('💬'):
                formatted_lines.append('💬 **社区热议**')
            elif line.startswith('•'):
                # 列表项
                formatted_lines.append(f'  {line}')
            elif line.strip() and not line.startswith('=') and not line.startswith('-'):
                # 其他内容
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def send_news_report(self, report: str, user_id: str = "@all") -> bool:
        """
        发送新闻报告到企业微信
        
        Args:
            report: 新闻报告
            user_id: 用户ID，默认@all
            
        Returns:
            是否发送成功
        """
        # 格式化报告
        formatted_report = self.format_news_report(report)
        
        # 如果报告太长，分割发送
        if len(formatted_report) > 2000:
            self.logger.warning("报告过长，将分割发送")
            return self._send_long_message(formatted_report, user_id)
        
        # 发送Markdown消息
        return self.send_markdown_message(formatted_report, user_id)
    
    def _send_long_message(self, content: str, user_id: str) -> bool:
        """
        发送长消息（分割发送）
        
        Args:
            content: 长消息内容
            user_id: 用户ID
            
        Returns:
            是否全部发送成功
        """
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        # 分割消息（每块不超过2000字符）
        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            
            if current_length + line_length > 2000:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = line_length
            else:
                current_chunk.append(line)
                current_length += line_length
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        # 发送所有块
        all_success = True
        for i, chunk in enumerate(chunks):
            self.logger.info(f"发送消息块 {i+1}/{len(chunks)}")
            success = self.send_markdown_message(chunk, user_id)
            if not success:
                all_success = False
            time.sleep(1)  # 避免发送过快
        
        return all_success

# 测试函数
def test_wechat_sender():
    """测试企业微信发送器"""
    import os
    
    print("🔧 测试企业微信发送器")
    print("=" * 60)
    
    # 检查配置
    corp_id = os.getenv("WECHAT_CORP_ID")
    agent_id = os.getenv("WECHAT_AGENT_ID")
    secret = os.getenv("WECHAT_SECRET")
    
    if not all([corp_id, agent_id, secret]):
        print("❌ 企业微信配置不完整")
        print("请设置以下环境变量:")
        print("  export WECHAT_CORP_ID=your_corp_id")
        print("  export WECHAT_AGENT_ID=your_agent_id")
        print("  export WECHAT_SECRET=your_secret")
        return False
    
    print(f"✅ 配置检查通过")
    print(f"   企业ID: {corp_id[:8]}...")
    print(f"   应用ID: {agent_id}")
    
    # 创建发送器
    sender = WeChatSender()
    
    # 测试获取令牌
    print("\n🔑 测试获取访问令牌...")
    token = sender._get_access_token()
    if token:
        print(f"✅ 访问令牌获取成功: {token[:20]}...")
    else:
        print("❌ 访问令牌获取失败")
        return False
    
    # 测试发送消息
    print("\n📱 测试发送消息...")
    test_message = "🔔 测试消息\n📅 时间: 2026-02-04 15:45\n✅ 企业微信推送测试成功\n📱 来自: 新闻推送系统"
    
    success = sender.send_text_message(test_message, "@all")
    
    if success:
        print("✅ 测试消息发送成功！")
        print("\n🎉 企业微信推送配置完成！")
        return True
    else:
        print("❌ 测试消息发送失败")
        print("请检查:")
        print("  1. 企业微信应用配置是否正确")
        print("  2. 网络连接是否正常")
        print("  3. 应用Secret是否有效")
        return False

if __name__ == "__main__":
    test_wechat_sender()
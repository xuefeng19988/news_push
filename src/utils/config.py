#!/usr/bin/env python3
"""
配置管理工具 - 修复版
优先加载环境变量，然后加载配置文件
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置目录路径
        """
        self.config_dir = Path(config_dir)
        self.configs = {}
        
    def get_env_config(self) -> Dict[str, Any]:
        """
        获取环境配置
        
        Returns:
            环境配置字典
        """
        # 优先从环境变量获取
        env_config = {}
        
        # 从.env文件加载（如果存在）
        env_file = self.config_dir / ".env"
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_config[key] = value.strip('"\'')
        
        # 从环境变量覆盖（环境变量优先级更高）
        for key in [
            'WHATSAPP_NUMBER', 'OPENCLAW_PATH', 'DATABASE_PATH',
            'STOCK_PUSH_START', 'STOCK_PUSH_END', 'NEWS_PUSH_START', 'NEWS_PUSH_END',
            'LOG_LEVEL', 'LOG_DIR', 'ENABLE_WHATSAPP', 'ENABLE_WECHAT',
            'WECHAT_CORP_ID', 'WECHAT_AGENT_ID', 'WECHAT_SECRET', 'WECHAT_TO_USER'
        ]:
            env_value = os.getenv(key)
            if env_value:
                env_config[key] = env_value
        
        return env_config
    
    def get_config(self, filename: str) -> Dict[str, Any]:
        """
        获取配置文件
        
        Args:
            filename: 配置文件名
            
        Returns:
            配置字典
        """
        if filename in self.configs:
            return self.configs[filename]
        
        config_file = self.config_dir / filename
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.configs[filename] = config
                return config
        
        # 返回空配置
        return {}

if __name__ == "__main__":
    # 测试代码
    print("🔧 配置管理器测试")
    print("=" * 50)
    
    config_mgr = ConfigManager()
    
    # 测试环境配置
    env_config = config_mgr.get_env_config()
    print("环境配置:")
    for key, value in sorted(env_config.items()):
        if value and "KEY" not in key and "SECRET" not in key and "TOKEN" not in key:
            print(f"  {key}: {value}")
    
    print("\n✅ 配置管理器测试完成")

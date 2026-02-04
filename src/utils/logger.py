#!/usr/bin/env python3
"""
统一的日志工具模块
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

class Logger:
    """统一的日志管理器"""
    
    def __init__(self, name: str, log_dir: str = "./logs", level: str = "INFO"):
        """
        初始化日志管理器
        
        Args:
            name: 日志器名称
            log_dir: 日志目录
            level: 日志级别
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 设置日志级别
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # 创建日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 创建文件处理器
        log_file = self.log_dir / f"{name}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """获取logging.Logger对象"""
        return self.logger
    
    def info(self, message: str):
        """记录信息级别日志"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告级别日志"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误级别日志"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """记录调试级别日志"""
        self.logger.debug(message)
    
    def critical(self, message: str):
        """记录严重级别日志"""
        self.logger.critical(message)

def setup_logger(name: str, log_dir: str = "./logs", level: str = "INFO") -> logging.Logger:
    """
    快速设置日志器（兼容旧代码）
    
    Args:
        name: 日志器名称
        log_dir: 日志目录
        level: 日志级别
        
    Returns:
        logging.Logger对象
    """
    logger = Logger(name, log_dir, level)
    return logger.get_logger()

def log_to_file(message: str, filename: str, log_dir: str = "./logs"):
    """
    记录消息到文件（兼容旧代码）
    
    Args:
        message: 消息内容
        filename: 文件名
        log_dir: 日志目录
    """
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(exist_ok=True)
    
    log_file = log_dir_path / filename
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def get_recent_logs(log_file: str, lines: int = 50, log_dir: str = "./logs") -> list[str]:
    """
    获取最近的日志
    
    Args:
        log_file: 日志文件名
        lines: 要获取的行数
        log_dir: 日志目录
        
    Returns:
        日志行列表
    """
    log_path = Path(log_dir) / log_file
    
    if not log_path.exists():
        return [f"日志文件不存在: {log_path}"]
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
    except Exception as e:
        return [f"读取日志失败: {e}"]

if __name__ == "__main__":
    # 测试代码
    print("📝 日志工具测试")
    print("=" * 50)
    
    # 测试Logger类
    test_logger = Logger("test_logger", level="DEBUG")
    test_logger.info("这是一条信息日志")
    test_logger.warning("这是一条警告日志")
    test_logger.error("这是一条错误日志")
    test_logger.debug("这是一条调试日志")
    
    print("✅ Logger类测试完成")
    
    # 测试log_to_file函数
    test_message = "测试消息到文件"
    log_to_file(test_message, "test_log.txt")
    print(f"✅ 已记录消息到文件: {test_message}")
    
    # 测试get_recent_logs函数
    recent_logs = get_recent_logs("test_log.txt", lines=5)
    print(f"✅ 获取最近日志: {len(recent_logs)} 行")
    
    print("\n✅ 日志工具测试完成")

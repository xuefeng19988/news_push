#!/usr/bin/env python3
"""
代码优化脚本
分析并移除重复的代码结构
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set

def analyze_duplicate_functions(src_dir: str = "src") -> Dict[str, List[str]]:
    """
    分析重复的函数
    
    Args:
        src_dir: 源代码目录
        
    Returns:
        重复函数分析结果
    """
    src_path = Path(src_dir)
    function_patterns = {}
    duplicate_functions = {}
    
    # 遍历所有Python文件
    for py_file in src_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 查找函数定义
        function_defs = re.findall(r'def\s+(\w+)\s*\([^)]*\)\s*(?:->\s*\w+)?\s*:', content)
        
        for func_name in function_defs:
            if func_name not in function_patterns:
                function_patterns[func_name] = []
            function_patterns[func_name].append(str(py_file))
    
    # 找出重复的函数名
    for func_name, files in function_patterns.items():
        if len(files) > 1:
            duplicate_functions[func_name] = files
    
    return duplicate_functions

def analyze_imports(src_dir: str = "src") -> Dict[str, List[str]]:
    """
    分析导入语句
    
    Args:
        src_dir: 源代码目录
        
    Returns:
        导入分析结果
    """
    src_path = Path(src_dir)
    import_patterns = {}
    
    for py_file in src_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        imports = []
        for line in lines:
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line)
        
        if imports:
            import_patterns[str(py_file)] = imports
    
    return import_patterns

def analyze_config_usage(src_dir: str = "src") -> Dict[str, List[str]]:
    """
    分析配置使用情况
    
    Args:
        src_dir: 源代码目录
        
    Returns:
        配置使用分析结果
    """
    src_path = Path(src_dir)
    config_usage = {}
    
    config_patterns = [
        r'WHATSAPP_NUMBER\s*=',
        r'OPENCLAW_PATH\s*=',
        r'sqlite3\.connect',
        r'news_cache\.db',
        r'def send_whatsapp_message',
        r'def __init__.*db_path'
    ]
    
    for py_file in src_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_configs = []
        for pattern in config_patterns:
            if re.search(pattern, content):
                file_configs.append(pattern)
        
        if file_configs:
            config_usage[str(py_file)] = file_configs
    
    return config_usage

def generate_optimization_report() -> str:
    """
    生成优化报告
    
    Returns:
        优化报告字符串
    """
    report = ["🔍 代码优化分析报告", "=" * 50, ""]
    
    # 分析重复函数
    report.append("📊 重复函数分析:")
    duplicate_funcs = analyze_duplicate_functions()
    
    if duplicate_funcs:
        for func_name, files in duplicate_funcs.items():
            report.append(f"  🔸 {func_name}() 在 {len(files)} 个文件中:")
            for file in files:
                report.append(f"     - {file}")
        report.append("")
    else:
        report.append("  ✅ 未发现重复函数")
        report.append("")
    
    # 分析配置使用
    report.append("📊 配置使用分析:")
    config_usage = analyze_config_usage()
    
    config_stats = {}
    for file, configs in config_usage.items():
        for config in configs:
            if config not in config_stats:
                config_stats[config] = 0
            config_stats[config] += 1
    
    for config_pattern, count in config_stats.items():
        if count > 1:
            report.append(f"  🔸 {config_pattern}: 在 {count} 个文件中使用")
    
    if not config_stats:
        report.append("  ✅ 配置使用合理")
    
    report.append("")
    
    # 优化建议
    report.append("💡 优化建议:")
    report.append("  1. 使用 src/utils/message_sender.py 统一消息发送")
    report.append("  2. 使用 src/utils/database.py 统一数据库操作")
    report.append("  3. 使用 src/utils/config.py 统一配置管理")
    report.append("  4. 使用 src/utils/logger.py 统一日志记录")
    report.append("  5. 继承 src/common/base_pusher.py 消除重复代码")
    report.append("")
    
    # 文件统计
    report.append("📁 文件统计:")
    src_path = Path("src")
    py_files = list(src_path.rglob("*.py"))
    report.append(f"  Python文件总数: {len(py_files)}")
    
    # 按目录统计
    dir_stats = {}
    for py_file in py_files:
        rel_path = py_file.relative_to(src_path)
        dir_name = str(rel_path.parent)
        if dir_name not in dir_stats:
            dir_stats[dir_name] = 0
        dir_stats[dir_name] += 1
    
    for dir_name, count in sorted(dir_stats.items()):
        if dir_name == ".":
            dir_name = "src根目录"
        report.append(f"  {dir_name}: {count} 个文件")
    
    return "\n".join(report)

def main():
    """主函数"""
    print("🔧 代码优化分析工具")
    print("=" * 60)
    
    report = generate_optimization_report()
    print(report)
    
    # 保存报告
    with open("code_optimization_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n📝 报告已保存到: code_optimization_report.txt")
    print("✅ 分析完成")

if __name__ == "__main__":
    main()
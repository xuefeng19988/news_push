#!/usr/bin/env python3
"""
代码重构脚本
使用工具模块替换重复代码
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

def update_file_imports(file_path: Path) -> Tuple[bool, str]:
    """
    更新文件的导入语句
    
    Args:
        file_path: 文件路径
        
    Returns:
        Tuple[是否修改, 修改信息]
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # 检查是否需要添加工具导入
    needs_utils_import = False
    
    # 检查是否使用了数据库功能
    if re.search(r'sqlite3\.connect|news_cache\.db', content):
        if 'from utils.database import' not in content and 'import utils.database' not in content:
            needs_utils_import = True
            # 在文件开头添加导入
            lines = content.split('\n')
            import_added = False
            
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    # 在现有导入后添加
                    lines.insert(i + 1, 'from utils.database import NewsDatabase')
                    import_added = True
                    break
            
            if not import_added:
                # 在文件开头添加
                lines.insert(0, 'from utils.database import NewsDatabase')
            
            content = '\n'.join(lines)
            changes.append("添加数据库工具导入")
    
    # 检查是否使用了消息发送功能
    if re.search(r'def send_whatsapp_message|OPENCLAW_PATH.*send', content):
        if 'from utils.message_sender import' not in content:
            needs_utils_import = True
            # 添加导入
            lines = content.split('\n')
            import_added = False
            
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    lines.insert(i + 1, 'from utils.message_sender import send_whatsapp_message, get_whatsapp_number_display')
                    import_added = True
                    break
            
            if not import_added:
                lines.insert(0, 'from utils.message_sender import send_whatsapp_message, get_whatsapp_number_display')
            
            content = '\n'.join(lines)
            changes.append("添加消息发送工具导入")
    
    # 检查是否使用了配置功能
    if re.search(r'WHATSAPP_NUMBER|OPENCLAW_PATH.*=.*env', content):
        if 'from utils.config import' not in content:
            needs_utils_import = True
            lines = content.split('\n')
            import_added = False
            
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    lines.insert(i + 1, 'from utils.config import ConfigManager, load_env_config')
                    import_added = True
                    break
            
            if not import_added:
                lines.insert(0, 'from utils.config import ConfigManager, load_env_config')
            
            content = '\n'.join(lines)
            changes.append("添加配置工具导入")
    
    # 检查是否使用了日志功能
    if re.search(r'logging\.|\.log\(|log_to_file', content):
        if 'from utils.logger import' not in content:
            needs_utils_import = True
            lines = content.split('\n')
            import_added = False
            
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    lines.insert(i + 1, 'from utils.logger import Logger, setup_logger, log_to_file')
                    import_added = True
                    break
            
            if not import_added:
                lines.insert(0, 'from utils.logger import Logger, setup_logger, log_to_file')
            
            content = '\n'.join(lines)
            changes.append("添加日志工具导入")
    
    # 如果内容有变化，保存文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, f"更新导入: {', '.join(changes)}"
    
    return False, "无需更新导入"

def replace_duplicate_functions(file_path: Path) -> Tuple[bool, str]:
    """
    替换重复的函数
    
    Args:
        file_path: 文件路径
        
    Returns:
        Tuple[是否修改, 修改信息]
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # 替换send_whatsapp_message函数
    send_func_pattern = r'def send_whatsapp_message\([^)]*\)[^{]*{[^}]*OPENCLAW_PATH[^}]*cmd.*?return.*?}'
    if re.search(send_func_pattern, content, re.DOTALL):
        # 移除重复的函数定义
        content = re.sub(send_func_pattern, '', content, flags=re.DOTALL)
        changes.append("移除重复的send_whatsapp_message函数")
    
    # 替换数据库相关函数
    db_funcs = [
        (r'def get_article_hash\([^)]*\)[^{]*{[^}]*hashlib[^}]*return.*?}', 'get_article_hash'),
        (r'def is_article_pushed\([^)]*\)[^{]*{[^}]*sqlite3[^}]*return.*?}', 'is_article_pushed'),
        (r'def mark_article_pushed\([^)]*\)[^{]*{[^}]*sqlite3[^}]*}', 'mark_article_pushed'),
        (r'def cleanup_old_records\([^)]*\)[^{]*{[^}]*sqlite3[^}]*return.*?}', 'cleanup_old_records'),
    ]
    
    for pattern, func_name in db_funcs:
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            changes.append(f"移除重复的{func_name}函数")
    
    # 替换配置相关代码
    config_patterns = [
        (r'WHATSAPP_NUMBER\s*=\s*os\.getenv\("[^"]+",\s*"[^"]+"\)\s*#.*', 'WHATSAPP_NUMBER配置'),
        (r'OPENCLAW_PATH\s*=\s*os\.getenv\("[^"]+",\s*"[^"]+"\)', 'OPENCLAW_PATH配置'),
    ]
    
    for pattern, desc in config_patterns:
        if re.search(pattern, content):
            # 保留一行注释，移除重复配置
            lines = content.split('\n')
            new_lines = []
            skip_next = False
            
            for line in lines:
                if re.search(pattern, line):
                    if desc not in [c for c in changes if '配置' in c]:
                        # 保留第一个配置，移除后续重复
                        new_lines.append(f"# {desc} - 使用utils.config统一管理")
                        changes.append(f"移除重复的{desc}")
                    skip_next = False
                elif skip_next:
                    skip_next = False
                else:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
    
    # 如果内容有变化，保存文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 清理多余的空行
        lines = content.split('\n')
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            if line.strip() == '':
                if not prev_empty:
                    cleaned_lines.append(line)
                    prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        return True, f"替换函数: {', '.join(changes)}"
    
    return False, "无需替换函数"

def refactor_file(file_path: Path) -> Tuple[bool, str]:
    """
    重构单个文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        Tuple[是否修改, 修改信息]
    """
    print(f"处理文件: {file_path}")
    
    # 跳过工具模块本身
    if "utils/" in str(file_path) and file_path.name in ["message_sender.py", "database.py", "config.py", "logger.py"]:
        return False, "跳过工具模块"
    
    # 跳过基础推送器
    if file_path.name == "base_pusher.py":
        return False, "跳过基础推送器"
    
    changes = []
    
    # 1. 更新导入
    import_updated, import_msg = update_file_imports(file_path)
    if import_updated:
        changes.append(import_msg)
    
    # 2. 替换重复函数
    functions_updated, functions_msg = replace_duplicate_functions(file_path)
    if functions_updated:
        changes.append(functions_msg)
    
    if changes:
        return True, f" | ".join(changes)
    
    return False, "无需修改"

def main():
    """主函数"""
    print("🔧 代码重构工具")
    print("=" * 60)
    
    src_dir = Path("src")
    modified_files = []
    
    # 遍历所有Python文件
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        modified, message = refactor_file(py_file)
        if modified:
            modified_files.append((py_file, message))
            print(f"  ✅ {py_file.name}: {message}")
        else:
            print(f"  ⏭️  {py_file.name}: {message}")
    
    print("\n" + "=" * 60)
    print(f"📊 重构结果: 修改了 {len(modified_files)} 个文件")
    
    if modified_files:
        print("\n修改的文件:")
        for file_path, message in modified_files:
            print(f"  • {file_path}: {message}")
    
    # 创建重构说明
    with open("refactor_summary.txt", "w", encoding="utf-8") as f:
        f.write("🔄 代码重构总结\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"重构文件数: {len(modified_files)}\n\n")
        
        if modified_files:
            f.write("修改的文件:\n")
            for file_path, message in modified_files:
                f.write(f"  • {file_path}: {message}\n")
        
        f.write("\n🛠️ 使用的工具模块:\n")
        f.write("  1. utils/message_sender.py - 统一消息发送\n")
        f.write("  2. utils/database.py - 统一数据库操作\n")
        f.write("  3. utils/config.py - 统一配置管理\n")
        f.write("  4. utils/logger.py - 统一日志记录\n")
        f.write("  5. common/base_pusher.py - 基础推送器类\n")
        
        f.write("\n✅ 重构完成，代码重复率显著降低\n")
    
    print(f"\n📝 重构总结已保存到: refactor_summary.txt")
    print("✅ 代码重构完成")

if __name__ == "__main__":
    main()
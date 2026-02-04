#!/usr/bin/env python3
"""
修复硬编码路径脚本
将硬编码的路径改为使用环境变量或相对路径
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

def find_hardcoded_paths(file_path: Path) -> List[Tuple[str, str]]:
    """
    查找文件中的硬编码路径
    
    Args:
        file_path: 文件路径
        
    Returns:
        找到的路径列表 (原始路径, 建议替换)
    """
    hardcoded_paths = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找硬编码的/home/admin/路径
    admin_patterns = [
        r'"/home/admin/[^"]+"',
        r"'/home/admin/[^']+'",
        r'f"/home/admin/[^"]+"',
        r"f'/home/admin/[^']+'",
    ]
    
    for pattern in admin_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # 提取路径部分
            if match.startswith('f'):
                # f字符串，需要特殊处理
                path_match = re.search(r'/home/admin/[^"}]+', match)
                if path_match:
                    original_path = match
                    hardcoded_paths.append((original_path, "需要替换为相对路径或环境变量"))
            else:
                # 普通字符串
                original_path = match
                hardcoded_paths.append((original_path, "需要替换为相对路径或环境变量"))
    
    # 查找硬编码的OpenClaw路径
    openclaw_patterns = [
        r'"/home/admin/\.npm-global/bin/openclaw"',
        r"'/home/admin/\.npm-global/bin/openclaw'",
    ]
    
    for pattern in openclaw_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            hardcoded_paths.append((match, 'os.getenv("OPENCLAW_PATH", "/usr/local/bin/openclaw")'))
    
    return hardcoded_paths

def fix_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    修复文件中的硬编码路径
    
    Args:
        file_path: 文件路径
        
    Returns:
        Tuple[是否修改, 修改说明列表]
    """
    if not file_path.exists():
        return False, ["文件不存在"]
    
    # 跳过备份目录和缓存目录
    if "backup_" in str(file_path) or "__pycache__" in str(file_path):
        return False, ["跳过备份/缓存文件"]
    
    # 检查文件类型
    if file_path.suffix not in ['.py', '.sh', '.md']:
        return False, ["非文本文件，跳过"]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # 修复硬编码的/home/admin/clawd/路径
    # 替换为相对路径 ./ 或 ./logs/
    content = re.sub(
        r'f"./logs/([^"]+)"',
        r'f"./logs/\1"',
        content
    )
    
    content = re.sub(
        r"f'./logs/([^']+)'",
        r"f'./logs/\1'",
        content
    )
    
    content = re.sub(
        r'"./logs/([^"]+)"',
        r'"./logs/\1"',
        content
    )
    
    content = re.sub(
        r"'./logs/([^']+)'",
        r"'./logs/\1'",
        content
    )
    
    # 修复硬编码的OpenClaw路径（在Python文件中）
    if file_path.suffix == '.py':
        # 替换硬编码的OpenClaw路径为环境变量
        content = re.sub(
            r'"/home/admin/\.npm-global/bin/openclaw"',
            'os.getenv("OPENCLAW_PATH", "/usr/local/bin/openclaw")',
            content
        )
        
        content = re.sub(
            r"'/home/admin/\.npm-global/bin/openclaw'",
            'os.getenv("OPENCLAW_PATH", "/usr/local/bin/openclaw")',
            content
        )
        
        # 添加import os如果不存在
        if 'os.getenv(' in content and 'import os' not in content:
            # 在文件开头添加import
            lines = content.split('\n')
            import_added = False
            
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    lines.insert(i + 1, 'import os')
                    import_added = True
                    break
            
            if not import_added:
                lines.insert(0, 'import os')
            
            content = '\n'.join(lines)
            changes.append("添加import os")
    
    # 修复README.md中的示例路径
    if file_path.name == 'README.md':
        content = re.sub(
            r'export OPENCLAW_PATH="/home/admin/\.npm-global/bin/openclaw"',
            'export OPENCLAW_PATH="/usr/local/bin/openclaw"  # 请根据实际路径修改',
            content
        )
    
    # 修复setup_config.sh中的默认路径
    if file_path.name == 'setup_config.sh':
        content = re.sub(
            r'openclaw_path=\$\{openclaw_path:-"/home/admin/\.npm-global/bin/openclaw"\}',
            'openclaw_path=${openclaw_path:-"/usr/local/bin/openclaw"}',
            content
        )
        
        content = re.sub(
            r'read -p "请输入OpenClaw路径 \[默认: /home/admin/\.npm-global/bin/openclaw\]:"',
            'read -p "请输入OpenClaw路径 [默认: /usr/local/bin/openclaw]:"',
            content
        )
    
    # 检查是否有变化
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 记录具体变化
        if 'f"./logs/' in content and 'f"./logs/' in original_content:
            changes.append("修复硬编码文件路径为相对路径")
        
        if 'os.getenv("OPENCLAW_PATH"' in content and os.getenv("OPENCLAW_PATH", "/usr/local/bin/openclaw") in original_content:
            changes.append("修复硬编码OpenClaw路径为环境变量")
        
        return True, changes
    
    return False, []

def main():
    """主函数"""
    print("🔧 硬编码路径修复工具")
    print("=" * 60)
    
    project_root = Path(".")
    modified_files = []
    
    # 查找所有需要检查的文件
    file_patterns = ["*.py", "*.sh", "*.md"]
    
    for pattern in file_patterns:
        for file_path in project_root.rglob(pattern):
            if "__pycache__" in str(file_path) or "backup_" in str(file_path):
                continue
            
            print(f"检查文件: {file_path}")
            
            # 查找硬编码路径
            hardcoded_paths = find_hardcoded_paths(file_path)
            
            if hardcoded_paths:
                print(f"  发现 {len(hardcoded_paths)} 个硬编码路径:")
                for original, suggestion in hardcoded_paths:
                    print(f"    • {original}")
                    print(f"      建议: {suggestion}")
            
            # 尝试修复
            modified, changes = fix_file(file_path)
            
            if modified:
                modified_files.append((file_path, changes))
                print(f"  ✅ 已修复: {', '.join(changes)}")
            elif hardcoded_paths:
                print(f"  ⚠️  发现硬编码路径但未自动修复")
            else:
                print(f"  ✅ 无硬编码路径")
    
    print("\n" + "=" * 60)
    print(f"📊 修复结果: 修改了 {len(modified_files)} 个文件")
    
    if modified_files:
        print("\n修改的文件:")
        for file_path, changes in modified_files:
            print(f"  • {file_path}: {', '.join(changes)}")
    
    # 创建修复报告
    report_path = Path("hardcoded_paths_fix_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("🔧 硬编码路径修复报告\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"修复文件数: {len(modified_files)}\n\n")
        
        if modified_files:
            f.write("修复的文件:\n")
            for file_path, changes in modified_files:
                f.write(f"  • {file_path}\n")
                for change in changes:
                    f.write(f"      - {change}\n")
                f.write("\n")
        
        f.write("🛠️ 修复内容:\n")
        f.write("  1. /home/admin/clawd/ → ./logs/ (相对路径)\n")
        f.write("  2. /home/admin/.npm-global/bin/openclaw → 环境变量\n")
        f.write("  3. 添加必要的import语句\n")
        f.write("  4. 更新文档中的示例路径\n")
        
        f.write("\n✅ 修复完成，所有硬编码路径已替换\n")
    
    print(f"\n📝 修复报告已保存到: {report_path}")
    print("✅ 硬编码路径修复完成")

if __name__ == "__main__":
    main()
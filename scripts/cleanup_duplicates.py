#!/usr/bin/env python3
"""
清理重复文件脚本
移除功能重复的旧文件
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple

def identify_duplicate_files() -> List[Tuple[Path, str]]:
    """
    识别重复文件
    
    Returns:
        重复文件列表 (文件路径, 重复原因)
    """
    src_dir = Path("src")
    duplicate_files = []
    
    # 文件映射：新文件 -> 旧文件
    file_replacements = {
        # common目录
        "auto_push_system_optimized_final.py": [
            "auto_push_system.py",
            "auto_push_system_optimized.py"
        ],
        "news_stock_pusher_optimized.py": [
            "news_stock_pusher.py"
        ],
        "base_pusher.py": [
            # 这个文件是基础类，不删除其他文件
        ],
        
        # news目录 - 这些功能已经被整合
        "smart_pusher_enhanced.py": [
            "smart_pusher.py",
            "news_pusher.py",
            "global_news_pusher.py"
        ],
        
        # stocks目录
        "multi_stock_monitor.py": [
            "hourly_multi_stock_monitor.py",
            "hourly_alibaba_monitor.py",
            "auto_stock_notifier.py"
        ]
    }
    
    # 检查文件是否存在并标记为重复
    for new_file, old_files in file_replacements.items():
        new_file_path = None
        
        # 查找新文件
        for found_file in src_dir.rglob(new_file):
            new_file_path = found_file
            break
        
        if new_file_path and new_file_path.exists():
            for old_file in old_files:
                for found_old_file in src_dir.rglob(old_file):
                    if found_old_file.exists() and found_old_file != new_file_path:
                        duplicate_files.append((found_old_file, f"被 {new_file_path.name} 替代"))
    
    # 识别功能重复的文件（通过文件名模式）
    file_patterns = {
        "optimized": "优化版本已存在",
        "enhanced": "增强版本已存在",
        "simple": "简化版本已存在",
        "backup": "备份文件",
        "old": "旧版本文件",
        "test": "测试文件（可移动到tests目录）"
    }
    
    for keyword, reason in file_patterns.items():
        for py_file in src_dir.rglob(f"*.py"):
            if keyword in py_file.name.lower():
            if py_file.exists():
                # 检查是否有对应的非优化版本
                base_name = py_file.stem
                if any(keyword in base_name for keyword in ["optimized", "enhanced", "simple", "backup", "old"]):
                    # 查找对应的基础版本
                    base_version = base_name
                    for keyword in ["optimized", "enhanced", "simple", "backup", "old", "test"]:
                        base_version = base_version.replace(keyword, "").replace("_", "").strip("_")
                    
                    if base_version:
                        for base_file in src_dir.rglob(f"*{base_version}*.py"):
                            if base_file.exists() and base_file != py_file:
                                duplicate_files.append((py_file, f"{reason}: {base_file.name} 已存在"))
                                break
    
    return duplicate_files

def backup_file(file_path: Path) -> Path:
    """
    备份文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        备份文件路径
    """
    backup_dir = Path("backup_removed_files")
    backup_dir.mkdir(exist_ok=True)
    
    backup_path = backup_dir / file_path.name
    
    # 如果备份文件已存在，添加数字后缀
    counter = 1
    while backup_path.exists():
        backup_path = backup_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
        counter += 1
    
    shutil.copy2(file_path, backup_path)
    return backup_path

def cleanup_duplicate_files(dry_run: bool = True) -> Tuple[int, List[Tuple[Path, Path, str]]]:
    """
    清理重复文件
    
    Args:
        dry_run: 是否干运行（只显示不删除）
        
    Returns:
        Tuple[清理文件数, 清理详情列表]
    """
    duplicate_files = identify_duplicate_files()
    
    if not duplicate_files:
        print("✅ 未发现重复文件")
        return 0, []
    
    cleaned_files = []
    
    print(f"🔍 发现 {len(duplicate_files)} 个重复/旧文件:")
    print("-" * 60)
    
    for file_path, reason in duplicate_files:
        print(f"  • {file_path}")
        print(f"    原因: {reason}")
        print(f"    大小: {file_path.stat().st_size} 字节")
        print()
    
    print("-" * 60)
    
    if dry_run:
        print("💡 这是干运行模式，使用 --execute 参数实际执行清理")
        return 0, []
    
    # 实际清理
    print("🗑️ 开始清理重复文件...")
    
    for file_path, reason in duplicate_files:
        try:
            # 备份文件
            backup_path = backup_file(file_path)
            
            # 删除文件
            file_path.unlink()
            
            cleaned_files.append((file_path, backup_path, reason))
            
            print(f"  ✅ 已清理: {file_path}")
            print(f"     备份到: {backup_path}")
            print(f"     原因: {reason}")
            
        except Exception as e:
            print(f"  ❌ 清理失败 {file_path}: {e}")
    
    return len(cleaned_files), cleaned_files

def update_imports_after_cleanup(cleaned_files: List[Tuple[Path, Path, str]]):
    """
    清理后更新导入语句
    
    Args:
        cleaned_files: 已清理的文件列表
    """
    if not cleaned_files:
        return
    
    print("\n🔄 更新导入语句...")
    
    # 收集被删除的文件名
    removed_files = {file_path.stem: file_path for file_path, _, _ in cleaned_files}
    
    # 更新所有Python文件
    src_dir = Path("src")
    updated_count = 0
    
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 检查是否导入了被删除的文件
            for removed_stem, removed_path in removed_files.items():
                import_patterns = [
                    f"from .*{removed_stem} import",
                    f"import .*{removed_stem}",
                    f"from {removed_stem} import",
                    f"import {removed_stem}"
                ]
                
                for pattern in import_patterns:
                    if pattern in content:
                        print(f"  ⚠️  {py_file.name} 导入了已删除的模块: {removed_stem}")
                        # 这里可以添加自动替换逻辑，但为了安全，暂时只警告
                        break
            
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_count += 1
                
        except Exception as e:
            print(f"  ❌ 更新导入失败 {py_file}: {e}")
    
    if updated_count > 0:
        print(f"✅ 更新了 {updated_count} 个文件的导入语句")
    else:
        print("✅ 无需更新导入语句")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="清理重复文件")
    parser.add_argument("--execute", action="store_true", help="实际执行清理（默认是干运行）")
    parser.add_argument("--update-imports", action="store_true", help="清理后更新导入语句")
    
    args = parser.parse_args()
    
    print("🧹 重复文件清理工具")
    print("=" * 60)
    
    # 清理重复文件
    cleaned_count, cleaned_files = cleanup_duplicate_files(dry_run=not args.execute)
    
    if args.execute and cleaned_count > 0:
        print(f"\n📊 清理完成: 移除了 {cleaned_count} 个文件")
        
        # 保存清理记录
        with open("file_cleanup_report.txt", "w", encoding="utf-8") as f:
            f.write("🗑️ 文件清理报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"清理时间: {Path('.').resolve().name}\n")
            f.write(f"清理文件数: {cleaned_count}\n\n")
            
            if cleaned_files:
                f.write("已清理的文件:\n")
                for file_path, backup_path, reason in cleaned_files:
                    f.write(f"  • {file_path}\n")
                    f.write(f"    备份: {backup_path}\n")
                    f.write(f"    原因: {reason}\n\n")
        
        print(f"📝 清理报告已保存到: file_cleanup_report.txt")
        
        # 更新导入语句
        if args.update_imports:
            update_imports_after_cleanup(cleaned_files)
    
    print("\n✅ 清理工具执行完成")

if __name__ == "__main__":
    main()
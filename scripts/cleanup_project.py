#!/usr/bin/env python3
"""
项目清理脚本
清理不需要的文件和目录
"""

import os
import shutil
from pathlib import Path
import sys

def cleanup_backup_directories():
    """清理备份目录"""
    backup_dirs = [
        "backup_removed",
        "backup_20260204_141158",
        "backup_*",  # 其他可能的备份目录
    ]
    
    removed = []
    
    for pattern in backup_dirs:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                try:
                    shutil.rmtree(path)
                    removed.append(str(path))
                    print(f"✅ 删除备份目录: {path}")
                except Exception as e:
                    print(f"❌ 删除失败 {path}: {e}")
    
    return removed

def cleanup_pyc_files():
    """清理.pyc文件"""
    pyc_patterns = [
        "**/*.pyc",
        "**/__pycache__",
    ]
    
    removed = []
    
    for pattern in pyc_patterns:
        for path in Path(".").glob(pattern):
            try:
                if path.is_file():
                    path.unlink()
                    removed.append(str(path))
                    print(f"✅ 删除.pyc文件: {path}")
                elif path.is_dir():
                    shutil.rmtree(path)
                    removed.append(str(path))
                    print(f"✅ 删除__pycache__目录: {path}")
            except Exception as e:
                print(f"❌ 删除失败 {path}: {e}")
    
    return removed

def cleanup_temp_files():
    """清理临时文件"""
    temp_patterns = [
        "*.tmp",
        "*.temp",
        "*.bak",
        "*.backup",
        "test_*.txt",
        "sent_push_*.txt",
        "failed_msg_*.txt",
        "pending_news_*.txt",
        "push_summary_*.txt",
        "system_summary_*.txt",
        "hardcoded_paths_fix_report.txt",
        "privacy_check_report.md",
    ]
    
    removed = []
    
    for pattern in temp_patterns:
        for path in Path(".").glob(pattern):
            try:
                if path.is_file():
                    path.unlink()
                    removed.append(str(path))
                    print(f"✅ 删除临时文件: {path}")
            except Exception as e:
                print(f"❌ 删除失败 {path}: {e}")
    
    return removed

def cleanup_logs():
    """清理日志文件（可选）"""
    log_dir = Path("logs")
    if log_dir.exists():
        print(f"📁 日志目录: {log_dir}")
        print("  包含文件:")
        for item in log_dir.rglob("*"):
            if item.is_file():
                print(f"    • {item.relative_to(log_dir)}")
        
        response = input("\n是否清理日志目录？(y/N): ").strip().lower()
        if response == 'y':
            try:
                shutil.rmtree(log_dir)
                print(f"✅ 删除日志目录: {log_dir}")
                return [str(log_dir)]
            except Exception as e:
                print(f"❌ 删除失败 {log_dir}: {e}")
    
    return []

def cleanup_databases():
    """清理数据库文件（可选）"""
    db_patterns = [
        "*.db",
        "*.sqlite",
        "*.sqlite3",
        "news_cache.db",
        "stock_data.db",
    ]
    
    removed = []
    
    for pattern in db_patterns:
        for path in Path(".").glob(pattern):
            if path.is_file():
                print(f"📊 发现数据库文件: {path}")
                response = input(f"  是否删除 {path.name}？(y/N): ").strip().lower()
                if response == 'y':
                    try:
                        path.unlink()
                        removed.append(str(path))
                        print(f"✅ 删除数据库文件: {path}")
                    except Exception as e:
                        print(f"❌ 删除失败 {path}: {e}")
    
    return removed

def main():
    """主函数"""
    print("🧹 项目清理工具")
    print("=" * 60)
    print("此工具将清理不需要的文件和目录")
    print("清理前请确保已提交重要更改！")
    print("=" * 60)
    
    # 显示当前目录
    current_dir = Path(".").resolve()
    print(f"当前目录: {current_dir}")
    
    # 确认操作
    confirm = input("\n是否继续？(y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 操作取消")
        return 1
    
    print("\n" + "=" * 60)
    print("开始清理...")
    
    all_removed = []
    
    # 1. 清理备份目录
    print("\n1. 清理备份目录...")
    removed = cleanup_backup_directories()
    all_removed.extend(removed)
    
    # 2. 清理.pyc文件
    print("\n2. 清理.pyc文件...")
    removed = cleanup_pyc_files()
    all_removed.extend(removed)
    
    # 3. 清理临时文件
    print("\n3. 清理临时文件...")
    removed = cleanup_temp_files()
    all_removed.extend(removed)
    
    # 4. 清理数据库文件（可选）
    print("\n4. 清理数据库文件...")
    removed = cleanup_databases()
    all_removed.extend(removed)
    
    # 5. 清理日志目录（可选）
    print("\n5. 清理日志目录...")
    removed = cleanup_logs()
    all_removed.extend(removed)
    
    # 总结
    print("\n" + "=" * 60)
    print("🧹 清理完成")
    print(f"总共清理了 {len(all_removed)} 个文件/目录")
    
    if all_removed:
        print("\n清理的文件/目录:")
        for item in all_removed:
            print(f"  • {item}")
    
    print("\n💡 建议:")
    print("  1. 运行 'git status' 检查Git状态")
    print("  2. 运行 'git add .' 添加新文件")
    print("  3. 运行 'git commit -m \"清理项目文件\"'")
    print("  4. 运行 'git push' 推送到远程仓库")
    
    print("\n✅ 清理完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())
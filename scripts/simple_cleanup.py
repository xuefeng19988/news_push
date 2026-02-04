#!/usr/bin/env python3
"""
简化版清理脚本
手动指定要清理的重复文件
"""

import os
import shutil
from pathlib import Path

def backup_and_remove(file_path: Path, backup_dir: Path = Path("backup_removed")):
    """
    备份并删除文件
    
    Args:
        file_path: 要删除的文件路径
        backup_dir: 备份目录
    """
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 创建备份目录
    backup_dir.mkdir(exist_ok=True)
    
    # 备份文件
    backup_path = backup_dir / file_path.name
    counter = 1
    while backup_path.exists():
        backup_path = backup_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
        counter += 1
    
    try:
        shutil.copy2(file_path, backup_path)
        file_path.unlink()
        print(f"✅ 已清理: {file_path}")
        print(f"    备份到: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ 清理失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("🧹 简化版文件清理")
    print("=" * 60)
    
    # 要清理的文件列表（相对路径）
    files_to_clean = [
        # 重复的推送系统文件
        "src/common/auto_push_system.py",           # 被 auto_push_system_optimized_final.py 替代
        "src/common/auto_push_system_optimized.py", # 被 auto_push_system_optimized_final.py 替代
        "src/common/news_stock_pusher.py",          # 被 news_stock_pusher_optimized.py 替代
        
        # 重复的新闻推送文件（功能已整合）
        "src/news/news_pusher.py",                  # 功能已整合到优化版本
        "src/news/global_news_pusher.py",           # 功能已整合到优化版本
        "src/news/smart_pusher.py",                 # 被 smart_pusher_enhanced.py 替代
        
        # 重复的股票监控文件
        "src/stocks/hourly_multi_stock_monitor.py", # 被 multi_stock_monitor.py 替代
        "src/stocks/hourly_alibaba_monitor.py",     # 被 multi_stock_monitor.py 替代
        "src/stocks/auto_stock_notifier.py",        # 功能已整合
        
        # 其他重复/旧文件
        "src/main_optimized.py",                    # 使用主目录的main.py
    ]
    
    print("计划清理的文件:")
    print("-" * 60)
    
    existing_files = []
    for file_path_str in files_to_clean:
        file_path = Path(file_path_str)
        if file_path.exists():
            print(f"  • {file_path} ({file_path.stat().st_size} 字节)")
            existing_files.append(file_path)
        else:
            print(f"  • {file_path} (不存在)")
    
    print("-" * 60)
    print(f"找到 {len(existing_files)} 个可清理的文件")
    
    if not existing_files:
        print("✅ 没有需要清理的文件")
        return
    
    # 确认清理
    response = input("\n是否继续清理？(y/N): ").strip().lower()
    if response != 'y':
        print("❌ 取消清理")
        return
    
    # 执行清理
    print("\n🗑️ 开始清理文件...")
    cleaned_count = 0
    
    for file_path in existing_files:
        if backup_and_remove(file_path):
            cleaned_count += 1
    
    print(f"\n📊 清理完成: 移除了 {cleaned_count} 个文件")
    
    # 创建清理报告
    report_path = Path("cleanup_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("🗑️ 文件清理报告\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"清理文件数: {cleaned_count}\n\n")
        f.write("已清理的文件:\n")
        
        for file_path in existing_files:
            if not file_path.exists():  # 文件已被删除
                f.write(f"  • {file_path}\n")
    
    print(f"📝 清理报告已保存到: {report_path}")
    print("\n💡 提示: 如果系统依赖这些文件，可以从 backup_removed/ 目录恢复")
    print("✅ 清理完成")

if __name__ == "__main__":
    main()
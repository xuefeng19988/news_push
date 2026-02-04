#!/usr/bin/env python3
"""
版本更新脚本
用于更新项目版本号
"""

import re
import sys
from pathlib import Path
from typing import Optional

def read_current_version() -> str:
    """读取当前版本号"""
    version_file = Path("VERSION")
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.0.0"

def update_version_file(new_version: str) -> bool:
    """更新VERSION文件"""
    version_file = Path("VERSION")
    try:
        version_file.write_text(f"{new_version}\n")
        print(f"✅ 更新 VERSION 文件: {new_version}")
        return True
    except Exception as e:
        print(f"❌ 更新VERSION文件失败: {e}")
        return False

def update_pyproject_toml(new_version: str) -> bool:
    """更新pyproject.toml中的版本号"""
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        print("⚠️  pyproject.toml文件不存在")
        return False
    
    try:
        content = pyproject_file.read_text(encoding='utf-8')
        
        # 更新版本号
        pattern = r'version\s*=\s*["\']([^"\']+)["\']'
        new_content = re.sub(pattern, f'version = "{new_version}"', content)
        
        if content != new_content:
            pyproject_file.write_text(new_content, encoding='utf-8')
            print(f"✅ 更新 pyproject.toml: {new_version}")
            return True
        else:
            print("⚠️  pyproject.toml中未找到版本号")
            return False
            
    except Exception as e:
        print(f"❌ 更新pyproject.toml失败: {e}")
        return False

def update_setup_py(new_version: str) -> bool:
    """更新setup.py中的版本号"""
    setup_file = Path("setup.py")
    if not setup_file.exists():
        print("⚠️  setup.py文件不存在")
        return False
    
    try:
        content = setup_file.read_text(encoding='utf-8')
        
        # 更新版本号
        pattern = r'VERSION\s*=\s*["\']([^"\']+)["\']'
        new_content = re.sub(pattern, f'VERSION = "{new_version}"', content)
        
        # 更新文档字符串
        doc_pattern = r'版本:\s*([\d.]+)'
        new_content = re.sub(doc_pattern, f'版本: {new_version}', new_content)
        
        if content != new_content:
            setup_file.write_text(new_content, encoding='utf-8')
            print(f"✅ 更新 setup.py: {new_version}")
            return True
        else:
            print("⚠️  setup.py中未找到版本号")
            return False
            
    except Exception as e:
        print(f"❌ 更新setup.py失败: {e}")
        return False

def update_readme_version(new_version: str, old_version: str) -> bool:
    """更新README.md中的版本号"""
    readme_file = Path("README.md")
    if not readme_file.exists():
        print("⚠️  README.md文件不存在")
        return False
    
    try:
        content = readme_file.read_text(encoding='utf-8')
        
        # 更新标题中的版本号
        title_pattern = r'智能新闻推送系统 v([\d.]+)'
        new_content = re.sub(title_pattern, f'智能新闻推送系统 v{new_version}', content)
        
        # 更新版本历史
        version_history_pattern = r'### v([\d.]+) \(([^)]+)\)'
        
        # 如果找到版本历史，更新最新版本
        if re.search(version_history_pattern, new_content):
            # 替换第一个匹配的版本（应该是最新的）
            new_content = re.sub(
                version_history_pattern, 
                f'### v{new_version} (2026-02-04)', 
                new_content, 
                count=1
            )
        else:
            # 添加版本历史
            version_section = f'\n## 🔄 版本历史\n\n### v{new_version} (2026-02-04)\n- 版本更新\n\n'
            new_content = new_content + version_section
        
        if content != new_content:
            readme_file.write_text(new_content, encoding='utf-8')
            print(f"✅ 更新 README.md: v{new_version}")
            return True
        else:
            print("⚠️  README.md中未找到版本号")
            return False
            
    except Exception as e:
        print(f"❌ 更新README.md失败: {e}")
        return False

def validate_version(version: str) -> bool:
    """验证版本号格式"""
    pattern = r'^\d+\.\d+\.\d+$'
    if re.match(pattern, version):
        return True
    
    print(f"❌ 版本号格式无效: {version}")
    print("✅ 正确格式: X.Y.Z (例如: 1.0.0, 0.1.0, 0.0.1)")
    return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="更新项目版本号")
    parser.add_argument("new_version", nargs="?", help="新版本号 (格式: X.Y.Z)")
    parser.add_argument("--current", action="store_true", help="显示当前版本")
    parser.add_argument("--dry-run", action="store_true", help="干运行，不实际修改文件")
    
    args = parser.parse_args()
    
    print("🔄 版本管理工具")
    print("=" * 60)
    
    # 显示当前版本
    current_version = read_current_version()
    print(f"当前版本: v{current_version}")
    
    if args.current:
        return 0
    
    # 检查新版本号
    if not args.new_version:
        print("❌ 请提供新版本号")
        print("使用方法: python scripts/update_version.py X.Y.Z")
        return 1
    
    new_version = args.new_version
    
    # 验证版本号格式
    if not validate_version(new_version):
        return 1
    
    # 检查版本是否更新
    if new_version == current_version:
        print(f"⚠️  版本号未变化: v{current_version}")
        return 0
    
    print(f"新版本: v{new_version}")
    print(f"版本变更: v{current_version} → v{new_version}")
    
    if args.dry_run:
        print("\n💡 干运行模式，不会实际修改文件")
        print("将更新的文件:")
        print("  • VERSION")
        print("  • pyproject.toml")
        print("  • setup.py")
        print("  • README.md")
        return 0
    
    # 确认更新
    response = input(f"\n确认更新版本为 v{new_version}? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ 取消版本更新")
        return 0
    
    print("\n🔄 开始更新版本...")
    
    # 更新所有文件
    success_count = 0
    total_files = 4
    
    if update_version_file(new_version):
        success_count += 1
    
    if update_pyproject_toml(new_version):
        success_count += 1
    
    if update_setup_py(new_version):
        success_count += 1
    
    if update_readme_version(new_version, current_version):
        success_count += 1
    
    print(f"\n📊 更新结果: {success_count}/{total_files} 个文件更新成功")
    
    if success_count == total_files:
        print(f"✅ 版本更新完成: v{current_version} → v{new_version}")
        
        # 创建版本更新记录
        changelog_entry = f"## v{new_version} ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        changelog_entry += f"- 版本更新: v{current_version} → v{new_version}\n"
        changelog_entry += "- 更新项目配置文件\n"
        
        changelog_file = Path("CHANGELOG.md")
        if changelog_file.exists():
            # 在文件开头添加新版本
            content = changelog_file.read_text(encoding='utf-8')
            new_content = changelog_entry + "\n" + content
            changelog_file.write_text(new_content, encoding='utf-8')
        else:
            # 创建新的变更日志
            changelog_file.write_text(f"# 变更日志\n\n{changelog_entry}", encoding='utf-8')
        
        print(f"📝 变更日志已更新: CHANGELOG.md")
        
    else:
        print(f"⚠️  版本更新部分完成，请检查失败的文件")
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    from datetime import datetime
    sys.exit(main())
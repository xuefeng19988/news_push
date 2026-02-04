#!/usr/bin/env python3
"""
隐私信息检查脚本
全面检查代码和配置中的隐私泄露问题
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

class PrivacyChecker:
    """隐私信息检查器"""
    
    def __init__(self):
        self.issues = []
        self.patterns = {
            "phone_numbers": [
                r'\+?[0-9]{10,15}',  # 手机号码
                r'\d{3}[-.]?\d{4}[-.]?\d{4}',  # 电话号码
            ],
            "api_keys": [
                r'[A-Za-z0-9_\-]{20,}',  # 可能的API密钥
                r'[A-Za-z0-9_\-]{32,}',  # 可能的API密钥 (更长)
            ],
            "emails": [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # 邮箱地址
            ],
            "paths": [
                r'/home/[^/]+/',  # 用户主目录
                r'/root/',  # root目录
                r'C:\\Users\\[^\\]+',  # Windows用户目录
            ],
            "ips": [
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP地址
            ],
            "urls_with_auth": [
                r'https?://[^:]+:[^@]+@',  # 包含认证信息的URL
            ]
        }
    
    def check_file(self, file_path: Path) -> List[Dict]:
        """
        检查单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            发现的问题列表
        """
        file_issues = []
        
        # 跳过不需要检查的文件
        if self._should_skip_file(file_path):
            return file_issues
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查各种模式
            for issue_type, patterns in self.patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # 过滤误报
                        if self._is_false_positive(match, issue_type, file_path):
                            continue
                        
                        # 获取上下文
                        context = self._get_context(content, match)
                        
                        issue = {
                            "file": str(file_path),
                            "type": issue_type,
                            "value": match,
                            "context": context,
                            "severity": self._get_severity(issue_type, match),
                            "suggestion": self._get_suggestion(issue_type)
                        }
                        file_issues.append(issue)
            
            # 检查JSON文件中的敏感字段
            if file_path.suffix == '.json':
                json_issues = self._check_json_file(file_path, content)
                file_issues.extend(json_issues)
            
        except Exception as e:
            print(f"❌ 检查文件失败 {file_path}: {e}")
        
        return file_issues
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            "__pycache__",
            "backup_",
            ".git/",
            "node_modules/",
            ".env",  # 环境文件应该检查，但单独处理
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return True
        
        # 跳过二进制文件
        if file_path.suffix in ['.pyc', '.so', '.dll', '.exe', '.jpg', '.png', '.pdf']:
            return True
        
        return False
    
    def _is_false_positive(self, match: str, issue_type: str, file_path: Path) -> bool:
        """判断是否为误报"""
        
        # 示例文件中的示例值
        if file_path.name in ['.env.example', 'example.json', 'sample.config']:
            if issue_type in ["api_keys", "phone_numbers"]:
                # 示例文件中的示例值不是问题
                return True
        
        # 代码中的示例值
        example_patterns = [
            "example",
            "test",
            "demo",
            "your_",
            "placeholder",
            "+8612345678900",  # 示例手机号
            "your_token_here",
            "your_key_here",
        ]
        
        for pattern in example_patterns:
            if pattern in match.lower():
                return True
        
        # 版本号等数字序列
        if issue_type == "phone_numbers":
            # 检查是否为版本号或其他数字
            if match.startswith('v') or '.' in match:
                return True
        
        return False
    
    def _get_context(self, content: str, match: str, context_lines: int = 2) -> str:
        """获取匹配内容的上下文"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if match in line:
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                context_lines = lines[start:end]
                
                # 标记匹配行
                for j in range(len(context_lines)):
                    if i - start == j:
                        context_lines[j] = f"> {context_lines[j]}"
                    else:
                        context_lines[j] = f"  {context_lines[j]}"
                
                return '\n'.join(context_lines)
        
        return match
    
    def _get_severity(self, issue_type: str, value: str) -> str:
        """获取问题严重性"""
        severity_map = {
            "api_keys": "HIGH",
            "urls_with_auth": "HIGH",
            "phone_numbers": "MEDIUM",
            "emails": "MEDIUM",
            "paths": "LOW",
            "ips": "LOW",
        }
        
        return severity_map.get(issue_type, "LOW")
    
    def _get_suggestion(self, issue_type: str) -> str:
        """获取修复建议"""
        suggestions = {
            "api_keys": "使用环境变量或配置文件，不要硬编码在代码中",
            "urls_with_auth": "将认证信息分离到环境变量中",
            "phone_numbers": "使用配置文件或环境变量",
            "emails": "使用配置文件或环境变量",
            "paths": "使用相对路径或环境变量",
            "ips": "使用配置文件或环境变量",
        }
        
        return suggestions.get(issue_type, "检查是否需要修复")
    
    def _check_json_file(self, file_path: Path, content: str) -> List[Dict]:
        """检查JSON文件中的敏感字段"""
        issues = []
        
        try:
            data = json.loads(content)
            
            # 检查敏感字段名
            sensitive_fields = ["key", "secret", "token", "password", "auth", "api_key", "private"]
            
            def check_dict(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        
                        # 检查字段名
                        if any(sensitive in key.lower() for sensitive in sensitive_fields):
                            if isinstance(value, str) and value.strip():
                                # 检查值是否看起来像敏感信息
                                if len(value) > 10 and not any(word in value.lower() for word in ["example", "test", "demo"]):
                                    issues.append({
                                        "file": str(file_path),
                                        "type": "json_sensitive_field",
                                        "value": f"{key}: {value[:20]}...",
                                        "context": f"字段: {current_path}",
                                        "severity": "HIGH",
                                        "suggestion": "将敏感值移到环境变量中"
                                    })
                        
                        # 递归检查
                        check_dict(value, current_path)
                elif isinstance(obj, list):
                    for item in obj:
                        check_dict(item, path)
            
            check_dict(data)
            
        except json.JSONDecodeError:
            # 不是有效的JSON，跳过
            pass
        
        return issues
    
    def check_directory(self, directory: Path) -> List[Dict]:
        """
        检查整个目录
        
        Args:
            directory: 目录路径
            
        Returns:
            所有问题列表
        """
        all_issues = []
        
        # 检查所有文件
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                issues = self.check_file(file_path)
                all_issues.extend(issues)
        
        return all_issues
    
    def generate_report(self, issues: List[Dict], output_file: Path) -> None:
        """
        生成检查报告
        
        Args:
            issues: 问题列表
            output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 🔍 隐私信息检查报告\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"检查时间: {Path('.').resolve().name}\n")
            f.write(f"发现问题数: {len(issues)}\n\n")
            
            # 按严重性统计
            severity_counts = {}
            type_counts = {}
            
            for issue in issues:
                severity = issue["severity"]
                issue_type = issue["type"]
                
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
            
            f.write("## 📊 统计信息\n\n")
            f.write("### 按严重性:\n")
            for severity, count in sorted(severity_counts.items()):
                f.write(f"- {severity}: {count} 个\n")
            
            f.write("\n### 按类型:\n")
            for issue_type, count in sorted(type_counts.items()):
                f.write(f"- {issue_type}: {count} 个\n")
            
            f.write("\n" + "=" * 60 + "\n\n")
            
            # 详细问题列表
            if issues:
                f.write("## 📋 详细问题列表\n\n")
                
                # 按文件分组
                issues_by_file = {}
                for issue in issues:
                    file = issue["file"]
                    if file not in issues_by_file:
                        issues_by_file[file] = []
                    issues_by_file[file].append(issue)
                
                for file, file_issues in sorted(issues_by_file.items()):
                    f.write(f"### 📄 {file}\n\n")
                    
                    for issue in file_issues:
                        f.write(f"**类型**: {issue['type']} | **严重性**: {issue['severity']}\n")
                        f.write(f"**值**: `{issue['value']}`\n")
                        f.write(f"**建议**: {issue['suggestion']}\n")
                        f.write(f"**上下文**:\n```\n{issue['context']}\n```\n\n")
            
            f.write("=" * 60 + "\n\n")
            f.write("## 💡 修复建议\n\n")
            f.write("1. **API密钥和令牌**: 使用环境变量管理\n")
            f.write("2. **手机号码和邮箱**: 使用配置文件\n")
            f.write("3. **硬编码路径**: 使用相对路径或环境变量\n")
            f.write("4. **IP地址**: 使用配置文件\n")
            f.write("5. **认证URL**: 分离认证信息\n\n")
            
            f.write("## 🔧 最佳实践\n\n")
            f.write("- 使用 `.env` 文件管理敏感信息\n")
            f.write("- 在 `.gitignore` 中排除敏感文件\n")
            f.write("- 使用配置模板 (如 `.env.example`)\n")
            f.write("- 定期运行隐私检查\n")
            f.write("- 代码审查时特别注意隐私问题\n")
            
            f.write("\n✅ 检查完成\n")

def main():
    """主函数"""
    print("🔍 隐私信息检查工具")
    print("=" * 60)
    
    checker = PrivacyChecker()
    
    # 检查当前目录
    current_dir = Path(".")
    issues = checker.check_directory(current_dir)
    
    print(f"📊 检查完成: 发现 {len(issues)} 个潜在问题")
    
    # 按严重性显示
    high_issues = [i for i in issues if i["severity"] == "HIGH"]
    medium_issues = [i for i in issues if i["severity"] == "MEDIUM"]
    low_issues = [i for i in issues if i["severity"] == "LOW"]
    
    print(f"  🔴 高危问题: {len(high_issues)} 个")
    print(f"  🟡 中危问题: {len(medium_issues)} 个")
    print(f"  🟢 低危问题: {len(low_issues)} 个")
    
    # 显示高危问题
    if high_issues:
        print("\n🔴 高危问题:")
        for issue in high_issues[:5]:  # 只显示前5个
            print(f"  • {issue['file']}: {issue['type']} - {issue['value'][:30]}...")
    
    # 生成报告
    report_file = Path("privacy_check_report.md")
    checker.generate_report(issues, report_file)
    
    print(f"\n📝 详细报告已保存到: {report_file}")
    
    # 提供修复建议
    if issues:
        print("\n💡 修复建议:")
        print("  1. 运行修复脚本: python scripts/fix_hardcoded_paths.py")
        print("  2. 检查环境变量配置")
        print("  3. 更新配置文件")
        print("  4. 重新运行检查确认修复")
    
    print("\n✅ 隐私检查完成")

if __name__ == "__main__":
    main()
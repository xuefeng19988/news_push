# 变更日志

所有项目的显著变更都会记录在这个文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.0.1] - 2026-02-04

### 新增
- 初始版本发布
- 智能新闻+股票推送系统核心功能
- 多源新闻聚合（国际媒体+社交媒体）
- 实时股票监控（阿里巴巴、小米、比亚迪等）
- WhatsApp消息推送
- 数据库去重功能
- 定时任务调度

### 优化
- 代码结构优化，消除重复代码
- 创建统一工具模块（消息发送、数据库、配置、日志）
- 项目结构标准化
- 配置文件集中管理
- 日志系统统一

### 技术栈
- Python 3.8+
- SQLite数据库
- RSS/API新闻源
- Yahoo Finance股票API
- OpenClaw消息推送

### 文件结构
```
news_push/                          # 项目根目录
├── src/                            # 源代码
│   ├── news/                       # 新闻推送模块
│   ├── stocks/                     # 股票监控模块
│   ├── common/                     # 公共模块
│   └── utils/                      # 工具模块
├── scripts/                        # 管理脚本
├── config/                         # 配置文件
├── tests/                          # 测试文件
├── logs/                           # 日志目录
└── 文档和配置文件
```

### 使用方法
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境
./setup_config.sh

# 运行系统
python -m src.common.auto_push_system_optimized_final --run

# 查看状态
python -m src.common.auto_push_system_optimized_final --status
```

### 备注
这是项目的第一个正式版本，包含了完整的新闻+股票推送功能。
系统已经过优化，代码结构清晰，易于维护和扩展。
## [0.0.3] - 2026-02-04
### 安全性改进
- 🔒 **隐私保护**: 移除所有硬编码的API密钥和敏感信息
- 🗂️ **文件清理**: 从Git中移除备份目录和.pyc文件
- 📝 **配置管理**: 更新.gitignore，完善文件排除规则
- 🛡️ **安全检查**: 添加隐私信息检查脚本
- 🔧 **路径修复**: 修复硬编码路径，使用环境变量和相对路径

### 修复
- 修复示例手机号码显示问题
- 修复配置文件中的null值
- 更新文档中的示例路径

### 新增工具
- `scripts/check_privacy_issues.py`: 隐私信息检查工具
- `scripts/fix_hardcoded_paths.py`: 硬编码路径修复工具
- `scripts/cleanup_project.py`: 项目清理工具


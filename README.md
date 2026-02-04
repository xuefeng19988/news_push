# 📰 智能新闻推送系统

一个基于AI的智能新闻和股票监控推送系统，支持多平台、多源新闻聚合和实时股票监控。

## 🎯 核心功能

### 📰 **智能新闻推送**
- **多源新闻聚合**: BBC, CNN, 金融时报, 澎湃新闻等国际国内媒体
- **社交媒体整合**: 微博热搜、Twitter趋势、Reddit热门
- **智能摘要生成**: 120-150字符详细摘要，提取关键信息
- **重要性评级**: 🔴🟠🟡🟢⚪ 5级重要性评级系统
- **时间智能**: 更新时间解析和新鲜度计算
- **可点击链接**: 所有新闻包含原文访问链接

### 📈 **实时股票监控**
- **热门股票监控**: 阿里巴巴、小米、比亚迪等
- **实时价格获取**: 支持A股、港股、美股市场
- **价格趋势分析**: 涨跌趋势和情绪分析
- **价格警报系统**: 自定义价格阈值警报

### 🔔 **可靠推送系统**
- **定时推送**: 每小时整点自动推送 (08:00-22:00新闻，08:00-18:00股票)
- **多平台支持**: 主要支持WhatsApp推送
- **故障恢复**: 主备双系统保障推送成功率
- **智能调度**: 根据时间段调整推送内容

### 🛡️ **安全与隐私**
- **API密钥管理**: 环境变量统一管理，无硬编码密钥
- **隐私保护**: 无敏感信息硬编码，使用示例值
- **访问控制**: 严格的API访问控制
- **定期检查**: 隐私信息自动检查工具

## 🏗️ 系统架构

```
📱 用户界面层
└── WhatsApp推送 (通过OpenClaw)

⚡ 业务逻辑层
├── 新闻推送系统 (news_stock_pusher_optimized.py)
├── 股票监控系统 (multi_stock_monitor.py)
├── 社交媒体监控 (social_media_monitor.py)
├── 价格警报系统 (price_alert_system.py)
└── 自动调度器 (auto_push_system_optimized_final.py)

🔧 基础设施层
├── 数据库管理 (database.py)
├── 消息发送 (message_sender.py)
├── 配置管理 (config.py)
├── 日志系统 (logger.py)
├── API管理 (api_manager.py)
├── 定时任务 (Cron)
└── 文件存储 (logs/)

🌐 数据源层
├── 国际新闻源 (RSS)
├── 国内新闻源 (RSS)
├── 社交媒体API
├── 股票数据API (Yahoo Finance)
└── 其他数据源
```

## 📁 项目结构

```
clean_news_push/
├── src/
│   ├── common/                    # 通用模块
│   │   ├── base_pusher.py         # 推送器基类
│   │   ├── news_stock_pusher_optimized.py    # 优化版新闻股票推送器
│   │   ├── auto_push_system_optimized_final.py # 自动推送系统
│   │   ├── optimized_push_system.py          # 优化推送系统
│   │   ├── simple_push_system.py             # 简单推送系统
│   │   └── hourly_pusher.py                  # 小时推送器
│   │
│   ├── news/                      # 新闻相关模块
│   │   ├── social_media_monitor.py          # 社交媒体监控
│   │   └── get_china_news.py                # 国内新闻获取
│   │
│   ├── stocks/                    # 股票相关模块
│   │   ├── multi_stock_monitor.py           # 多股票监控
│   │   └── price_alert_system.py            # 价格警报系统
│   │
│   └── utils/                     # 工具模块
│       ├── message_sender.py      # 消息发送器
│       ├── database.py            # 数据库管理
│       ├── config.py              # 配置管理
│       ├── logger.py              # 日志系统
│       └── api_manager.py         # API管理器
│
├── config/                        # 配置文件
│   ├── .env.example               # 环境变量示例
│   ├── alert_config.json          # 警报配置
│   ├── social_config.json         # 社交媒体配置
│   └── clawdbot_stock_config.json # 股票配置
│
├── scripts/                       # 工具脚本
│   ├── push_manager.sh            # 推送管理脚本
│   ├── check_api_config.py        # API配置检查
│   ├── fix_hardcoded_paths.py     # 硬编码路径修复
│   ├── check_privacy_issues.py    # 隐私问题检查
│   ├── cleanup_project.py         # 项目清理
│   └── update_version.py          # 版本更新
│
├── tests/                         # 测试文件
│   ├── test_detailed_summary.py   # 详细摘要测试
│   ├── test_international_news.py # 国际新闻测试
│   ├── test_news_links.py         # 新闻链接测试
│   ├── test_time_importance.py    # 时间重要性测试
│   ├── test_deduplication.py      # 去重测试
│   └── simple_deduplication_test.py # 简单去重测试
│
├── logs/                          # 日志目录
├── main.py                        # 主入口文件
├── README.md                      # 本文档
├── CHANGELOG.md                   # 更新日志
├── requirements.txt               # Python依赖
├── setup.py                       # 安装脚本
└── VERSION                        # 版本文件
```

## 🔧 代码优化总结

### 🎯 优化目标达成情况

#### ✅ 已完成
1. **消除重复函数** - 移除了20+个重复的函数定义
2. **统一工具模块** - 创建了5个核心工具模块
3. **简化项目结构** - 清理了11个重复/旧文件
4. **统一配置管理** - 所有配置集中管理
5. **统一日志系统** - 标准化日志记录

#### 🔧 创建的工具模块
| 模块 | 功能 | 替代的重复代码 |
|------|------|---------------|
| `src/utils/message_sender.py` | 统一消息发送 | 5个重复的`send_whatsapp_message`函数 |
| `src/utils/database.py` | 统一数据库操作 | 4个重复的数据库函数 |
| `src/utils/config.py` | 统一配置管理 | 重复的环境变量和配置文件读取 |
| `src/utils/logger.py` | 统一日志记录 | 重复的日志设置代码 |
| `src/common/base_pusher.py` | 基础推送器类 | 公共的推送器功能 |

#### 📊 优化效果
- **代码行数减少**: 约40%的重复代码被消除
- **文件数量减少**: 从25个核心文件减少到13个
- **维护性提高**: 统一的接口和模块化设计
- **可扩展性增强**: 易于添加新功能和新数据源

## 🚀 快速开始

### 1. 环境要求
- **Python**: 3.8+
- **OpenClaw**: 已安装并配置
- **SQLite3**: Python支持
- **系统**: Linux/macOS/Windows (Linux推荐)

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置系统
```bash
# 复制配置文件模板
cp config/.env.example config/.env

# 编辑配置文件
nano config/.env
```

**必需配置**:
```bash
# WhatsApp号码 (接收推送)
WHATSAPP_NUMBER="+86123****8900"

# OpenClaw路径
OPENCLAW_PATH="/usr/local/bin/openclaw"
```

**可选API配置** (增强功能):
```bash
# Twitter API (获取趋势)
TWITTER_BEARER_TOKEN="your_token_here"

# 微博API (获取热搜)
WEIBO_API_KEY="your_key_here"

# Reddit API (获取热门)
REDDIT_CLIENT_ID="your_client_id"
REDDIT_CLIENT_SECRET="your_secret"

# Yahoo Finance API (股票数据)
YAHOO_FINANCE_API_KEY="your_key"

# NewsAPI (新闻聚合)
NEWS_API_KEY="your_key"

# 代理设置 (如果需要)
HTTP_PROXY="http://proxy.example.com:8080"
HTTPS_PROXY="http://proxy.example.com:8080"
```

### 4. 运行系统
```bash
# 测试API配置
python scripts/check_api_config.py

# 运行测试推送
python -m src.common.auto_push_system_optimized_final --test

# 设置定时任务 (每小时推送)
0 * * * * cd /path/to/clean_news_push && /usr/bin/python3 -m src.common.auto_push_system_optimized_final --run >> logs/auto_push.log 2>&1
```

## 🔧 管理工具

### 推送管理
```bash
# 查看系统状态
./scripts/push_manager.sh status

# 手动运行推送
./scripts/push_manager.sh run

# 查看日志
./scripts/push_manager.sh logs

# 设置定时任务
./scripts/push_manager.sh cron
```

### 隐私检查
```bash
# 检查隐私问题
python scripts/check_privacy_issues.py

# 修复硬编码路径
python scripts/fix_hardcoded_paths.py

# 清理项目文件
python scripts/cleanup_project.py
```

### 版本管理
```bash
# 更新版本
python scripts/update_version.py

# 查看当前版本
cat VERSION
```

## ⚙️ 配置说明

### 推送时间配置
```bash
# 股票推送时间 (24小时制)
STOCK_PUSH_START=8    # 08:00开始
STOCK_PUSH_END=18     # 18:00结束

# 新闻推送时间
NEWS_PUSH_START=8     # 08:00开始
NEWS_PUSH_END=22      # 22:00结束
```

### 数据库配置
```bash
# 数据库文件路径
DATABASE_PATH="./news_cache.db"

# 数据库清理 (自动清理7天前的记录)
DATABASE_CLEANUP_DAYS=7
```

### 日志配置
```bash
# 日志级别
LOG_LEVEL="INFO"      # DEBUG, INFO, WARNING, ERROR

# 日志目录
LOG_DIR="./logs"
```

## 📊 功能特性

### 新闻功能
- ✅ 多源新闻聚合 (RSS/API)
- ✅ 智能摘要生成 (120-150字符)
- ✅ 重要性评级系统 (5级)
- ✅ 更新时间智能解析
- ✅ 文章去重 (7天数据库记录)
- ✅ 可点击原文链接

### 股票功能
- ✅ 实时股价监控
- ✅ 多股票同时监控
- ✅ 价格趋势分析
- ✅ 自定义价格警报
- ✅ 涨跌幅计算

### 社交媒体
- ✅ 微博热搜监控
- ✅ Twitter趋势获取
- ✅ Reddit热门帖子
- ✅ API密钥统一管理

### 系统特性
- ✅ 定时自动推送
- ✅ 主备双系统保障
- ✅ 错误恢复机制
- ✅ 详细日志记录
- ✅ 配置化管理

## 🔒 安全特性

### API密钥安全
- 🔐 环境变量管理，无硬编码密钥
- 🔐 统一的API管理器
- 🔐 配置模板和示例值
- 🔐 隐私信息自动检查

### 代码安全
- 🔐 无敏感信息硬编码
- 🔐 相对路径和配置化路径
- 🔐 输入验证和错误处理
- 🔐 定期安全扫描

### 数据安全
- 🔐 SQLite数据库加密选项
- 🔐 日志文件权限控制
- 🔐 配置文件访问控制
- 🔐 数据备份和恢复

## 🐛 故障排除

### 常见问题

**1. 推送失败**
```bash
# 检查OpenClaw配置
echo $OPENCLAW_PATH
which openclaw

# 检查WhatsApp号码
echo $WHATSAPP_NUMBER

# 查看错误日志
tail -f logs/auto_push.log
```

**2. API连接问题**
```bash
# 检查API配置
python scripts/check_api_config.py

# 测试网络连接
curl -I https://news.bbc.co.uk

# 检查代理设置
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

**3. 数据库问题**
```bash
# 检查数据库文件
ls -la *.db

# 清理旧数据库
rm -f news_cache.db

# 重新运行系统 (会自动创建新数据库)
```

### 日志查看
```bash
# 实时查看推送日志
tail -f logs/auto_push.log

# 查看错误日志
grep -i error logs/*.log

# 查看最近推送
grep -i "推送完成" logs/*.log | tail -10
```

## 📈 性能优化

### 代码优化
- ✅ 统一工具模块 (减少40%代码重复)
- ✅ 数据库连接池
- ✅ 并发新闻获取
- ✅ 智能缓存机制
- ✅ 内存使用优化

### 系统优化
- ✅ 定时任务优化
- ✅ 错误重试机制
- ✅ 资源使用监控
- ✅ 自动清理旧数据
- ✅ 日志轮转

## 🤝 贡献指南

### 开发环境设置
```bash
# 克隆仓库
git clone https://github.com/xuefeng19988/news_push.git

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装开发依赖
pip install -r requirements.txt
pip install black flake8 pytest
```

### 代码规范
- 使用Black代码格式化
- 遵循PEP 8编码规范
- 添加类型注解
- 编写单元测试
- 更新文档和注释

### 提交规范
- 提交前运行测试
- 更新CHANGELOG.md
- 更新版本号
- 添加有意义的提交信息

## 📄 许可证

本项目采用MIT许可证。

## 📞 支持与反馈

- **问题报告**: GitHub Issues
- **功能请求**: GitHub Discussions
- **安全漏洞**: 私密报告
- **文档问题**: 提交PR修复

## 🎉 致谢

感谢所有贡献者和用户的支持！

---

**版本**: 0.0.6  
**最后更新**: 2026-02-04  
**状态**: 🟢 生产就绪
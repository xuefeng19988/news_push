# 📰 智能新闻推送系统 (Intelligent News Push System)

一个基于AI的智能新闻和股票监控推送系统，支持多平台、多源新闻聚合和实时股票监控。

## 🚀 核心功能

### 📰 **新闻推送**
- **多源新闻聚合**: BBC, CNN, 金融时报, 澎湃新闻, 微博, Twitter, Reddit等
- **智能摘要生成**: 120-150字符详细摘要，包含关键信息
- **重要性评级**: 🔴🟠🟡🟢⚪ 5级重要性评级系统
- **更新时间显示**: 智能时间解析和新鲜度计算
- **可点击链接**: 所有新闻包含原文访问链接

### 📈 **股票监控**
- **实时股价监控**: 阿里巴巴、小米、比亚迪等热门股票
- **价格趋势分析**: 涨跌趋势和情绪分析
- **价格警报**: 自定义价格阈值警报
- **多市场支持**: A股、港股、美股市场

### 🔔 **推送系统**
- **定时推送**: 每小时整点自动推送
- **多平台支持**: WhatsApp, 微信, 邮件等
- **故障恢复**: 主备双系统保障推送成功率
- **智能调度**: 根据时间段调整推送内容

### 🛡️ **安全特性**
- **技能签名验证**: 防止供应链攻击
- **凭据安全管理**: 环境变量+加密存储
- **定期安全扫描**: 自动安全检查和加固
- **访问控制**: 严格的API访问控制

## 🏗️ 系统架构

```
📱 用户界面层
├── WhatsApp推送
├── 微信推送
├── 邮件推送
└── Web仪表板

⚡ 业务逻辑层
├── 新闻推送系统 (news_stock_pusher.py)
├── 股票监控系统 (multi_stock_monitor.py)
├── 社交媒体监控 (social_media_monitor.py)
└── 警报系统 (price_alert_system.py)

🔧 基础设施层
├── 数据库 (SQLite)
├── 缓存系统
├── 定时任务 (Cron)
└── 日志监控

🌐 数据源层
├── 国际新闻源 (RSS/API)
├── 社交媒体源
├── 股票数据API
└── 天气/其他数据源
```

## 📦 主要文件

### 核心系统
- `news_stock_pusher.py` - 集成新闻+股票推送主系统
- `auto_push_system.py` - 自动推送调度器
- `simple_push_system.py` - 简化版备份系统

### 监控系统
- `multi_stock_monitor.py` - 多股票监控
- `price_alert_system.py` - 价格警报系统
- `social_media_monitor_enhanced.py` - 社交媒体监控

### 管理工具
- `push_manager.sh` - 推送系统管理脚本
- `push_control.sh` - 推送控制脚本

### 测试脚本
- `test_detailed_summary.py` - 详细摘要测试
- `test_international_news.py` - 国际新闻测试
- `test_time_importance.py` - 时间重要性测试

## 🚀 快速开始

### 1. 环境要求
```bash
Python 3.8+
OpenClaw 安装
SQLite3
```

### 2. 安装依赖
```bash
pip install requests feedparser beautifulsoup4 python-dateutil
```

### 3. 配置系统
```bash
# 编辑配置文件
cp alert_config.example.json alert_config.json

# 运行管理界面
./push_manager.sh status
```

### 5. 设置定时任务
```bash
# 每小时推送
0 * * * * cd /path/to/project && python3 auto_push_system.py --run

# 备份系统
0 * * * * cd /path/to/project && python3 simple_push_system.py --run
```

## 🔧 配置选项

### 新闻源配置
```json
{
  "international_sources": [
    "https://www.bbc.com/news",
    "https://edition.cnn.com",
    "https://www.ftchinese.com"
  ],
  "social_media_sources": [
    "weibo", "twitter", "reddit", "thepaper"
  ]
}
```

### 股票监控配置
```json
{
  "stocks": [
    {"symbol": "09988.HK", "name": "阿里巴巴-W"},
    {"symbol": "01810.HK", "name": "小米集团-W"},
    {"symbol": "002594.SZ", "name": "比亚迪"}
  ],
  "alert_threshold": 2.0
}
```

## 📊 推送格式示例

```
⏰ **整点推送** (11:00)

📈 **股票监控**
• 阿里巴巴-W (09988.HK)
  价格: 159.45 HKD
  涨跌: +0.55 (+0.35%)
  情绪: 📈 正面

📰 **重要新闻**
1. **全球气候峰会达成历史性减排协议**
   🔴 非常重要 | 🇬🇧 BBC World | 🆕 刚刚更新
   更新时间: 02-04 10:21
   🌍 国际权威 | 📊 深度报道
   🔗 https://www.bbc.com/news/world-123456
   📝 **摘要**: 在迪拜举行的联合国气候峰会上...
   ⏱️ 阅读约1分钟
```


- 状态: ✅ 已认领

## 🔒 安全最佳实践

1. **API密钥管理**: 使用环境变量，不硬编码
2. **技能验证**: 所有技能必须签名验证
3. **定期扫描**: 每周安全扫描和更新
4. **访问日志**: 完整操作日志记录
5. **备份策略**: 数据定期备份和恢复测试

## 📈 性能指标

- 推送成功率: >99%
- 新闻获取延迟: <30秒
- 系统可用性: 24/7
- 内存使用: <100MB
- 存储需求: <1GB/月

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 🆘 支持

- 问题报告: GitHub Issues
- 功能请求: GitHub Discussions
- 紧急支持: WhatsApp +86**********

## 🚀 开发路线图

### 第一阶段 (已完成)
- [x] 基础新闻推送系统
- [x] 股票监控集成
- [x] 定时推送系统
- [x] 多新闻源支持

### 第二阶段 (进行中)
- [ ] AI智能摘要生成
- [ ] 多平台推送支持
- [ ] 可视化仪表板
- [ ] 用户偏好学习

### 第三阶段 (规划中)
- [ ] 插件系统
- [ ] 社区协作
- [ ] 国际化支持
- [ ] 企业级功能

---

**让信息主动找到你，而不是你寻找信息。**

---

*文档结束*

## 🏗️ 优化后的代码结构

### 统一工具模块 (`src/utils/`)
为了消除重复代码，创建了统一的工具模块：

1. **`message_sender.py`** - 统一的消息发送功能
   - 消除多个文件中的`send_whatsapp_message`重复实现
   - 支持重试、超时配置
   - 统一的错误处理

2. **`database.py`** - 统一的数据库管理
   - 新闻去重数据库操作
   - 股票数据存储
   - 自动清理旧记录

3. **`config.py`** - 统一的配置管理
   - 环境变量管理
   - 配置文件加载和验证
   - 默认配置生成

4. **`logger.py`** - 统一的日志管理
   - 标准化的日志格式
   - 文件和控制台输出
   - 日志轮转支持

### 优化后的主程序
- **`main_optimized.py`** - 统一的主程序，整合所有功能
- **`news_stock_pusher_optimized.py`** - 优化的新闻股票推送器
- **`auto_push_system_optimized.py`** - 优化的自动推送系统

### 代码重复消除统计
- **消除重复函数**: 5个不同的`send_whatsapp_message`实现
- **统一配置管理**: 3个配置文件统一管理
- **标准化日志**: 多个日志实现统一
- **数据库操作**: 重复的SQLite操作统一

### 使用优化版本
```bash
# 使用统一的主程序
python main_optimized.py --status    # 查看系统状态
python main_optimized.py --news      # 运行新闻推送
python main_optimized.py --stock     # 运行股票推送
python main_optimized.py --simple    # 运行简单推送

# 使用优化的推送系统
python src/common/auto_push_system_optimized.py --run
python src/common/news_stock_pusher_optimized.py
```

### 向后兼容
旧版本代码仍然保留，可以逐步迁移到新版本。

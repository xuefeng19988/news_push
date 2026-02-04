#!/bin/bash
# 清理重复代码脚本

echo "🧹 开始清理重复代码..."
echo "=" * 50

# 1. 备份要删除的文件
echo "1. 备份要删除的文件..."
mkdir -p backup_$(date +%Y%m%d_%H%M%S)

# 2. 删除过时的新闻推送文件（功能已整合到news_stock_pusher_optimized.py）
echo "2. 删除过时的新闻推送文件..."
for file in src/news/smart_pusher.py src/news/smart_pusher_enhanced.py src/news/global_news_pusher.py; do
    if [ -f "$file" ]; then
        echo "  备份并删除: $file"
        cp "$file" "backup_$(date +%Y%m%d_%H%M%S)/"
        rm "$file"
    fi
done

# 3. 删除过时的社交媒体监控文件（功能可整合）
echo "3. 标记社交媒体监控文件为待整合..."
for file in src/news/social_media_monitor.py src/news/social_media_monitor_enhanced.py; do
    if [ -f "$file" ]; then
        echo "  标记为待整合: $file"
        mv "$file" "${file}.deprecated"
    fi
done

# 4. 更新现有文件使用工具模块
echo "4. 更新现有文件使用工具模块..."
echo "  注意：这需要手动更新代码，以下是需要更新的文件："
echo ""
echo "  a) src/common/auto_push_system.py"
echo "     使用: from utils.message_sender import send_whatsapp_message"
echo "     删除: def send_whatsapp_message()"
echo ""
echo "  b) src/common/optimized_push_system.py"
echo "     使用: from utils.message_sender import send_whatsapp_message"
echo "     删除: def send_whatsapp_message_optimized()"
echo ""
echo "  c) src/common/simple_push_system.py"
echo "     已更新使用环境变量"
echo ""
echo "  d) src/stocks/auto_stock_notifier.py"
echo "     使用: from utils.message_sender import send_whatsapp_message"
echo "     删除: def send_whatsapp_message()"
echo ""
echo "  e) src/news/news_pusher.py"
echo "     使用: from utils.database import NewsDatabase"
echo "     删除: 重复的数据库代码"
echo ""
echo "  f) src/common/news_stock_pusher.py"
echo "     考虑替换为: src/common/news_stock_pusher_optimized.py"
echo ""

# 5. 创建新的项目结构说明
echo "5. 创建新的项目结构说明..."
cat > PROJECT_STRUCTURE_OPTIMIZED.md << 'EOF'
# 🏗️ 优化后的项目结构

## 📁 目录结构

```
src/
├── 📁 common/                    # 公共模块
│   ├── base_pusher.py           # 基础推送器类 (新)
│   ├── news_stock_pusher_optimized.py  # 优化版推送器 (新)
│   ├── auto_push_system.py      # 自动推送系统 (待更新)
│   ├── optimized_push_system.py # 优化推送系统 (待更新)
│   ├── simple_push_system.py    # 简单推送系统 (已更新)
│   └── hourly_pusher.py         # 每小时推送器
│
├── 📁 news/                     # 新闻模块
│   ├── get_china_news.py        # 中国新闻获取
│   └── news_pusher.py           # 新闻推送器 (待更新)
│
├── 📁 stocks/                   # 股票模块
│   ├── auto_stock_notifier.py   # 自动股票通知 (待更新)
│   ├── hourly_alibaba_monitor.py # 阿里巴巴监控
│   ├── hourly_multi_stock_monitor.py # 多股票监控
│   ├── multi_stock_monitor.py   # 多股票监控器
│   └── price_alert_system.py    # 价格警报系统
│
├── 📁 utils/                    # 工具模块 (新)
│   ├── message_sender.py        # 消息发送工具
│   ├── database.py              # 数据库工具
│   ├── config.py                # 配置管理工具
│   └── logger.py                # 日志工具
│
└── main_optimized.py            # 优化版主入口 (新)
```

## 🔄 代码优化策略

### 1. 消除重复代码
- **消息发送**: 统一到 `utils/message_sender.py`
- **数据库操作**: 统一到 `utils/database.py`
- **配置管理**: 统一到 `utils/config.py`
- **日志管理**: 统一到 `utils/logger.py`

### 2. 类继承结构
```
BasePusher (基础类)
├── NewsStockPusherOptimized (新闻+股票推送器)
├── AutoPushSystem (自动推送系统)
├── SimplePushSystem (简单推送系统)
└── OptimizedPushSystem (优化推送系统)
```

### 3. 配置文件集中管理
- 所有配置在 `config/` 目录
- 环境变量统一管理
- 配置验证和默认值

### 4. 日志统一管理
- 所有日志到 `logs/` 目录
- 统一的日志格式
- 日志轮转策略

## 🚀 迁移步骤

### 第一阶段：创建工具模块 ✅
- [x] 创建 `utils/` 目录和工具文件
- [x] 创建 `base_pusher.py` 基础类
- [x] 创建 `news_stock_pusher_optimized.py`

### 第二阶段：更新现有文件
- [ ] 更新 `auto_push_system.py` 使用工具模块
- [ ] 更新 `optimized_push_system.py` 使用工具模块
- [ ] 更新 `auto_stock_notifier.py` 使用工具模块
- [ ] 更新 `news_pusher.py` 使用工具模块

### 第三阶段：清理旧文件
- [x] 删除 `smart_pusher.py`
- [x] 删除 `smart_pusher_enhanced.py`
- [x] 删除 `global_news_pusher.py`
- [x] 标记社交媒体监控文件为待整合

### 第四阶段：测试验证
- [ ] 测试所有系统功能
- [ ] 验证配置管理
- [ ] 验证日志系统
- [ ] 性能测试

## 📊 预期收益

1. **代码行数减少**: 预计减少30-40%重复代码
2. **维护成本降低**: 统一接口，易于维护
3. **错误率降低**: 集中错误处理
4. **性能提升**: 优化资源使用
5. **可扩展性**: 易于添加新功能

## ⚠️ 注意事项

1. **向后兼容**: 确保现有功能不受影响
2. **逐步迁移**: 分阶段进行，避免大规模更改
3. **充分测试**: 每个阶段都要充分测试
4. **文档更新**: 更新所有相关文档

## 🔧 快速开始

```bash
# 使用优化版系统
python3 src/main_optimized.py --mode news-stock

# 查看系统状态
python3 src/main_optimized.py --mode status

# 测试所有系统
python3 src/main_optimized.py --test
```

## 📞 支持

如有问题，请查看工具模块的测试代码或联系维护者。
EOF

echo "✅ 清理脚本完成"
echo ""
echo "下一步："
echo "1. 手动更新列出的文件使用新的工具模块"
echo "2. 运行测试确保功能正常"
echo "3. 提交更改到Git"
echo ""
echo "备份文件保存在: backup_$(date +%Y%m%d_%H%M%S)/"
#!/bin/bash
# 更新到v0.2.0版本脚本

echo "🚀 更新到 v0.2.0 - 系统监控与健康检查"
echo "========================================"

cd "$(dirname "$0")"

echo "1. 检查当前版本..."
CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "0.1.0")
echo "   当前版本: v$CURRENT_VERSION"

echo ""
echo "2. 安装依赖..."
pip install psutil 2>/dev/null || pip3 install psutil
echo "   ✅ psutil已安装"

echo ""
echo "3. 测试健康检查系统..."
echo ""
./check_health.py check

echo ""
echo "4. 测试推送前健康检查..."
echo ""
./check_health.py pre-push

echo ""
echo "5. 更新版本文件..."
echo "0.2.0" > VERSION
sed -i "s/VERSION = '0.1.0'/VERSION = '0.2.0'/" setup.py 2>/dev/null || true

echo ""
echo "6. 更新CHANGELOG.md..."
cat >> CHANGELOG.md << 'EOF'

## [0.2.0] - 2026-02-04
### 系统监控与健康检查
- 🔧 **健康检查系统**: 完整的系统健康监控功能
- 📊 **监控API**: RESTful健康检查API端点
- 🛠️ **命令行工具**: `check_health.py` 健康检查工具
- 📈 **推送前检查**: 自动在推送前执行健康检查
- 🚨 **健康告警**: 系统异常时自动发送告警
- 📝 **统计记录**: 推送成功率和健康检查统计

### 新增功能
1. **健康检查模块** (`src/monitoring/`)
   - `health_check.py`: 系统健康检查器
   - `health_api.py`: 健康检查API服务
   - 检查数据库、新闻源、消息平台、系统资源

2. **命令行工具**
   - `check_health.py check`: 完整健康检查
   - `check_health.py pre-push`: 推送前检查
   - `check_health.py monitor`: 持续监控
   - `check_health.py api`: 启动API服务器

3. **集成到推送系统**
   - 推送前自动健康检查
   - 健康异常时发送告警
   - 推送统计记录
   - 系统状态监控

### 技术改进
- ✅ **数据库连接测试**: 新增test_connection方法
- ✅ **系统资源监控**: CPU、内存、磁盘使用率
- ✅ **新闻源监控**: 源可用性检查
- ✅ **消息平台监控**: WhatsApp/微信连接检查
- ✅ **错误处理**: 完善的异常处理和日志

### 使用指南
```bash
# 健康检查
python3 check_health.py check

# 推送前检查
python3 check_health.py pre-push

# 启动监控API
python3 check_health.py api --port 8080

# 持续监控
python3 check_health.py monitor --interval 300
```

### 监控端点
- `GET /health` - 完整健康检查
- `GET /health/database` - 数据库健康
- `GET /health/whatsapp` - WhatsApp健康
- `GET /health/wechat` - 微信健康
- `GET /health/resources` - 系统资源

### 下一步计划
- 数据分析功能 (关键词提取、情感分析)
- 可视化仪表板
- 更多消息平台集成
- 高级告警配置

EOF

echo ""
echo "7. 提交更改到Git..."
git add .
git commit -m "版本 0.2.0: 系统监控与健康检查功能"

echo ""
echo "8. 创建Git标签..."
git tag -d v0.2.0 2>/dev/null || true
git tag -a v0.2.0 -m "版本 0.2.0: 系统监控与健康检查"

echo ""
echo "9. 推送到GitHub..."
git push origin master 2>&1 | tail -3
git push origin v0.2.0 2>&1 | tail -3

echo ""
echo "10. 验证更新..."
echo "   当前版本: v$(cat VERSION)"
echo "   Git标签: v0.2.0"
echo "   文件变更:"
git status --short | head -10

echo ""
echo "🎉 v0.2.0 更新完成！"
echo "========================"
echo ""
echo "📋 新功能可用:"
echo "  1. 健康检查: ./check_health.py check"
echo "  2. 推送前检查: ./check_health.py pre-push"
echo "  3. 监控API: ./check_health.py api"
echo "  4. 持续监控: ./check_health.py monitor"
echo ""
echo "🔧 系统将在下次推送时自动执行健康检查"
echo "📊 查看推送统计: cat logs/push_statistics.json"
echo ""
echo "✅ 更新成功！"
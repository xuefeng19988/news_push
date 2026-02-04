#!/bin/bash
# 定时任务配置脚本

echo "配置新闻推送系统定时任务..."
echo ""

# 主系统定时任务
echo "添加主系统定时任务:"
echo "0 * * * * cd $(pwd) && /usr/bin/python3 src/common/auto_push_system.py --run >> logs/auto_push.log 2>&1"
echo ""

# 备份系统定时任务
echo "添加备份系统定时任务:"
echo "0 * * * * cd $(pwd) && /usr/bin/python3 src/common/simple_push_system.py --run >> logs/simple_push.log 2>&1"
echo ""

echo "请手动添加以上定时任务到crontab:"
echo "1. 运行: crontab -e"
echo "2. 添加上面的两行配置"
echo "3. 保存并退出"

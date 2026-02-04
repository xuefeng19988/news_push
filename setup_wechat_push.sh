#!/bin/bash
# 微信推送配置脚本

echo "🚀 微信推送配置向导"
echo "========================"

# 检查当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "1. 检查当前配置..."
echo ""

# 检查环境变量文件
if [ ! -f "config/.env" ]; then
    echo "❌ 配置文件不存在: config/.env"
    echo "正在创建配置文件..."
    cp config/.env.example config/.env
    echo "✅ 配置文件已创建"
fi

echo "当前配置:"
echo "---------"
grep -E "^(WHATSAPP_NUMBER|ENABLE_WHATSAPP|ENABLE_WECHAT|WECHAT_)" config/.env || echo "未找到相关配置"

echo ""
echo "2. 配置微信推送..."
echo ""

# 询问是否启用微信推送
read -p "是否启用微信推送？(y/N): " enable_wechat
enable_wechat=${enable_wechat:-n}

if [[ "$enable_wechat" =~ ^[Yy]$ ]]; then
    echo ""
    echo "📱 企业微信配置"
    echo "--------------"
    
    # 获取企业微信配置
    read -p "请输入企业ID (WECHAT_CORP_ID): " corp_id
    read -p "请输入应用ID (WECHAT_AGENT_ID): " agent_id
    read -p "请输入应用Secret (WECHAT_SECRET): " secret
    read -p "请输入接收用户 (默认: @all): " to_user
    to_user=${to_user:-@all}
    
    # 更新配置文件
    echo ""
    echo "更新配置文件..."
    
    # 启用微信推送
    sed -i 's/ENABLE_WECHAT=false/ENABLE_WECHAT=true/' config/.env
    
    # 更新微信配置
    if [ -n "$corp_id" ]; then
        sed -i "s/WECHAT_CORP_ID=\"\"/WECHAT_CORP_ID=\"$corp_id\"/" config/.env
    fi
    
    if [ -n "$agent_id" ]; then
        sed -i "s/WECHAT_AGENT_ID=\"\"/WECHAT_AGENT_ID=\"$agent_id\"/" config/.env
    fi
    
    if [ -n "$secret" ]; then
        sed -i "s/WECHAT_SECRET=\"\"/WECHAT_SECRET=\"$secret\"/" config/.env
    fi
    
    if [ -n "$to_user" ]; then
        sed -i "s/WECHAT_TO_USER=\"@all\"/WECHAT_TO_USER=\"$to_user\"/" config/.env
    fi
    
    echo "✅ 微信配置已更新"
    
    # 测试微信推送
    echo ""
    echo "3. 测试微信推送..."
    echo ""
    
    read -p "是否立即测试微信推送？(Y/n): " test_wechat
    test_wechat=${test_wechat:-y}
    
    if [[ "$test_wechat" =~ ^[Yy]$ ]]; then
        echo "运行微信推送测试..."
        python3 test_wechat_push.py
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ 微信推送测试成功！"
        else
            echo ""
            echo "❌ 微信推送测试失败"
            echo "请检查配置是否正确"
        fi
    fi
    
else
    echo "跳过微信推送配置"
    # 确保微信推送被禁用
    sed -i 's/ENABLE_WECHAT=true/ENABLE_WECHAT=false/' config/.env 2>/dev/null || true
fi

echo ""
echo "4. 配置WhatsApp推送..."
echo ""

# 检查WhatsApp配置
whatsapp_number=$(grep 'WHATSAPP_NUMBER=' config/.env | cut -d'=' -f2 | tr -d '"')
if [[ "$whatsapp_number" == "+86**********" ]]; then
    echo "⚠️  WhatsApp号码未配置"
    read -p "请输入你的WhatsApp号码 (格式: +8612345678900): " new_whatsapp
    
    if [ -n "$new_whatsapp" ]; then
        sed -i "s/WHATSAPP_NUMBER=\"+86**********\"/WHATSAPP_NUMBER=\"$new_whatsapp\"/" config/.env
        echo "✅ WhatsApp号码已更新"
    else
        echo "❌ 未提供WhatsApp号码，推送可能失败"
    fi
else
    echo "✅ WhatsApp号码已配置: $whatsapp_number"
fi

echo ""
echo "5. 验证完整配置..."
echo ""

# 运行配置检查
python3 -c "
import os
from pathlib import Path

# 加载环境变量
env_file = Path('config/.env')
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value.strip('\"\\'')

# 检查配置
print('📋 配置状态:')
print('-' * 40)

# WhatsApp配置
whatsapp_number = os.getenv('WHATSAPP_NUMBER', '')
enable_whatsapp = os.getenv('ENABLE_WHATSAPP', 'true').lower() == 'true'
openclaw_path = os.getenv('OPENCLAW_PATH', '/home/admin/.npm-global/bin/openclaw')

if enable_whatsapp:
    if whatsapp_number and whatsapp_number != '+86**********':
        print(f'✅ WhatsApp: 已配置 ({whatsapp_number[:4]}...{whatsapp_number[-4:]})')
    else:
        print('❌ WhatsApp: 号码未配置')
else:
    print('⚠️  WhatsApp: 已禁用')

# 微信配置
enable_wechat = os.getenv('ENABLE_WECHAT', 'false').lower() == 'true'
corp_id = os.getenv('WECHAT_CORP_ID')
agent_id = os.getenv('WECHAT_AGENT_ID')
secret = os.getenv('WECHAT_SECRET')

if enable_wechat:
    if corp_id and agent_id and secret:
        print(f'✅ 微信: 已配置 (企业ID: {corp_id[:4]}...)')
    else:
        print('❌ 微信: 配置不完整')
else:
    print('⚠️  微信: 已禁用')

# OpenClaw路径
import os.path
if os.path.exists(openclaw_path):
    print(f'✅ OpenClaw: 路径有效')
else:
    print(f'❌ OpenClaw: 路径无效 ({openclaw_path})')

print('-' * 40)
"

echo ""
echo "6. 更新定时任务..."
echo ""

# 检查定时任务
echo "当前定时任务:"
crontab -l | grep "clean_news_push" || echo "未找到相关定时任务"

echo ""
read -p "是否更新定时任务以使用新配置？(Y/n): " update_cron
update_cron=${update_cron:-y}

if [[ "$update_cron" =~ ^[Yy]$ ]]; then
    echo "更新定时任务..."
    
    # 删除旧的定时任务
    (crontab -l | grep -v "clean_news_push") | crontab -
    
    # 添加新的定时任务
    (crontab -l; echo "0 * * * * cd /home/admin/clawd/clean_news_push && /usr/bin/python3 -m src.common.auto_push_system_optimized_final --run >> /home/admin/clawd/clean_news_push/logs/auto_push.log 2>&1") | crontab -
    
    echo "✅ 定时任务已更新"
fi

echo ""
echo "🎉 配置完成！"
echo "========================"
echo ""
echo "📋 下一步操作:"
echo ""
echo "1. 手动测试推送系统:"
echo "   python3 -m src.common.auto_push_system_optimized_final --run"
echo ""
echo "2. 查看推送日志:"
echo "   tail -f logs/auto_push.log"
echo ""
echo "3. 使用管理工具:"
echo "   ./scripts/push_manager.sh status"
echo ""
echo "4. 下次推送时间: 下一个整点"
echo ""
echo "✅ 微信推送配置向导完成！"
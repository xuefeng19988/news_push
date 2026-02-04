#!/bin/bash
# 配置设置脚本

echo "📱 新闻推送系统 - 配置设置"
echo "=" * 50

# 检查是否已存在配置文件
if [ -f "config/.env" ]; then
    echo "⚠️  发现现有配置文件: config/.env"
    echo "当前配置:"
    grep -E "WHATSAPP_NUMBER|OPENCLAW_PATH" config/.env || echo "   (未找到配置)"
    echo ""
    read -p "是否覆盖现有配置? (y/N): " overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        echo "✅ 保留现有配置"
        exit 0
    fi
fi

# 创建配置目录
mkdir -p config

# 复制模板
if [ ! -f "config/.env.example" ]; then
    echo "❌ 找不到配置文件模板: config/.env.example"
    echo "请确保已正确克隆仓库"
    exit 1
fi

cp config/.env.example config/.env

echo ""
echo "📝 请填写以下配置信息:"
echo ""

# 获取WhatsApp号码
read -p "请输入你的WhatsApp号码 (例如: +86123****8900): " whatsapp_number
while [[ ! "$whatsapp_number" =~ ^\+[0-9]{10,15}$ ]]; do
    echo "❌ 号码格式不正确，请使用国际格式: +国家代码手机号"
    read -p "请输入你的WhatsApp号码 (例如: +86123****8900): " whatsapp_number
done

# 获取OpenClaw路径
read -p "请输入OpenClaw路径 [默认: /usr/local/bin/openclaw]: " openclaw_path
openclaw_path=${openclaw_path:-"/usr/local/bin/openclaw"}

# 更新配置文件
sed -i "s|WHATSAPP_NUMBER=\"+86.*\"|WHATSAPP_NUMBER=\"$whatsapp_number\"|g" config/.env
sed -i "s|OPENCLAW_PATH=\".*\"|OPENCLAW_PATH=\"$openclaw_path\"|g" config/.env

echo ""
echo "📡 API密钥配置 (可选):"
echo "如果需要使用Twitter、微博、Reddit等API，请编辑 config/.env 文件"
echo "并填写相应的API密钥。"

echo ""
echo "✅ 配置已保存到: config/.env"
echo ""
echo "📋 配置内容:"
echo "=" * 30
grep -E "WHATSAPP_NUMBER|OPENCLAW_PATH" config/.env
echo "=" * 30

echo ""
echo "🚀 加载配置到当前会话:"
echo "source config/.env"
echo ""
echo "📝 永久配置 (添加到 ~/.bashrc 或 ~/.zshrc):"
echo "echo 'source $(pwd)/config/.env' >> ~/.bashrc"
echo ""
echo "✅ 配置完成！现在可以运行系统了。"
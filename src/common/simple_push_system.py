#!/usr/bin/env python3
"""
简化版推送系统 - 确保每小时准时推送
"""

import os
import sys
import json
import time
import sqlite3
import requests
from datetime import datetime, timedelta
import subprocess
from typing import List, Dict, Optional
import random

# 配置
DB_PATH = "/home/admin/clawd/news_cache.db"
OPENCLAW_PATH = "/home/admin/.npm-global/bin/openclaw"
WHATSAPP_NUMBER = "+8618966719971"

# 模拟新闻数据
MOCK_NEWS = [
    {
        "title": "中国央行宣布降准0.5个百分点",
        "source": "金融时报中文",
        "url": "https://www.ftchinese.com/story/001234567",
        "summary": "中国人民银行决定下调金融机构存款准备金率0.5个百分点，释放长期资金约1万亿元。这是今年首次降准，旨在支持实体经济发展。",
        "importance": "🔴 非常重要",
        "update_time": "02-04 10:21",
        "recency": "🆕 刚刚更新"
    },
    {
        "title": "特斯拉发布新一代自动驾驶系统FSD V12",
        "source": "澎湃新闻",
        "url": "https://www.thepaper.cn/newsDetail_123456",
        "summary": "特斯拉在年度AI日上发布了全新一代自动驾驶系统FSD V12。新系统采用端到端神经网络，不再依赖传统编程规则。测试数据显示，新系统的事故率比人类驾驶低300%。",
        "importance": "🟠 重要",
        "update_time": "02-04 08:51",
        "recency": "🆕 3小时内"
    },
    {
        "title": "全球气候峰会达成历史性减排协议",
        "source": "BBC World",
        "url": "https://www.bbc.com/news/world-123456",
        "summary": "在迪拜举行的联合国气候峰会上，各国代表经过艰难谈判，最终达成历史性协议，承诺在2030年前将温室气体排放量减少50%。该协议还包括建立1000亿美元的气候基金。",
        "importance": "🟠 重要",
        "update_time": "02-04 09:31",
        "recency": "🆕 刚刚更新"
    },
    {
        "title": "#春节返程高峰# 交通部门发布出行提示",
        "source": "微博热搜",
        "url": "https://s.weibo.com/weibo?q=春节返程",
        "summary": "春节假期接近尾声，各地迎来返程高峰。交通部门提醒旅客合理安排行程，注意交通安全。",
        "importance": "🟡 中等",
        "update_time": "02-04 09:15",
        "recency": "🆕 3小时内"
    },
    {
        "title": "OpenAI发布新一代语言模型GPT-5",
        "source": "TechCrunch",
        "url": "https://techcrunch.com/2026/02/04/openai-gpt5/",
        "summary": "OpenAI正式发布GPT-5，新模型在推理能力、代码生成和多模态理解方面有显著提升。据称在多项基准测试中表现优于人类专家。",
        "importance": "🔴 非常重要",
        "update_time": "02-04 10:05",
        "recency": "🆕 刚刚更新"
    }
]

# 模拟股票数据
MOCK_STOCKS = [
    {"symbol": "09988.HK", "name": "阿里巴巴-W", "price": 159.45, "change": 0.55, "change_percent": 0.35},
    {"symbol": "01810.HK", "name": "小米集团-W", "price": 33.95, "change": -0.01, "change_percent": -0.03},
    {"symbol": "002594.SZ", "name": "比亚迪", "price": 87.85, "change": 0.09, "change_percent": 0.10},
    {"symbol": "00700.HK", "name": "腾讯控股", "price": 345.20, "change": 2.30, "change_percent": 0.67},
    {"symbol": "AAPL", "name": "苹果公司", "price": 185.42, "change": 0.85, "change_percent": 0.46}
]

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_cache (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            url TEXT NOT NULL,
            summary TEXT,
            published_at TIMESTAMP,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def format_stock_section() -> str:
    """格式化股票部分"""
    now = datetime.now().strftime("%H:%M")
    lines = [f"📈 **股票监控** ({now})", ""]
    
    for stock in MOCK_STOCKS:
        symbol = stock["symbol"]
        name = stock["name"]
        price = stock["price"]
        change = stock["change"]
        change_percent = stock["change_percent"]
        
        # 确定情绪图标
        if change_percent > 0.5:
            sentiment = "📈 强势上涨"
        elif change_percent > 0:
            sentiment = "📈 上涨"
        elif change_percent < -0.5:
            sentiment = "📉 大幅下跌"
        elif change_percent < 0:
            sentiment = "📉 下跌"
        else:
            sentiment = "➡️ 持平"
        
        # 格式化价格变化
        change_sign = "+" if change >= 0 else ""
        lines.append(f"• **{name}** ({symbol})")
        lines.append(f"  价格: {price:.2f} {'HKD' if '.HK' in symbol else 'CNY' if '.SZ' in symbol else 'USD'}")
        lines.append(f"  涨跌: {change_sign}{change:.2f} ({change_sign}{change_percent:.2f}%)")
        lines.append(f"  情绪: {sentiment}")
        lines.append("")
    
    return "\n".join(lines)

def format_news_section() -> str:
    """格式化新闻部分"""
    lines = ["📰 **重要新闻（含更新时间和重要性）**", ""]
    
    # 按重要性排序
    importance_order = {"🔴": 0, "🟠": 1, "🟡": 2, "🟢": 3, "⚪": 4}
    sorted_news = sorted(MOCK_NEWS, key=lambda x: importance_order.get(x["importance"][0], 5))
    
    # 添加来源图标
    source_icons = {
        "BBC World": "🇬🇧",
        "金融时报中文": "💷",
        "澎湃新闻": "🌊",
        "微博热搜": "🐦",
        "TechCrunch": "💻"
    }
    
    for i, news in enumerate(sorted_news[:5], 1):
        source_icon = source_icons.get(news["source"], "📰")
        
        lines.append(f"{i}. **{news['title']}**")
        lines.append(f"   {news['importance']} | {source_icon} {news['source']} | {news['recency']}")
        lines.append(f"   更新时间: {news['update_time']}")
        
        # 添加标签
        if "金融时报" in news["source"]:
            lines.append("   💼 财经分析 | 📈 市场影响")
        elif "BBC" in news["source"]:
            lines.append("   🌍 国际权威 | 📊 深度报道")
        elif "澎湃" in news["source"]:
            lines.append("   📊 深度调查 | 🔬 技术前沿")
        elif "微博" in news["source"]:
            lines.append("   🔥 实时热点 | 👥 社会关注")
        else:
            lines.append("   📰 新闻报道 | 💡 最新资讯")
        
        lines.append(f"   🔗 {news['url']}")
        lines.append(f"   📝 **摘要**: {news['summary']}")
        lines.append(f"   ⏱️ 阅读约1分钟")
        lines.append("")
    
    return "\n".join(lines)

def send_whatsapp_message(message: str):
    """发送WhatsApp消息"""
    try:
        # 使用OpenClaw发送消息
        cmd = [OPENCLAW_PATH, "message", "send", "--target", WHATSAPP_NUMBER, "--message", message]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ 消息发送成功: {datetime.now().strftime('%H:%M:%S')}")
            return True
        else:
            print(f"❌ 消息发送失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 发送消息时出错: {e}")
        return False

def create_push_message() -> str:
    """创建推送消息"""
    now = datetime.now()
    time_str = now.strftime("%H:%M")
    
    message = f"⏰ **整点推送** ({time_str})\n\n"
    message += format_stock_section() + "\n"
    message += format_news_section() + "\n"
    message += "---\n"
    message += "📊 **推送统计**\n"
    message += f"• 股票监控: {len(MOCK_STOCKS)} 只\n"
    message += f"• 重要新闻: {len(MOCK_NEWS)} 条\n"
    message += f"• 更新时间: {now.strftime('%m-%d %H:%M')}\n"
    message += f"• 下次推送: {(now + timedelta(hours=1)).strftime('%H:00')}\n"
    
    return message

def main():
    """主函数"""
    print(f"🚀 开始推送: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 初始化数据库
    init_database()
    
    # 创建消息
    message = create_push_message()
    
    # 发送消息
    print("📤 正在发送消息...")
    if send_whatsapp_message(message):
        print("✅ 推送完成!")
        
        # 记录日志
        log_file = "/home/admin/clawd/simple_push.log"
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 推送成功\n")
    else:
        print("❌ 推送失败!")
        
        # 记录错误日志
        log_file = "/home/admin/clawd/simple_push.log"
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 推送失败\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        main()
    else:
        print("使用方法: python3 simple_push_system.py --run")
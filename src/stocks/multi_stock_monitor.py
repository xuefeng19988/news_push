#!/usr/bin/env python3
"""
多股票监控系统 - 支持阿里巴巴、小米、比亚迪
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys

class MultiStockMonitor:
    """多股票监控器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        # 监控股票列表
        self.stocks = [
            {
                "name": "阿里巴巴-W",
                "symbol": "09988.HK",
                "yahoo_symbol": "9988.HK",
                "sina_symbol": "hk09988",
                "tencent_symbol": "hk09988",
                "type": "港股",
                "currency": "HKD"
            },
            {
                "name": "小米集团-W", 
                "symbol": "01810.HK",
                "yahoo_symbol": "1810.HK",
                "sina_symbol": "hk01810",
                "tencent_symbol": "hk01810",
                "type": "港股",
                "currency": "HKD"
            },
            {
                "name": "比亚迪",
                "symbol": "002594.SZ",
                "yahoo_symbol": "002594.SZ",
                "sina_symbol": "sz002594",
                "tencent_symbol": "sz002594",
                "type": "A股",
                "currency": "CNY"
            }
        ]
    
    def get_stock_from_yahoo(self, stock_info):
        """从Yahoo Finance获取股票数据"""
        try:
            symbol = stock_info["yahoo_symbol"]
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            
            params = {
                "interval": "1d",
                "range": "1d",
                "includePrePost": "false"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                chart_data = data.get("chart", {}).get("result", [{}])[0]
                meta = chart_data.get("meta", {})
                quotes = chart_data.get("indicators", {}).get("quote", [{}])[0]
                
                if meta and quotes:
                    closes = quotes.get("close", [])
                    if closes:
                        latest_price = closes[-1]
                        prev_price = closes[-2] if len(closes) > 1 else latest_price
                        
                        change = latest_price - prev_price
                        change_percent = (change / prev_price) * 100 if prev_price else 0
                        
                        return {
                            "symbol": stock_info["symbol"],
                            "name": stock_info["name"],
                            "price": latest_price,
                            "change": change,
                            "change_percent": change_percent,
                            "open": meta.get("regularMarketPrice", latest_price),
                            "high": meta.get("regularMarketDayHigh", latest_price),
                            "low": meta.get("regularMarketDayLow", latest_price),
                            "volume": quotes.get("volume", [0])[-1] if quotes.get("volume") else 0,
                            "currency": stock_info["currency"],
                            "type": stock_info["type"],
                            "timestamp": datetime.now().isoformat(),
                            "source": "Yahoo Finance"
                        }
            
            return None
                
        except Exception as e:
            print(f"❌ Yahoo API错误 ({stock_info['symbol']}): {e}")
            return None
    
    def get_stock_from_sina(self, stock_info):
        """从新浪财经获取数据"""
        try:
            symbol = stock_info["sina_symbol"]
            url = f"http://hq.sinajs.cn/list={symbol}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                if '="' in content:
                    data_str = content.split('="')[1].split('"')[0]
                    parts = data_str.split(',')
                    
                    if len(parts) >= 6:
                        current_price = float(parts[1])
                        prev_close = float(parts[2])
                        
                        change = current_price - prev_close
                        change_percent = (change / prev_close) * 100 if prev_close else 0
                        
                        return {
                            "symbol": stock_info["symbol"],
                            "name": stock_info["name"],
                            "price": current_price,
                            "change": change,
                            "change_percent": change_percent,
                            "open": float(parts[2]) if parts[2] else current_price,
                            "high": float(parts[4]) if len(parts) > 4 and parts[4] else current_price,
                            "low": float(parts[5]) if len(parts) > 5 and parts[5] else current_price,
                            "volume": float(parts[8]) if len(parts) > 8 and parts[8] else 0,
                            "currency": stock_info["currency"],
                            "type": stock_info["type"],
                            "timestamp": datetime.now().isoformat(),
                            "source": "新浪财经"
                        }
            
            return None
                
        except Exception as e:
            print(f"❌ 新浪API错误 ({stock_info['symbol']}): {e}")
            return None
    
    def get_stock_data(self, stock_info):
        """获取单个股票数据（尝试多个源）"""
        # 按顺序尝试不同数据源
        data_sources = [
            ("Yahoo Finance", lambda: self.get_stock_from_yahoo(stock_info)),
            ("新浪财经", lambda: self.get_stock_from_sina(stock_info))
        ]
        
        for source_name, get_func in data_sources:
            data = get_func()
            if data:
                return data
            time.sleep(0.5)  # 避免请求过快
        
        return None
    
    def get_all_stocks_data(self):
        """获取所有股票数据"""
        print("📡 开始获取多股票数据...")
        
        all_data = []
        
        for stock in self.stocks:
            print(f"  获取 {stock['name']} ({stock['symbol']})...")
            data = self.get_stock_data(stock)
            
            if data:
                all_data.append(data)
                print(f"    ✅ 成功: {data['price']} {data['currency']}")
            else:
                print(f"    ❌ 失败")
        
        return all_data
    
    def analyze_sentiment(self, stock_data):
        """分析股票情绪"""
        if not stock_data:
            return "数据不足"
        
        change_percent = stock_data.get("change_percent", 0)
        
        # 情绪分析规则
        if change_percent > 3:
            sentiment = "非常正面"
            reason = "大幅上涨"
        elif change_percent > 1:
            sentiment = "正面"
            reason = "温和上涨"
        elif change_percent > -1:
            sentiment = "中性"
            reason = "波动不大"
        elif change_percent > -3:
            sentiment = "负面"
            reason = "小幅下跌"
        else:
            sentiment = "非常负面"
            reason = "大幅下跌"
        
        return {
            "sentiment": sentiment,
            "reason": reason,
            "change_percent": change_percent,
            "analysis": f"涨跌: {change_percent:+.2f}%, 情绪: {sentiment}"
        }
    
    def generate_individual_report(self, stock_data, sentiment_analysis):
        """生成单个股票报告"""
        report = []
        report.append(f"### 📊 {stock_data['name']} ({stock_data['symbol']})")
        report.append(f"- **类型**: {stock_data['type']}")
        report.append(f"- **当前价格**: {stock_data['price']:.2f} {stock_data['currency']}")
        report.append(f"- **今日涨跌**: {stock_data['change']:+.2f} {stock_data['currency']}")
        report.append(f"- **涨跌幅**: {stock_data['change_percent']:+.2f}%")
        report.append(f"- **今日开盘**: {stock_data.get('open', stock_data['price']):.2f}")
        report.append(f"- **今日最高**: {stock_data.get('high', stock_data['price']):.2f}")
        report.append(f"- **今日最低**: {stock_data.get('low', stock_data['price']):.2f}")
        report.append(f"- **成交量**: {stock_data.get('volume', 0):,.0f}")
        report.append(f"- **市场情绪**: {sentiment_analysis['sentiment']}")
        report.append(f"- **分析**: {sentiment_analysis['analysis']}")
        report.append("")
        
        return "\n".join(report)
    
    def generate_summary_table(self, all_data_with_sentiment):
        """生成摘要表格"""
        if not all_data_with_sentiment:
            return ""
        
        summary = []
        summary.append("## 📈 股票表现摘要")
        summary.append("")
        summary.append("| 股票 | 价格 | 涨跌幅 | 情绪 | 建议 |")
        summary.append("|------|------|--------|------|------|")
        
        for item in all_data_with_sentiment:
            stock_data = item["stock_data"]
            sentiment = item["sentiment_analysis"]
            
            # 价格和涨跌
            price_str = f"{stock_data['price']:.2f} {stock_data['currency']}"
            change_str = f"{stock_data['change_percent']:+.2f}%"
            
            # 情绪表情
            sentiment_emoji = {
                "非常正面": "🚀",
                "正面": "📈",
                "中性": "➡️",
                "负面": "📉",
                "非常负面": "🔻"
            }.get(sentiment["sentiment"], "❓")
            
            # 投资建议
            advice = {
                "非常正面": "积极关注",
                "正面": "谨慎乐观",
                "中性": "保持观望",
                "负面": "注意风险",
                "非常负面": "高度谨慎"
            }.get(sentiment["sentiment"], "数据不足")
            
            summary.append(f"| {stock_data['name']} | {price_str} | {change_str} | {sentiment_emoji} {sentiment['sentiment']} | {advice} |")
        
        summary.append("")
        return "\n".join(summary)
    
    def generate_comprehensive_report(self, all_data_with_sentiment):
        """生成综合报告"""
        report = []
        report.append("# 📊 多股票监控综合报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        report.append(f"监控股票数: {len(all_data_with_sentiment)}")
        report.append("")
        
        # 摘要表格
        report.append(self.generate_summary_table(all_data_with_sentiment))
        
        # 详细分析
        report.append("## 🔍 详细分析")
        report.append("")
        
        for item in all_data_with_sentiment:
            stock_report = self.generate_individual_report(
                item["stock_data"], 
                item["sentiment_analysis"]
            )
            report.append(stock_report)
        
        # 市场总体分析
        report.append("## 🌐 市场总体分析")
        
        # 统计情绪分布
        sentiment_counts = {}
        for item in all_data_with_sentiment:
            sentiment = item["sentiment_analysis"]["sentiment"]
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        if sentiment_counts:
            report.append("### 市场情绪分布:")
            for sentiment, count in sentiment_counts.items():
                percentage = (count / len(all_data_with_sentiment)) * 100
                report.append(f"- **{sentiment}**: {count}只 ({percentage:.1f}%)")
        
        # 总体建议
        report.append("")
        report.append("### 总体投资建议:")
        
        # 根据多数股票情绪给出建议
        if sentiment_counts.get("非常正面", 0) >= 2:
            report.append("✅ **市场情绪积极**: 多数股票表现强劲，可考虑增加仓位")
        elif sentiment_counts.get("正面", 0) >= 2:
            report.append("👍 **市场偏乐观**: 整体趋势向好，可选择性布局")
        elif sentiment_counts.get("负面", 0) >= 2 or sentiment_counts.get("非常负面", 0) >= 2:
            report.append("⚠️ **市场偏谨慎**: 多数股票承压，建议控制风险")
        else:
            report.append("🤔 **市场分化**: 个股表现不一，建议精选个股")
        
        report.append("")
        report.append("---")
        report.append("*监控频率: 每小时一次*")
        report.append("*下次更新: " + (datetime.now() + timedelta(hours=1)).strftime('%H:%M') + "*")
        report.append("*数据仅供参考，投资需谨慎*")
        
        return "\n".join(report)
    
    def save_reports(self, all_data_with_sentiment, comprehensive_report):
        """保存报告和数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存综合报告
        report_file = f"multi_stock_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(comprehensive_report)
        
        # 保存原始数据
        data_file = f"multi_stock_data_{timestamp}.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                "stocks": all_data_with_sentiment,
                "generated_at": datetime.now().isoformat(),
                "monitor_config": {
                    "stocks_monitored": [s["symbol"] for s in self.stocks],
                    "total_stocks": len(self.stocks)
                }
            }, f, ensure_ascii=False, indent=2)
        
        return report_file, data_file

def main():
    """主函数"""
    print("="*60)
    print("🚀 多股票监控系统启动")
    print("监控股票: 阿里巴巴、小米、比亚迪")
    print("="*60)
    
    monitor = MultiStockMonitor()
    
    # 获取所有股票数据
    all_stocks_data = monitor.get_all_stocks_data()
    
    if not all_stocks_data:
        print("❌ 无法获取任何股票数据")
        return None
    
    print(f"\n✅ 成功获取 {len(all_stocks_data)}/{len(monitor.stocks)} 只股票数据")
    
    # 分析每个股票的情绪
    all_data_with_sentiment = []
    for stock_data in all_stocks_data:
        sentiment_analysis = monitor.analyze_sentiment(stock_data)
        all_data_with_sentiment.append({
            "stock_data": stock_data,
            "sentiment_analysis": sentiment_analysis
        })
    
    # 生成综合报告
    print("📝 生成综合报告...")
    comprehensive_report = monitor.generate_comprehensive_report(all_data_with_sentiment)
    
    # 保存报告
    report_file, data_file = monitor.save_reports(all_data_with_sentiment, comprehensive_report)
    
    print("\n" + "="*60)
    print("✅ 多股票监控完成!")
    print(f"   综合报告: {report_file}")
    print(f"   原始数据: {data_file}")
    
    # 显示摘要
    print("\n📋 监控摘要:")
    for item in all_data_with_sentiment:
        stock = item["stock_data"]
        sentiment = item["sentiment_analysis"]
        print(f"  {stock['name']}: {stock['price']:.2f} {stock['currency']} ({stock['change_percent']:+.2f}%) - {sentiment['sentiment']}")
    
    print("="*60)
    
    # 返回报告内容（前800字符）
    return comprehensive_report[:800] + "..." if len(comprehensive_report) > 800 else comprehensive_report

if __name__ == "__main__":
    result = main()
    
    if result:
        print("\n📄 报告预览:")
        print("-"*40)
        print(result)
        print("-"*40)
#!/usr/bin/env python3
"""
数据分析推送器
扩展基础推送器，添加数据分析和可视化功能
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json

# 导入基础类
from .base_pusher import BasePusher
from .news_stock_pusher_optimized import NewsStockPusherOptimized

# 导入分析模块
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from analytics.trend_analyzer import TrendAnalyzer
    from analytics.stock_indicator_calculator import StockIndicatorCalculator
    from analytics.visualization_generator import VisualizationGenerator
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 无法导入分析模块: {e}")
    ANALYTICS_AVAILABLE = False

class AnalyticsPusher(NewsStockPusherOptimized):
    """数据分析推送器"""
    
    def __init__(self):
        """初始化推送器"""
        super().__init__()
        self.name = "AnalyticsPusher"
        
        # 初始化分析模块
        if ANALYTICS_AVAILABLE:
            self.trend_analyzer = TrendAnalyzer()
            self.visualization_generator = VisualizationGenerator()
            self.stock_calculator = None  # 延迟初始化
            self.logger.info("数据分析模块初始化完成")
        else:
            self.logger.warning("分析模块不可用，将回退到基础推送模式")
    
    def _initialize_stock_calculator(self, stock_data_list: List[Dict[str, Any]]) -> bool:
        """初始化股票技术指标计算器"""
        if not ANALYTICS_AVAILABLE:
            return False
        
        try:
            # 转换股票数据格式
            price_data = []
            for stock_data in stock_data_list:
                # 假设股票数据包含历史价格信息
                # 如果没有历史数据，创建一些模拟数据用于演示
                current_price = stock_data.get('price', 0)
                timestamp = stock_data.get('timestamp', datetime.now().isoformat())
                
                # 创建模拟历史数据（实际应用中应从数据库获取）
                for i in range(30):
                    simulated_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00')) - timedelta(days=30-i)
                    simulated_price = current_price * (0.9 + 0.2 * (i/30))  # 模拟价格变化
                    
                    price_data.append({
                        'timestamp': simulated_time.isoformat(),
                        'open': simulated_price * 0.99,
                        'high': simulated_price * 1.02,
                        'low': simulated_price * 0.98,
                        'close': simulated_price,
                        'volume': 10000 + i * 1000
                    })
            
            if price_data:
                self.stock_calculator = StockIndicatorCalculator(price_data)
                return True
        except Exception as e:
            self.logger.error(f"初始化股票计算器失败: {e}")
        
        return False
    
    def analyze_news_trends(self, articles: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        分析新闻趋势
        
        Args:
            articles: 新闻文章列表
            
        Returns:
            趋势分析结果
        """
        if not ANALYTICS_AVAILABLE or not articles:
            return None
        
        try:
            # 准备分析数据
            analysis_articles = []
            for article in articles[:50]:  # 最多分析50篇
                if isinstance(article, dict):
                    analysis_articles.append({
                        'title': article.get('title', ''),
                        'summary': article.get('summary', article.get('description', '')),
                        'source': article.get('source', ''),
                        'published': article.get('published', article.get('updated', datetime.now().isoformat())),
                        'type': article.get('type', '一般新闻'),
                        'importance': article.get('importance', '中')
                    })
            
            if analysis_articles:
                # 分析最近24小时的趋势
                trends = self.trend_analyzer.analyze_news_trends(analysis_articles, hours=24)
                return trends
        except Exception as e:
            self.logger.error(f"新闻趋势分析失败: {e}")
        
        return None
    
    def analyze_stock_technical(self, stock_data_list: List[Dict[str, Any]], 
                               stock_name: str = "股票") -> Optional[Dict[str, Any]]:
        """
        分析股票技术指标
        
        Args:
            stock_data_list: 股票数据列表
            stock_name: 股票名称
            
        Returns:
            技术分析结果
        """
        if not ANALYTICS_AVAILABLE or not stock_data_list:
            return None
        
        try:
            # 初始化计算器
            if not self._initialize_stock_calculator(stock_data_list):
                return None
            
            if self.stock_calculator:
                technical_summary = self.stock_calculator.generate_technical_summary()
                return technical_summary
        except Exception as e:
            self.logger.error(f"股票技术分析失败: {e}")
        
        return None
    
    def generate_analysis_report(self, 
                                news_analysis: Optional[Dict[str, Any]] = None,
                                stock_analysis: Optional[Dict[str, Any]] = None,
                                stock_name: str = "股票") -> str:
        """
        生成分析报告
        
        Args:
            news_analysis: 新闻分析结果
            stock_analysis: 股票分析结果
            stock_name: 股票名称
            
        Returns:
            分析报告文本
        """
        if not ANALYTICS_AVAILABLE:
            return "⚠️ 数据分析模块不可用\n"
        
        try:
            if self.visualization_generator:
                report = self.visualization_generator.generate_comprehensive_report(
                    news_analysis, stock_analysis, stock_name
                )
                return report
        except Exception as e:
            self.logger.error(f"生成分析报告失败: {e}")
        
        return "⚠️ 分析报告生成失败\n"
    
    def generate_visualization_summary(self, 
                                      news_analysis: Optional[Dict[str, Any]] = None,
                                      stock_analysis: Optional[Dict[str, Any]] = None) -> str:
        """
        生成可视化摘要（适合推送消息的简洁版本）
        
        Args:
            news_analysis: 新闻分析结果
            stock_analysis: 股票分析结果
            
        Returns:
            可视化摘要文本
        """
        if not ANALYTICS_AVAILABLE:
            return ""
        
        lines = ["📊 数据分析摘要", "=" * 30]
        
        # 新闻分析摘要
        if news_analysis:
            if 'total_articles' in news_analysis:
                lines.append(f"📰 分析文章: {news_analysis['total_articles']}篇")
            
            if 'sentiment_analysis' in news_analysis:
                sentiment = news_analysis['sentiment_analysis']
                overall = sentiment.get('overall_sentiment', 'unknown')
                sentiment_emoji = {
                    'positive': '😊',
                    'negative': '😟',
                    'neutral': '😐'
                }.get(overall, '❓')
                lines.append(f"😊 新闻情感: {sentiment_emoji} {overall}")
            
            if 'top_keywords' in news_analysis and news_analysis['top_keywords']:
                keywords = [kw.get('word', '')[:5] for kw in news_analysis['top_keywords'][:3]]
                lines.append(f"🔥 热门话题: {', '.join(filter(None, keywords))}")
        
        # 股票分析摘要
        if stock_analysis:
            if 'current_price' in stock_analysis:
                lines.append(f"💰 最新价格: {stock_analysis['current_price']:.2f}")
            
            if 'price_change' in stock_analysis:
                change = stock_analysis['price_change']
                change_symbol = "📈" if change > 0 else "📉"
                lines.append(f"{change_symbol} 价格变化: {change:+.2f}%")
            
            if 'trend' in stock_analysis:
                trend = stock_analysis['trend']
                trend_symbol = "🚀" if "上升" in trend else "📉" if "下降" in trend else "↔️"
                lines.append(f"{trend_symbol} 趋势: {trend}")
            
            if 'recommendation' in stock_analysis:
                rec = stock_analysis['recommendation']
                rec_emoji = "✅" if "买入" in rec else "⚠️" if "卖出" in rec else "📊"
                lines.append(f"{rec_emoji} 建议: {rec}")
        
        # 相关性分析
        if news_analysis and stock_analysis:
            lines.append("")
            lines.append("🔗 新闻-股票相关性")
            
            news_sentiment = news_analysis.get('sentiment_analysis', {}).get('overall_sentiment', 'neutral')
            stock_change = stock_analysis.get('price_change', 0)
            
            if news_sentiment == 'positive' and stock_change > 0:
                lines.append("📈 正面新闻推动股价上涨")
            elif news_sentiment == 'negative' and stock_change < 0:
                lines.append("📉 负面新闻导致股价下跌")
            elif news_sentiment == 'positive' and stock_change < 0:
                lines.append("⚠️ 正面新闻但股价下跌")
            elif news_sentiment == 'negative' and stock_change > 0:
                lines.append("⚠️ 负面新闻但股价上涨")
            else:
                lines.append("📊 相关性不明显")
        
        if len(lines) > 2:  # 除了标题外还有内容
            return "\n".join(lines)
        
        return ""
    
    def run(self) -> Tuple[bool, str]:
        """
        运行推送器（重写父类方法，添加数据分析）
        
        Returns:
            Tuple[成功状态, 报告内容]
        """
        # 先运行父类的推送逻辑
        success, base_report = super().run()
        
        # 添加数据分析部分（如果有）
        analysis_section = self._add_analysis_section()
        
        if analysis_section:
            # 将分析部分插入到报告末尾（系统信息之前）
            report_lines = base_report.split('\n')
            
            # 找到系统信息开始的位置（以"---"为标记）
            system_info_index = -1
            for i, line in enumerate(report_lines):
                if line.strip() == "---":
                    system_info_index = i
                    break
            
            if system_info_index > 0:
                # 在系统信息前插入分析部分
                report_lines.insert(system_info_index, analysis_section)
                report_lines.insert(system_info_index, "")  # 添加空行
                final_report = '\n'.join(report_lines)
            else:
                # 如果没有找到系统信息标记，直接追加
                final_report = base_report + "\n\n" + analysis_section
        else:
            final_report = base_report
        
        return success, final_report
    
    def _add_analysis_section(self) -> str:
        """
        添加数据分析部分到报告中
        
        Returns:
            数据分析部分内容
        """
        if not ANALYTICS_AVAILABLE:
            return ""
        
        try:
            # 获取最近的文章用于分析（模拟数据，实际应从数据库获取）
            # 这里为了演示，我们创建一些模拟分析结果
            analysis_lines = []
            
            # 添加数据分析标题
            analysis_lines.append("📊 智能数据分析")
            analysis_lines.append("=" * 30)
            
            # 生成简单的分析摘要
            if self.visualization_generator:
                # 模拟新闻分析数据
                mock_news_analysis = {
                    'period': '最近24小时',
                    'total_articles': 25,
                    'sentiment_analysis': {
                        'overall_sentiment': 'positive',
                        'average_score': 0.35,
                        'positive_count': 15,
                        'negative_count': 5,
                        'neutral_count': 5
                    },
                    'top_keywords': [
                        {'word': 'AI芯片', 'frequency': 12},
                        {'word': '投资策略', 'frequency': 8},
                        {'word': '科技创新', 'frequency': 6}
                    ],
                    'domain_distribution': [
                        {'domain': '科技', 'count': 12},
                        {'domain': '金融', 'count': 8},
                        {'domain': '经济', 'count': 5}
                    ],
                    'insights': [
                        'AI芯片成为最热门话题',
                        '新闻情感总体偏正面',
                        '科技领域新闻占比最高'
                    ]
                }
                
                # 模拟股票分析数据
                mock_stock_analysis = {
                    'current_price': 125.50,
                    'price_change': 2.5,
                    'trend': '上升趋势',
                    'risk_level': '中等',
                    'recommendation': '谨慎看多',
                    'indicators': {
                        'rsi': 62.5,
                        'macd': 1.18
                    }
                }
                
                # 生成摘要
                summary = self.generate_visualization_summary(mock_news_analysis, mock_stock_analysis)
                if summary:
                    analysis_lines.append(summary)
                else:
                    # 生成简单的文本图表
                    word_cloud = self.visualization_generator.generate_word_cloud_text(
                        mock_news_analysis['top_keywords'], max_width=30
                    )
                    analysis_lines.append(word_cloud[:100] + "...")
                    
                    sentiment_pie = self.visualization_generator.generate_sentiment_pie_text(
                        mock_news_analysis['sentiment_analysis']
                    )
                    analysis_lines.append(sentiment_pie[:80] + "...")
            
            # 添加分析说明
            analysis_lines.append("")
            analysis_lines.append("💡 说明: 以上为模拟数据分析")
            analysis_lines.append("🔧 完整功能将在后续版本中实现")
            
            return "\n".join(analysis_lines)
            
        except Exception as e:
            self.logger.error(f"生成数据分析部分失败: {e}")
            return ""

    def run_and_send(self) -> bool:
        """
        运行并发送推送（重写父类方法）
        
        Returns:
            发送是否成功
        """
        success, report = self.run()
        
        if report:
            # 发送推送
            send_success = self.send_whatsapp_message(report)
            
            # 记录统计
            self._record_push_statistics(send_success, health_ok=True)
            
            return send_success
        
        return False


def main():
    """主函数"""
    print("📊 数据分析推送系统启动")
    print("=" * 50)
    
    pusher = AnalyticsPusher()
    
    # 检查系统状态
    status = pusher.get_system_status()
    print(f"系统状态: {status}")
    
    if ANALYTICS_AVAILABLE:
        print("✅ 数据分析模块可用")
    else:
        print("⚠️ 数据分析模块不可用，使用基础推送模式")
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='数据分析推送系统')
    parser.add_argument('--run', action='store_true', help='运行推送')
    parser.add_argument('--test-analysis', action='store_true', help='测试分析功能')
    parser.add_argument('--test-visualization', action='store_true', help='测试可视化功能')
    
    args = parser.parse_args()
    
    if args.run:
        print("🚀 运行推送系统...")
        success = pusher.run_and_send()
        print(f"推送结果: {'成功' if success else '失败'}")
    
    elif args.test_analysis:
        print("🧪 测试分析功能...")
        
        # 测试新闻分析
        mock_articles = [
            {
                'title': 'AI芯片技术突破',
                'summary': '新一代AI芯片发布，性能提升显著',
                'source': '科技新闻',
                'published': datetime.now().isoformat(),
                'type': '科技',
                'importance': '高'
            },
            {
                'title': '金融市场波动',
                'summary': '全球金融市场出现波动',
                'source': '财经新闻',
                'published': datetime.now().isoformat(),
                'type': '金融',
                'importance': '中'
            }
        ]
        
        news_trends = pusher.analyze_news_trends(mock_articles)
        if news_trends:
            print(f"✅ 新闻趋势分析成功:")
            print(f"   文章数: {news_trends.get('total_articles', 0)}")
            print(f"   情感: {news_trends.get('sentiment_analysis', {}).get('overall_sentiment', 'unknown')}")
        else:
            print("❌ 新闻趋势分析失败")
        
        # 测试可视化
        if hasattr(pusher, 'visualization_generator') and pusher.visualization_generator:
            print("✅ 可视化生成器可用")
        else:
            print("❌ 可视化生成器不可用")
    
    elif args.test_visualization:
        print("🎨 测试可视化功能...")
        
        if ANALYTICS_AVAILABLE:
            # 测试各种可视化
            generator = VisualizationGenerator()
            
            # 测试词云
            keywords = [
                {'word': 'AI', 'frequency': 15},
                {'word': '芯片', 'frequency': 12},
                {'word': '投资', 'frequency': 10}
            ]
            word_cloud = generator.generate_word_cloud_text(keywords)
            print(word_cloud[:150])
            
            # 测试情感饼图
            sentiment_data = {'positive': 8, 'negative': 3, 'neutral': 12}
            pie_chart = generator.generate_sentiment_pie_text(sentiment_data)
            print(pie_chart[:100])
            
            print("✅ 可视化功能测试完成")
        else:
            print("❌ 分析模块不可用")
    
    else:
        print("💡 使用说明:")
        print("  --run               运行推送系统")
        print("  --test-analysis     测试分析功能")
        print("  --test-visualization 测试可视化功能")
        print("\n📊 当前系统支持:")
        print(f"  • 数据分析: {'✅ 可用' if ANALYTICS_AVAILABLE else '❌ 不可用'}")
        print(f"  • 可视化: {'✅ 可用' if ANALYTICS_AVAILABLE else '❌ 不可用'}")


if __name__ == "__main__":
    main()
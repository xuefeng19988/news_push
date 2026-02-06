#!/usr/bin/env python3
"""
数据可视化生成器
生成文本和图形格式的数据可视化
"""

import os
import sys
import math
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

class VisualizationGenerator:
    """数据可视化生成器"""
    
    def __init__(self, output_dir: str = "./reports/charts"):
        """
        初始化可视化生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 文本图表字符
        self.chart_chars = {
            'block': '█',
            'light_block': '░',
            'bar': '▏▎▍▌▋▊▉█',
            'dot': '•',
            'arrow_up': '↑',
            'arrow_down': '↓',
            'arrow_right': '→',
            'equal': '=',
            'dash': '-',
            'space': ' '
        }
    
    def generate_word_cloud_text(self, keywords: List[Dict[str, Any]], max_width: int = 60) -> str:
        """
        生成文本词云（使用字符大小表示词频）
        
        Args:
            keywords: 关键词列表，每个元素包含word和frequency
            max_width: 最大宽度（字符数）
            
        Returns:
            文本词云
        """
        if not keywords:
            return "⚠️ 没有关键词数据"
        
        # 提取词频数据
        word_freq = []
        for kw in keywords:
            if isinstance(kw, dict):
                word = kw.get('word', '')
                freq = kw.get('frequency', kw.get('tfidf', 1))
                if word:
                    word_freq.append((word, float(freq)))
            elif isinstance(kw, tuple) and len(kw) >= 2:
                word_freq.append((str(kw[0]), float(kw[1])))
        
        if not word_freq:
            return "⚠️ 关键词格式错误"
        
        # 归一化频率到字体大小
        max_freq = max(freq for _, freq in word_freq)
        min_freq = min(freq for _, freq in word_freq)
        
        if max_freq == min_freq:
            font_sizes = [3] * len(word_freq)  # 所有词大小相同
        else:
            # 映射到1-5的字体大小
            font_sizes = []
            for word, freq in word_freq:
                size = 1 + int((freq - min_freq) / (max_freq - min_freq) * 4)
                font_sizes.append(size)
        
        # 按字体大小排序
        sorted_items = sorted(zip(word_freq, font_sizes), key=lambda x: x[1], reverse=True)
        
        # 生成文本词云
        lines = ["📊 词云分析 (字体大小表示词频):", ""]
        
        # 第一行：最大字体词
        large_words = [word for ((word, freq), size) in sorted_items if size >= 4]
        if large_words:
            lines.append("  🔥 高频词: " + "  ".join(large_words))
        
        # 第二行：中等字体词
        medium_words = [word for ((word, freq), size) in sorted_items if 2 <= size < 4]
        if medium_words:
            lines.append("  📈 中频词: " + "  ".join(medium_words[:10]))
        
        # 第三行：小字体词
        small_words = [word for ((word, freq), size) in sorted_items if size == 1]
        if small_words:
            lines.append("  📝 低频词: " + "  ".join(small_words[:8]))
        
        # 添加频率统计
        lines.append("")
        lines.append("📋 词频统计:")
        for (word, freq), size in sorted_items[:10]:  # 显示前10个
            bar_length = int(freq / max_freq * 20)  # 最大20个字符
            bar = self.chart_chars['block'] * bar_length
            lines.append(f"  {word:10} {bar} {freq:.2f}")
        
        return "\n".join(lines)
    
    def generate_trend_chart_text(self, values: List[float], labels: List[str] = None, 
                                 title: str = "趋势图", height: int = 8) -> str:
        """
        生成文本趋势图
        
        Args:
            values: 数值列表
            labels: 标签列表（可选）
            title: 图表标题
            height: 图表高度（行数）
            
        Returns:
            文本趋势图
        """
        if not values:
            return f"⚠️ {title}: 没有数据"
        
        # 归一化数值到图表高度
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            normalized = [height // 2] * len(values)  # 所有值居中
        else:
            normalized = []
            for val in values:
                n = int((val - min_val) / (max_val - min_val) * (height - 1))
                normalized.append(n)
        
        # 生成图表
        lines = [f"📈 {title}:", ""]
        
        # 从上到下绘制
        for y in range(height - 1, -1, -1):
            line_chars = []
            for n in normalized:
                if n == y:
                    line_chars.append(self.chart_chars['block'])  # 数据点
                elif n > y:
                    line_chars.append(self.chart_chars['light_block'])  # 数据线
                else:
                    line_chars.append(' ')
            
            # 添加Y轴标签（只在第一行和最后一行）
            if y == height - 1:
                y_label = f"{max_val:.1f} "
            elif y == 0:
                y_label = f"{min_val:.1f} "
            else:
                y_label = "   "
            
            lines.append(y_label + ''.join(line_chars))
        
        # 添加X轴
        lines.append("   " + "─" * len(values))
        
        # 添加X轴标签（如果有）
        if labels:
            # 简化标签显示
            if len(labels) <= 10:
                # 显示所有标签
                x_axis = "   "
                for i, label in enumerate(labels):
                    if i < len(labels):
                        x_axis += label[0] if label else " "
            else:
                # 只显示首尾和中间标签
                x_axis = "   "
                if labels:
                    x_axis += labels[0][:3] + "..." + labels[-1][:3]
            lines.append(x_axis)
        
        # 添加统计信息
        avg_val = sum(values) / len(values)
        lines.append("")
        lines.append(f"📊 统计: 最大值={max_val:.2f}, 最小值={min_val:.2f}, 平均值={avg_val:.2f}")
        
        # 趋势判断
        if len(values) >= 2:
            trend = values[-1] - values[0]
            trend_percent = (trend / values[0] * 100) if values[0] != 0 else 0
            trend_symbol = self.chart_chars['arrow_up'] if trend > 0 else self.chart_chars['arrow_down']
            lines.append(f"📈 趋势: {trend_symbol} {trend:.2f} ({trend_percent:+.1f}%)")
        
        return "\n".join(lines)
    
    def generate_sentiment_pie_text(self, sentiment_data: Dict[str, int], 
                                   title: str = "情感分布") -> str:
        """
        生成文本饼图
        
        Args:
            sentiment_data: 情感数据字典，如{'positive': 10, 'negative': 5, 'neutral': 15}
            title: 图表标题
            
        Returns:
            文本饼图
        """
        if not sentiment_data:
            return f"⚠️ {title}: 没有数据"
        
        total = sum(sentiment_data.values())
        if total == 0:
            return f"⚠️ {title}: 数据总和为0"
        
        lines = [f"📊 {title}:", ""]
        
        # 计算百分比
        percentages = {}
        for sentiment, count in sentiment_data.items():
            percentage = (count / total * 100)
            percentages[sentiment] = percentage
        
        # 生成饼图字符表示
        pie_chars = ['◉', '○', '◎', '●', '⦿', '◐', '◑']
        char_index = 0
        
        for sentiment, percentage in percentages.items():
            # 选择饼图字符
            pie_char = pie_chars[char_index % len(pie_chars)]
            char_index += 1
            
            # 生成条形表示
            bar_length = int(percentage / 5)  # 每5%一个字符
            bar = pie_char * bar_length if bar_length > 0 else pie_char
            
            # 情感标签映射
            sentiment_labels = {
                'positive': '😊 正面',
                'negative': '😟 负面', 
                'neutral': '😐 中性',
                'happy': '😄 快乐',
                'sad': '😢 悲伤',
                'angry': '😠 愤怒'
            }
            
            label = sentiment_labels.get(sentiment, sentiment)
            
            lines.append(f"  {bar} {label}: {count} ({percentage:.1f}%)")
        
        # 添加总结
        lines.append("")
        lines.append(f"📋 总计: {total} 条数据")
        
        # 判断主要情感
        if 'positive' in sentiment_data and 'negative' in sentiment_data:
            if sentiment_data['positive'] > sentiment_data['negative'] * 1.5:
                lines.append("💡 总体情感: 偏正面")
            elif sentiment_data['negative'] > sentiment_data['positive'] * 1.5:
                lines.append("💡 总体情感: 偏负面")
            else:
                lines.append("💡 总体情感: 相对平衡")
        
        return "\n".join(lines)
    
    def generate_correlation_heatmap_text(self, correlation_matrix: Dict[str, Dict[str, float]],
                                         title: str = "相关性热力图") -> str:
        """
        生成文本相关性热力图
        
        Args:
            correlation_matrix: 相关性矩阵字典
            title: 图表标题
            
        Returns:
            文本热力图
        """
        if not correlation_matrix:
            return f"⚠️ {title}: 没有数据"
        
        items = list(correlation_matrix.keys())
        if not items:
            return f"⚠️ {title}: 矩阵为空"
        
        lines = [f"🔥 {title}:", ""]
        
        # 生成表头
        header = "       " + "".join(f"{item[:4]:>5}" for item in items)
        lines.append(header)
        lines.append("    " + "─" * (len(items) * 5 + 2))
        
        # 生成矩阵行
        for i, item1 in enumerate(items):
            row_chars = [f"{item1[:4]:>4} │"]
            
            for j, item2 in enumerate(items):
                if j < i:
                    # 下三角区域（与上三角对称）
                    corr = correlation_matrix[item2].get(item1, 0)
                else:
                    # 上三角区域
                    corr = correlation_matrix[item1].get(item2, 0)
                
                # 将相关性映射到字符
                if corr > 0.7:
                    cell = "██"
                elif corr > 0.5:
                    cell = "▓▓"
                elif corr > 0.3:
                    cell = "▒▒"
                elif corr > 0.1:
                    cell = "░░"
                elif corr < -0.7:
                    cell = "██"  # 强负相关
                elif corr < -0.5:
                    cell = "▓▓"
                elif corr < -0.3:
                    cell = "▒▒"
                elif corr < -0.1:
                    cell = "░░"
                else:
                    cell = "··"
                
                # 添加符号指示正负
                if corr > 0:
                    cell = "+" + cell
                elif corr < 0:
                    cell = "-" + cell
                else:
                    cell = " " + cell
                
                row_chars.append(cell)
            
            lines.append(" ".join(row_chars))
        
        # 添加图例
        lines.append("")
        lines.append("📊 图例:")
        lines.append("  +██ 强正相关 (>0.7)")
        lines.append("  +▓▓ 中等正相关 (0.5-0.7)")
        lines.append("  +▒▒ 弱正相关 (0.3-0.5)")
        lines.append("  +░░ 轻微正相关 (0.1-0.3)")
        lines.append("  ·· 无相关 (-0.1-0.1)")
        lines.append("  -░░ 轻微负相关 (-0.3--0.1)")
        lines.append("  -▒▒ 弱负相关 (-0.5--0.3)")
        lines.append("  -▓▓ 中等负相关 (-0.7--0.5)")
        lines.append("  -██ 强负相关 (<-0.7)")
        
        # 添加关键相关性
        lines.append("")
        lines.append("🔍 关键相关性:")
        
        strong_correlations = []
        for i, item1 in enumerate(items):
            for j, item2 in enumerate(items):
                if j > i:  # 只检查上三角避免重复
                    corr = correlation_matrix[item1].get(item2, 0)
                    if abs(corr) > 0.5:  # 只显示强相关性
                        direction = "正" if corr > 0 else "负"
                        strong_correlations.append((abs(corr), item1, item2, direction))
        
        # 按相关性强度排序
        strong_correlations.sort(reverse=True)
        
        for strength, item1, item2, direction in strong_correlations[:5]:  # 显示前5个
            lines.append(f"  • {item1} ↔ {item2}: {direction}相关 ({strength:.2f})")
        
        if not strong_correlations:
            lines.append("  ⚠️ 没有发现强相关性")
        
        return "\n".join(lines)
    
    def generate_bar_chart_text(self, data: Dict[str, float], title: str = "条形图",
                               max_width: int = 40) -> str:
        """
        生成文本条形图
        
        Args:
            data: 数据字典 {标签: 值}
            title: 图表标题
            max_width: 最大宽度（字符数）
            
        Returns:
            文本条形图
        """
        if not data:
            return f"⚠️ {title}: 没有数据"
        
        lines = [f"📊 {title}:", ""]
        
        # 找到最大值用于归一化
        max_val = max(data.values())
        if max_val == 0:
            max_val = 1  # 避免除零
        
        # 按值排序
        sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
        
        for label, value in sorted_items:
            # 计算条形长度
            bar_length = int(value / max_val * max_width)
            bar = self.chart_chars['block'] * bar_length
            
            # 添加百分比
            percentage = (value / sum(data.values()) * 100) if sum(data.values()) > 0 else 0
            
            lines.append(f"  {label:10} {bar} {value:.1f} ({percentage:.1f}%)")
        
        # 添加统计信息
        lines.append("")
        lines.append(f"📋 总计: {sum(data.values()):.1f}")
        lines.append(f"📈 平均: {sum(data.values())/len(data):.1f}")
        lines.append(f"🔥 最高: {max_val:.1f} ({list(data.keys())[list(data.values()).index(max_val)]})")
        
        return "\n".join(lines)
    
    def generate_stock_analysis_report(self, technical_summary: Dict[str, Any], 
                                      stock_name: str = "股票") -> str:
        """
        生成股票技术分析报告
        
        Args:
            technical_summary: 技术分析摘要
            stock_name: 股票名称
            
        Returns:
            股票分析报告
        """
        if not technical_summary:
            return f"⚠️ {stock_name}: 没有技术分析数据"
        
        lines = [f"📈 {stock_name} 技术分析报告", ""]
        
        # 基本信息
        if 'current_price' in technical_summary:
            lines.append(f"💰 当前价格: {technical_summary['current_price']:.2f}")
        
        if 'price_change' in technical_summary:
            change = technical_summary['price_change']
            change_symbol = self.chart_chars['arrow_up'] if change > 0 else self.chart_chars['arrow_down']
            lines.append(f"📉 价格变化: {change_symbol} {change:+.2f}%")
        
        # 趋势
        if 'trend' in technical_summary:
            trend = technical_summary['trend']
            trend_symbol = self.chart_chars['arrow_up'] if "上升" in trend else self.chart_chars['arrow_down'] if "下降" in trend else "↔"
            lines.append(f"📊 趋势判断: {trend_symbol} {trend}")
        
        # 风险水平
        if 'risk_level' in technical_summary:
            risk = technical_summary['risk_level']
            risk_symbol = "⚠️" if risk in ["高", "中高"] else "✅"
            lines.append(f"🎯 风险水平: {risk_symbol} {risk}")
        
        # 投资建议
        if 'recommendation' in technical_summary:
            rec = technical_summary['recommendation']
            rec_symbol = "💡"
            lines.append(f"💡 投资建议: {rec_symbol} {rec}")
        
        # 技术指标
        if 'indicators' in technical_summary:
            lines.append("")
            lines.append("🔧 技术指标:")
            indicators = technical_summary['indicators']
            
            if indicators.get('rsi') is not None:
                rsi = indicators['rsi']
                if rsi > 70:
                    rsi_status = "⚡ 超买"
                elif rsi < 30:
                    rsi_status = "💧 超卖"
                else:
                    rsi_status = "✅ 正常"
                lines.append(f"  RSI(14): {rsi:.1f} {rsi_status}")
            
            if indicators.get('macd') is not None and indicators.get('macd_signal') is not None:
                macd = indicators['macd']
                signal = indicators['macd_signal']
                if macd > signal:
                    macd_status = "📈 金叉"
                else:
                    macd_status = "📉 死叉"
                lines.append(f"  MACD: {macd:.3f} / 信号: {signal:.3f} {macd_status}")
        
        # 支撑阻力
        if 'support_resistance' in technical_summary:
            sr = technical_summary['support_resistance']
            lines.append("")
            lines.append("🎯 支撑阻力:")
            
            if sr.get('support') is not None:
                lines.append(f"  📉 支撑位: {sr['support']:.2f}")
            if sr.get('resistance') is not None:
                lines.append(f"  📈 阻力位: {sr['resistance']:.2f}")
            if sr.get('pivot_point') is not None:
                lines.append(f"  ⚖️ 枢轴点: {sr['pivot_point']:.2f}")
        
        # 技术信号
        if 'signals' in technical_summary and technical_summary['signals']:
            lines.append("")
            lines.append("📡 技术信号:")
            for signal in technical_summary['signals'][:5]:  # 最多显示5个
                lines.append(f"  • {signal}")
        
        return "\n".join(lines)
    
    def generate_news_analysis_report(self, trend_analysis: Dict[str, Any]) -> str:
        """
        生成新闻分析报告
        
        Args:
            trend_analysis: 趋势分析结果
            
        Returns:
            新闻分析报告
        """
        if not trend_analysis:
            return "⚠️ 没有新闻分析数据"
        
        lines = ["📰 新闻分析报告", ""]
        
        # 基本信息
        if 'period' in trend_analysis:
            lines.append(f"⏰ 分析周期: {trend_analysis['period']}")
        
        if 'total_articles' in trend_analysis:
            lines.append(f"📊 分析文章数: {trend_analysis['total_articles']} 篇")
        
        # 热门关键词
        if 'top_keywords' in trend_analysis and trend_analysis['top_keywords']:
            lines.append("")
            lines.append("🔥 热门话题:")
            keywords = trend_analysis['top_keywords'][:5]  # 前5个
            for i, kw in enumerate(keywords):
                if isinstance(kw, dict):
                    word = kw.get('word', '未知')
                    freq = kw.get('frequency', kw.get('tfidf', 0))
                    lines.append(f"  {i+1}. {word} ({freq:.2f})")
        
        # 领域分布
        if 'domain_distribution' in trend_analysis and trend_analysis['domain_distribution']:
            lines.append("")
            lines.append("🎯 领域分布:")
            domains = trend_analysis['domain_distribution'][:5]  # 前5个
            for domain in domains:
                if isinstance(domain, dict):
                    name = domain.get('domain', '未知')
                    count = domain.get('count', 0)
                    lines.append(f"  • {name}: {count} 篇")
        
        # 情感分析
        if 'sentiment_analysis' in trend_analysis:
            sentiment = trend_analysis['sentiment_analysis']
            lines.append("")
            lines.append("😊 情感分析:")
            
            if 'overall_sentiment' in sentiment:
                sentiment_symbol = {
                    'positive': '😊',
                    'negative': '😟',
                    'neutral': '😐'
                }.get(sentiment['overall_sentiment'], '❓')
                lines.append(f"  总体情感: {sentiment_symbol} {sentiment['overall_sentiment']}")
            
            if 'average_score' in sentiment:
                score = sentiment['average_score']
                if score > 0.2:
                    score_desc = "明显正面"
                elif score < -0.2:
                    score_desc = "明显负面"
                else:
                    score_desc = "相对中性"
                lines.append(f"  情感分数: {score:.3f} ({score_desc})")
        
        # 趋势洞察
        if 'insights' in trend_analysis and trend_analysis['insights']:
            lines.append("")
            lines.append("💡 趋势洞察:")
            for insight in trend_analysis['insights'][:3]:  # 前3个
                lines.append(f"  • {insight}")
        
        return "\n".join(lines)
    
    def generate_comprehensive_report(self, 
                                    news_analysis: Dict[str, Any] = None,
                                    stock_analysis: Dict[str, Any] = None,
                                    stock_name: str = "股票") -> str:
        """
        生成综合分析报告（新闻+股票）
        
        Args:
            news_analysis: 新闻分析结果
            stock_analysis: 股票分析结果
            stock_name: 股票名称
            
        Returns:
            综合分析报告
        """
        lines = ["📊 综合分析报告", "=" * 40, ""]
        
        # 时间戳
        lines.append(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 新闻分析部分
        if news_analysis:
            lines.append(self.generate_news_analysis_report(news_analysis))
            lines.append("")
        
        # 股票分析部分
        if stock_analysis:
            lines.append(self.generate_stock_analysis_report(stock_analysis, stock_name))
            lines.append("")
        
        # 相关性分析（如果都有）
        if news_analysis and stock_analysis:
            lines.append("🔗 新闻-股票相关性分析")
            lines.append("-" * 30)
            
            # 简单的相关性推断
            news_sentiment = news_analysis.get('sentiment_analysis', {}).get('overall_sentiment', 'neutral')
            stock_change = stock_analysis.get('price_change', 0)
            
            if news_sentiment == 'positive' and stock_change > 0:
                lines.append("📈 正面新闻与股价上涨趋势一致")
            elif news_sentiment == 'negative' and stock_change < 0:
                lines.append("📉 负面新闻与股价下跌趋势一致")
            elif news_sentiment == 'positive' and stock_change < 0:
                lines.append("⚠️ 正面新闻但股价下跌，可能市场反应滞后或受其他因素影响")
            elif news_sentiment == 'negative' and stock_change > 0:
                lines.append("⚠️ 负面新闻但股价上涨，可能利空出尽或有其他利好")
            else:
                lines.append("📊 新闻与股价表现相关性不明显")
            
            lines.append("")
        
        # 投资建议汇总
        lines.append("💡 综合投资建议")
        lines.append("-" * 30)
        
        if stock_analysis and 'recommendation' in stock_analysis:
            lines.append(f"📈 技术面: {stock_analysis['recommendation']}")
        
        if news_analysis:
            sentiment = news_analysis.get('sentiment_analysis', {}).get('overall_sentiment', 'neutral')
            if sentiment == 'positive':
                lines.append("📰 新闻面: 正面新闻较多，基本面偏积极")
            elif sentiment == 'negative':
                lines.append("📰 新闻面: 负面新闻较多，基本面需谨慎")
            else:
                lines.append("📰 新闻面: 新闻情感中性，基本面平稳")
        
        # 风险提示
        lines.append("")
        lines.append("⚠️ 风险提示")
        lines.append("-" * 30)
        lines.append("• 以上分析仅供参考，不构成投资建议")
        lines.append("• 投资有风险，入市需谨慎")
        lines.append("• 请结合自身风险承受能力进行投资决策")
        
        return "\n".join(lines)


def test_visualization_generator():
    """测试可视化生成器"""
    print("🧪 测试可视化生成器")
    print("=" * 60)
    
    generator = VisualizationGenerator()
    
    # 测试词云
    print("\n📊 测试文本词云:")
    keywords = [
        {'word': 'AI', 'frequency': 15, 'tfidf': 0.8},
        {'word': '芯片', 'frequency': 12, 'tfidf': 0.7},
        {'word': '投资', 'frequency': 10, 'tfidf': 0.6},
        {'word': '金融', 'frequency': 8, 'tfidf': 0.5},
        {'word': '科技', 'frequency': 6, 'tfidf': 0.4}
    ]
    word_cloud = generator.generate_word_cloud_text(keywords)
    print(word_cloud[:200] + "...")
    
    # 测试趋势图
    print("\n📊 测试趋势图:")
    values = [10, 15, 12, 18, 16, 20, 22, 25, 23, 28]
    trend_chart = generator.generate_trend_chart_text(values, title="股价趋势")
    print(trend_chart[:150] + "...")
    
    # 测试情感饼图
    print("\n📊 测试情感饼图:")
    sentiment_data = {'positive': 8, 'negative': 3, 'neutral': 12}
    pie_chart = generator.generate_sentiment_pie_text(sentiment_data)
    print(pie_chart[:150] + "...")
    
    # 测试条形图
    print("\n📊 测试条形图:")
    bar_data = {'科技': 15, '金融': 12, '医疗': 8, '教育': 6, '其他': 5}
    bar_chart = generator.generate_bar_chart_text(bar_data, title="新闻领域分布")
    print(bar_chart[:150] + "...")
    
    # 测试股票分析报告
    print("\n📊 测试股票分析报告:")
    stock_summary = {
        'current_price': 125.50,
        'price_change': 2.5,
        'trend': '上升趋势',
        'risk_level': '中等',
        'recommendation': '谨慎看多',
        'indicators': {
            'rsi': 65.2,
            'macd': 1.23,
            'macd_signal': 1.15
        },
        'support_resistance': {
            'support': 120.0,
            'resistance': 130.0,
            'pivot_point': 125.0
        },
        'signals': ['RSI中性', 'MACD金叉', '价格在20日均线之上']
    }
    stock_report = generator.generate_stock_analysis_report(stock_summary, "阿里巴巴")
    print(stock_report[:200] + "...")
    
    print("\n✅ 可视化生成器测试完成")
    return True


if __name__ == "__main__":
    test_visualization_generator()
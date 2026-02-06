#!/usr/bin/env python3
"""
趋势分析器
分析新闻趋势、关键词提取、情感分析
"""

import re
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import math

class TrendAnalyzer:
    """趋势分析器"""
    
    def __init__(self, db_path: str = "./news_cache.db"):
        """
        初始化分析器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        
        # 中文停用词（简化版）
        self.chinese_stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要',
            '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '她', '他', '它', '我们', '你们', '他们', '她们',
            '它们', '这个', '那个', '这些', '那些', '这里', '那里', '这样', '那样', '这么', '那么', '什么', '怎么', '为什么',
            '可以', '可能', '可能', '能够', '需要', '应该', '必须', '一定', '也许', '大概', '大约', '左右', '上下', '前后'
        }
        
        # 情感词典（简化版）
        self.sentiment_lexicon = {
            'positive': {
                '好', '优秀', '成功', '胜利', '进步', '发展', '增长', '提高', '提升', '改善', '优化', '创新', '突破', '领先',
                '先进', '强大', '繁荣', '稳定', '安全', '可靠', '信任', '满意', '高兴', '快乐', '幸福', '爱', '喜欢', '支持',
                '赞成', '同意', '认可', '表扬', '赞美', '鼓励', '帮助', '合作', '共赢', '成功', '成就', '辉煌', '光明', '希望',
                '未来', '前景', '机会', '机遇', '潜力', '价值', '意义', '重要', '关键', '核心', '中心', '主要', '首要', '必要'
            },
            'negative': {
                '坏', '糟糕', '失败', '失利', '退步', '衰退', '下降', '降低', '下跌', '恶化', '恶化', '落后', '落后', '弱小',
                '贫穷', '动荡', '危险', '不可靠', '不信任', '不满意', '不高兴', '悲伤', '痛苦', '恨', '讨厌', '反对', '否决',
                '拒绝', '否认', '批评', '指责', '抱怨', '妨碍', '破坏', '冲突', '矛盾', '问题', '困难', '挑战', '风险', '危机',
                '威胁', '压力', '紧张', '焦虑', '恐惧', '担忧', '失望', '绝望', '黑暗', '过去', '历史', '教训', '损失', '损害',
                '伤害', '破坏', '毁灭', '灾难', '事故', '错误', '失误', '缺点', '不足', '缺陷', '漏洞', '弱点', '短板'
            }
        }
        
        # 领域关键词
        self.domain_keywords = {
            '政治': ['政府', '政治', '外交', '国际', '国家', '主席', '总统', '总理', '国会', '议会', '选举', '政策', '法律', '法规'],
            '经济': ['经济', 'GDP', '财政', '金融', '货币', '银行', '投资', '市场', '贸易', '商业', '企业', '公司', '产业', '行业'],
            '科技': ['科技', '技术', '创新', '研发', '科学', '研究', '开发', 'AI', '人工智能', '芯片', '半导体', '互联网', '数字'],
            '股票': ['股票', '股市', '股价', '指数', '投资', '证券', '交易所', '市值', '涨跌', '交易', '买卖', '牛市', '熊市'],
            '国际': ['国际', '全球', '世界', '国家', '地区', '大陆', '海外', '外国', '跨国', '跨境', '外交', '关系', '合作', '竞争'],
            '社会': ['社会', '民生', '人民', '群众', '公众', '公民', '生活', '工作', '就业', '教育', '医疗', '健康', '环境', '安全']
        }
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        提取关键词（基于TF-IDF简化版）
        
        Args:
            text: 文本内容
            top_n: 返回前N个关键词
            
        Returns:
            关键词列表，每个关键词包含词、频率、TF-IDF分数
        """
        if not text or len(text) < 10:
            return []
        
        # 中文分词（简化版：按标点和空格分割）
        words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        words = [word for word in words if word not in self.chinese_stopwords]
        
        if not words:
            return []
        
        # 计算词频
        word_counts = Counter(words)
        total_words = len(words)
        
        # 计算TF（词频）
        keywords = []
        for word, count in word_counts.most_common(top_n * 2):  # 多取一些用于过滤
            tf = count / total_words
            
            # 简单IDF估计（基于领域词典）
            idf = 1.0
            for domain, domain_words in self.domain_keywords.items():
                if word in domain_words:
                    idf = 2.0  # 领域关键词权重更高
                    break
            
            tfidf = tf * idf
            
            # 过滤太常见的词
            if tf < 0.01:  # 频率太低，可能不重要
                continue
                
            keywords.append({
                'word': word,
                'frequency': count,
                'tf': round(tf, 4),
                'idf': idf,
                'tfidf': round(tfidf, 4),
                'domain': self._identify_domain(word)
            })
        
        # 按TF-IDF排序
        keywords.sort(key=lambda x: x['tfidf'], reverse=True)
        return keywords[:top_n]
    
    def _identify_domain(self, word: str) -> str:
        """识别词所属领域"""
        for domain, keywords in self.domain_keywords.items():
            if word in keywords:
                return domain
        return '其他'
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        分析文本情感
        
        Args:
            text: 文本内容
            
        Returns:
            情感分析结果
        """
        if not text:
            return {'sentiment': 'neutral', 'score': 0.0, 'positive_words': [], 'negative_words': []}
        
        # 提取中文词语
        words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        
        positive_words = []
        negative_words = []
        positive_count = 0
        negative_count = 0
        
        for word in words:
            if word in self.sentiment_lexicon['positive']:
                positive_words.append(word)
                positive_count += 1
            elif word in self.sentiment_lexicon['negative']:
                negative_words.append(word)
                negative_count += 1
        
        total_emotional_words = positive_count + negative_count
        
        if total_emotional_words == 0:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'positive_words': [],
                'negative_words': [],
                'positive_count': 0,
                'negative_count': 0,
                'total_emotional_words': 0
            }
        
        sentiment_score = (positive_count - negative_count) / total_emotional_words
        
        if sentiment_score > 0.2:
            sentiment = 'positive'
        elif sentiment_score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': round(sentiment_score, 3),
            'positive_words': list(set(positive_words)),
            'negative_words': list(set(negative_words)),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'total_emotional_words': total_emotional_words
        }
    
    def analyze_news_trends(self, articles: List[Dict[str, Any]], hours: int = 24) -> Dict[str, Any]:
        """
        分析新闻趋势
        
        Args:
            articles: 文章列表
            hours: 分析的时间范围（小时）
            
        Returns:
            趋势分析结果
        """
        if not articles:
            return {'error': '没有文章数据'}
        
        # 按时间分组（简化：按最近N小时）
        now = datetime.now()
        cutoff_time = now - timedelta(hours=hours)
        
        recent_articles = []
        for article in articles:
            try:
                if isinstance(article.get('published'), str):
                    # 尝试解析时间
                    pub_time = datetime.fromisoformat(article['published'].replace('Z', '+00:00'))
                else:
                    pub_time = now
                
                if pub_time > cutoff_time:
                    recent_articles.append(article)
            except:
                recent_articles.append(article)
        
        if not recent_articles:
            return {'error': f'最近{hours}小时内没有文章'}
        
        # 收集所有文本内容
        all_text = ' '.join([
            f"{article.get('title', '')} {article.get('summary', '')}"
            for article in recent_articles
        ])
        
        # 提取关键词
        keywords = self.extract_keywords(all_text, top_n=20)
        
        # 分析领域分布
        domain_distribution = {}
        for article in recent_articles:
            article_type = article.get('type', '一般新闻')
            if '、' in article_type:
                types = article_type.split('、')
                for t in types:
                    domain_distribution[t] = domain_distribution.get(t, 0) + 1
            else:
                domain_distribution[article_type] = domain_distribution.get(article_type, 0) + 1
        
        # 分析重要性分布
        importance_distribution = {}
        for article in recent_articles:
            importance = article.get('importance', '中')
            importance_distribution[importance] = importance_distribution.get(importance, 0) + 1
        
        # 分析来源分布
        source_distribution = {}
        for article in recent_articles:
            source = article.get('source', '未知')
            source_distribution[source] = source_distribution.get(source, 0) + 1
        
        # 情感分析
        sentiment_results = []
        for article in recent_articles[:10]:  # 只分析前10篇
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            sentiment = self.analyze_sentiment(text)
            sentiment_results.append({
                'title': article.get('title', '')[:50],
                'sentiment': sentiment['sentiment'],
                'score': sentiment['score']
            })
        
        # 计算总体情感
        total_score = sum(s.get('score', 0) for s in sentiment_results)
        avg_sentiment_score = total_score / len(sentiment_results) if sentiment_results else 0
        
        if avg_sentiment_score > 0.1:
            overall_sentiment = 'positive'
        elif avg_sentiment_score < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'period': f'最近{hours}小时',
            'total_articles': len(recent_articles),
            'timestamp': now.isoformat(),
            
            # 关键词分析
            'top_keywords': keywords[:10],
            
            # 分布分析
            'domain_distribution': [
                {'domain': domain, 'count': count}
                for domain, count in sorted(domain_distribution.items(), key=lambda x: x[1], reverse=True)
            ],
            'importance_distribution': [
                {'importance': imp, 'count': count}
                for imp, count in sorted(importance_distribution.items(), key=lambda x: x[1], reverse=True)
            ],
            'source_distribution': [
                {'source': src, 'count': count}
                for src, count in sorted(source_distribution.items(), key=lambda x: x[1], reverse=True)
            ],
            
            # 情感分析
            'sentiment_analysis': {
                'overall_sentiment': overall_sentiment,
                'average_score': round(avg_sentiment_score, 3),
                'sample_articles': sentiment_results[:5],
                'positive_count': sum(1 for s in sentiment_results if s['sentiment'] == 'positive'),
                'negative_count': sum(1 for s in sentiment_results if s['sentiment'] == 'negative'),
                'neutral_count': sum(1 for s in sentiment_results if s['sentiment'] == 'neutral')
            },
            
            # 趋势洞察
            'insights': self._generate_insights(
                keywords,
                domain_distribution,
                importance_distribution,
                sentiment_results
            )
        }
    
    def _generate_insights(self, keywords, domain_distribution, importance_distribution, sentiment_results) -> List[str]:
        """生成趋势洞察"""
        insights = []
        
        # 基于关键词的洞察
        if keywords:
            top_keyword = keywords[0]['word']
            insights.append(f"热门话题: '{top_keyword}' 是当前最受关注的话题")
        
        # 基于领域的洞察
        if domain_distribution:
            top_domain = max(domain_distribution.items(), key=lambda x: x[1])
            insights.append(f"主要领域: {top_domain[0]}类新闻占比最高 ({top_domain[1]}篇)")
        
        # 基于重要性的洞察
        if importance_distribution:
            high_importance = importance_distribution.get('高', 0)
            if high_importance > 0:
                insights.append(f"重要新闻: 有 {high_importance} 篇高重要性新闻，值得特别关注")
        
        # 基于情感的洞察
        if sentiment_results:
            positive_count = sum(1 for s in sentiment_results if s['sentiment'] == 'positive')
            negative_count = sum(1 for s in sentiment_results if s['sentiment'] == 'negative')
            
            if positive_count > negative_count * 2:
                insights.append("情感倾向: 当前新闻总体偏正面")
            elif negative_count > positive_count * 2:
                insights.append("情感倾向: 当前新闻总体偏负面")
            else:
                insights.append("情感倾向: 当前新闻情感分布较为平衡")
        
        # 组合洞察
        if len(insights) < 3:
            insights.append("趋势观察: 新闻分布较为均衡，没有明显热点")
        
        return insights[:5]  # 最多5条洞察
    
    def analyze_stock_correlation(self, news_trends: Dict[str, Any], stock_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析新闻与股票相关性（简化版）
        
        Args:
            news_trends: 新闻趋势分析结果
            stock_data: 股票数据列表
            
        Returns:
            相关性分析结果
        """
        if not stock_data:
            return {'error': '没有股票数据'}
        
        # 简化的相关性分析
        # 在实际应用中，这里会使用时间序列分析和相关性计算
        
        correlation_results = []
        
        for stock in stock_data:
            stock_name = stock.get('name', '未知')
            stock_symbol = stock.get('symbol', '')
            stock_change = stock.get('change_percent', 0)
            
            # 简单的相关性逻辑（示例）
            correlation = 'unknown'
            correlation_score = 0
            
            if news_trends.get('overall_sentiment') == 'positive' and stock_change > 0:
                correlation = 'positive'
                correlation_score = 0.7
            elif news_trends.get('overall_sentiment') == 'negative' and stock_change < 0:
                correlation = 'negative'
                correlation_score = 0.7
            elif abs(stock_change) < 0.5:
                correlation = 'neutral'
                correlation_score = 0.3
            
            correlation_results.append({
                'stock': stock_name,
                'symbol': stock_symbol,
                'change_percent': stock_change,
                'correlation': correlation,
                'correlation_score': correlation_score,
                'news_impact': self._estimate_news_impact(stock_name, news_trends)
            })
        
        return {
            'analysis_period': news_trends.get('period', '未知'),
            'overall_sentiment': news_trends.get('sentiment_analysis', {}).get('overall_sentiment', 'unknown'),
            'stock_correlations': correlation_results,
            'insights': [
                f"新闻情感与股票涨跌的简单相关性分析",
                f"基于最近新闻趋势对股票表现的初步评估"
            ]
        }
    
    def _estimate_news_impact(self, stock_name: str, news_trends: Dict[str, Any]) -> str:
        """估计新闻对股票的影响（简化版）"""
        # 基于股票名称和新闻关键词的简单匹配
        stock_keywords = {
            '阿里巴巴': ['电商', '科技', '互联网', '马云', '淘宝', '天猫'],
            '小米': ['手机', '科技', '智能', '雷军', '硬件'],
            '比亚迪': ['汽车', '新能源', '电动车', '电池', '制造']
        }
        
        keywords = [kw['word'] for kw in news_trends.get('top_keywords', [])]
        
        for stock, stock_kws in stock_keywords.items():
            if stock in stock_name:
                matching_keywords = [kw for kw in keywords if kw in stock_kws]
                if matching_keywords:
                    return f"高相关（相关关键词: {', '.join(matching_keywords[:3])}）"
        
        return "一般相关"


def test_trend_analyzer():
    """测试趋势分析器"""
    print("🧪 测试趋势分析器")
    print("=" * 60)
    
    analyzer = TrendAnalyzer()
    
    # 测试文本
    test_text = """
    中国政府宣布新的经济刺激计划，旨在促进经济增长和创造就业。
    这一举措受到了市场的积极回应，股市今天大幅上涨。
    专家认为这一政策将有助于稳定经济和增强市场信心。
    """
    
    print("📊 测试关键词提取:")
    keywords = analyzer.extract_keywords(test_text, top_n=5)
    for kw in keywords:
        print(f"  • {kw['word']} (频率: {kw['frequency']}, TF-IDF: {kw['tfidf']}, 领域: {kw['domain']})")
    
    print("\n📊 测试情感分析:")
    sentiment = analyzer.analyze_sentiment(test_text)
    print(f"  情感: {sentiment['sentiment']}")
    print(f"  分数: {sentiment['score']}")
    print(f"  积极词: {', '.join(sentiment['positive_words'][:5])}")
    print(f"  消极词: {', '.join(sentiment['negative_words'][:5])}")
    
    print("\n📊 测试新闻趋势分析:")
    test_articles = [
        {
            'title': '中国经济刺激计划推动股市上涨',
            'summary': '政府宣布新政策，市场反应积极',
            'source': '测试源',
            'published': datetime.now().isoformat(),
            'type': '经济、政治',
            'importance': '高'
        },
        {
            'title': '科技公司发布新产品',
            'summary': '领先科技公司推出创新产品',
            'source': '测试源',
            'published': datetime.now().isoformat(),
            'type': '科技',
            'importance': '中'
        }
    ]
    
    trends = analyzer.analyze_news_trends(test_articles, hours=24)
    print(f"  分析周期: {trends['period']}")
    print(f"  文章总数: {trends['total_articles']}")
    print(f"  情感倾向: {trends['sentiment_analysis']['overall_sentiment']}")
    
    if trends.get('insights'):
        print("  趋势洞察:")
        for insight in trends['insights'][:3]:
            print(f"    • {insight}")
    
    print("\n✅ 趋势分析器测试完成")
    return True


if __name__ == "__main__":
    test_trend_analyzer()
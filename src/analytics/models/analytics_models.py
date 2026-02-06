"""
数据分析模块 - 数据模型定义
定义数据分析所需的数据结构和模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class PushStatus(str, Enum):
    """推送状态枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    PENDING = "pending"


class ContentType(str, Enum):
    """内容类型枚举"""
    NEWS = "news"
    STOCK = "stock"
    SYSTEM = "system"
    MIXED = "mixed"


class ImportanceLevel(str, Enum):
    """重要性级别枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class PushRecord:
    """
    推送记录数据模型
    记录每次推送的详细信息
    """
    push_id: str
    timestamp: datetime
    content_type: ContentType
    status: PushStatus
    message_length: int
    processing_time: float  # 秒
    
    # 内容信息
    news_count: int = 0
    stock_count: int = 0
    sources: List[str] = field(default_factory=list)
    
    # 系统信息
    system_health: float = 0.0  # 健康度百分比
    error_message: Optional[str] = None
    
    # 用户交互（如果有）
    user_feedback: Optional[str] = None
    interaction_time: Optional[datetime] = None
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "push_id": self.push_id,
            "timestamp": self.timestamp.isoformat(),
            "content_type": self.content_type.value,
            "status": self.status.value,
            "message_length": self.message_length,
            "processing_time": self.processing_time,
            "news_count": self.news_count,
            "stock_count": self.stock_count,
            "sources": self.sources,
            "system_health": self.system_health,
            "error_message": self.error_message,
            "user_feedback": self.user_feedback,
            "interaction_time": self.interaction_time.isoformat() if self.interaction_time else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PushRecord':
        """从字典创建实例"""
        return cls(
            push_id=data["push_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            content_type=ContentType(data["content_type"]),
            status=PushStatus(data["status"]),
            message_length=data["message_length"],
            processing_time=data["processing_time"],
            news_count=data.get("news_count", 0),
            stock_count=data.get("stock_count", 0),
            sources=data.get("sources", []),
            system_health=data.get("system_health", 0.0),
            error_message=data.get("error_message"),
            user_feedback=data.get("user_feedback"),
            interaction_time=datetime.fromisoformat(data["interaction_time"]) if data.get("interaction_time") else None,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )


@dataclass
class NewsArticle:
    """
    新闻文章数据模型
    记录新闻文章的详细信息
    """
    article_id: str
    title: str
    source: str
    url: str
    publish_time: datetime
    summary: str
    
    # 分析字段
    importance: ImportanceLevel = ImportanceLevel.UNKNOWN
    relevance_score: float = 0.0  # 相关性评分 0-1
    read_time_estimate: int = 0  # 预计阅读时间（秒）
    
    # 推送信息
    push_times: List[datetime] = field(default_factory=list)
    user_feedback: Optional[str] = None
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "article_id": self.article_id,
            "title": self.title,
            "source": self.source,
            "url": self.url,
            "publish_time": self.publish_time.isoformat(),
            "summary": self.summary,
            "importance": self.importance.value,
            "relevance_score": self.relevance_score,
            "read_time_estimate": self.read_time_estimate,
            "push_times": [t.isoformat() for t in self.push_times],
            "user_feedback": self.user_feedback,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class StockData:
    """
    股票数据模型
    记录股票数据的详细信息
    """
    stock_id: str
    symbol: str
    name: str
    market: str
    
    # 价格数据
    price: float
    change: float
    change_percent: float
    volume: int
    
    # 分析字段
    volatility_score: float = 0.0  # 波动性评分
    trend_direction: str = "neutral"  # 趋势方向: up/down/neutral
    
    # 时间信息
    timestamp: datetime = field(default_factory=datetime.now)
    data_source: str = "unknown"  # 数据来源
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "stock_id": self.stock_id,
            "symbol": self.symbol,
            "name": self.name,
            "market": self.market,
            "price": self.price,
            "change": self.change,
            "change_percent": self.change_percent,
            "volume": self.volume,
            "volatility_score": self.volatility_score,
            "trend_direction": self.trend_direction,
            "timestamp": self.timestamp.isoformat(),
            "data_source": self.data_source,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class UserInteraction:
    """
    用户交互数据模型
    记录用户与推送的交互信息
    """
    interaction_id: str
    user_id: str
    push_id: str
    
    # 交互类型
    interaction_type: str  # read, click, reply, feedback, etc.
    interaction_time: datetime
    
    # 交互内容
    content: Optional[str] = None
    sentiment_score: float = 0.0  # 情感评分 -1到1
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "interaction_id": self.interaction_id,
            "user_id": self.user_id,
            "push_id": self.push_id,
            "interaction_type": self.interaction_type,
            "interaction_time": self.interaction_time.isoformat(),
            "content": self.content,
            "sentiment_score": self.sentiment_score,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class SystemPerformance:
    """
    系统性能数据模型
    记录系统运行性能指标
    """
    performance_id: str
    timestamp: datetime
    
    # 资源使用
    cpu_usage: float  # CPU使用率百分比
    memory_usage: float  # 内存使用率百分比
    disk_usage: float  # 磁盘使用率百分比
    
    # 网络性能
    network_latency: float  # 网络延迟（毫秒）
    api_success_rate: float  # API成功率百分比
    
    # 推送性能
    push_success_rate: float  # 推送成功率百分比
    avg_processing_time: float  # 平均处理时间（秒）
    
    # 错误信息
    error_count: int = 0
    warning_count: int = 0
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "performance_id": self.performance_id,
            "timestamp": self.timestamp.isoformat(),
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "network_latency": self.network_latency,
            "api_success_rate": self.api_success_rate,
            "push_success_rate": self.push_success_rate,
            "avg_processing_time": self.avg_processing_time,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class AnalyticsSummary:
    """
    分析总结数据模型
    汇总分析结果
    """
    summary_id: str
    period_start: datetime
    period_end: datetime
    
    # 推送统计
    total_pushes: int
    success_pushes: int
    avg_message_length: float
    avg_processing_time: float
    
    # 内容统计
    total_news_articles: int
    total_stock_updates: int
    top_sources: List[Dict[str, Any]]
    
    # 用户交互统计
    total_interactions: int
    avg_sentiment_score: float
    common_feedback: List[str]
    
    # 系统性能
    avg_system_health: float
    performance_trend: str  # improving/stable/declining
    
    # 优化建议
    optimization_suggestions: List[str]
    
    # 元数据
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "summary_id": self.summary_id,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_pushes": self.total_pushes,
            "success_pushes": self.success_pushes,
            "avg_message_length": self.avg_message_length,
            "avg_processing_time": self.avg_processing_time,
            "total_news_articles": self.total_news_articles,
            "total_stock_updates": self.total_stock_updates,
            "top_sources": self.top_sources,
            "total_interactions": self.total_interactions,
            "avg_sentiment_score": self.avg_sentiment_score,
            "common_feedback": self.common_feedback,
            "avg_system_health": self.avg_system_health,
            "performance_trend": self.performance_trend,
            "optimization_suggestions": self.optimization_suggestions,
            "generated_at": self.generated_at.isoformat()
        }


# 数据模型工厂函数
def create_push_record(
    push_id: str,
    timestamp: datetime,
    content_type: ContentType,
    status: PushStatus,
    message_length: int,
    processing_time: float,
    **kwargs
) -> PushRecord:
    """创建推送记录"""
    return PushRecord(
        push_id=push_id,
        timestamp=timestamp,
        content_type=content_type,
        status=status,
        message_length=message_length,
        processing_time=processing_time,
        **kwargs
    )


def create_news_article(
    article_id: str,
    title: str,
    source: str,
    url: str,
    publish_time: datetime,
    summary: str,
    **kwargs
) -> NewsArticle:
    """创建新闻文章记录"""
    return NewsArticle(
        article_id=article_id,
        title=title,
        source=source,
        url=url,
        publish_time=publish_time,
        summary=summary,
        **kwargs
    )


# 测试函数
def test_models():
    """测试数据模型"""
    print("测试数据模型...")
    
    # 测试推送记录
    push_record = create_push_record(
        push_id="test_001",
        timestamp=datetime.now(),
        content_type=ContentType.MIXED,
        status=PushStatus.SUCCESS,
        message_length=1500,
        processing_time=12.5,
        news_count=5,
        stock_count=3,
        sources=["BBC", "CNN", "FT"],
        system_health=95.0
    )
    
    print(f"推送记录创建: {push_record.push_id}")
    print(f"内容类型: {push_record.content_type.value}")
    print(f"状态: {push_record.status.value}")
    
    # 转换为字典并返回
    push_dict = push_record.to_dict()
    print(f"转换为字典成功: {len(push_dict)} 个字段")
    
    # 从字典创建
    push_from_dict = PushRecord.from_dict(push_dict)
    print(f"从字典创建成功: {push_from_dict.push_id}")
    
    print("✅ 数据模型测试通过")
    return True


if __name__ == "__main__":
    test_models()
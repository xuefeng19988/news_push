#!/usr/bin/env python3
"""
股票技术指标计算器
计算移动平均线、RSI、MACD、布林带等指标
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import statistics

class StockIndicatorCalculator:
    """股票技术指标计算器"""
    
    def __init__(self, price_data: List[Dict[str, Any]] = None):
        """
        初始化计算器
        
        Args:
            price_data: 价格数据列表，每个元素包含以下字段:
                - timestamp: 时间戳
                - open: 开盘价
                - high: 最高价  
                - low: 最低价
                - close: 收盘价
                - volume: 成交量 (可选)
        """
        self.price_data = price_data or []
        
        # 按时间排序（从旧到新）
        if self.price_data:
            self.price_data.sort(key=lambda x: x.get('timestamp', ''))
    
    def add_price_data(self, price_data: Dict[str, Any]):
        """添加价格数据"""
        self.price_data.append(price_data)
        self.price_data.sort(key=lambda x: x.get('timestamp', ''))
    
    def get_close_prices(self) -> List[float]:
        """获取收盘价列表（时间顺序）"""
        return [float(item.get('close', 0)) for item in self.price_data]
    
    def get_high_prices(self) -> List[float]:
        """获取最高价列表（时间顺序）"""
        return [float(item.get('high', 0)) for item in self.price_data]
    
    def get_low_prices(self) -> List[float]:
        """获取最低价列表（时间顺序）"""
        return [float(item.get('low', 0)) for item in self.price_data]
    
    def get_volumes(self) -> List[float]:
        """获取成交量列表（时间顺序）"""
        return [float(item.get('volume', 0)) for item in self.price_data]
    
    def calculate_sma(self, period: int = 5) -> List[Optional[float]]:
        """
        计算简单移动平均线 (SMA)
        
        Args:
            period: 周期（例如5日、10日、20日）
            
        Returns:
            移动平均值列表，前period-1个为None
        """
        close_prices = self.get_close_prices()
        if len(close_prices) < period:
            return [None] * len(close_prices)
        
        sma_values = [None] * (period - 1)
        
        for i in range(period - 1, len(close_prices)):
            window = close_prices[i - period + 1:i + 1]
            sma = sum(window) / period
            sma_values.append(sma)
        
        return sma_values
    
    def calculate_ema(self, period: int = 12) -> List[Optional[float]]:
        """
        计算指数移动平均线 (EMA)
        
        Args:
            period: 周期
            
        Returns:
            EMA值列表，前period-1个为None
        """
        close_prices = self.get_close_prices()
        if len(close_prices) < period:
            return [None] * len(close_prices)
        
        # 计算平滑系数
        k = 2 / (period + 1)
        
        # 初始EMA使用SMA
        sma = sum(close_prices[:period]) / period
        
        ema_values = [None] * (period - 1)
        ema_values.append(sma)
        
        # 计算后续EMA
        for i in range(period, len(close_prices)):
            ema = close_prices[i] * k + ema_values[i - 1] * (1 - k)
            ema_values.append(ema)
        
        return ema_values
    
    def calculate_rsi(self, period: int = 14) -> List[Optional[float]]:
        """
        计算相对强弱指数 (RSI)
        
        Args:
            period: RSI周期，通常为14
            
        Returns:
            RSI值列表，前period个为None
        """
        close_prices = self.get_close_prices()
        if len(close_prices) < period + 1:
            return [None] * len(close_prices)
        
        # 计算价格变化
        price_changes = []
        for i in range(1, len(close_prices)):
            change = close_prices[i] - close_prices[i - 1]
            price_changes.append(change)
        
        rsi_values = [None] * period
        
        # 计算初始平均增益和平均损失
        gains = [max(0, change) for change in price_changes[:period]]
        losses = [max(0, -change) for change in price_changes[:period]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        # 计算第一个RSI
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        rsi_values.append(rsi)
        
        # 计算后续RSI值
        for i in range(period, len(price_changes)):
            gain = max(0, price_changes[i])
            loss = max(0, -price_changes[i])
            
            # 平滑平均增益和损失
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        # 添加一个None以匹配原始价格数据长度
        if len(rsi_values) < len(close_prices):
            rsi_values = [None] * (len(close_prices) - len(rsi_values)) + rsi_values
        
        return rsi_values
    
    def calculate_macd(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, List[Optional[float]]]:
        """
        计算MACD指标
        
        Args:
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            包含MACD、信号线和柱状图的字典
        """
        close_prices = self.get_close_prices()
        min_period = max(fast_period, slow_period) + signal_period
        
        if len(close_prices) < min_period:
            empty_list = [None] * len(close_prices)
            return {"macd_line": empty_list, "signal_line": empty_list, "histogram": empty_list}
        
        # 计算快线和慢线EMA
        fast_ema = self.calculate_ema(fast_period)
        slow_ema = self.calculate_ema(slow_period)
        
        # 计算MACD线 (快线 - 慢线)
        macd_line = []
        for i in range(len(close_prices)):
            if fast_ema[i] is None or slow_ema[i] is None:
                macd_line.append(None)
            else:
                macd_line.append(fast_ema[i] - slow_ema[i])
        
        # 计算信号线 (MACD线的EMA)
        # 创建临时的Calculator来计算信号线
        temp_calc = StockIndicatorCalculator()
        macd_data_points = []
        
        for i, macd in enumerate(macd_line):
            if macd is not None:
                timestamp = self.price_data[i].get('timestamp', i)
                temp_calc.add_price_data({
                    'timestamp': timestamp,
                    'close': macd,
                    'open': macd,
                    'high': macd,
                    'low': macd,
                    'volume': 0
                })
        
        signal_line_ema = temp_calc.calculate_ema(signal_period)
        
        # 对齐信号线
        signal_line = [None] * len(close_prices)
        signal_index = 0
        for i in range(len(close_prices)):
            if macd_line[i] is not None:
                if signal_index < len(signal_line_ema):
                    signal_line[i] = signal_line_ema[signal_index]
                    signal_index += 1
        
        # 计算柱状图 (MACD线 - 信号线)
        histogram = []
        for i in range(len(close_prices)):
            if macd_line[i] is None or signal_line[i] is None:
                histogram.append(None)
            else:
                histogram.append(macd_line[i] - signal_line[i])
        
        return {
            "macd_line": macd_line,
            "signal_line": signal_line,
            "histogram": histogram
        }
    
    def calculate_bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> Dict[str, List[Optional[float]]]:
        """
        计算布林带
        
        Args:
            period: 移动平均周期
            std_dev: 标准差倍数
            
        Returns:
            包含上轨、中轨、下轨的字典
        """
        close_prices = self.get_close_prices()
        if len(close_prices) < period:
            empty_list = [None] * len(close_prices)
            return {"upper_band": empty_list, "middle_band": empty_list, "lower_band": empty_list}
        
        # 中轨：SMA
        middle_band = self.calculate_sma(period)
        
        # 计算标准差和布林带
        upper_band = [None] * len(close_prices)
        lower_band = [None] * len(close_prices)
        
        for i in range(period - 1, len(close_prices)):
            if middle_band[i] is not None:
                window = close_prices[i - period + 1:i + 1]
                std = statistics.stdev(window) if len(window) > 1 else 0
                
                upper_band[i] = middle_band[i] + std_dev * std
                lower_band[i] = middle_band[i] - std_dev * std
        
        return {
            "upper_band": upper_band,
            "middle_band": middle_band,
            "lower_band": lower_band
        }
    
    def calculate_volume_indicators(self) -> Dict[str, List[Optional[float]]]:
        """
        计算成交量指标
        
        Returns:
            包含成交量移动平均和量比指标的字典
        """
        volumes = self.get_volumes()
        if not volumes:
            empty_list = [None] * len(self.price_data)
            return {"volume_sma": empty_list, "volume_ratio": empty_list}
        
        # 成交量移动平均 (5日)
        volume_sma = [None] * 4  # 前4天没有SMA
        
        for i in range(4, len(volumes)):
            window = volumes[i - 4:i + 1]
            sma = sum(window) / 5
            volume_sma.append(sma)
        
        # 确保长度匹配
        if len(volume_sma) < len(volumes):
            volume_sma.extend([None] * (len(volumes) - len(volume_sma)))
        
        # 量比 (当日成交量 / 5日平均成交量)
        volume_ratio = [None] * len(volumes)
        for i in range(len(volumes)):
            if volume_sma[i] is not None and volume_sma[i] > 0:
                volume_ratio[i] = volumes[i] / volume_sma[i]
        
        return {
            "volume_sma": volume_sma,
            "volume_ratio": volume_ratio
        }
    
    def calculate_support_resistance(self, lookback_period: int = 20) -> Dict[str, Any]:
        """
        计算支撑位和阻力位
        
        Args:
            lookback_period: 回顾周期
            
        Returns:
            支撑位和阻力位信息
        """
        if len(self.price_data) < lookback_period:
            return {"support": None, "resistance": None, "pivot_point": None}
        
        recent_prices = self.price_data[-lookback_period:]
        highs = [p.get('high', 0) for p in recent_prices]
        lows = [p.get('low', 0) for p in recent_prices]
        closes = [p.get('close', 0) for p in recent_prices]
        
        # 计算典型价格
        typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        
        # 简单的支撑阻力计算
        resistance = max(highs)
        support = min(lows)
        
        # 枢轴点 (简化计算)
        if len(recent_prices) >= 1:
            last = recent_prices[-1]
            pivot = (last.get('high', 0) + last.get('low', 0) + last.get('close', 0)) / 3
            r1 = 2 * pivot - last.get('low', 0)
            s1 = 2 * pivot - last.get('high', 0)
        else:
            pivot = r1 = s1 = None
        
        return {
            "support": support,
            "resistance": resistance,
            "pivot_point": pivot,
            "r1": r1,
            "s1": s1,
            "price_range": resistance - support,
            "current_price": closes[-1] if closes else None
        }
    
    def generate_technical_summary(self) -> Dict[str, Any]:
        """
        生成技术分析摘要
        
        Returns:
            技术分析摘要
        """
        if len(self.price_data) < 10:
            return {"error": "数据不足，需要至少10个价格数据点"}
        
        # 获取当前价格数据
        current_price = self.get_close_prices()[-1]
        
        # 计算各种指标
        sma_5 = self.calculate_sma(5)
        sma_10 = self.calculate_sma(10)
        sma_20 = self.calculate_sma(20)
        
        rsi = self.calculate_rsi(14)
        macd = self.calculate_macd()
        bollinger = self.calculate_bollinger_bands()
        volume_indicators = self.calculate_volume_indicators()
        support_resistance = self.calculate_support_resistance()
        
        # 获取最新指标值
        latest_sma_5 = sma_5[-1] if sma_5 and sma_5[-1] is not None else None
        latest_sma_10 = sma_10[-1] if sma_10 and sma_10[-1] is not None else None
        latest_sma_20 = sma_20[-1] if sma_20 and sma_20[-1] is not None else None
        latest_rsi = rsi[-1] if rsi and rsi[-1] is not None else None
        latest_macd = macd["macd_line"][-1] if macd["macd_line"] and macd["macd_line"][-1] is not None else None
        latest_signal = macd["signal_line"][-1] if macd["signal_line"] and macd["signal_line"][-1] is not None else None
        
        # 生成技术信号
        signals = []
        
        # RSI信号
        if latest_rsi is not None:
            if latest_rsi > 70:
                signals.append("RSI超买 (>70)")
            elif latest_rsi < 30:
                signals.append("RSI超卖 (<30)")
            else:
                signals.append("RSI中性")
        
        # MACD信号
        if latest_macd is not None and latest_signal is not None:
            if latest_macd > latest_signal:
                signals.append("MACD金叉 (看涨)")
            elif latest_macd < latest_signal:
                signals.append("MACD死叉 (看跌)")
        
        # 移动平均线信号
        if latest_sma_5 is not None and latest_sma_10 is not None:
            if latest_sma_5 > latest_sma_10:
                signals.append("5日均线上穿10日均线")
            elif latest_sma_5 < latest_sma_10:
                signals.append("5日均线下穿10日均线")
        
        # 价格相对于移动平均线
        if latest_sma_20 is not None:
            if current_price > latest_sma_20:
                signals.append("价格在20日均线之上")
            else:
                signals.append("价格在20日均线之下")
        
        # 布林带信号
        upper_band = bollinger["upper_band"][-1] if bollinger["upper_band"] and bollinger["upper_band"][-1] is not None else None
        lower_band = bollinger["lower_band"][-1] if bollinger["lower_band"] and bollinger["lower_band"][-1] is not None else None
        
        if upper_band is not None and lower_band is not None:
            if current_price > upper_band:
                signals.append("价格突破布林带上轨")
            elif current_price < lower_band:
                signals.append("价格跌破布林带下轨")
            else:
                signals.append("价格在布林带内运行")
        
        # 成交量信号
        volume_ratio = volume_indicators["volume_ratio"][-1] if volume_indicators["volume_ratio"] and volume_indicators["volume_ratio"][-1] is not None else None
        if volume_ratio is not None:
            if volume_ratio > 1.5:
                signals.append("放量交易")
            elif volume_ratio < 0.5:
                signals.append("缩量交易")
        
        # 生成分析摘要
        summary = {
            "timestamp": datetime.now().isoformat(),
            "current_price": current_price,
            "price_change": None,
            "indicators": {
                "sma_5": latest_sma_5,
                "sma_10": latest_sma_10,
                "sma_20": latest_sma_20,
                "rsi": latest_rsi,
                "macd": latest_macd,
                "macd_signal": latest_signal,
                "bollinger_upper": upper_band,
                "bollinger_lower": lower_band,
                "volume_ratio": volume_ratio
            },
            "support_resistance": support_resistance,
            "signals": signals,
            "trend": self._assess_trend(sma_5, sma_10, sma_20),
            "risk_level": self._assess_risk_level(latest_rsi, signals),
            "recommendation": self._generate_recommendation(signals, latest_rsi, current_price, support_resistance)
        }
        
        # 计算价格变化（如果有足够数据）
        if len(self.get_close_prices()) >= 2:
            prev_price = self.get_close_prices()[-2]
            price_change = ((current_price - prev_price) / prev_price * 100) if prev_price != 0 else 0
            summary["price_change"] = round(price_change, 2)
        
        return summary
    
    def _assess_trend(self, sma_5: List, sma_10: List, sma_20: List) -> str:
        """评估趋势"""
        if not sma_5 or not sma_10 or not sma_20:
            return "不确定"
        
        latest_sma_5 = sma_5[-1]
        latest_sma_10 = sma_10[-1]
        latest_sma_20 = sma_20[-1]
        
        if latest_sma_5 is None or latest_sma_10 is None or latest_sma_20 is None:
            return "不确定"
        
        # 检查均线排列
        if latest_sma_5 > latest_sma_10 > latest_sma_20:
            return "上升趋势"
        elif latest_sma_5 < latest_sma_10 < latest_sma_20:
            return "下降趋势"
        else:
            return "震荡趋势"
    
    def _assess_risk_level(self, rsi: float, signals: List[str]) -> str:
        """评估风险水平"""
        if rsi is None:
            return "中等"
        
        risk_factors = 0
        
        # RSI风险因素
        if rsi > 75 or rsi < 25:
            risk_factors += 2
        elif rsi > 70 or rsi < 30:
            risk_factors += 1
        
        # 信号风险因素
        for signal in signals:
            if "超买" in signal or "超卖" in signal or "突破" in signal or "跌破" in signal:
                risk_factors += 1
        
        if risk_factors >= 3:
            return "高"
        elif risk_factors >= 2:
            return "中高"
        elif risk_factors >= 1:
            return "中等"
        else:
            return "低"
    
    def _generate_recommendation(self, signals: List[str], rsi: float, current_price: float, support_resistance: Dict) -> str:
        """生成投资建议"""
        if not signals:
            return "观望"
        
        # 计算积极和消极信号
        bullish_signals = 0
        bearish_signals = 0
        
        for signal in signals:
            signal_lower = signal.lower()
            if any(word in signal_lower for word in ["金叉", "看涨", "之上", "突破上轨", "放量"]):
                bullish_signals += 1
            elif any(word in signal_lower for word in ["死叉", "看跌", "之下", "跌破下轨", "缩量", "超买", "超卖"]):
                bearish_signals += 1
        
        # RSI考虑
        if rsi is not None:
            if rsi > 70:
                bearish_signals += 1
            elif rsi < 30:
                bullish_signals += 1
        
        # 价格相对于支撑阻力
        if support_resistance.get("support") and support_resistance.get("resistance"):
            support = support_resistance["support"]
            resistance = support_resistance["resistance"]
            
            if current_price < support * 1.02:  # 接近支撑
                bullish_signals += 1
            elif current_price > resistance * 0.98:  # 接近阻力
                bearish_signals += 1
        
        # 生成建议
        if bullish_signals > bearish_signals + 1:
            return "考虑买入"
        elif bearish_signals > bullish_signals + 1:
            return "考虑卖出"
        elif bullish_signals > bearish_signals:
            return "谨慎看多"
        elif bearish_signals > bullish_signals:
            return "谨慎看空"
        else:
            return "观望"


def test_indicator_calculator():
    """测试技术指标计算器"""
    print("🧪 测试技术指标计算器")
    print("=" * 60)
    
    # 生成模拟价格数据
    import random
    from datetime import datetime, timedelta
    
    price_data = []
    base_price = 100.0
    current_time = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        # 模拟价格波动
        change = random.uniform(-2.0, 2.0)
        base_price = max(10.0, base_price + change)
        
        price_data.append({
            "timestamp": (current_time + timedelta(days=i)).isoformat(),
            "open": base_price + random.uniform(-0.5, 0.5),
            "high": base_price + random.uniform(0.5, 1.5),
            "low": base_price - random.uniform(0.5, 1.5),
            "close": base_price,
            "volume": random.randint(10000, 50000)
        })
    
    # 创建计算器
    calculator = StockIndicatorCalculator(price_data)
    
    print("📊 价格数据统计:")
    print(f"  数据点数: {len(price_data)}")
    print(f"  最新价格: {price_data[-1]['close']}")
    print(f"  时间范围: {price_data[0]['timestamp'][:10]} 至 {price_data[-1]['timestamp'][:10]}")
    
    print("\n📈 计算技术指标:")
    
    # 移动平均线
    sma_5 = calculator.calculate_sma(5)
    sma_10 = calculator.calculate_sma(10)
    print(f"  5日SMA: {sma_5[-1] if sma_5[-1] else 'N/A'}")
    print(f"  10日SMA: {sma_10[-1] if sma_10[-1] else 'N/A'}")
    
    # RSI
    rsi = calculator.calculate_rsi(14)
    print(f"  14日RSI: {rsi[-1] if rsi[-1] else 'N/A'}")
    
    # MACD
    macd = calculator.calculate_macd()
    print(f"  MACD: {macd['macd_line'][-1] if macd['macd_line'][-1] else 'N/A'}")
    print(f"  信号线: {macd['signal_line'][-1] if macd['signal_line'][-1] else 'N/A'}")
    
    # 布林带
    bollinger = calculator.calculate_bollinger_bands()
    print(f"  布林带上轨: {bollinger['upper_band'][-1] if bollinger['upper_band'][-1] else 'N/A'}")
    print(f"  布林带中轨: {bollinger['middle_band'][-1] if bollinger['middle_band'][-1] else 'N/A'}")
    print(f"  布林带下轨: {bollinger['lower_band'][-1] if bollinger['lower_band'][-1] else 'N/A'}")
    
    print("\n📋 生成技术分析摘要:")
    summary = calculator.generate_technical_summary()
    
    print(f"  当前价格: {summary.get('current_price')}")
    print(f"  趋势评估: {summary.get('trend')}")
    print(f"  风险水平: {summary.get('risk_level')}")
    print(f"  投资建议: {summary.get('recommendation')}")
    
    if summary.get('signals'):
        print(f"  技术信号:")
        for signal in summary['signals'][:5]:  # 最多显示5个
            print(f"    • {signal}")
    
    if summary.get('support_resistance'):
        sr = summary['support_resistance']
        print(f"  支撑阻力:")
        print(f"    支撑位: {sr.get('support')}")
        print(f"    阻力位: {sr.get('resistance')}")
        print(f"    枢轴点: {sr.get('pivot_point')}")
    
    print("\n✅ 技术指标计算器测试完成")
    return True


if __name__ == "__main__":
    test_indicator_calculator()
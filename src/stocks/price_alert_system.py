#!/usr/bin/env python3
"""
价格预警系统 - 实时监控股票价格，触发预警通知
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PriceAlertSystem:
    """价格预警系统"""
    
    def __init__(self, config_file: str = "/home/admin/clawd/alert_config.json"):
        self.config_file = config_file
        
        # 默认预警配置
        self.default_alerts = {
            "阿里巴巴-W": {
                "symbol": "09988.HK",
                "alerts": [
                    {"type": "price_above", "value": 165.00, "message": "阿里巴巴突破165港元"},
                    {"type": "price_below", "value": 158.00, "message": "阿里巴巴跌破158港元"},
                    {"type": "percent_change", "value": 3.0, "message": "阿里巴巴涨跌幅超过3%"}
                ]
            },
            "小米集团-W": {
                "symbol": "01810.HK",
                "alerts": [
                    {"type": "price_above", "value": 35.00, "message": "小米突破35港元"},
                    {"type": "price_below", "value": 34.00, "message": "小米跌破34港元"},
                    {"type": "percent_change", "value": 3.0, "message": "小米涨跌幅超过3%"}
                ]
            },
            "比亚迪": {
                "symbol": "002594.SZ",
                "alerts": [
                    {"type": "price_above", "value": 88.00, "message": "比亚迪突破88元"},
                    {"type": "price_below", "value": 86.00, "message": "比亚迪跌破86元"},
                    {"type": "percent_change", "value": 3.0, "message": "比亚迪涨跌幅超过3%"}
                ]
            }
        }
        
        self.alerts_config = self.load_config()
        self.alert_history_file = "/home/admin/clawd/alert_history.json"
        self.alert_history = self.load_alert_history()
        
        # 预警冷却时间 (避免重复预警)
        self.cooldown_minutes = 30
    
    def load_config(self) -> Dict:
        """加载预警配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 创建默认配置
                config = {
                    "alerts": self.default_alerts,
                    "enabled": True,
                    "notification_channels": ["whatsapp"],
                    "check_interval_minutes": 5,
                    "working_hours": {"start": 8, "end": 22}
                }
                self.save_config(config)
                return config
        except Exception as e:
            logger.error(f"加载预警配置失败: {e}")
            return {"alerts": self.default_alerts, "enabled": True}
    
    def save_config(self, config: Dict):
        """保存预警配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存预警配置失败: {e}")
    
    def load_alert_history(self) -> Dict:
        """加载预警历史"""
        try:
            if os.path.exists(self.alert_history_file):
                with open(self.alert_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"alerts": [], "last_check": None}
        except Exception as e:
            logger.error(f"加载预警历史失败: {e}")
            return {"alerts": [], "last_check": None}
    
    def save_alert_history(self):
        """保存预警历史"""
        try:
            with open(self.alert_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.alert_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存预警历史失败: {e}")
    
    def should_check_alerts(self) -> bool:
        """是否应该检查预警"""
        if not self.alerts_config.get("enabled", True):
            return False
        
        # 检查工作时间
        current_hour = datetime.now().hour
        working_hours = self.alerts_config.get("working_hours", {"start": 8, "end": 22})
        
        if current_hour < working_hours["start"] or current_hour >= working_hours["end"]:
            logger.info(f"⏭️ 非工作时间，跳过预警检查 (当前时间: {current_hour}:00)")
            return False
        
        # 检查冷却时间
        last_check = self.alert_history.get("last_check")
        if last_check:
            last_check_time = datetime.fromisoformat(last_check)
            time_diff = datetime.now() - last_check_time
            if time_diff.total_seconds() < self.alerts_config.get("check_interval_minutes", 5) * 60:
                logger.info(f"⏭️ 冷却时间内，跳过预警检查")
                return False
        
        return True
    
    def check_price_alert(self, stock_name: str, current_price: float, previous_price: float = None) -> List[Dict]:
        """检查价格预警"""
        alerts_triggered = []
        
        if stock_name not in self.alerts_config.get("alerts", {}):
            return alerts_triggered
        
        stock_config = self.alerts_config["alerts"][stock_name]
        symbol = stock_config.get("symbol", "")
        
        for alert in stock_config.get("alerts", []):
            alert_type = alert.get("type")
            alert_value = alert.get("value")
            alert_message = alert.get("message", "")
            
            triggered = False
            alert_details = None
            
            if alert_type == "price_above" and current_price > alert_value:
                triggered = True
                alert_details = {
                    "type": "price_above",
                    "threshold": alert_value,
                    "current": current_price,
                    "difference": current_price - alert_value,
                    "message": f"{stock_name} ({symbol}) 当前价格 {current_price} 超过预警阈值 {alert_value}"
                }
            
            elif alert_type == "price_below" and current_price < alert_value:
                triggered = True
                alert_details = {
                    "type": "price_below",
                    "threshold": alert_value,
                    "current": current_price,
                    "difference": alert_value - current_price,
                    "message": f"{stock_name} ({symbol}) 当前价格 {current_price} 低于预警阈值 {alert_value}"
                }
            
            elif alert_type == "percent_change" and previous_price:
                percent_change = ((current_price - previous_price) / previous_price) * 100
                if abs(percent_change) >= alert_value:
                    triggered = True
                    alert_details = {
                        "type": "percent_change",
                        "threshold": alert_value,
                        "current_change": percent_change,
                        "previous_price": previous_price,
                        "current_price": current_price,
                        "message": f"{stock_name} ({symbol}) 涨跌幅 {percent_change:.2f}% 超过预警阈值 {alert_value}%"
                    }
            
            if triggered and alert_details:
                # 检查是否已经触发过相同预警
                if not self.is_duplicate_alert(stock_name, alert_type, alert_value):
                    alert_details["stock"] = stock_name
                    alert_details["symbol"] = symbol
                    alert_details["alert_message"] = alert_message
                    alert_details["timestamp"] = datetime.now().isoformat()
                    
                    alerts_triggered.append(alert_details)
                    logger.info(f"⚠️ 预警触发: {alert_details['message']}")
        
        return alerts_triggered
    
    def is_duplicate_alert(self, stock_name: str, alert_type: str, alert_value: float) -> bool:
        """检查是否为重复预警"""
        recent_alerts = self.alert_history.get("alerts", [])
        
        # 只检查最近30分钟的预警
        cutoff_time = datetime.now() - timedelta(minutes=self.cooldown_minutes)
        
        for alert in recent_alerts:
            if (alert.get("stock") == stock_name and 
                alert.get("type") == alert_type and 
                alert.get("threshold") == alert_value):
                
                alert_time = datetime.fromisoformat(alert.get("timestamp"))
                if alert_time > cutoff_time:
                    return True
        
        return False
    
    def format_alert_message(self, alert: Dict) -> str:
        """格式化预警消息"""
        emoji = "⚠️" if alert["type"] in ["price_below", "percent_change"] else "🚀"
        
        message = f"{emoji} **价格预警**\n\n"
        message += f"📈 **股票**: {alert['stock']} ({alert['symbol']})\n"
        message += f"💰 **当前价格**: {alert['current']}\n"
        
        if alert["type"] == "price_above":
            message += f"📊 **突破阈值**: {alert['threshold']}\n"
            message += f"📈 **超出**: +{alert['difference']:.2f}\n"
        
        elif alert["type"] == "price_below":
            message += f"📊 **跌破阈值**: {alert['threshold']}\n"
            message += f"📉 **低于**: -{alert['difference']:.2f}\n"
        
        elif alert["type"] == "percent_change":
            change_emoji = "📈" if alert["current_change"] > 0 else "📉"
            message += f"📊 **涨跌幅**: {change_emoji} {alert['current_change']:.2f}%\n"
            message += f"🎯 **预警阈值**: {alert['threshold']}%\n"
            message += f"📅 **前价/现价**: {alert['previous_price']} → {alert['current_price']}\n"
        
        message += f"\n💡 **预警说明**: {alert.get('alert_message', '')}\n"
        message += f"⏰ **触发时间**: {datetime.now().strftime('%H:%M:%S')}\n"
        
        # 添加建议
        if alert["type"] == "price_above":
            message += "\n🎯 **操作建议**: 考虑部分获利了结或设置止损"
        elif alert["type"] == "price_below":
            message += "\n🎯 **操作建议**: 关注支撑位，谨慎抄底"
        elif alert["type"] == "percent_change":
            if alert["current_change"] > 0:
                message += "\n🎯 **操作建议**: 关注成交量配合，避免追高"
            else:
                message += "\n🎯 **操作建议**: 控制仓位，等待企稳"
        
        return message
    
    def process_stock_data(self, stock_data: List[Dict]) -> List[Dict]:
        """处理股票数据，检查预警"""
        if not self.should_check_alerts():
            return []
        
        logger.info("🔍 开始检查价格预警...")
        
        all_alerts = []
        
        for stock in stock_data:
            stock_name = stock.get("name")
            current_price = stock.get("price")
            
            if not stock_name or not current_price:
                continue
            
            # 获取前一次价格 (简化处理，实际应该从历史数据获取)
            previous_price = None
            
            # 检查预警
            alerts = self.check_price_alert(stock_name, current_price, previous_price)
            
            if alerts:
                all_alerts.extend(alerts)
                
                # 记录预警历史
                for alert in alerts:
                    self.alert_history["alerts"].append(alert)
                
                # 限制历史记录数量
                if len(self.alert_history["alerts"]) > 100:
                    self.alert_history["alerts"] = self.alert_history["alerts"][-100:]
        
        # 更新最后检查时间
        self.alert_history["last_check"] = datetime.now().isoformat()
        self.save_alert_history()
        
        if all_alerts:
            logger.info(f"✅ 发现 {len(all_alerts)} 个预警")
        else:
            logger.info("✅ 未发现预警")
        
        return all_alerts
    
    def get_alert_summary(self, alerts: List[Dict]) -> str:
        """获取预警摘要"""
        if not alerts:
            return "✅ 当前无价格预警"
        
        summary = f"⚠️ **价格预警摘要** ({len(alerts)}个预警)\n\n"
        
        for i, alert in enumerate(alerts, 1):
            summary += f"{i}. **{alert['stock']}** ({alert['symbol']})\n"
            summary += f"   📊 {alert['message']}\n"
            summary += f"   ⏰ {alert['timestamp'][11:19]}\n\n"
        
        summary += "---\n"
        summary += f"📅 检查时间: {datetime.now().strftime('%H:%M:%S')}\n"
        summary += f"🔔 预警总数: {len(alerts)}\n"
        summary += f"🔄 下次检查: {self.alerts_config.get('check_interval_minutes', 5)}分钟后\n"
        
        return summary

def test_price_alert_system():
    """测试价格预警系统"""
    print("⚠️ 测试价格预警系统...")
    
    alert_system = PriceAlertSystem()
    
    # 测试数据
    test_stocks = [
        {
            "name": "阿里巴巴-W",
            "symbol": "09988.HK",
            "price": 166.50,  # 超过165预警阈值
            "change_percent": 3.5
        },
        {
            "name": "小米集团-W", 
            "symbol": "01810.HK",
            "price": 33.80,  # 低于34预警阈值
            "change_percent": -2.3
        },
        {
            "name": "比亚迪",
            "symbol": "002594.SZ",
            "price": 89.50,  # 超过88预警阈值
            "change_percent": 4.2
        }
    ]
    
    # 处理预警
    alerts = alert_system.process_stock_data(test_stocks)
    
    if alerts:
        print(f"✅ 发现 {len(alerts)} 个预警:")
        for alert in alerts:
            print(f"  - {alert['message']}")
        
        # 格式化消息
        for alert in alerts:
            message = alert_system.format_alert_message(alert)
            print(f"\n📱 预警消息示例:\n{'-'*40}")
            print(message)
            print(f"{'-'*40}")
        
        # 摘要
        summary = alert_system.get_alert_summary(alerts)
        print(f"\n📋 预警摘要:\n{'-'*40}")
        print(summary)
    else:
        print("✅ 未发现预警")
    
    return alert_system

if __name__ == "__main__":
    alert_system = test_price_alert_system()
    print("\n⚠️ 价格预警系统测试完成")
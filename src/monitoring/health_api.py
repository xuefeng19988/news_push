#!/usr/bin/env python3
"""
健康检查API模块
提供RESTful API接口检查系统健康状态
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict, Any
from datetime import datetime
from .health_check import HealthChecker

class HealthAPI:
    """健康检查API类"""
    
    def __init__(self):
        """初始化API"""
        self.health_checker = HealthChecker()
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        获取健康状态
        
        Returns:
            健康状态响应
        """
        report = self.health_checker.check_all()
        
        # 根据总体状态设置HTTP状态码
        status_code = 200 if report["overall_status"] == "healthy" else 503
        
        response = {
            "status": report["overall_status"],
            "timestamp": report["timestamp"],
            "health_percentage": report["summary"]["health_percentage"],
            "checks": report["checks"],
            "summary": report["summary"],
            "formatted_report": self.health_checker.format_report_for_display(report)
        }
        
        return response, status_code
    
    def get_database_health(self) -> Dict[str, Any]:
        """
        获取数据库健康状态
        
        Returns:
            数据库健康状态
        """
        check_result = self.health_checker.check_database()
        
        response = {
            "component": "database",
            "status": check_result["status"],
            "timestamp": check_result["timestamp"],
            "response_time_ms": check_result["response_time"],
            "message": check_result["message"]
        }
        
        status_code = 200 if check_result["status"] == "healthy" else 503
        
        return response, status_code
    
    def get_whatsapp_health(self) -> Dict[str, Any]:
        """
        获取WhatsApp健康状态
        
        Returns:
            WhatsApp健康状态
        """
        check_result = self.health_checker.check_whatsapp_connection()
        
        response = {
            "component": "whatsapp",
            "status": check_result["status"],
            "timestamp": check_result["timestamp"],
            "response_time_ms": check_result["response_time"],
            "message": check_result["message"]
        }
        
        status_code = 200 if check_result["status"] == "healthy" else 503
        
        return response, status_code
    
    def get_wechat_health(self) -> Dict[str, Any]:
        """
        获取微信健康状态
        
        Returns:
            微信健康状态
        """
        check_result = self.health_checker.check_wechat_connection()
        
        response = {
            "component": "wechat",
            "status": check_result["status"],
            "timestamp": check_result["timestamp"],
            "response_time_ms": check_result["response_time"],
            "message": check_result["message"]
        }
        
        # 微信未配置时返回200，只有错误时才返回503
        if check_result["status"] in ["disabled", "warning"]:
            status_code = 200
        elif check_result["status"] == "healthy":
            status_code = 200
        else:
            status_code = 503
        
        return response, status_code
    
    def get_system_resources(self) -> Dict[str, Any]:
        """
        获取系统资源状态
        
        Returns:
            系统资源状态
        """
        check_result = self.health_checker.check_system_resources()
        
        response = {
            "component": "system_resources",
            "status": check_result["status"],
            "timestamp": check_result["timestamp"],
            "response_time_ms": check_result["response_time"],
            "message": check_result["message"]
        }
        
        # 添加资源详情
        if "cpu_percent" in check_result:
            response.update({
                "cpu_percent": check_result["cpu_percent"],
                "memory_percent": check_result["memory_percent"],
                "memory_used_gb": check_result["memory_used_gb"],
                "memory_total_gb": check_result["memory_total_gb"],
                "disk_percent": check_result["disk_percent"],
                "disk_used_gb": check_result["disk_used_gb"],
                "disk_total_gb": check_result["disk_total_gb"]
            })
        
        status_code = 200
        
        return response, status_code

# FastAPI实现
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    import uvicorn
    
    app = FastAPI(
        title="新闻推送系统健康检查API",
        description="提供系统健康状态检查的RESTful API",
        version="0.1.0"
    )
    
    health_api = HealthAPI()
    
    @app.get("/")
    async def root():
        """根端点，返回API信息"""
        return {
            "name": "新闻推送系统健康检查API",
            "version": "0.1.0",
            "endpoints": {
                "/health": "完整健康检查",
                "/health/database": "数据库健康检查",
                "/health/whatsapp": "WhatsApp健康检查",
                "/health/wechat": "微信健康检查",
                "/health/resources": "系统资源检查"
            }
        }
    
    @app.get("/health")
    async def health_check():
        """完整健康检查"""
        response, status_code = health_api.get_health_status()
        
        if status_code == 200:
            return JSONResponse(content=response, status_code=status_code)
        else:
            raise HTTPException(status_code=status_code, detail=response)
    
    @app.get("/health/database")
    async def database_health():
        """数据库健康检查"""
        response, status_code = health_api.get_database_health()
        
        if status_code == 200:
            return JSONResponse(content=response, status_code=status_code)
        else:
            raise HTTPException(status_code=status_code, detail=response)
    
    @app.get("/health/whatsapp")
    async def whatsapp_health():
        """WhatsApp健康检查"""
        response, status_code = health_api.get_whatsapp_health()
        
        if status_code == 200:
            return JSONResponse(content=response, status_code=status_code)
        else:
            raise HTTPException(status_code=status_code, detail=response)
    
    @app.get("/health/wechat")
    async def wechat_health():
        """微信健康检查"""
        response, status_code = health_api.get_wechat_health()
        
        if status_code == 200:
            return JSONResponse(content=response, status_code=status_code)
        else:
            raise HTTPException(status_code=status_code, detail=response)
    
    @app.get("/health/resources")
    async def system_resources():
        """系统资源检查"""
        response, status_code = health_api.get_system_resources()
        
        if status_code == 200:
            return JSONResponse(content=response, status_code=status_code)
        else:
            raise HTTPException(status_code=status_code, detail=response)
    
    def run_server(host: str = "0.0.0.0", port: int = 8000):
        """运行API服务器"""
        print(f"🚀 启动健康检查API服务器: http://{host}:{port}")
        print(f"📋 可用端点:")
        print(f"  GET /              - API信息")
        print(f"  GET /health        - 完整健康检查")
        print(f"  GET /health/database - 数据库健康")
        print(f"  GET /health/whatsapp - WhatsApp健康")
        print(f"  GET /health/wechat   - 微信健康")
        print(f"  GET /health/resources - 系统资源")
        print()
        
        uvicorn.run(app, host=host, port=port)
    
except ImportError:
    # FastAPI未安装时的简化版本
    print("⚠️  FastAPI未安装，使用简化版本")
    
    class SimpleHealthServer:
        """简化版健康检查服务器"""
        
        def __init__(self):
            self.health_api = HealthAPI()
        
        def handle_request(self, path: str) -> tuple:
            """处理HTTP请求"""
            if path == "/health":
                return self.health_api.get_health_status()
            elif path == "/health/database":
                return self.health_api.get_database_health()
            elif path == "/health/whatsapp":
                return self.health_api.get_whatsapp_health()
            elif path == "/health/wechat":
                return self.health_api.get_wechat_health()
            elif path == "/health/resources":
                return self.health_api.get_system_resources()
            elif path == "/":
                return {
                    "name": "新闻推送系统健康检查API",
                    "version": "0.1.0",
                    "message": "FastAPI未安装，使用简化版本"
                }, 200
            else:
                return {"error": "Endpoint not found"}, 404
        
        def run_simple_server(self, port: int = 8000):
            """运行简化服务器"""
            import http.server
            import json
            
            class HealthHandler(http.server.BaseHTTPRequestHandler):
                def do_GET(self):
                    response, status_code = self.server.health_server.handle_request(self.path)
                    
                    self.send_response(status_code)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            
            server = http.server.HTTPServer(('0.0.0.0', port), HealthHandler)
            server.health_server = self
            
            print(f"🚀 启动简化健康检查服务器: http://0.0.0.0:{port}")
            print(f"📋 可用端点: /health, /health/database, /health/whatsapp, /health/wechat, /health/resources")
            print()
            
            server.serve_forever()

# 测试函数
def test_health_api():
    """测试健康检查API"""
    print("🔧 测试健康检查API")
    print("=" * 60)
    
    api = HealthAPI()
    
    print("1. 测试完整健康检查...")
    response, status_code = api.get_health_status()
    print(f"   状态码: {status_code}")
    print(f"   健康度: {response['health_percentage']}%")
    print(f"   检查数量: {response['summary']['total_checks']}")
    
    print("\n2. 测试数据库健康检查...")
    response, status_code = api.get_database_health()
    print(f"   状态码: {status_code}")
    print(f"   状态: {response['status']}")
    print(f"   消息: {response['message']}")
    
    print("\n3. 测试WhatsApp健康检查...")
    response, status_code = api.get_whatsapp_health()
    print(f"   状态码: {status_code}")
    print(f"   状态: {response['status']}")
    print(f"   消息: {response['message']}")
    
    print("\n4. 测试系统资源检查...")
    response, status_code = api.get_system_resources()
    print(f"   状态码: {status_code}")
    print(f"   状态: {response['status']}")
    print(f"   消息: {response['message']}")
    
    print("\n✅ 健康检查API测试完成")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_health_api()
    elif len(sys.argv) > 1 and sys.argv[1] == "server":
        try:
            run_server()
        except NameError:
            server = SimpleHealthServer()
            server.run_simple_server()
    else:
        print("用法:")
        print("  python health_api.py test     - 测试API")
        print("  python health_api.py server   - 启动服务器")
        print()
        test_health_api()
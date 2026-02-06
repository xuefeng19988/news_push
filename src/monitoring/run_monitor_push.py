#!/usr/bin/env python3
"""
运行监控推送 - 定时任务入口
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def main():
    """主函数"""
    print(f"🚀 运行监控推送 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        from src.monitoring.monitor_push_service import MonitorPushService
        
        # 创建服务实例
        service = MonitorPushService()
        
        # 执行检查并推送（根据规则决定是否推送）
        result = service.check_and_push(force_push=False)
        
        # 输出结果
        print(f"📊 检查结果:")
        print(f"  整体状态: {result.get('overall_status', 'unknown')}")
        print(f"  检查耗时: {result.get('check_time', 0):.2f}秒")
        print(f"  是否推送: {result.get('pushed', False)}")
        
        if result.get('pushed'):
            print(f"  ✅ 推送成功: {result.get('push_type')}")
        else:
            print(f"  ⚠️  未推送: {result.get('message', '')}")
        
        if result.get('error'):
            print(f"  ❌ 错误: {result['error']}")
        
        # 根据结果返回退出码
        if result.get('error'):
            return 1
        elif result.get('overall_status') == 'unhealthy':
            return 2
        elif result.get('overall_status') == 'warning':
            return 3
        else:
            return 0
            
    except Exception as e:
        print(f"❌ 监控推送执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 4

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
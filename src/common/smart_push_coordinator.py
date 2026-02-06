#!/usr/bin/env python3
"""
智能推送协调器
主系统失败时自动切换到备份系统
避免每小时收到两条消息
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
import traceback

# 修复导入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入工具模块
from utils.logger import Logger, log_to_file
from utils.config import ConfigManager

class SmartPushCoordinator:
    """智能推送协调器"""
    
    def __init__(self):
        """初始化协调器"""
        self.name = "SmartPushCoordinator"
        self.logger = Logger(self.name).get_logger()
        self.config_mgr = ConfigManager()
        self.env_config = self.config_mgr.get_env_config()
        
        # 状态文件
        self.state_dir = Path("logs/coordinator")
        self.state_dir.mkdir(exist_ok=True)
        self.state_file = self.state_dir / "push_state.json"
        
        self.logger.info("智能推送协调器初始化完成")
    
    def run_main_system(self) -> tuple[bool, str, float]:
        """
        运行主推送系统
        
        Returns:
            Tuple[是否成功, 结果消息, 执行时间]
        """
        start_time = time.time()
        
        try:
            self.logger.info("开始运行主推送系统...")
            
            # 导入主系统
            from .auto_push_system_optimized_final import AutoPushSystemOptimized
            
            system = AutoPushSystemOptimized()
            success, result_msg = system.run_push()
            
            execution_time = time.time() - start_time
            
            if success:
                self.logger.info(f"主系统运行成功: {result_msg}")
                return True, result_msg, execution_time
            else:
                self.logger.warning(f"主系统运行失败: {result_msg}")
                return False, result_msg, execution_time
                
        except ImportError as e:
            self.logger.error(f"无法导入主系统: {e}")
            return False, f"无法导入主系统: {str(e)}", time.time() - start_time
        except Exception as e:
            self.logger.error(f"运行主系统时异常: {e}")
            return False, f"运行主系统时异常: {str(e)}", time.time() - start_time
    
    def run_backup_system(self) -> tuple[bool, str, float]:
        """
        运行备份推送系统
        
        Returns:
            Tuple[是否成功, 结果消息, 执行时间]
        """
        start_time = time.time()
        
        try:
            self.logger.info("开始运行备份推送系统...")
            
            # 导入备份系统
            from .simple_push_system import SimplePushSystem
            
            system = SimplePushSystem()
            success = system.run()
            
            execution_time = time.time() - start_time
            
            if success:
                self.logger.info("备份系统运行成功")
                return True, "备份系统运行成功", execution_time
            else:
                self.logger.warning("备份系统运行失败")
                return False, "备份系统运行失败", execution_time
                
        except ImportError as e:
            self.logger.error(f"无法导入备份系统: {e}")
            return False, f"无法导入备份系统: {str(e)}", time.time() - start_time
        except Exception as e:
            self.logger.error(f"运行备份系统时异常: {e}")
            return False, f"运行备份系统时异常: {str(e)}", time.time() - start_time
    
    def run_smart_switch(self) -> tuple[bool, str, str]:
        """
        执行智能切换逻辑
        
        Returns:
            Tuple[总体是否成功, 最终结果消息, 使用的系统]
        """
        start_time = time.time()
        
        self.logger.info("🚀 开始智能推送协调")
        print("=" * 60)
        print("🤖 智能推送协调器")
        print("=" * 60)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 步骤1: 尝试运行主系统
        print("\n🔄 步骤1: 运行主推送系统...")
        main_success, main_msg, main_time = self.run_main_system()
        
        if main_success:
            # 主系统成功，直接返回
            total_time = time.time() - start_time
            result_msg = f"主系统成功: {main_msg} (主系统耗时: {main_time:.1f}s, 总耗时: {total_time:.1f}s)"
            
            print(f"✅ 主系统运行成功!")
            print(f"   结果: {main_msg}")
            print(f"   耗时: {main_time:.1f}秒")
            
            self._log_coordinator_decision("main", True, result_msg)
            return True, result_msg, "main"
        
        # 主系统失败，记录日志
        print(f"⚠️ 主系统运行失败: {main_msg}")
        print(f"   耗时: {main_time:.1f}秒")
        print(f"   失败原因: {main_msg}")
        
        # 步骤2: 运行备份系统
        print("\n🔄 步骤2: 运行备份系统...")
        backup_success, backup_msg, backup_time = self.run_backup_system()
        
        total_time = time.time() - start_time
        
        if backup_success:
            # 备份系统成功
            result_msg = f"主系统失败，备份系统成功: 主系统失败原因: {main_msg} | 备份系统结果: {backup_msg} (主系统: {main_time:.1f}s, 备份: {backup_time:.1f}s, 总: {total_time:.1f}s)"
            
            print(f"✅ 备份系统运行成功!")
            print(f"   结果: {backup_msg}")
            print(f"   耗时: {backup_time:.1f}秒")
            print(f"   总耗时: {total_time:.1f}秒")
            
            self._log_coordinator_decision("backup", True, result_msg)
            return True, result_msg, "backup"
        else:
            # 两个系统都失败
            result_msg = f"主系统和备份系统都失败: 主系统: {main_msg} | 备份系统: {backup_msg} (主系统: {main_time:.1f}s, 备份: {backup_time:.1f}s, 总: {total_time:.1f}s)"
            
            print(f"❌ 两个系统都失败!")
            print(f"   主系统失败: {main_msg}")
            print(f"   备份系统失败: {backup_msg}")
            print(f"   总耗时: {total_time:.1f}秒")
            
            self._log_coordinator_decision("failed", False, result_msg)
            return False, result_msg, "failed"
    
    def _log_coordinator_decision(self, system_used: str, success: bool, message: str):
        """记录协调器决策"""
        try:
            import json
            
            decision = {
                "timestamp": datetime.now().isoformat(),
                "system_used": system_used,
                "success": success,
                "message": message,
                "coordinator": self.name
            }
            
            # 写入状态文件
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(decision, f, indent=2, ensure_ascii=False)
            
            # 追加到日志文件
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 决策: {system_used}, 成功: {success}, 消息: {message[:100]}\n"
            log_to_file(log_entry, "coordinator.log")
            
            self.logger.info(f"决策记录完成: 使用系统={system_used}, 成功={success}")
            
        except Exception as e:
            self.logger.error(f"记录决策时出错: {e}")
    
    def get_coordinator_status(self) -> dict:
        """获取协调器状态"""
        try:
            import json
            
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "system_used": "unknown",
                    "success": False,
                    "message": "无历史记录",
                    "coordinator": self.name
                }
                
        except Exception as e:
            self.logger.error(f"读取状态文件失败: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "system_used": "error",
                "success": False,
                "message": f"读取状态失败: {str(e)}",
                "coordinator": self.name
            }

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="智能推送协调器")
    parser.add_argument("--run", action="store_true", help="运行智能推送")
    parser.add_argument("--status", action="store_true", help="显示协调器状态")
    parser.add_argument("--test", action="store_true", help="测试模式，不实际发送")
    
    args = parser.parse_args()
    
    print("🤖 智能推送协调器")
    print("=" * 60)
    
    coordinator = SmartPushCoordinator()
    
    if args.status:
        # 显示状态
        status = coordinator.get_coordinator_status()
        print(f"最后运行时间: {status.get('timestamp', '未知')}")
        print(f"使用的系统: {status.get('system_used', '未知')}")
        print(f"是否成功: {'✅' if status.get('success') else '❌'}")
        print(f"消息: {status.get('message', '无消息')}")
        
        # 显示最近的日志
        log_file = Path("logs/coordinator.log")
        if log_file.exists():
            print(f"\n📄 最近决策日志:")
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-5:]  # 最后5行
                for line in lines:
                    print(f"  {line.strip()}")
    
    elif args.test:
        # 测试模式
        print("🧪 测试模式 - 不实际发送消息")
        print("=" * 60)
        
        # 测试主系统导入
        try:
            from .auto_push_system_optimized_final import AutoPushSystemOptimized
            print("✅ 主系统导入成功")
        except Exception as e:
            print(f"❌ 主系统导入失败: {e}")
        
        # 测试备份系统导入
        try:
            from .simple_push_system import SimplePushSystem
            print("✅ 备份系统导入成功")
        except Exception as e:
            print(f"❌ 备份系统导入失败: {e}")
        
        print("\n📊 协调器状态测试完成")
        
    elif args.run:
        # 运行智能推送
        success, message, system_used = coordinator.run_smart_switch()
        
        print("\n" + "=" * 60)
        if success:
            print(f"✅ 智能推送完成! (使用系统: {system_used})")
        else:
            print(f"❌ 智能推送失败! (使用系统: {system_used})")
        print(f"📝 结果: {message}")
        
        return 0 if success else 1
        
    else:
        parser.print_help()
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

import os
import time
from pathlib import Path

class PushCoordinator:
    """推送协调器：确保主系统优先，备份系统作为保障"""
    
    def __init__(self):
        self.lock_file = Path("logs/push_lock.txt")
        self.lock_timeout = 300  # 5分钟超时
    
    def acquire_lock(self) -> bool:
        """获取推送锁"""
        try:
            if self.lock_file.exists():
                # 检查锁是否过期
                lock_time = self.lock_file.stat().st_mtime
                if time.time() - lock_time < self.lock_timeout:
                    print("🔒 推送锁已被占用")
                    return False
            
            # 创建锁文件
            with open(self.lock_file, 'w') as f:
                f.write(str(time.time()))
            return True
        except Exception as e:
            print(f"❌ 获取推送锁失败: {e}")
            return False
    
    def release_lock(self):
        """释放推送锁"""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
        except Exception as e:
            print(f"❌ 释放推送锁失败: {e}")
    
    def should_run_backup(self) -> bool:
        """检查是否应该运行备份系统"""
        # 检查主系统是否在最近5分钟内运行过
        push_log = Path("logs/auto_push.log")
        if not push_log.exists():
            return True
        
        try:
            # 读取最后几行日志
            with open(push_log, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-20:] if len(lines) > 20 else lines
            
            # 检查是否有最近的成功推送
            for line in reversed(recent_lines):
                if '推送成功' in line and '耗时:' in line:
                    # 提取时间戳
                    import re
                    time_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
                    if time_match:
                        from datetime import datetime
                        push_time = datetime.strptime(time_match.group(), '%Y-%m-%d %H:%M:%S')
                        current_time = datetime.now()
                        
                        # 如果5分钟内有成功推送，不需要运行备份
                        time_diff = (current_time - push_time).total_seconds()
                        if time_diff < 300:
                            return False
            
            return True
        except Exception as e:
            print(f"❌ 检查备份运行条件失败: {e}")
            return True

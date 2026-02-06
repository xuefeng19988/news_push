#!/bin/bash
# 新版智能推送shell脚本协调器
# 使用situation-monitor架构作为主系统
# 主系统失败时自动切换到备份系统

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
START_TIME=$(date +%s)

echo "============================================================"
echo "🤖 新版智能推送协调器 (situation-monitor架构)"
echo "开始时间: $TIMESTAMP"
echo "============================================================"

# 日志函数
log() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_DIR/smart_coordinator.log"
}

log "INFO" "开始智能推送协调"

# 步骤1: 尝试运行新版主系统 (基于situation-monitor架构)
log "INFO" "步骤1: 运行新版主推送系统 (situation-monitor)..."
MAIN_START=$(date +%s)

if python3 src/situation_monitor/new_push_system.py >> "$LOG_DIR/new_push_system.log" 2>&1; then
    MAIN_END=$(date +%s)
    MAIN_DURATION=$((MAIN_END - MAIN_START))
    
    log "SUCCESS" "新版主系统运行成功 (耗时: ${MAIN_DURATION}秒)"
    
    # 记录决策
    END_TIME=$(date +%s)
    TOTAL_DURATION=$((END_TIME - START_TIME))
    
    log "INFO" "智能推送完成: 使用新版主系统(situation-monitor)，总耗时: ${TOTAL_DURATION}秒"
    echo "✅ 智能推送完成: 使用新版主系统(situation-monitor)"
    
    # 保存状态
    echo "{
        \"timestamp\": \"$(date -Iseconds)\",
        \"system_used\": \"new_situation_monitor\",
        \"success\": true,
        \"message\": \"主系统运行成功，耗时: ${MAIN_DURATION}秒\",
        \"total_duration\": ${TOTAL_DURATION},
        \"coordinator\": \"shell_smart_push\"
    }" > "$LOG_DIR/coordinator_state.json"
    
    exit 0
else
    MAIN_END=$(date +%s)
    MAIN_DURATION=$((MAIN_END - MAIN_START))
    
    log "WARNING" "新版主系统运行失败 (耗时: ${MAIN_DURATION}秒)"
    log "INFO" "新版主系统失败原因: 详见 $LOG_DIR/new_push_system.log"
fi

# 步骤2: 运行备份系统
log "INFO" "步骤2: 运行备份系统..."
BACKUP_START=$(date +%s)

if python3 src/common/simple_push_system.py --run >> "$LOG_DIR/simple_push.log" 2>&1; then
    BACKUP_END=$(date +%s)
    BACKUP_DURATION=$((BACKUP_END - BACKUP_START))
    
    log "SUCCESS" "备份系统运行成功 (耗时: ${BACKUP_DURATION}秒)"
    
    # 记录决策
    END_TIME=$(date +%s)
    TOTAL_DURATION=$((END_TIME - START_TIME))
    
    log "INFO" "智能推送完成: 使用备份系统，总耗时: ${TOTAL_DURATION}秒"
    echo "✅ 智能推送完成: 使用备份系统"
    
    # 保存状态
    echo "{
        \"timestamp\": \"$(date -Iseconds)\",
        \"system_used\": \"backup\",
        \"success\": true,
        \"message\": \"主系统失败，备份系统成功。主系统耗时: ${MAIN_DURATION}秒，备份系统耗时: ${BACKUP_DURATION}秒\",
        \"total_duration\": ${TOTAL_DURATION},
        \"coordinator\": \"shell_smart_push\"
    }" > "$LOG_DIR/coordinator_state.json"
    
    exit 0
else
    BACKUP_END=$(date +%s)
    BACKUP_DURATION=$((BACKUP_END - BACKUP_START))
    
    log "ERROR" "备份系统也运行失败 (耗时: ${BACKUP_DURATION}秒)"
    
    # 两个系统都失败
    END_TIME=$(date +%s)
    TOTAL_DURATION=$((END_TIME - START_TIME))
    
    log "ERROR" "两个系统都失败! 总耗时: ${TOTAL_DURATION}秒"
    echo "❌ 两个系统都失败!"
    
    # 保存状态
    echo "{
        \"timestamp\": \"$(date -Iseconds)\",
        \"system_used\": \"failed\",
        \"success\": false,
        \"message\": \"主系统和备份系统都失败。主系统耗时: ${MAIN_DURATION}秒，备份系统耗时: ${BACKUP_DURATION}秒\",
        \"total_duration\": ${TOTAL_DURATION},
        \"coordinator\": \"shell_smart_push\"
    }" > "$LOG_DIR/coordinator_state.json"
    
    exit 1
fi
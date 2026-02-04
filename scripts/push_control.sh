#!/bin/bash
# 推送系统控制脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 函数定义
print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                   推送系统控制中心                       ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}➤ $1${NC}"
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

# 检查系统状态
check_status() {
    print_header
    print_step "检查系统状态..."
    echo ""
    
    # 检查定时任务
    echo "📅 定时任务状态:"
    if crontab -l | grep -q "ultimate_push_system.py"; then
        print_success "已设置"
        CRON_JOB=$(crontab -l | grep "ultimate_push_system.py")
        echo "   任务: $CRON_JOB"
    else
        print_error "未设置"
    fi
    echo ""
    
    # 检查日志文件
    echo "📝 系统日志:"
    LOG_FILES=("ultimate_push.log" "auto_push.log" "enhanced_pusher.log")
    for log_file in "${LOG_FILES[@]}"; do
        if [ -f "$log_file" ]; then
            SIZE=$(stat -c%s "$log_file")
            MTIME=$(stat -c%y "$log_file" | cut -d' ' -f1,2)
            print_success "$log_file"
            echo "   大小: ${SIZE}字节, 最后修改: $MTIME"
            
            # 显示最后错误（如果有）
            if tail -5 "$log_file" | grep -q "❌"; then
                echo "   最近错误:"
                tail -5 "$log_file" | grep "❌" | sed 's/^/     /'
            fi
        else
            print_info "$log_file - 文件不存在"
        fi
        echo ""
    done
    
    # 检查Python脚本
    echo "🐍 Python脚本:"
    SCRIPTS=("ultimate_push_system.py" "news_stock_pusher.py" "social_media_monitor_enhanced.py")
    for script in "${SCRIPTS[@]}"; do
        if [ -f "$script" ]; then
            SIZE=$(stat -c%s "$script")
            print_success "$script"
            echo "   大小: ${SIZE}字节"
        else
            print_error "$script - 文件不存在"
        fi
    done
    echo ""
    
    # 检查数据文件
    echo "💾 数据文件:"
    DATA_FILES=("news_cache.db" "social_media_history.json" "alert_config.json")
    for data_file in "${DATA_FILES[@]}"; do
        if [ -f "$data_file" ]; then
            SIZE=$(stat -c%s "$data_file")
            print_success "$data_file"
            echo "   大小: ${SIZE}字节"
        else
            print_info "$data_file - 文件不存在（将自动创建）"
        fi
    done
    echo ""
    
    # 当前时间分析
    CURRENT_HOUR=$(date +%H)
    CURRENT_MINUTE=$(date +%M)
    
    echo "⏰ 当前时间: $(date '+%H:%M')"
    echo "   股票推送: $([ $CURRENT_HOUR -ge 8 ] && [ $CURRENT_HOUR -le 18 ] && echo "✅ 启用" || echo "⏭️ 暂停") (08:00-18:00)"
    echo "   新闻推送: $([ $CURRENT_HOUR -ge 8 ] && [ $CURRENT_HOUR -le 22 ] && echo "✅ 启用" || echo "⏭️ 暂停") (08:00-22:00)"
    echo "   社交媒体: $([ $CURRENT_HOUR -ge 8 ] && [ $CURRENT_HOUR -le 22 ] && echo "✅ 启用" || echo "⏭️ 暂停") (08:00-22:00)"
    echo ""
    
    # 距离下次推送
    MINUTES_TO_NEXT_HOUR=$((60 - CURRENT_MINUTE))
    echo "🔄 距离下次自动推送: ${MINUTES_TO_NEXT_HOUR}分钟"
    
    # 最近推送记录
    echo ""
    echo "📊 最近推送记录:"
    PUSH_FILES=$(ls -1t push_summary_*.txt 2>/dev/null | head -3)
    if [ -n "$PUSH_FILES" ]; then
        for file in $PUSH_FILES; do
            DATE=${file:12:12}
            SIZE=$(stat -c%s "$file")
            echo "   📄 $DATE - ${SIZE}字节"
        done
    else
        print_info "无推送记录"
    fi
}

# 立即运行推送
run_now() {
    print_header
    print_step "立即运行推送..."
    echo ""
    
    python3 ultimate_push_system.py --run
    
    if [ $? -eq 0 ]; then
        print_success "推送运行完成"
    else
        print_error "推送运行失败"
    fi
}

# 设置定时任务
setup_cron() {
    print_header
    print_step "设置定时任务..."
    echo ""
    
    python3 ultimate_push_system.py --setup
    
    if [ $? -eq 0 ]; then
        print_success "定时任务设置完成"
        echo ""
        echo "📅 推送安排:"
        echo "   每小时整点运行"
        echo "   股票: 08:00-18:00"
        echo "   新闻: 08:00-22:00"
        echo "   社交媒体: 08:00-22:00"
    else
        print_error "定时任务设置失败"
    fi
}

# 测试消息发送
test_send() {
    print_header
    print_step "测试消息发送..."
    echo ""
    
    python3 ultimate_push_system.py --test
    
    if [ $? -eq 0 ]; then
        print_success "测试消息发送成功"
    else
        print_error "测试消息发送失败"
    fi
}

# 查看日志
view_log() {
    print_header
    print_step "查看系统日志..."
    echo ""
    
    LOG_FILE="ultimate_push.log"
    
    if [ -f "$LOG_FILE" ]; then
        echo "最后20行日志:"
        echo "────────────────────────────────────────────"
        tail -20 "$LOG_FILE"
        echo "────────────────────────────────────────────"
        echo ""
        print_info "实时查看: tail -f $LOG_FILE"
        print_info "完整日志: less $LOG_FILE"
    else
        print_error "日志文件不存在"
    fi
}

# 清理旧文件
cleanup() {
    print_header
    print_step "清理旧文件..."
    echo ""
    
    # 保留最近7天的文件
    DAYS=7
    
    echo "清理推送报告 (保留最近${DAYS}天):"
    find . -name "push_*_*.txt" -mtime +$DAYS -type f -delete -print | sed 's/^/   删除: /'
    find . -name "push_*_*.json" -mtime +$DAYS -type f -delete -print | sed 's/^/   删除: /'
    echo ""
    
    echo "清理发送记录 (保留最近${DAYS}天):"
    find . -name "sent_*.txt" -mtime +$DAYS -type f -delete -print | sed 's/^/   删除: /'
    echo ""
    
    echo "清理备份消息 (保留最近${DAYS}天):"
    find . -name "*_msg_*.txt" -mtime +$DAYS -type f -delete -print | sed 's/^/   删除: /'
    echo ""
    
    echo "清理旧日志 (保留最近${DAYS}天):"
    find . -name "*.log" -mtime +$DAYS -type f -delete -print | sed 's/^/   删除: /'
    echo ""
    
    print_success "清理完成"
}

# 系统信息
system_info() {
    print_header
    print_step "系统信息..."
    echo ""
    
    echo "📱 推送系统信息"
    echo "────────────────────────────────────────────"
    echo "系统名称: 终极推送系统"
    echo "版本: v1.0"
    echo "开发时间: 2026-02-04"
    echo "接收号码: +8618966719971"
    echo ""
    
    echo "📰 新闻源配置:"
    echo "  国内媒体: 新浪、网易、凤凰、澎湃、今日头条"
    echo "  国际媒体: BBC、CNN、金融时报、日经亚洲、南华早报"
    echo "  社交媒体: 微博、Reddit、Twitter"
    echo ""
    
    echo "📈 股票监控:"
    echo "  阿里巴巴-W (09988.HK)"
    echo "  小米集团-W (01810.HK)"
    echo "  比亚迪 (002594.SZ)"
    echo ""
    
    echo "⚙️ 系统特性:"
    echo "  • 智能时间调度"
    echo "  • 分类内容显示"
    echo "  • 自动去重过滤"
    echo "  • 错误恢复机制"
    echo "  • 定时自动推送"
    echo ""
    
    echo "🔄 工作流程:"
    echo "  1. 每小时整点自动运行"
    echo "  2. 获取新闻、股票、社交媒体数据"
    echo "  3. 分析过滤重要内容"
    echo "  4. 格式化生成报告"
    echo "  5. 自动发送到WhatsApp"
    echo ""
    
    print_info "使用 './push_control.sh help' 查看所有命令"
}

# 显示帮助
show_help() {
    print_header
    echo "📋 使用方法: ./push_control.sh [命令]"
    echo ""
    echo "可用命令:"
    echo "  status     检查系统状态"
    echo "  run        立即运行推送"
    echo "  setup      设置定时任务"
    echo "  test       测试消息发送"
    echo "  log        查看系统日志"
    echo "  cleanup    清理旧文件"
    echo "  info       显示系统信息"
    echo "  help       显示帮助信息"
    echo ""
    echo "示例:"
    echo "  ./push_control.sh status    # 检查系统状态"
    echo "  ./push_control.sh run       # 立即运行推送"
    echo "  ./push_control.sh setup     # 设置定时任务"
    echo ""
    echo "💡 提示:"
    echo "  • 系统每小时整点自动运行"
    echo "  • 所有日志保存在当前目录"
    echo "  • 错误消息会自动记录和恢复"
    echo ""
}

# 主逻辑
case "${1:-help}" in
    status)
        check_status
        ;;
    run)
        run_now
        ;;
    setup)
        setup_cron
        ;;
    test)
        test_send
        ;;
    log)
        view_log
        ;;
    cleanup)
        cleanup
        ;;
    info)
        system_info
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "未知命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
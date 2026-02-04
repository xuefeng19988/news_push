#!/bin/bash
# 推送系统管理脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数定义
print_header() {
    echo -e "${BLUE}"
    echo "============================================================"
    echo "📱 新闻+股票推送系统管理"
    echo "============================================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}💡 $1${NC}"
}

# 检查系统状态
check_status() {
    print_header
    echo "🔍 检查系统状态..."
    echo ""
    
    # 检查定时任务
    echo "📅 定时任务:"
    if crontab -l | grep -q "optimized_push_system.py"; then
        print_success "定时任务已设置"
        crontab -l | grep "optimized_push_system.py"
    else
        print_error "定时任务未设置"
    fi
    echo ""
    
    # 检查日志文件
    echo "📝 日志文件:"
    LOG_FILE="logs/logs/auto_push.log"
    if [ -f "$LOG_FILE" ]; then
        SIZE=$(stat -c%s "$LOG_FILE")
        MTIME=$(stat -c%y "$LOG_FILE" | cut -d' ' -f1,2)
        print_success "$LOG_FILE - ${SIZE}字节, 最后修改: $MTIME"
        
        # 显示最后3行
        echo "   最后记录:"
        tail -3 "$LOG_FILE" | sed 's/^/      /'
    else
        print_error "$LOG_FILE - 文件不存在"
    fi
    echo ""
    
    # 检查Python脚本
    echo "🐍 Python脚本:"
    for script in "src/common/news_stock_pusher.py" "src/common/optimized_push_system.py" "src/common/simple_push_system.py"; do
        if [ -f "$script" ]; then
            SIZE=$(stat -c%s "$script")
            print_success "$(basename $script) - ${SIZE}字节"
        else
            print_error "$(basename $script) - 文件不存在"
        fi
    done
    echo ""
    
    # 检查数据库
    echo "💾 数据库文件:"
    DB_FILE="news_cache.db"
    if [ -f "$DB_FILE" ]; then
        SIZE=$(stat -c%s "$DB_FILE")
        print_success "$DB_FILE - ${SIZE}字节"
    else
        print_error "$DB_FILE - 文件不存在"
    fi
    echo ""
    
    # 检查最近推送
    echo "📊 最近推送记录:"
    PUSH_FILES=$(ls -1t push_report_*.txt 2>/dev/null | head -3)
    if [ -n "$PUSH_FILES" ]; then
        for file in $PUSH_FILES; do
            DATE=${file:11:12}
            SIZE=$(stat -c%s "$file")
            echo "   📄 $DATE - ${SIZE}字节"
        done
    else
        print_error "无推送记录"
    fi
    echo ""
    
    # 当前时间分析
    CURRENT_HOUR=$(date +%H)
    echo "⏰ 当前时间: $(date '+%H:%M')"
    echo "   股票推送: $([ $CURRENT_HOUR -ge 8 ] && [ $CURRENT_HOUR -le 18 ] && echo "✅ 启用" || echo "⏭️ 暂停") (08:00-18:00)"
    echo "   新闻推送: $([ $CURRENT_HOUR -ge 8 ] && [ $CURRENT_HOUR -le 22 ] && echo "✅ 启用" || echo "⏭️ 暂停") (08:00-22:00)"
    echo ""
    
    # 距离下次推送
    CURRENT_MINUTE=$(date +%M)
    MINUTES_TO_NEXT_HOUR=$((60 - CURRENT_MINUTE))
    echo "🔄 距离下次自动推送: ${MINUTES_TO_NEXT_HOUR}分钟"
}

# 立即运行推送
run_now() {
    print_header
    echo "🚀 立即运行推送..."
    echo ""
    
    python3 auto_push_system.py --run
    
    if [ $? -eq 0 ]; then
        print_success "推送运行完成"
    else
        print_error "推送运行失败"
    fi
}

# 设置定时任务
setup_cron() {
    print_header
    echo "⏰ 设置定时任务..."
    echo ""
    
    python3 auto_push_system.py --setup
    
    if [ $? -eq 0 ]; then
        print_success "定时任务设置完成"
        echo ""
        echo "📅 推送安排:"
        echo "  每小时整点运行"
        echo "  股票推送: 08:00-18:00"
        echo "  新闻推送: 08:00-22:00"
        echo "  自动发送到WhatsApp"
    else
        print_error "定时任务设置失败"
    fi
}

# 查看日志
view_log() {
    print_header
    echo "📝 查看日志..."
    echo ""
    
    LOG_FILE="logs/logs/auto_push.log"
    
    if [ -f "$LOG_FILE" ]; then
        echo "最后20行日志:"
        echo "----------------------------------------"
        tail -20 "$LOG_FILE"
        echo "----------------------------------------"
        echo ""
        print_info "完整日志: tail -f $LOG_FILE"
    else
        print_error "日志文件不存在"
    fi
}

# 测试消息发送
test_send() {
    print_header
    echo "🧪 测试消息发送..."
    echo ""
    
    python3 auto_push_system.py --test
    
    if [ $? -eq 0 ]; then
        print_success "测试消息发送成功"
    else
        print_error "测试消息发送失败"
    fi
}

# 测试新闻链接功能
test_news_links() {
    print_header
    echo "🔗 测试新闻链接功能..."
    echo ""
    
    python3 test_news_links.py
    
    if [ $? -eq 0 ]; then
        print_success "新闻链接测试完成"
        echo ""
        echo "📋 测试报告已生成，可以发送测试消息验证链接功能"
    else
        print_error "新闻链接测试失败"
    fi
}

# 测试详细摘要功能
test_detailed_summary() {
    print_header
    echo "📝 测试详细摘要功能..."
    echo ""
    
    python3 test_detailed_summary.py
    
    if [ $? -eq 0 ]; then
        print_success "详细摘要测试完成"
        echo ""
        echo "📋 测试报告已生成，展示了增强的摘要功能"
    else
        print_error "详细摘要测试失败"
    fi
}

# 测试更新时间和重要性功能
test_time_importance() {
    print_header
    echo "⏰ 测试更新时间和重要性功能..."
    echo ""
    
    python3 test_time_importance.py
    
    if [ $? -eq 0 ]; then
        print_success "更新时间和重要性测试完成"
        echo ""
        echo "📋 测试报告已生成，展示了时间解析和重要性评级功能"
    else
        print_error "更新时间和重要性测试失败"
    fi
}

# 清理旧文件
cleanup() {
    print_header
    echo "🧹 清理旧文件..."
    echo ""
    
    # 保留最近7天的文件
    DAYS=7
    
    echo "清理推送报告 (保留最近${DAYS}天):"
    find . -name "push_report_*.txt" -mtime +$DAYS -type f -delete -print | sed 's/^/  删除: /'
    echo ""
    
    echo "清理发送记录 (保留最近${DAYS}天):"
    find . -name "sent_*.txt" -mtime +$DAYS -type f -delete -print | sed 's/^/  删除: /'
    echo ""
    
    echo "清理备份消息 (保留最近${DAYS}天):"
    find . -name "backup_msg_*.txt" -mtime +$DAYS -type f -delete -print | sed 's/^/  删除: /'
    find . -name "failed_msg_*.txt" -mtime +$DAYS -type f -delete -print | sed 's/^/  删除: /'
    echo ""
    
    print_success "清理完成"
}

# 显示帮助
show_help() {
    print_header
    echo "📋 使用方法: ./push_manager.sh [命令]"
    echo ""
    echo "可用命令:"
    echo "  status      检查系统状态"
    echo "  run         立即运行推送"
    echo "  setup       设置定时任务"
    echo "  log         查看日志"
    echo "  test        测试消息发送"
    echo "  testlinks   测试新闻链接功能"
    echo "  testsummary 测试详细摘要功能"
    echo "  testtime    测试更新时间和重要性"
    echo "  cleanup     清理旧文件"
    echo "  help        显示帮助"
    echo ""
    echo "示例:"
    echo "  ./push_manager.sh status      # 检查系统状态"
    echo "  ./push_manager.sh run         # 立即推送"
    echo "  ./push_manager.sh testlinks   # 测试新闻链接"
    echo "  ./push_manager.sh testsummary # 测试详细摘要"
    echo "  ./push_manager.sh testtime    # 测试更新时间和重要性"
    echo "  ./push_manager.sh setup       # 设置定时任务"
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
    log)
        view_log
        ;;
    test)
        test_send
        ;;
    testlinks)
        test_news_links
        ;;
    testsummary)
        test_detailed_summary
        ;;
    testtime)
        test_time_importance
        ;;
    cleanup)
        cleanup
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
echo -e "${BLUE}============================================================${NC}"
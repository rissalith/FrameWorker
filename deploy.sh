#!/bin/bash

###############################################################################
# MaxGamer 自动化部署脚本
# 实现前后端、数据库、平台和游戏的完全隔离
###############################################################################

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印横幅
print_banner() {
    echo -e "${BLUE}"
    echo "========================================"
    echo "  MaxGamer 自动化部署脚本"
    echo "  版本: 2.0.0"
    echo "========================================"
    echo -e "${NC}"
}

# 检查必要的工具
check_requirements() {
    print_info "检查必要工具..."

    local missing_tools=()

    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi

    if ! command -v docker-compose &> /dev/null; then
        missing_tools+=("docker-compose")
    fi

    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    fi

    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "缺少必要工具: ${missing_tools[*]}"
        print_info "请先安装: sudo apt-get install docker.io docker-compose git"
        exit 1
    fi

    print_success "所有必要工具已安装"
}

# 拉取最新代码
pull_latest_code() {
    print_info "拉取最新代码..."

    if [ -d ".git" ]; then
        git fetch origin
        git pull origin main
        print_success "代码已更新到最新版本"
    else
        print_warning "当前目录不是 Git 仓库，跳过代码拉取"
    fi
}

# 备份数据库
backup_database() {
    print_info "备份数据库..."

    local backup_dir="./backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)

    mkdir -p "$backup_dir"

    if [ -f "./data/frameworker.db" ]; then
        cp "./data/frameworker.db" "$backup_dir/frameworker_$timestamp.db"
        print_success "数据库已备份到: $backup_dir/frameworker_$timestamp.db"

        # 只保留最近 7 天的备份
        find "$backup_dir" -name "frameworker_*.db" -mtime +7 -delete
        print_info "已清理 7 天前的旧备份"
    else
        print_warning "数据库文件不存在，跳过备份"
    fi
}

# 检查环境变量
check_environment() {
    print_info "检查环境变量配置..."

    if [ ! -f ".env" ]; then
        print_warning ".env 文件不存在，从模板创建..."

        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "请编辑 .env 文件并配置必要的环境变量！"
            print_info "必须配置的变量："
            echo "  - SECRET_KEY"
            echo "  - JWT_SECRET"
            echo "  - TWITCH_CLIENT_SECRET"
            echo "  - TWITCH_REDIRECT_URI"

            read -p "配置完成后按回车继续..."
        else
            print_error ".env.example 模板文件不存在"
            exit 1
        fi
    else
        print_success ".env 文件已存在"
    fi

    # 检查关键环境变量
    source .env

    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" == "your-secret-key-change-this-to-random-string" ]; then
        print_error "SECRET_KEY 未配置或使用默认值，请修改 .env 文件"
        exit 1
    fi

    if [ -z "$JWT_SECRET" ] || [ "$JWT_SECRET" == "your-jwt-secret-change-this-to-random-string" ]; then
        print_error "JWT_SECRET 未配置或使用默认值，请修改 .env 文件"
        exit 1
    fi

    print_success "环境变量配置检查通过"
}

# 构建并启动服务
start_services() {
    print_info "构建并启动 Docker 服务..."

    # 停止旧容器
    print_info "停止旧容器..."
    docker-compose down || true

    # 构建新镜像
    print_info "构建 Docker 镜像..."
    docker-compose build --no-cache

    # 启动服务
    print_info "启动服务..."
    docker-compose up -d

    print_success "Docker 服务已启动"
}

# 等待服务就绪
wait_for_service() {
    print_info "等待服务启动..."

    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
            print_success "服务已就绪"
            return 0
        fi

        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done

    echo ""
    print_error "服务启动超时"
    print_info "请查看日志: docker-compose logs -f"
    exit 1
}

# 初始化数据库
initialize_database() {
    print_info "初始化数据库..."

    # 创建管理员账号
    print_info "创建管理员账号..."
    docker-compose exec -T maxgamer-backend python create_admin.py

    # 注册游戏
    print_info "注册游戏到数据库..."
    docker-compose exec -T maxgamer-backend python register_games.py

    print_success "数据库初始化完成"
}

# 验证部署
verify_deployment() {
    print_info "验证部署..."

    # 检查容器状态
    print_info "检查容器状态..."
    if ! docker-compose ps | grep -q "Up"; then
        print_error "容器未正常运行"
        docker-compose ps
        exit 1
    fi

    # 检查 API 端点
    print_info "检查 API 端点..."
    local api_response=$(curl -s http://localhost:3000/api/games)

    if echo "$api_response" | grep -q "fortune-game"; then
        print_success "API 端点正常，游戏数据已加载"
    else
        print_warning "API 返回数据可能不完整"
        print_info "响应: $api_response"
    fi

    # 检查数据持久化
    print_info "检查数据持久化配置..."
    if [ -f "./data/frameworker.db" ]; then
        print_success "数据库文件已持久化到宿主机"
    else
        print_error "数据库文件不存在，数据持久化可能配置错误"
        exit 1
    fi

    print_success "部署验证通过"
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo -e "${GREEN}========================================"
    echo "  部署完成！"
    echo "========================================${NC}"
    echo ""
    echo "服务地址:"
    echo "  - API: http://localhost:3000"
    echo "  - 游戏市场: http://localhost:3000/game-market.html"
    echo "  - 设置页面: http://localhost:3000/settings.html"
    echo ""
    echo "管理员账号:"
    echo "  - 邮箱: admin@maxgamer.local"
    echo "  - 密码: pXw1995"
    echo ""
    echo "常用命令:"
    echo "  - 查看日志: docker-compose logs -f"
    echo "  - 重启服务: docker-compose restart"
    echo "  - 停止服务: docker-compose down"
    echo "  - 进入容器: docker-compose exec maxgamer-backend bash"
    echo ""
    echo "数据存储位置:"
    echo "  - 数据库: ./data/frameworker.db"
    echo "  - 日志: ./logs/"
    echo "  - 备份: ./backups/"
    echo ""
}

# 主函数
main() {
    print_banner

    # 解析命令行参数
    local skip_backup=false
    local skip_init=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-backup)
                skip_backup=true
                shift
                ;;
            --skip-init)
                skip_init=true
                shift
                ;;
            --help)
                echo "用法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --skip-backup    跳过数据库备份"
                echo "  --skip-init      跳过数据库初始化（仅更新代码）"
                echo "  --help           显示此帮助信息"
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                exit 1
                ;;
        esac
    done

    # 执行部署步骤
    check_requirements
    pull_latest_code

    if [ "$skip_backup" = false ]; then
        backup_database
    fi

    check_environment
    start_services
    wait_for_service

    if [ "$skip_init" = false ]; then
        initialize_database
    fi

    verify_deployment
    show_deployment_info

    print_success "部署完成！"
}

# 运行主函数
main "$@"

#!/bin/bash

# MaxGamer 部署更新脚本
# 用于更新远程服务器上的代码并重启服务

echo "=========================================="
echo "MaxGamer 部署更新"
echo "=========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "backend/app.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "📦 准备部署文件..."

# 1. 提交本地更改
echo ""
echo "1️⃣ 提交本地更改到Git..."
git add .
git commit -m "修复CORS配置以支持跨域API请求" || echo "没有新的更改需要提交"

# 2. 推送到远程仓库
echo ""
echo "2️⃣ 推送到远程仓库..."
git push origin main || git push origin master

echo ""
echo "✅ 代码已推送到远程仓库"
echo ""
echo "📋 接下来需要在服务器上执行以下命令："
echo ""
echo "ssh root@api.xmframer.com"
echo "cd /root/xmgamer"
echo "git pull"
echo "docker-compose restart backend"
echo ""
echo "或者运行一键部署命令："
echo "ssh root@api.xmframer.com 'cd /root/xmgamer && git pull && docker-compose restart backend'"
echo ""
echo "=========================================="

# ========================================
# FrameWorker 服务器更新脚本
# 用于更新已部署的服务器代码
# ========================================

set -e

echo "=========================================="
echo "FrameWorker 服务器更新脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PROJECT_DIR="/var/www/FrameWorker"
BACKUP_DIR="/var/backups/frameworker"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 检查是否在服务器上运行
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}错误: 项目目录不存在: $PROJECT_DIR${NC}"
    echo "此脚本应该在服务器上运行"
    exit 1
fi

echo -e "${BLUE}当前项目目录: $PROJECT_DIR${NC}"
echo ""

# ========================================
# 步骤 1: 显示当前状态
# ========================================
echo -e "${GREEN}步骤 1/7: 检查当前状态...${NC}"
cd $PROJECT_DIR

# 检查是否是git仓库
if [ -d ".git" ]; then
    echo "当前版本:"
    git log --oneline -1 2>/dev/null || echo "无法获取git信息"
    echo ""
    echo "检查远程更新..."
    git fetch origin 2>/dev/null || echo "无法连接到远程仓库"
    echo "远程最新版本:"
    git log origin/main --oneline -1 2>/dev/null || echo "无法获取远程信息"
else
    echo -e "${YELLOW}注意: 这不是一个git仓库${NC}"
    echo "将使用rsync方式更新文件"
fi

echo ""
read -p "是否继续更新? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消更新"
    exit 0
fi

# ========================================
# 步骤 2: 创建备份
# ========================================
echo ""
echo -e "${GREEN}步骤 2/7: 创建备份...${NC}"
mkdir -p $BACKUP_DIR

# 备份关键文件
echo "备份 Nginx 配置..."
if [ -d "$PROJECT_DIR/nginx" ]; then
    cp -r $PROJECT_DIR/nginx $BACKUP_DIR/nginx_$TIMESTAMP
fi

echo "备份数据库..."
if [ -f "$PROJECT_DIR/MaxGamer/backend/frameworker.db" ]; then
    cp $PROJECT_DIR/MaxGamer/backend/frameworker.db $BACKUP_DIR/frameworker_$TIMESTAMP.db
fi

echo "备份 .env 文件..."
if [ -f "$PROJECT_DIR/MaxGamer/backend/.env" ]; then
    cp $PROJECT_DIR/MaxGamer/backend/.env $BACKUP_DIR/.env_$TIMESTAMP
fi

echo -e "${GREEN}✅ 备份完成: $BACKUP_DIR${NC}"

# ========================================
# 步骤 3: 更新代码
# ========================================
echo ""
echo -e "${GREEN}步骤 3/7: 更新代码...${NC}"

if [ -d ".git" ]; then
    # Git 方式更新
    echo "使用 git pull 更新..."
    git fetch origin
    git reset --hard origin/main
    echo -e "${GREEN}✅ 代码已更新到最新版本${NC}"
else
    # 非Git仓库，提示手动更新
    echo -e "${YELLOW}⚠️  此目录不是git仓库${NC}"
    echo "请使用以下方式之一更新代码:"
    echo "1. 通过 GitHub Actions 自动部署"
    echo "2. 手动上传文件: scp -r MaxGamer/frontend/* root@149.88.69.87:/var/www/FrameWorker/MaxGamer/frontend/"
    echo ""
    read -p "是否已经手动更新了文件? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "请先更新文件后再继续"
        exit 1
    fi
fi

# ========================================
# 步骤 4: 更新 Python 依赖
# ========================================
echo ""
echo -e "${GREEN}步骤 4/7: 更新 Python 依赖...${NC}"
cd $PROJECT_DIR/MaxGamer/backend

if [ -f "requirements.txt" ]; then
    if [ -d "venv" ]; then
        echo "激活虚拟环境并更新依赖..."
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        deactivate
        echo -e "${GREEN}✅ Python 依赖已更新${NC}"
    else
        echo -e "${YELLOW}⚠️  虚拟环境不存在，跳过依赖更新${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  未找到 requirements.txt，跳过${NC}"
fi

# ========================================
# 步骤 5: 清理缓存
# ========================================
echo ""
echo -e "${GREEN}步骤 5/7: 清理缓存...${NC}"
cd $PROJECT_DIR

# 更新静态文件的修改时间，强制浏览器刷新
echo "更新静态文件时间戳..."
find $PROJECT_DIR/MaxGamer/frontend -type f \( -name "*.css" -o -name "*.js" -o -name "*.html" \) -exec touch {} \;

echo -e "${GREEN}✅ 缓存已清理${NC}"

# ========================================
# 步骤 6: 重启服务
# ========================================
echo ""
echo -e "${GREEN}步骤 6/7: 重启服务...${NC}"

# 重启 Docker 容器
if command -v docker &> /dev/null; then
    echo "重启 Docker 容器..."
    
    if docker ps | grep -q maxgamer-gateway; then
        docker restart maxgamer-gateway
        echo "✅ maxgamer-gateway 已重启"
    else
        echo "⚠️  maxgamer-gateway 容器未运行"
    fi

    if docker ps | grep -q maxgamer-api; then
        docker restart maxgamer-api
        echo "✅ maxgamer-api 已重启"
    else
        echo "⚠️  maxgamer-api 容器未运行"
    fi
fi

# 重启 Systemd 服务
if systemctl is-active --quiet frameworker 2>/dev/null; then
    echo "重启 frameworker 服务..."
    sudo systemctl restart frameworker
    echo "✅ frameworker 服务已重启"
fi

# 重启 Nginx
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "重新加载 Nginx 配置..."
    sudo nginx -t && sudo systemctl reload nginx
    echo "✅ Nginx 已重新加载"
fi

# ========================================
# 步骤 7: 验证部署
# ========================================
echo ""
echo -e "${GREEN}步骤 7/7: 验证部署...${NC}"

# 检查服务状态
echo "检查服务状态..."
if command -v docker &> /dev/null; then
    docker ps | grep maxgamer || true
fi

if systemctl is-active --quiet frameworker 2>/dev/null; then
    systemctl status frameworker --no-pager | head -10
fi

# 测试 API
echo ""
echo "测试 API 连接..."
sleep 2
API_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health 2>/dev/null || echo "000")
if [ "$API_TEST" = "200" ]; then
    echo -e "${GREEN}✅ API 正常响应${NC}"
else
    echo -e "${YELLOW}⚠️  API 响应异常 (HTTP $API_TEST)${NC}"
fi

# ========================================
# 完成
# ========================================
echo ""
echo -e "${GREEN}=========================================="
echo "🎉 更新完成！"
echo "==========================================${NC}"
echo ""

if [ -d ".git" ]; then
    echo "当前版本:"
    git log --oneline -1
    echo ""
fi

echo "备份位置: $BACKUP_DIR"
echo ""
echo -e "${YELLOW}重要提示:${NC}"
echo "1. 请在浏览器中强制刷新页面 (Ctrl+Shift+R 或 Cmd+Shift+R)"
echo "2. 如果遇到问题，可以从备份恢复"
echo "3. 查看日志: sudo journalctl -u frameworker -f"
echo ""

# 清理旧备份（保留最近10个）
echo "清理旧备份..."
cd $BACKUP_DIR
ls -t | tail -n +11 | xargs -r rm -rf
echo "✅ 已清理旧备份（保留最近10个）"
echo ""
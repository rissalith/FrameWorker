#!/bin/bash

# FrameWorker 快速部署脚本
# 适用于 Ubuntu/Debian 系统

set -e

echo "=========================================="
echo "FrameWorker 部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}请使用 sudo 运行此脚本${NC}"
    exit 1
fi

# 获取实际用户
ACTUAL_USER=${SUDO_USER:-$USER}
PROJECT_DIR="/var/www/FrameWorker"

echo -e "${GREEN}步骤 1/8: 更新系统包...${NC}"
apt update
apt upgrade -y

echo -e "${GREEN}步骤 2/8: 安装必要软件...${NC}"
apt install -y python3 python3-pip python3-venv nginx git

echo -e "${GREEN}步骤 3/8: 克隆项目...${NC}"
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}项目目录已存在，跳过克隆${NC}"
else
    mkdir -p /var/www
    cd /var/www
    git clone https://github.com/rissalith/FrameWorker.git
    chown -R $ACTUAL_USER:$ACTUAL_USER $PROJECT_DIR
fi

echo -e "${GREEN}步骤 4/8: 配置 Python 环境...${NC}"
cd $PROJECT_DIR/backend
if [ ! -d "venv" ]; then
    sudo -u $ACTUAL_USER python3 -m venv venv
fi
sudo -u $ACTUAL_USER venv/bin/pip install -r requirements.txt

echo -e "${GREEN}步骤 5/8: 配置环境变量...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}请编辑 $PROJECT_DIR/backend/.env 文件配置环境变量${NC}"
    echo -e "${YELLOW}按任意键继续...${NC}"
    read -n 1 -s
fi

echo -e "${GREEN}步骤 6/8: 初始化数据库...${NC}"
cd $PROJECT_DIR/backend
sudo -u $ACTUAL_USER venv/bin/python init_db.py

echo -e "${GREEN}步骤 7/8: 配置 Systemd 服务...${NC}"
cat > /etc/systemd/system/frameworker.service << EOF
[Unit]
Description=FrameWorker Flask Application
After=network.target

[Service]
User=$ACTUAL_USER
Group=$ACTUAL_USER
WorkingDirectory=$PROJECT_DIR/backend
Environment="PATH=$PROJECT_DIR/backend/venv/bin"
ExecStart=$PROJECT_DIR/backend/venv/bin/python app.py

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable frameworker
systemctl start frameworker

echo -e "${GREEN}步骤 8/8: 配置 Nginx...${NC}"
cat > /etc/nginx/sites-available/frameworker << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        root /var/www/FrameWorker/frontend;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 50M;
}
EOF

ln -sf /etc/nginx/sites-available/frameworker /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo -e "${GREEN}步骤 9/8: 配置防火墙...${NC}"
ufw allow 'Nginx Full'
ufw allow OpenSSH
echo "y" | ufw enable

echo ""
echo -e "${GREEN}=========================================="
echo "部署完成！"
echo "==========================================${NC}"
echo ""
echo "服务状态："
systemctl status frameworker --no-pager
echo ""
echo "访问地址："
echo "  http://$(hostname -I | awk '{print $1}')"
echo ""
echo "管理命令："
echo "  查看日志: sudo journalctl -u frameworker -f"
echo "  重启服务: sudo systemctl restart frameworker"
echo "  停止服务: sudo systemctl stop frameworker"
echo ""
echo -e "${YELLOW}重要提示：${NC}"
echo "1. 请编辑 $PROJECT_DIR/backend/.env 配置环境变量"
echo "2. 如需 HTTPS，请运行: sudo certbot --nginx"
echo "3. 建议配置定期备份"
echo ""
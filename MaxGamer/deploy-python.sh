#!/bin/bash

# ========================================
# FrameWorker Python 后端自动化部署脚本
# 目标服务器: Ubuntu 24.04 (149.88.69.87)
# ========================================

set -e  # 遇到错误立即退出

echo "🚀 开始部署 FrameWorker (Python 后端)..."

# ========================================
# 1. 安装基础环境
# ========================================
echo ""
echo "📦 步骤 1/9: 安装基础环境..."
sudo apt update
sudo apt install -y curl wget git nginx python3 python3-pip python3-venv

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version)
echo "Python 版本: $PYTHON_VERSION"

# ========================================
# 2. 创建项目目录
# ========================================
echo ""
echo "📁 步骤 2/9: 创建项目目录..."
sudo mkdir -p /var/www/xmframer/{frontend,backend}
sudo chown -R $USER:$USER /var/www/xmframer
echo "✅ 目录创建完成: /var/www/xmframer"

# ========================================
# 3. 部署后端
# ========================================
echo ""
echo "🔧 步骤 3/9: 部署 Python 后端..."
cd /var/www/xmframer/backend

# 创建 Python 虚拟环境
if [ ! -d "venv" ]; then
    echo "正在创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "正在安装 Python 依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "✅ Python 依赖安装完成"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: 未找到 .env 文件"
    if [ -f ".env.example" ]; then
        echo "正在从 .env.example 创建 .env 文件..."
        cp .env.example .env
        echo "⚠️  请编辑 /var/www/xmframer/backend/.env 文件并配置 API 密钥"
    fi
fi

# ========================================
# 4. 创建 systemd 服务
# ========================================
echo ""
echo "🚀 步骤 4/9: 配置 systemd 服务..."

sudo tee /etc/systemd/system/frameworker.service > /dev/null <<EOF
[Unit]
Description=FrameWorker Python Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/var/www/xmframer/backend
Environment="PATH=/var/www/xmframer/backend/venv/bin"
ExecStart=/var/www/xmframer/backend/venv/bin/python app.py
Restart=always
RestartSec=10

# 日志配置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=frameworker

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd 并启动服务
sudo systemctl daemon-reload
sudo systemctl enable frameworker
sudo systemctl restart frameworker

echo "✅ 后端服务已启动"
sleep 2
sudo systemctl status frameworker --no-pager

# ========================================
# 5. 部署前端（静态文件）
# ========================================
echo ""
echo "🎨 步骤 5/9: 部署前端..."
sudo mkdir -p /var/www/html/xmframer
sudo cp -r /var/www/xmframer/frontend/* /var/www/html/xmframer/
sudo chown -R www-data:www-data /var/www/html/xmframer
echo "✅ 前端文件已复制到 /var/www/html/xmframer"

# ========================================
# 6. 配置 Nginx
# ========================================
echo ""
echo "⚙️  步骤 6/9: 配置 Nginx..."

sudo tee /etc/nginx/sites-available/xmframer > /dev/null <<'EOF'
server {
    listen 80;
    server_name xmframer.com www.xmframer.com 149.88.69.87;

    # 前端静态文件
    location / {
        root /var/www/html/xmframer;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # 缓存静态资源
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|webp)$ {
            expires 7d;
            add_header Cache-Control "public, immutable";
        }
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # 超时设置（AI 生成可能需要较长时间）
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # 增加上传文件大小限制
    client_max_body_size 100M;

    # 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json image/svg+xml;
}
EOF

# 启用配置
sudo ln -sf /etc/nginx/sites-available/xmframer /etc/nginx/sites-enabled/

# 删除默认配置（可选）
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
echo "正在测试 Nginx 配置..."
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "✅ Nginx 配置完成"

# ========================================
# 7. 配置防火墙
# ========================================
echo ""
echo "🔒 步骤 7/9: 配置防火墙..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 'Nginx Full' 2>/dev/null || true
    sudo ufw allow 22/tcp 2>/dev/null || true
    echo "✅ 防火墙规则已更新"
else
    echo "⚠️  UFW 未安装，跳过防火墙配置"
fi

# ========================================
# 8. 安装 SSL 证书 (Let's Encrypt)
# ========================================
echo ""
echo "🔐 步骤 8/9: 配置 HTTPS..."
if ! command -v certbot &> /dev/null; then
    echo "正在安装 Certbot..."
    sudo apt install -y certbot python3-certbot-nginx
fi

echo ""
echo "⚠️  SSL 证书需要域名已正确解析到服务器 IP"
read -p "是否现在安装 SSL 证书？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo certbot --nginx -d xmframer.com -d www.xmframer.com --non-interactive --agree-tos --register-unsafely-without-email || {
        echo "⚠️  SSL 证书安装失败，可能是域名未解析或已有证书"
        echo "   稍后可手动执行: sudo certbot --nginx -d xmframer.com"
    }
else
    echo "⏭️  跳过 SSL 配置，稍后可手动执行:"
    echo "   sudo certbot --nginx -d xmframer.com -d www.xmframer.com"
fi

# ========================================
# 9. 测试部署
# ========================================
echo ""
echo "🧪 步骤 9/9: 测试部署..."

# 测试后端 API
echo "测试后端 API..."
sleep 3
API_RESPONSE=$(curl -s http://localhost:3000/api/health || echo "failed")
if [[ $API_RESPONSE == *"ok"* ]]; then
    echo "✅ 后端 API 正常: http://localhost:3000/api/health"
else
    echo "❌ 后端 API 测试失败"
    echo "查看日志: sudo journalctl -u frameworker -n 50"
fi

# 测试前端
echo "测试前端访问..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo "✅ 前端页面正常: http://localhost/"
else
    echo "❌ 前端页面测试失败 (HTTP $FRONTEND_RESPONSE)"
fi

# 显示服务状态
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 部署完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 服务信息:"
echo "   • 前端地址: http://149.88.69.87"
echo "   • API 地址: http://149.88.69.87/api/health"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   • HTTPS: https://xmframer.com"
fi
echo ""
echo "📊 服务管理命令:"
echo "   • 查看状态: sudo systemctl status frameworker"
echo "   • 查看日志: sudo journalctl -u frameworker -f"
echo "   • 重启服务: sudo systemctl restart frameworker"
echo "   • 停止服务: sudo systemctl stop frameworker"
echo ""
echo "🔧 Nginx 管理:"
echo "   • 重启: sudo systemctl restart nginx"
echo "   • 查看状态: sudo systemctl status nginx"
echo "   • 测试配置: sudo nginx -t"
echo ""
echo "⚠️  重要提示:"
echo "   请确保已配置 /var/www/xmframer/backend/.env 文件"
echo "   包含正确的 AI_IMAGE_API_KEY"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
# FrameWorker 部署指南

本文档提供了将 FrameWorker 部署到云服务器的详细步骤。

## 前置要求

- 云服务器（推荐 Ubuntu 20.04 或更高版本）
- Python 3.8+
- Nginx（用于反向代理）
- Git

## 部署步骤

### 1. 服务器准备

```bash
# 更新系统包
sudo apt update
sudo apt upgrade -y

# 安装必要的软件
sudo apt install -y python3 python3-pip python3-venv nginx git
```

### 2. 克隆项目

```bash
# 创建项目目录
cd /var/www
sudo git clone https://github.com/rissalith/FrameWorker.git
cd FrameWorker
sudo chown -R $USER:$USER /var/www/FrameWorker
```

### 3. 配置 Python 环境

```bash
# 创建虚拟环境
cd /var/www/FrameWorker/backend
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入实际配置
nano .env
```

重要配置项：
- `SECRET_KEY`: 生成一个强随机密钥
- `JWT_SECRET_KEY`: 生成另一个强随机密钥
- `FLASK_ENV`: 设置为 `production`
- 其他 OAuth 和邮件服务配置（根据需要）

### 5. 初始化数据库

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 运行数据库初始化脚本
python init_db.py
```

### 6. 配置 Systemd 服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/frameworker.service
```

添加以下内容：

```ini
[Unit]
Description=FrameWorker Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/FrameWorker/backend
Environment="PATH=/var/www/FrameWorker/backend/venv/bin"
ExecStart=/var/www/FrameWorker/backend/venv/bin/python app.py

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start frameworker

# 设置开机自启
sudo systemctl enable frameworker

# 检查服务状态
sudo systemctl status frameworker
```

### 7. 配置 Nginx

创建 Nginx 配置文件：

```bash
sudo nano /etc/nginx/sites-available/frameworker
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或服务器IP

    # 静态文件
    location / {
        root /var/www/FrameWorker/frontend;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 增加上传文件大小限制
    client_max_body_size 50M;
}
```

启用配置：

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/frameworker /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 8. 配置防火墙

```bash
# 允许 HTTP 和 HTTPS
sudo ufw allow 'Nginx Full'

# 如果需要 SSH
sudo ufw allow OpenSSH

# 启用防火墙
sudo ufw enable
```

### 9. 配置 HTTPS（可选但推荐）

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

## 更新部署

当需要更新代码时：

```bash
# 进入项目目录
cd /var/www/FrameWorker

# 拉取最新代码
git pull origin master

# 更新 Python 依赖（如果有变化）
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl restart frameworker
```

## 日志查看

```bash
# 查看应用日志
sudo journalctl -u frameworker -f

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 故障排查

### 服务无法启动

```bash
# 检查服务状态
sudo systemctl status frameworker

# 查看详细日志
sudo journalctl -u frameworker -n 50
```

### 数据库问题

```bash
# 检查数据库文件权限
ls -la /var/www/FrameWorker/backend/frameworker.db

# 如果需要，修改权限
sudo chown www-data:www-data /var/www/FrameWorker/backend/frameworker.db
```

### Nginx 502 错误

- 检查 Flask 应用是否正在运行
- 检查端口 3000 是否被占用
- 查看 Nginx 错误日志

## 性能优化建议

1. **使用 Gunicorn 替代 Flask 内置服务器**

```bash
pip install gunicorn

# 修改 systemd 服务文件中的 ExecStart
ExecStart=/var/www/FrameWorker/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:3000 app:app
```

2. **启用 Nginx 缓存**

在 Nginx 配置中添加静态文件缓存。

3. **使用 PostgreSQL 替代 SQLite**（生产环境推荐）

对于高并发场景，建议使用 PostgreSQL。

## 安全建议

1. 定期更新系统和依赖包
2. 使用强密码和密钥
3. 启用 HTTPS
4. 配置防火墙规则
5. 定期备份数据库
6. 限制文件上传大小
7. 实施速率限制

## 备份策略

```bash
# 创建备份脚本
sudo nano /usr/local/bin/backup-frameworker.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/frameworker"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp /var/www/FrameWorker/backend/frameworker.db $BACKUP_DIR/frameworker_$DATE.db

# 删除 30 天前的备份
find $BACKUP_DIR -name "frameworker_*.db" -mtime +30 -delete
```

```bash
# 添加执行权限
sudo chmod +x /usr/local/bin/backup-frameworker.sh

# 添加到 crontab（每天凌晨 2 点备份）
sudo crontab -e
# 添加：0 2 * * * /usr/local/bin/backup-frameworker.sh
```

## 监控

建议使用以下工具监控应用：
- Prometheus + Grafana
- New Relic
- Datadog

## 支持

如有问题，请访问：https://github.com/rissalith/FrameWorker/issues
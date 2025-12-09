# MaxGamer 自动化部署指南

## 概述

本指南介绍如何使用自动化脚本部署 MaxGamer 平台，实现**前后端、数据库、平台和游戏的完全隔离**。

## 架构设计

### 隔离层次

```
┌─────────────────────────────────────────────────────────────┐
│                     MaxGamer 隔离架构                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   前端容器    │  │   后端容器    │  │  数据库容器   │      │
│  │  (Nginx)     │  │  (Flask API) │  │ (PostgreSQL) │      │
│  │              │  │              │  │              │      │
│  │ - 静态文件    │  │ - API 服务   │  │ - 用户数据    │      │
│  │ - 游戏前端    │  │ - 业务逻辑   │  │ - 游戏数据    │      │
│  │   (只读)     │  │ - 游戏管理   │  │ - 平台绑定    │      │
│  └───────┬──────┘  └──────┬───────┘  └──────┬───────┘      │
│          │                │                 │              │
│          │    HTTP/REST   │     SQL         │              │
│          └────────────────┼─────────────────┘              │
│                           │                                │
│  ┌──────────────┐  ┌──────┴───────┐  ┌──────────────┐      │
│  │  Redis 缓存  │  │  游戏容器 1   │  │  游戏容器 2   │      │
│  │   (隔离)     │  │ (Fortune抖音) │  │ (FortuneTwitch)│    │
│  │              │  │              │  │              │      │
│  │ - Session    │  │ - 游戏逻辑   │  │ - 游戏逻辑   │      │
│  │ - Token      │  │ - 游戏数据   │  │ - 游戏数据   │      │
│  │ - 临时数据    │  │   (隔离)     │  │   (隔离)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 网络隔离

1. **前端网络** (`maxgamer-frontend-network`)
   - 前端容器独立网络
   - 通过代理访问后端

2. **后端网络** (`maxgamer-backend-network`)
   - 后端、前端、Redis 通信
   - 对外暴露 API

3. **数据库网络** (`maxgamer-db-network`)
   - **内部网络** (internal: true)
   - 仅后端可访问
   - 外部完全隔离

4. **游戏网络** (`maxgamer-game-network`)
   - **内部网络** (internal: true)
   - 游戏容器只能与后端通信
   - 游戏之间完全隔离

### 数据隔离

```
./data/
├── postgres/        # 数据库数据（PostgreSQL）
│   └── frameworker.db (旧版 SQLite，废弃)
├── redis/          # Redis 缓存数据
├── vector_db/      # RAG 向量数据库
├── uploads/        # 用户上传文件
└── games/          # 游戏专用数据
    ├── fortune-douyin/    # 抖音版游戏数据
    └── fortune-twitch/    # Twitch 版游戏数据
```

## 快速开始

### 1. 环境准备

```bash
# 克隆代码（如果还没有）
git clone https://github.com/WistonPeng/Max-Gamer-Platform.git
cd Max-Gamer-Platform

# 确保 Docker 和 Docker Compose 已安装
docker --version
docker-compose --version
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env  # 或使用 vim
```

**必须配置的关键变量**：

```bash
# 安全密钥（生成随机字符串）
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# 数据库密码
DB_PASSWORD=your_secure_database_password_here

# Redis 密码
REDIS_PASSWORD=your_secure_redis_password_here

# Twitch OAuth
TWITCH_CLIENT_SECRET=your_twitch_client_secret_here
TWITCH_REDIRECT_URI=https://your-domain.com/api/auth/platform-callback/twitch
```

### 3. 运行自动化部署脚本

```bash
# 赋予执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

部署脚本会自动完成：
- ✅ 拉取最新代码
- ✅ 备份现有数据库
- ✅ 检查环境变量配置
- ✅ 构建 Docker 镜像
- ✅ 启动所有隔离容器
- ✅ 等待服务就绪
- ✅ 初始化数据库
- ✅ 创建管理员账号
- ✅ 注册游戏
- ✅ 验证部署

## 部署选项

### 选项 1：简单部署（SQLite + 单容器）

适用于开发环境或小规模部署。

```bash
# 使用默认的 docker-compose.yml
docker-compose up -d
```

### 选项 2：隔离部署（PostgreSQL + 多容器）

**推荐用于生产环境**，提供完全隔离。

```bash
# 使用隔离版 docker-compose
docker-compose -f docker-compose.isolated.yml up -d
```

### 选项 3：自动化部署脚本

**最推荐**，自动处理所有步骤。

```bash
./deploy.sh

# 跳过数据库备份
./deploy.sh --skip-backup

# 仅更新代码，不初始化数据库
./deploy.sh --skip-init
```

## 部署后操作

### 访问服务

- **前端页面**: http://your-server:8080
- **后端 API**: http://your-server:3000/api
- **游戏市场**: http://your-server:8080/game-market.html
- **设置页面**: http://your-server:8080/settings.html

### 管理员登录

```
邮箱: admin@maxgamer.local
密码: pXw1995
```

### 常用命令

```bash
# 查看所有容器状态
docker-compose ps

# 查看日志
docker-compose logs -f                    # 所有容器
docker-compose logs -f maxgamer-backend   # 仅后端
docker-compose logs -f maxgamer-frontend  # 仅前端
docker-compose logs -f maxgamer-db        # 仅数据库

# 进入容器
docker-compose exec maxgamer-backend bash  # 后端容器
docker-compose exec maxgamer-db psql -U maxgamer_user -d maxgamer  # 数据库

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 完全清理（包括数据）
docker-compose down -v  # ⚠️ 危险：会删除所有数据卷
```

## 数据备份与恢复

### 自动备份

部署脚本会在每次部署前自动备份数据库到 `./backups/` 目录。

### 手动备份

```bash
# PostgreSQL 备份
docker-compose exec maxgamer-db pg_dump -U maxgamer_user maxgamer > backup_$(date +%Y%m%d).sql

# Redis 备份
docker-compose exec maxgamer-redis redis-cli --raw SAVE
cp ./data/redis/dump.rdb ./backups/redis_$(date +%Y%m%d).rdb
```

### 恢复数据

```bash
# PostgreSQL 恢复
cat backup_20231209.sql | docker-compose exec -T maxgamer-db psql -U maxgamer_user -d maxgamer

# Redis 恢复
docker-compose stop maxgamer-redis
cp ./backups/redis_20231209.rdb ./data/redis/dump.rdb
docker-compose start maxgamer-redis
```

## 安全加固

### 1. 更改默认密码

```bash
# 修改 .env 文件中的所有密码
nano .env

# 更改数据库密码
DB_PASSWORD=your_new_secure_password

# 更改 Redis 密码
REDIS_PASSWORD=your_new_redis_password
```

### 2. 启用防火墙

```bash
# 只开放必要端口
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 22/tcp    # SSH
sudo ufw enable
```

### 3. 配置 HTTPS (SSL/TLS)

```bash
# 安装 Certbot
sudo apt-get install certbot

# 获取 SSL 证书
sudo certbot certonly --standalone -d your-domain.com

# 更新 nginx.conf 启用 SSL
# 重启前端容器
docker-compose restart maxgamer-frontend
```

## 监控与维护

### 查看资源使用

```bash
# 容器资源使用情况
docker stats

# 磁盘使用
du -sh ./data/*
```

### 日志管理

```bash
# 查看日志大小
du -sh ./logs/*

# 清理旧日志（7天前）
find ./logs -name "*.log" -mtime +7 -delete
```

### 健康检查

```bash
# 检查所有服务健康状态
curl http://localhost:3000/api/health
curl http://localhost:8080/health

# 检查数据库连接
docker-compose exec maxgamer-db pg_isready -U maxgamer_user
```

## 故障排查

### 问题 1: 容器无法启动

```bash
# 查看容器日志
docker-compose logs maxgamer-backend

# 检查端口占用
sudo netstat -tlnp | grep :3000

# 重新构建镜像
docker-compose build --no-cache
docker-compose up -d
```

### 问题 2: 数据库连接失败

```bash
# 检查数据库容器状态
docker-compose ps maxgamer-db

# 查看数据库日志
docker-compose logs maxgamer-db

# 测试数据库连接
docker-compose exec maxgamer-backend python -c "from database import get_db_session; db=get_db_session(); print('Connected')"
```

### 问题 3: 游戏无法加载

```bash
# 检查游戏库挂载
docker-compose exec maxgamer-backend ls -la /app/GameLibrary

# 重新注册游戏
docker-compose exec maxgamer-backend python register_games.py

# 检查游戏 API
curl http://localhost:3000/api/games
```

## 更新升级

### 更新代码

```bash
# 拉取最新代码
git pull origin main

# 重新部署
./deploy.sh --skip-backup  # 跳过备份加快部署
```

### 滚动更新（零停机）

```bash
# 1. 构建新镜像
docker-compose build

# 2. 逐个更新容器
docker-compose up -d --no-deps --build maxgamer-backend
docker-compose up -d --no-deps --build maxgamer-frontend
```

## 扩展与定制

### 添加新游戏容器

编辑 `docker-compose.isolated.yml`:

```yaml
game-your-new-game:
  build:
    context: ./GameLibrary/platform/your-new-game
    dockerfile: Dockerfile
  container_name: game-your-new-game
  restart: unless-stopped

  networks:
    - maxgamer-game-network
    - maxgamer-backend-network

  volumes:
    - ./data/games/your-new-game:/app/data

  environment:
    - GAME_ID=your-new-game
    - PLATFORM=platform
    - API_BASE_URL=http://maxgamer-backend:5000
```

### 配置负载均衡

```bash
# 安装 Nginx
sudo apt-get install nginx

# 配置反向代理
sudo nano /etc/nginx/sites-available/maxgamer

# 添加负载均衡配置
upstream maxgamer_backend {
    server localhost:3000;
    server localhost:3001;  # 第二个后端实例
}
```

## 联系支持

如果遇到问题，请查看：
- 📖 [完整文档](DEPLOYMENT.md)
- 🐛 [GitHub Issues](https://github.com/WistonPeng/Max-Gamer-Platform/issues)
- 📝 后端日志: `./logs/backend/`
- 📝 前端日志: `./logs/nginx/`

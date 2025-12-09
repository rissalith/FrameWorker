# 🎮 MaxGamer - 多平台直播游戏平台

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](docker-compose.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![CI Tests](https://github.com/WistonPeng/Max-Gamer-Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/WistonPeng/Max-Gamer-Platform/actions/workflows/ci.yml)
[![Deploy](https://github.com/WistonPeng/Max-Gamer-Platform/actions/workflows/deploy.yml/badge.svg)](https://github.com/WistonPeng/Max-Gamer-Platform/actions/workflows/deploy.yml)

MaxGamer 是一个支持多平台（抖音、TikTok、Twitch、YouTube）的直播互动游戏平台，提供完整的游戏管理、用户认证和平台绑定功能。

## ✨ 特性

### 核心功能
- 🎯 **多平台支持**: 抖音、TikTok、Twitch、YouTube
- 🎮 **游戏市场**: 浏览、购买和启动游戏
- 🔐 **用户认证**: JWT 令牌、OAuth 绑定
- 💬 **实时互动**: WebSocket 连接、礼物检测
- 🎨 **响应式设计**: 适配桌面和移动端

### Twitch 平台特性
- ✅ OAuth 2.0 自动绑定
- ✅ Access Token 自动刷新
- ✅ IRC 实时连接
- ✅ Bits 打赏检测
- ✅ 订阅事件支持 (sub/resub/subgift)
- ✅ Raid 事件检测

### 技术架构
- 🐳 **完全容器化**: Docker + Docker Compose
- 🔒 **多层隔离**: 前后端、数据库、游戏完全隔离
- 📦 **自动化部署**: 一键部署脚本 + GitHub Actions CI/CD
- 💾 **数据持久化**: PostgreSQL + Redis
- 🚀 **高性能**: Nginx 反向代理、缓存优化
- ✅ **自动化测试**: CI/CD 流水线、单元测试

## 🚀 快速开始

### 方式一：自动化部署（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/WistonPeng/Max-Gamer-Platform.git
cd Max-Gamer-Platform

# 2. 配置环境变量
cp .env.example .env
nano .env  # 配置必要的环境变量

# 3. 运行自动化部署脚本
chmod +x deploy.sh
./deploy.sh
```

**就这么简单！** 🎉

脚本会自动完成：
- 拉取最新代码
- 备份数据库
- 构建 Docker 镜像
- 启动所有服务
- 初始化数据库
- 创建管理员账号
- 注册游戏

### 方式二：手动部署

```bash
# 1. 克隆仓库
git clone https://github.com/WistonPeng/Max-Gamer-Platform.git
cd Max-Gamer-Platform

# 2. 配置环境变量
cp .env.example .env
nano .env

# 3. 启动服务
docker-compose up -d

# 4. 等待服务启动
sleep 10

# 5. 初始化数据库
docker-compose exec maxgamer-backend python create_admin.py
docker-compose exec maxgamer-backend python register_games.py
```

## 📋 环境变量配置

### 必须配置

```bash
# 安全密钥
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# 数据库
DB_PASSWORD=your-secure-database-password

# Redis
REDIS_PASSWORD=your-redis-password

# Twitch OAuth
TWITCH_CLIENT_SECRET=your-twitch-client-secret
TWITCH_REDIRECT_URI=https://your-domain.com/api/auth/platform-callback/twitch
```

### 生成随机密钥

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🏗️ 架构说明

### 完全隔离架构

```
┌─────────────────────────────────────────────┐
│              MaxGamer 平台                   │
├─────────────────────────────────────────────┤
│                                              │
│  前端容器 ←→ 后端容器 ←→ 数据库容器          │
│  (Nginx)     (Flask)     (PostgreSQL)       │
│     ↓            ↓            ↓             │
│  静态文件    API服务      用户数据           │
│  游戏前端    游戏管理     游戏数据           │
│                                              │
│  ┌──────────┐  ┌──────────┐                │
│  │ Redis    │  │ 游戏容器  │                │
│  │ 缓存     │  │ (隔离)   │                │
│  └──────────┘  └──────────┘                │
│                                              │
└─────────────────────────────────────────────┘
```

### 网络隔离

- **前端网络**: 独立网络，通过代理访问后端
- **后端网络**: 后端、前端、Redis 通信
- **数据库网络**: 内部网络，仅后端可访问
- **游戏网络**: 内部网络，游戏容器完全隔离

详见 [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)

## 📚 文档

- 📖 [部署指南](DEPLOYMENT.md) - 详细部署步骤
- 🚀 [自动化部署指南](DEPLOY_GUIDE.md) - 隔离架构和自动化部署
- 🎮 [游戏开发指南](GameLibrary/README.md) - 如何开发新游戏
- 🔧 [API 文档](docs/API.md) - 后端 API 接口文档

## 🎮 已支持游戏

| 游戏名称 | 平台 | 状态 | 说明 |
|---------|------|------|------|
| Miko Fortune (抖音版) | 抖音 | ✅ 可用 | 礼物检测、占卜互动 |
| Miko Fortune (Twitch版) | Twitch | ✅ 可用 | Bits、订阅、Raid 互动 |
| Miko Fortune (TikTok版) | TikTok | 🚧 开发中 | 敬请期待 |
| Miko Fortune (YouTube版) | YouTube | 🚧 开发中 | 敬请期待 |

## 🔐 管理员账号

部署完成后，使用以下账号登录后台：

```
邮箱: admin@maxgamer.local
密码: pXw1995
```

**⚠️ 安全提示**: 首次登录后请立即修改密码！

## 🌐 访问地址

部署完成后，可通过以下地址访问：

- 前端页面: http://your-server:8080
- 后端 API: http://your-server:3000/api
- 游戏市场: http://your-server:8080/game-market.html
- 设置页面: http://your-server:8080/settings.html

## 🛠️ 常用命令

```bash
# 查看所有容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 进入后端容器
docker-compose exec maxgamer-backend bash

# 备份数据库
./deploy.sh --skip-init  # 自动备份

# 查看资源使用
docker stats
```

## 🔄 GitHub Actions CI/CD

项目已配置自动化部署流水线，每次推送到 `main` 分支时自动触发。

### 自动化流程

**CI 测试流程：**
1. ✅ Python 单元测试
2. ✅ 代码质量检查 (flake8)
3. ✅ Docker 镜像构建
4. ✅ 配置文件验证

**自动部署流程：**
1. 🚀 SSH 连接到服务器
2. 📥 拉取最新代码
3. 🔨 执行部署脚本
4. ✅ 健康检查验证

### 配置 Actions

参考 [GitHub Actions 设置指南](.github/ACTIONS_SETUP.md) 配置自动化部署。

**必须配置的 Secrets：**
- `SSH_PRIVATE_KEY` - SSH 私钥
- `SERVER_HOST` - 服务器地址
- `SERVER_USER` - SSH 用户名
- `DEPLOY_PATH` - 项目路径

### 手动触发部署

访问仓库的 **Actions** 页面，选择 **Deploy to Production**，点击 **Run workflow** 即可手动触发部署。

## 📊 项目结构

```
MaxGamer/
├── MaxGamer/                 # 平台核心代码
│   ├── backend/             # 后端 Flask API
│   │   ├── routes/         # API 路由
│   │   ├── database.py     # 数据库模型
│   │   └── app.py          # 应用入口
│   └── frontend/           # 前端静态文件
│       ├── pages/          # HTML 页面
│       ├── js/             # JavaScript 模块
│       └── css/            # 样式文件
├── GameLibrary/             # 游戏库
│   ├── douyin/             # 抖音平台游戏
│   ├── twitch/             # Twitch 平台游戏
│   ├── tiktok/             # TikTok 平台游戏
│   └── youtube/            # YouTube 平台游戏
├── docker-compose.yml       # Docker Compose 配置
├── docker-compose.isolated.yml  # 隔离架构配置
├── deploy.sh               # 自动化部署脚本
├── nginx.conf              # Nginx 配置
├── .env.example            # 环境变量模板
├── .github/                # GitHub Actions
│   ├── workflows/          # CI/CD 工作流
│   └── ACTIONS_SETUP.md    # Actions 配置指南
├── DEPLOYMENT.md           # 部署文档
└── DEPLOY_GUIDE.md         # 自动化部署指南
```

## 🔧 开发指南

### 添加新游戏

1. 在 `GameLibrary/{platform}/` 创建游戏目录
2. 添加 `game.json` 元数据文件
3. 开发游戏前后端代码
4. 运行 `python register_games.py` 注册游戏

### 本地开发

```bash
# 启动开发环境
cd MaxGamer/backend
python app.py

# 访问本地服务
# Backend: http://localhost:5000
# Frontend: file://MaxGamer/frontend/pages/index.html
```

## 🐛 故障排查

### 问题 1: 容器无法启动

```bash
docker-compose logs maxgamer-backend
docker-compose build --no-cache
docker-compose up -d
```

### 问题 2: 数据库连接失败

```bash
docker-compose ps maxgamer-db
docker-compose logs maxgamer-db
```

### 问题 3: 游戏无法加载

```bash
docker-compose exec maxgamer-backend python register_games.py
curl http://localhost:3000/api/games
```

更多故障排查请参考 [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md#故障排查)

## 📝 更新日志

### v2.0.0 (2025-12-09)

**🎉 重大更新: 自动化部署和完全隔离架构**

- ✨ 新增自动化部署脚本 `deploy.sh`
- 🔒 实现前后端、数据库、游戏完全隔离
- 🐳 新增 Docker Compose 隔离配置
- 🌐 新增 Nginx 前端服务器
- 📦 新增 PostgreSQL + Redis 支持
- 📖 新增详细部署指南
- ✅ 新增 Twitch 平台游戏支持
- ✅ 实现 Twitch OAuth 绑定和 Token 自动刷新
- ✅ 集成 Twitch IRC 实时连接
- ✅ 修复数据库持久化问题
- ✅ 新增管理员账号和游戏注册脚本

详见 [DEPLOYMENT.md](DEPLOYMENT.md)

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 💬 联系我们

- GitHub Issues: [提交问题](https://github.com/WistonPeng/Max-Gamer-Platform/issues)
- 后端日志: `./logs/backend/`
- 前端日志: `./logs/nginx/`

## 🙏 致谢

本项目由 [Claude Code](https://claude.com/claude-code) 辅助开发。

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**

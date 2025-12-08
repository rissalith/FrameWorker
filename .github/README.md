# 自动化部署配置

本目录包含 GitHub Actions 自动化部署的配置文件。

## 📁 文件说明

- [`workflows/deploy.yml`](workflows/deploy.yml) - GitHub Actions 工作流配置
- [`SECRETS_SETUP.md`](SECRETS_SETUP.md) - GitHub Secrets 配置详细指南
- [`generate-secrets.py`](generate-secrets.py) - 密钥生成工具

## 🚀 快速开始

### 1. 生成密钥

```bash
# 运行密钥生成工具
python3 .github/generate-secrets.py
```

这将生成所有必需的随机密钥，并创建 `.env.generated` 文件。

### 2. 配置 GitHub Secrets

访问仓库的 Secrets 设置页面：
```
https://github.com/rissalith/FrameWorker/settings/secrets/actions
```

按照 [`SECRETS_SETUP.md`](SECRETS_SETUP.md) 中的说明，添加以下必需的 Secrets：

#### 最小必需配置（9 个）

- [ ] `SERVER_HOST` - 服务器 IP 地址
- [ ] `SERVER_USER` - SSH 用户名
- [ ] `SERVER_SSH_KEY` - SSH 私钥
- [ ] `MYSQL_ROOT_PASSWORD` - MySQL root 密码
- [ ] `MYSQL_PASSWORD` - MySQL 用户密码
- [ ] `REDIS_PASSWORD` - Redis 密码
- [ ] `SECRET_KEY` - Flask 密钥
- [ ] `JWT_SECRET_KEY` - JWT 密钥
- [ ] `DEEPSEEK_API_KEY` - DeepSeek API 密钥

#### 推荐配置（额外 6 个）

- [ ] `MYSQL_DATABASE` - 数据库名称
- [ ] `MYSQL_USER` - 数据库用户名
- [ ] `DOMAIN` - 主域名
- [ ] `API_DOMAIN` - API 域名
- [ ] `GAME_WITCH_DOMAIN` - 游戏域名
- [ ] `CORS_ORIGINS` - CORS 允许的源

### 3. 准备服务器

在服务器上执行以下操作：

```bash
# 1. 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com | sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 2. 创建部署目录
sudo mkdir -p /var/www/FrameWorker
sudo chown -R $USER:$USER /var/www/FrameWorker

# 3. 克隆仓库
cd /var/www
git clone https://github.com/rissalith/FrameWorker.git
cd FrameWorker

# 4. 添加 SSH 公钥到 authorized_keys
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 4. 触发部署

有两种方式触发自动部署：

#### 方式 1：推送代码（自动触发）

```bash
git add .
git commit -m "feat: add new feature"
git push origin main
```

#### 方式 2：手动触发

1. 访问 Actions 页面：https://github.com/rissalith/FrameWorker/actions
2. 选择 "Build and Deploy to Production" 工作流
3. 点击 "Run workflow"
4. 选择分支并点击 "Run workflow"

## 🔄 部署流程

工作流包含以下步骤：

### 1. 构建阶段（build-and-push）

- ✅ 检出代码
- ✅ 设置 Docker Buildx
- ✅ 登录 GitHub Container Registry
- ✅ 构建 Docker 镜像
  - `platform-api` - 平台 API 服务
  - `game-witch` - 女巫游戏服务
- ✅ 推送镜像到 GHCR

### 2. 部署阶段（deploy）

- ✅ 创建 `.env` 文件
- ✅ 创建 `docker-compose.prod.yml`
- ✅ 通过 SSH 连接服务器
- ✅ 拉取最新代码
- ✅ 拉取最新镜像
- ✅ 重启服务
- ✅ 健康检查

### 3. 通知阶段（notify）

- ✅ 发送部署结果通知

## 📊 服务架构

部署后的服务架构：

```
┌─────────────────────────────────────────┐
│           Nginx (Gateway)               │
│         Port: 80, 443                   │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────────┐    ┌────▼──────────┐
│ Platform   │    │  Game Witch   │
│   API      │    │   Service     │
│ Port: 5000 │    │  Port: 5001   │
└───┬────────┘    └────┬──────────┘
    │                  │
    └─────────┬────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐        ┌────▼────┐
│ MySQL  │        │  Redis  │
│ Port:  │        │  Port:  │
│  3306  │        │  6379   │
└────────┘        └─────────┘
```

## 🔍 监控和日志

### 查看部署日志

在 GitHub Actions 页面查看：
```
https://github.com/rissalith/FrameWorker/actions
```

### 查看服务日志

SSH 到服务器后：

```bash
# 查看所有服务状态
cd /var/www/FrameWorker
docker-compose -f docker-compose.prod.yml ps

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f platform-api
docker-compose -f docker-compose.prod.yml logs -f game-witch

# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f
```

## 🛠️ 故障排查

### 部署失败

1. **检查 GitHub Actions 日志**
   - 访问 Actions 页面查看详细错误信息

2. **SSH 连接失败**
   ```bash
   # 在本地测试 SSH 连接
   ssh -i ~/.ssh/your_key user@server_ip
   ```

3. **Docker 镜像拉取失败**
   ```bash
   # 在服务器上手动登录 GHCR
   echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
   ```

4. **服务启动失败**
   ```bash
   # 检查容器状态
   docker-compose -f docker-compose.prod.yml ps
   
   # 查看容器日志
   docker-compose -f docker-compose.prod.yml logs
   ```

### 常见问题

**Q: 如何回滚到上一个版本？**

A: 在服务器上执行：
```bash
cd /var/www/FrameWorker
git checkout <previous-commit-hash>
docker-compose -f docker-compose.prod.yml up -d
```

**Q: 如何更新环境变量？**

A: 
1. 在 GitHub Secrets 中更新变量
2. 重新触发部署工作流

**Q: 如何手动重启服务？**

A: 在服务器上执行：
```bash
cd /var/www/FrameWorker
docker-compose -f docker-compose.prod.yml restart
```

## 🔒 安全建议

1. ✅ 定期轮换密钥和密码
2. ✅ 使用强密码（至少 16 字符）
3. ✅ 限制 SSH 访问 IP
4. ✅ 启用 GitHub 2FA
5. ✅ 定期更新依赖包
6. ✅ 监控异常访问日志
7. ✅ 配置防火墙规则
8. ✅ 启用 HTTPS（使用 Let's Encrypt）

## 📚 相关文档

- [部署指南](../MaxGamer/DEPLOYMENT.md)
- [Docker 配置](../docker-compose.yml)
- [环境变量模板](../.env.example)
- [Secrets 配置指南](SECRETS_SETUP.md)

## 🆘 获取帮助

如有问题，请：
1. 查看 [SECRETS_SETUP.md](SECRETS_SETUP.md) 详细配置指南
2. 访问 [GitHub Issues](https://github.com/rissalith/FrameWorker/issues)
3. 查看 [部署文档](../MaxGamer/DEPLOYMENT.md)

## 📝 更新日志

- **2024-11-26**: 初始化自动化部署配置
  - 添加 GitHub Actions 工作流
  - 配置 GHCR 镜像推送
  - 实现 SSH 自动部署
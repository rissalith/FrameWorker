# 🚀 自动化部署操作指南

您已经完成了所有必需的配置！现在可以开始自动化部署了。

## ✅ 当前配置状态

已配置的 GitHub Secrets（22 个）：
- ✅ SERVER_HOST - 服务器地址
- ✅ SERVER_USER - SSH 用户名  
- ✅ SERVER_SSH_KEY - SSH 私钥
- ✅ MYSQL_ROOT_PASSWORD - MySQL root 密码
- ✅ MYSQL_DATABASE - 数据库名称
- ✅ MYSQL_USER - 数据库用户名
- ✅ MYSQL_PASSWORD - 数据库密码
- ✅ REDIS_PASSWORD - Redis 密码
- ✅ SECRET_KEY - Flask 密钥
- ✅ JWT_SECRET_KEY - JWT 密钥
- ✅ DEEPSEEK_API_KEY - DeepSeek API
- ✅ GEMINI_API_KEY - Gemini API
- ✅ SENDGRID_API_KEY - SendGrid API
- ✅ SENDGRID_FROM_EMAIL - 发件人邮箱
- ✅ GOOGLE_CLIENT_ID - Google OAuth ID
- ✅ GOOGLE_CLIENT_SECRET - Google OAuth Secret
- ✅ SMTP_HOST - SMTP 服务器
- ✅ SMTP_PORT - SMTP 端口
- ✅ SMTP_USER - SMTP 用户名
- ✅ SMTP_PASSWORD - SMTP 密码
- ✅ SMTP_FROM_NAME - 发件人名称
- ✅ DOMAIN - 主域名

**配置完整度：22/25（88%）✅ 可以开始部署！**

---

## 🎯 部署方式

### 方式 1：自动部署（推荐）⭐

每次推送代码到 `main` 或 `master` 分支时，会自动触发部署。

```bash
# 1. 提交您的更改
git add .
git commit -m "feat: 添加新功能"

# 2. 推送到 main 分支（会自动触发部署）
git push origin main
```

**自动触发条件：**
- 推送到 `main` 分支
- 推送到 `master` 分支

### 方式 2：手动触发部署 🖱️

如果您想在不推送代码的情况下重新部署：

#### 步骤 1：访问 GitHub Actions 页面

打开浏览器，访问：
```
https://github.com/rissalith/FrameWorker/actions
```

#### 步骤 2：选择工作流

在左侧菜单中，点击：
```
📋 Build and Deploy to Production
```

#### 步骤 3：运行工作流

1. 点击右上角的 **"Run workflow"** 按钮（蓝色下拉按钮）
2. 在弹出的对话框中：
   - **Use workflow from:** 选择 `main` 分支
3. 点击绿色的 **"Run workflow"** 按钮

#### 步骤 4：查看部署进度

- 页面会自动刷新，显示新的工作流运行
- 点击运行记录可以查看详细日志
- 实时查看每个步骤的执行情况

---

## 📊 部署流程说明

部署会自动执行以下 3 个阶段：

### 阶段 1：构建和推送镜像（约 3-5 分钟）

```
✓ Checkout code                    # 检出代码
✓ Set up Docker Buildx             # 设置 Docker 构建器
✓ Log in to GitHub Container Registry  # 登录镜像仓库
✓ Build platform-api image         # 构建平台 API 镜像
✓ Build game-witch image           # 构建游戏服务镜像
✓ Push images to registry          # 推送镜像到仓库
```

**构建的镜像：**
- `ghcr.io/rissalith/maxgamer-platform-api:latest`
- `ghcr.io/rissalith/maxgamer-game-witch:latest`

### 阶段 2：部署到服务器（约 2-3 分钟）

```
✓ Create .env file                 # 创建环境变量文件
✓ Create docker-compose.prod.yml   # 创建生产环境配置
✓ Copy files to server             # 复制文件到服务器
✓ SSH to server                    # SSH 连接服务器
✓ Pull latest code                 # 拉取最新代码
✓ Pull Docker images               # 拉取 Docker 镜像
✓ Stop old containers              # 停止旧容器
✓ Start new containers             # 启动新容器
✓ Health check                     # 健康检查
```

### 阶段 3：通知（约 10 秒）

```
✓ Send deployment notification     # 发送部署通知
```

---

## 🔍 查看部署日志

### 在 GitHub Actions 中查看

1. 访问：https://github.com/rissalith/FrameWorker/actions
2. 点击最新的工作流运行
3. 展开各个步骤查看详细日志

**关键日志位置：**
- **构建日志：** `build-and-push` → `Build and push Docker image`
- **部署日志：** `deploy` → `Deploy to server via SSH`
- **健康检查：** `deploy` → `Health check`

### 在服务器上查看

SSH 登录服务器后：

```bash
# 进入项目目录
cd /var/www/FrameWorker

# 查看所有服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f platform-api
docker-compose -f docker-compose.prod.yml logs -f game-witch
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f mysql
docker-compose -f docker-compose.prod.yml logs -f redis
```

---

## ✅ 验证部署成功

### 1. 检查 GitHub Actions 状态

在 Actions 页面，确认：
- ✅ 所有步骤都显示绿色对勾
- ✅ 没有红色的错误标记
- ✅ 最后显示 "✅ 部署成功！服务运行正常"

### 2. 访问网站

打开浏览器，访问：

```
http://YOUR_SERVER_IP
```

或者如果配置了域名：

```
https://maxgamer.com
```

**应该能看到：**
- ✅ 网站首页正常显示
- ✅ 可以注册/登录
- ✅ 游戏列表正常加载

### 3. 检查 API 健康状态

```bash
# 使用 curl 检查
curl http://YOUR_SERVER_IP/health

# 或访问浏览器
http://YOUR_SERVER_IP/health
```

**预期响应：**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 4. 检查服务器容器状态

SSH 登录服务器：

```bash
cd /var/www/FrameWorker
docker-compose -f docker-compose.prod.yml ps
```

**所有服务应该显示 "Up"：**
```
NAME                STATUS
maxgamer-gateway     Up
maxgamer-api         Up
game-witch          Up
maxgamer-db          Up
maxgamer-redis       Up
```

---

## 🔧 常见问题排查

### 问题 1：构建失败

**症状：** `build-and-push` 阶段失败

**可能原因：**
- Dockerfile 配置错误
- 依赖包安装失败
- 网络连接问题

**解决方法：**
1. 查看构建日志，找到具体错误
2. 检查 Dockerfile 配置
3. 本地测试构建：
   ```bash
   docker build -t test-image ./MaxGamer
   ```

### 问题 2：SSH 连接失败

**症状：** `deploy` 阶段显示 SSH 连接错误

**可能原因：**
- SSH 密钥格式不正确
- 服务器防火墙阻止连接
- 服务器 IP 地址错误

**解决方法：**
1. 验证 SSH 密钥格式（应包含完整的 BEGIN/END 标记）
2. 测试本地 SSH 连接：
   ```bash
   ssh -i ~/.ssh/your_key user@server_ip
   ```
3. 检查服务器防火墙规则：
   ```bash
   sudo ufw status
   sudo ufw allow 22/tcp
   ```

### 问题 3：容器启动失败

**症状：** 容器状态显示 "Exited" 或 "Restarting"

**可能原因：**
- 环境变量配置错误
- 端口冲突
- 数据库连接失败

**解决方法：**
1. 查看容器日志：
   ```bash
   docker-compose -f docker-compose.prod.yml logs service-name
   ```
2. 检查端口占用：
   ```bash
   sudo netstat -tulpn | grep :5000
   ```
3. 验证环境变量：
   ```bash
   docker-compose -f docker-compose.prod.yml config
   ```

### 问题 4：健康检查失败

**症状：** 最后的健康检查步骤失败

**可能原因：**
- 服务启动时间过长
- 健康检查端点未配置
- 防火墙阻止访问

**解决方法：**
1. 增加等待时间（已设置 30 秒）
2. 手动测试健康检查：
   ```bash
   curl http://YOUR_SERVER_IP/health
   ```
3. 检查 Nginx 配置

---

## 🔄 回滚部署

如果新版本有问题，可以快速回滚：

### 方法 1：重新部署上一个版本

1. 在 GitHub 找到上一个成功的提交
2. 创建新分支或直接 revert：
   ```bash
   git revert HEAD
   git push origin main
   ```

### 方法 2：使用旧镜像

SSH 登录服务器：

```bash
cd /var/www/FrameWorker

# 查看可用的镜像标签
docker images | grep xmgamer

# 修改 docker-compose.prod.yml 使用特定版本
# 例如：image: ghcr.io/rissalith/maxgamer-platform-api:main-abc123

# 重启服务
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📈 监控和维护

### 定期检查

建议每天检查：

```bash
# 1. 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 2. 检查磁盘空间
df -h

# 3. 检查日志大小
du -sh logs/

# 4. 清理旧镜像
docker image prune -af
```

### 自动备份

系统已配置自动备份：
- **备份时间：** 每天凌晨 2:00
- **保留天数：** 7 天
- **备份位置：** `/var/www/FrameWorker/backups/`

查看备份：
```bash
ls -lh /var/www/FrameWorker/backups/
```

---

## 🎉 开始您的第一次部署！

### 快速开始（3 步）

1. **访问 Actions 页面**
   ```
   https://github.com/rissalith/FrameWorker/actions
   ```

2. **点击 "Run workflow"**
   - 选择 `main` 分支
   - 点击绿色按钮

3. **等待部署完成**
   - 观看实时日志
   - 约 5-8 分钟完成

### 或者推送代码自动部署

```bash
git add .
git commit -m "feat: 启用自动化部署"
git push origin main
```

---

## 📞 需要帮助？

如果遇到问题：

1. **查看文档：**
   - [SECRETS_SETUP.md](SECRETS_SETUP.md) - Secrets 配置指南
   - [SECRETS_CHECKLIST.md](SECRETS_CHECKLIST.md) - 配置检查清单
   - [README.md](README.md) - 项目总览

2. **查看日志：**
   - GitHub Actions 日志
   - 服务器容器日志

3. **提交 Issue：**
   - https://github.com/rissalith/FrameWorker/issues

---

## 🔒 安全提醒

- ✅ 所有敏感信息已存储在 GitHub Secrets
- ✅ SSH 密钥仅用于部署
- ⚠️ 定期更换密钥（建议每 3-6 个月）
- ⚠️ 监控部署日志，发现异常及时处理

---

**祝您部署顺利！🚀**
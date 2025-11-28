# 🚀 快速部署指南（3 分钟）

## ✅ 前提条件

您已经配置了 22 个 GitHub Secrets：
- ✅ 服务器连接配置（SERVER_HOST, SERVER_USER, SERVER_SSH_KEY）
- ✅ 数据库配置（MYSQL_*）
- ✅ 应用密钥（SECRET_KEY, JWT_SECRET_KEY）
- ✅ API 密钥（DEEPSEEK_API_KEY, GEMINI_API_KEY）
- ✅ 其他服务配置

---

## 🎯 两种部署方式

### 方式 1：自动部署（推荐）⭐

**只需推送代码到 main 分支，系统会自动部署！**

```bash
git add .
git commit -m "feat: 启用自动化部署"
git push origin main
```

✨ **就这么简单！** 推送后会自动：
1. 构建 Docker 镜像
2. 推送到 GitHub Container Registry
3. 部署到服务器
4. 启动所有服务

---

### 方式 2：手动触发部署 🖱️

**不推送代码也能重新部署：**

#### 步骤 1：打开 Actions 页面
```
https://github.com/rissalith/FrameWorker/actions
```

#### 步骤 2：运行工作流
1. 点击左侧 **"Build and Deploy to Production"**
2. 点击右上角 **"Run workflow"** 按钮
3. 选择 **main** 分支
4. 点击绿色的 **"Run workflow"** 按钮

#### 步骤 3：等待完成
- 约 5-8 分钟完成
- 可以实时查看日志

---

## 📊 查看部署进度

### 在 GitHub 上查看

访问：https://github.com/rissalith/FrameWorker/actions

**部署流程：**
```
1. ✓ Build and Push Docker Images (3-5 分钟)
   ├─ Build platform-api image
   └─ Build game-witch image

2. ✓ Deploy to Server (2-3 分钟)
   ├─ Copy files to server
   ├─ SSH to server
   ├─ Pull latest images
   ├─ Restart services
   └─ Health check

3. ✓ Send Notification (10 秒)
```

---

## ✅ 验证部署成功

### 1. 检查 GitHub Actions
- 所有步骤显示 ✅ 绿色对勾
- 最后显示 "✅ 部署成功！服务运行正常"

### 2. 访问网站
```
http://YOUR_SERVER_IP
```

### 3. 检查 API 健康状态
```bash
curl http://YOUR_SERVER_IP/health
```

预期响应：
```json
{"status": "healthy"}
```

---

## 🔧 常见问题

### Q1: 构建失败怎么办？
**A:** 查看 Actions 日志，找到具体错误信息。通常是：
- Dockerfile 配置问题
- 依赖包安装失败
- 网络连接问题

### Q2: SSH 连接失败？
**A:** 检查：
- SERVER_HOST 是否正确
- SERVER_SSH_KEY 格式是否完整（包含 BEGIN/END 标记）
- 服务器防火墙是否允许 SSH 连接

### Q3: 容器启动失败？
**A:** SSH 登录服务器查看日志：
```bash
cd /var/www/FrameWorker
docker-compose -f docker-compose.prod.yml logs
```

### Q4: 健康检查失败？
**A:** 可能需要更长的启动时间，或者：
- 检查服务器防火墙是否开放 80 端口
- 手动测试：`curl http://YOUR_SERVER_IP/health`

---

## 📞 需要详细文档？

- **完整部署指南：** [HOW_TO_DEPLOY.md](HOW_TO_DEPLOY.md)
- **Secrets 配置：** [SECRETS_SETUP.md](SECRETS_SETUP.md)
- **配置检查清单：** [SECRETS_CHECKLIST.md](SECRETS_CHECKLIST.md)

---

## 🎉 开始部署！

**现在就试试吧：**

```bash
# 方式 1：推送代码自动部署
git push origin main

# 方式 2：访问 Actions 页面手动触发
# https://github.com/rissalith/FrameWorker/actions
```

**祝您部署顺利！🚀**
# 🚀 部署监控指南

## 当前状态

✅ **代码已推送**: Commit `730e308` - "🚀 触发完整构建和部署 - 修复Docker镜像缺失问题"

✅ **GitHub Actions已触发**: 完整的构建和部署流程正在运行

## 📊 监控链接

### GitHub Actions Workflow
🔗 **主要监控页面**: https://github.com/rissalith/FrameWorker/actions

**当前运行的Workflow**:
- Workflow名称: `Build and Deploy`
- 触发方式: Push to main branch
- Commit: `730e308`

### 预期执行流程

#### 1️⃣ Build and Push Docker Images (5-10分钟)
```
✓ Checkout code
✓ Set up Docker Buildx
✓ Login to GitHub Container Registry
✓ Build Docker image from ./XMGamer/Dockerfile
✓ Push to ghcr.io/rissalith/xmgamer-platform-api:latest
```

**关键检查点**:
- ✅ Docker镜像构建成功
- ✅ 镜像推送到 ghcr.io 成功
- ✅ 镜像标签正确: `latest`

#### 2️⃣ Deploy to Server (3-5分钟)
```
✓ Create .env file with all secrets
✓ Create docker-compose.prod.yml
✓ Copy files to server via SCP
✓ SSH to server and deploy
  - Pull Docker images
  - Stop old containers
  - Start new containers
  - Verify containers are running
✓ Health check
```

**关键检查点**:
- ✅ 文件成功复制到服务器
- ✅ Docker镜像成功拉取
- ✅ 容器成功启动
- ✅ 健康检查通过

#### 3️⃣ Notify (1分钟)
```
✓ Send deployment notification
```

## 🔍 如何监控

### 方法1: GitHub Actions Web界面 (推荐)

1. **访问Actions页面**:
   ```
   https://github.com/rissalith/FrameWorker/actions
   ```

2. **找到最新的运行**:
   - 查找 "🚀 触发完整构建和部署 - 修复Docker镜像缺失问题"
   - 状态应该是 🟡 黄色(运行中) 或 🟢 绿色(成功)

3. **查看详细日志**:
   - 点击workflow运行
   - 展开 "build-and-push" job
   - 展开 "deploy" job
   - 查看每个步骤的输出

### 方法2: 命令行监控

```bash
# 检查最新workflow状态
gh run list --limit 1

# 查看特定运行的详细信息
gh run view <run-id>

# 实时查看日志
gh run watch
```

### 方法3: 服务器直接检查

```bash
# SSH到服务器
ssh user@your-server

# 查看容器状态
docker-compose -f docker-compose.prod.yml ps

# 查看容器日志
docker-compose -f docker-compose.prod.yml logs -f platform-api

# 检查镜像
docker images | grep xmgamer-platform-api
```

## ⏱️ 预计时间线

| 时间 | 阶段 | 状态 |
|------|------|------|
| T+0分钟 | 代码推送完成 | ✅ 完成 |
| T+1分钟 | GitHub Actions触发 | ✅ 完成 |
| T+2-10分钟 | Docker镜像构建 | 🟡 进行中 |
| T+10-15分钟 | 部署到服务器 | ⏳ 等待中 |
| T+15-20分钟 | 服务启动和验证 | ⏳ 等待中 |
| T+20分钟 | **服务完全恢复** | ⏳ 等待中 |

## ✅ 成功标志

### GitHub Actions成功标志:
- ✅ "build-and-push" job 显示绿色勾号
- ✅ "deploy" job 显示绿色勾号
- ✅ "notify" job 显示绿色勾号
- ✅ 整个workflow显示绿色勾号

### 服务器成功标志:
```bash
# 容器运行状态
$ docker-compose -f docker-compose.prod.yml ps
NAME                    STATUS
platform-api            Up 2 minutes
mysql                   Up 2 minutes
redis                   Up 2 minutes
nginx                   Up 2 minutes

# 网站可访问
$ curl -I https://www.xmframer.com
HTTP/2 200 OK

# 健康检查通过
$ curl https://www.xmframer.com/health
{"status":"healthy"}
```

## ❌ 失败处理

### 如果Build失败:
1. 查看GitHub Actions日志中的错误信息
2. 检查Dockerfile语法
3. 检查依赖项是否正确
4. 修复后重新推送代码

### 如果Deploy失败:
1. 检查SSH连接是否正常
2. 检查服务器磁盘空间
3. 检查Docker服务是否运行
4. 查看服务器上的Docker日志

### 如果镜像拉取失败:
**这是之前的主要问题!**

如果看到类似错误:
```
Error response from daemon: manifest for ghcr.io/rissalith/xmgamer-platform-api:latest not found
```

**解决方案**:
1. 确认build-and-push job成功完成
2. 检查ghcr.io上是否有镜像
3. 如果仍然失败,使用中国镜像方案(见 fix-server-china-mirror.bat)

## 🔧 紧急回滚

如果部署失败且需要立即回滚:

```bash
# SSH到服务器
ssh user@your-server

# 回滚到之前的版本
cd /var/www/FrameWorker
git checkout <previous-commit>

# 重新部署
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

详细回滚步骤见: `EMERGENCY_ROLLBACK.md`

## 📞 问题排查

### 问题1: Workflow没有触发
**检查**:
- GitHub Actions是否启用
- 分支名称是否正确(main/master)
- workflow文件语法是否正确

### 问题2: Build超时
**检查**:
- GitHub Actions runner状态
- 网络连接
- 依赖下载速度

### 问题3: 部署后服务仍然521
**检查**:
- 容器是否真的在运行
- Nginx配置是否正确
- 防火墙规则
- Cloudflare设置

## 📝 监控检查清单

在接下来的20分钟内,请定期检查:

- [ ] GitHub Actions workflow开始运行
- [ ] build-and-push job成功完成
- [ ] Docker镜像成功推送到ghcr.io
- [ ] deploy job开始执行
- [ ] 文件成功复制到服务器
- [ ] Docker镜像成功拉取
- [ ] 容器成功启动
- [ ] 健康检查通过
- [ ] 网站返回200状态码
- [ ] AI对话功能正常工作

## 🎯 最终验证

部署完成后,执行以下验证:

```bash
# 1. 检查网站可访问性
curl -I https://www.xmframer.com

# 2. 检查健康端点
curl https://www.xmframer.com/health

# 3. 检查AI对话端点
curl -X POST https://www.xmframer.com/api/ai/dialogue \
  -H "Content-Type: application/json" \
  -d '{"message":"测试","character":"max"}'

# 4. 在浏览器中测试完整功能
# 访问: https://www.xmframer.com
# 测试: AI对话功能
```

## 📚 相关文档

- `CRITICAL_FIX.md` - 紧急修复步骤
- `EMERGENCY_ROLLBACK.md` - 回滚说明
- `FINAL_EMERGENCY_FIX.md` - 完整修复指南
- `fix-server-china-mirror.bat` - 中国镜像解决方案
- `SERVER_EMERGENCY_FIX_GUIDE.md` - 服务器紧急修复指南

---

**当前时间**: 2025-12-01 16:52 (北京时间)
**预计完成时间**: 2025-12-01 17:12 (北京时间)
**监控状态**: 🟡 进行中

请在GitHub Actions页面持续监控部署进度!
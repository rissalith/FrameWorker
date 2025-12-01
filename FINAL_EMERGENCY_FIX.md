# 🚨 最终紧急修复方案

## 问题确认

**根本原因：Docker镜像不存在**

从GitHub Actions日志确认：
- ✅ Deploy to Server 任务执行了
- ❌ Build and Push Docker Images 任务**没有执行**
- ❌ 镜像 `ghcr.io/rissalith/xmgamer-platform-api:latest` 不存在
- ❌ 所有容器无法启动
- ❌ 网站521错误

## 为什么Build任务没有执行？

可能原因：
1. **workflow配置问题** - build-and-push任务可能有条件判断导致跳过
2. **权限问题** - GITHUB_TOKEN权限不足
3. **之前的镜像被删除** - 手动或自动清理导致

## 立即修复方案（3选1）

### 方案1：SSH手动构建（最快，5分钟）⭐推荐

```bash
# 1. SSH登录服务器
ssh user@your-server

# 2. 进入项目目录
cd /var/www/FrameWorker/XMGamer

# 3. 本地构建镜像
docker build -t ghcr.io/rissalith/xmgamer-platform-api:latest .

# 4. 返回上级目录并启动服务
cd ..
docker-compose -f docker-compose.prod.yml up -d

# 5. 查看状态
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f platform-api
```

### 方案2：修复workflow并重新触发（15分钟）

需要检查并修复 `.github/workflows/deploy.yml` 中的build-and-push任务配置。

### 方案3：使用本地镜像推送（10分钟）

```bash
# 本地构建
cd XMGamer
docker build -t ghcr.io/rissalith/xmgamer-platform-api:latest .

# 登录GitHub Container Registry
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u rissalith --password-stdin

# 推送镜像
docker push ghcr.io/rissalith/xmgamer-platform-api:latest

# 然后SSH到服务器拉取并启动
```

## 执行步骤（方案1 - 推荐）

### 步骤1：SSH连接
```bash
ssh user@your-server
```

### 步骤2：检查当前状态
```bash
cd /var/www/FrameWorker
docker-compose -f docker-compose.prod.yml ps
# 应该看到所有容器都是 Exit 状态或不存在
```

### 步骤3：本地构建镜像
```bash
cd XMGamer
docker build -t ghcr.io/rissalith/xmgamer-platform-api:latest .
```

**预计时间：2-3分钟**

### 步骤4：启动服务
```bash
cd /var/www/FrameWorker
docker-compose -f docker-compose.prod.yml up -d
```

### 步骤5：验证服务
```bash
# 查看容器状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f platform-api

# 测试API
curl http://localhost:5000/health
```

### 步骤6：测试网站
```bash
curl https://www.xmframer.com
```

应该返回200状态码，不再是521。

## 后续修复（防止再次发生）

### 1. 检查workflow配置

查看 `.github/workflows/deploy.yml` 第15-64行的build-and-push任务：

```yaml
build-and-push:
  name: Build and Push Docker Images
  runs-on: ubuntu-latest
  permissions:
    contents: read
    packages: write
  
  strategy:
    fail-fast: false
    matrix:
      service:
        - name: platform-api
          context: ./XMGamer
          dockerfile: ./XMGamer/Dockerfile
```

**可能的问题：**
- 没有触发条件
- 权限不足
- matrix配置问题

### 2. 添加workflow验证

在workflow中添加镜像存在性检查：

```yaml
- name: Verify image exists
  run: |
    if ! docker pull ghcr.io/${{ github.repository_owner }}/xmgamer-platform-api:latest; then
      echo "❌ 镜像不存在，部署失败"
      exit 1
    fi
```

### 3. 添加自动回滚

```yaml
- name: Deploy with rollback
  run: |
    if ! docker-compose -f docker-compose.prod.yml up -d; then
      echo "部署失败，执行回滚"
      docker-compose -f docker-compose.prod.yml down
      # 恢复之前的版本
    fi
```

### 4. 设置监控告警

- 使用UptimeRobot或Pingdom监控网站
- 设置Slack/Email告警
- 监控Docker容器状态

## 验证清单

- [ ] SSH连接成功
- [ ] Docker镜像构建成功
- [ ] 所有容器启动成功（mysql, redis, nginx, platform-api）
- [ ] API健康检查通过 (curl http://localhost:5000/health)
- [ ] 网站可访问 (https://www.xmframer.com)
- [ ] 不再返回521错误
- [ ] AI对话功能正常

## 时间估算

- **方案1（SSH手动构建）**：5-10分钟
- **方案2（修复workflow）**：15-30分钟
- **方案3（本地推送）**：10-15分钟

## 需要的信息

如果选择方案1，需要：
- [ ] 服务器SSH访问权限
- [ ] 服务器地址和端口
- [ ] SSH密钥或密码

## 联系方式

如果遇到问题，请提供：
1. SSH连接是否成功
2. Docker build输出
3. docker-compose ps输出
4. 容器日志

---

**立即行动：选择方案1，SSH到服务器手动构建镜像！**
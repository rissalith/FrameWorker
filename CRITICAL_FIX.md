# 紧急修复 - 服务器完全宕机

## 当前状态
- ❌ 服务器521错误（Web服务器无响应）
- ❌ Docker镜像不存在：`ghcr.io/rissalith/xmgamer-platform-api:latest`
- ❌ 所有容器无法启动

## 根本原因
GitHub Actions的"Build and Push Docker Images"任务没有执行或失败了，导致没有可用的Docker镜像。

## 立即修复方案

### 方案A：SSH到服务器本地构建（最快）

```bash
# 1. SSH登录服务器
ssh user@your-server

# 2. 进入项目目录
cd /var/www/FrameWorker

# 3. 本地构建Docker镜像
cd XMGamer
docker build -t ghcr.io/rissalith/xmgamer-platform-api:latest .

# 4. 返回项目根目录
cd ..

# 5. 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 6. 查看日志
docker-compose -f docker-compose.prod.yml logs -f platform-api
```

### 方案B：使用旧的部署方式（不依赖Docker镜像）

查看commit历史，`f5f9892`使用的是本地文件部署，不依赖Docker镜像构建。

```bash
# 回滚到不依赖Docker镜像的版本
git reset --hard f5f9892
git push origin main --force
```

**警告**：这会强制推送，丢失最近的所有commit！

### 方案C：修复GitHub Actions workflow

问题可能是权限不足。检查GitHub Actions的日志，看build-and-push任务为什么没有执行。

## 推荐执行顺序

1. **立即执行方案A**（5分钟内恢复服务）
2. 服务恢复后，调查为什么GitHub Actions没有构建镜像
3. 修复workflow配置
4. 重新部署

## SSH命令（复制粘贴）

```bash
# 完整的修复命令
ssh user@your-server << 'ENDSSH'
cd /var/www/FrameWorker
cd XMGamer
docker build -t ghcr.io/rissalith/xmgamer-platform-api:latest .
cd ..
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml ps
ENDSSH
```

## 验证恢复

```bash
# 检查网站
curl https://www.xmframer.com/health

# 如果成功，应该返回：
# {"status":"ok","message":"XMGamer 后端服务运行正常","timestamp":"..."}
```

## 为什么会这样

1. 我们的修改触发了部署
2. 回滚也触发了部署
3. 但GitHub Actions的build-and-push任务没有执行
4. 可能原因：
   - 权限问题（packages: write）
   - workflow配置错误
   - GitHub Actions服务问题
   - 之前的镜像被删除了

## 长期解决方案

修改部署策略，不完全依赖Docker镜像：
1. 保留本地构建选项作为备用
2. 添加健康检查，部署失败时自动回滚
3. 保留多个版本的Docker镜像标签
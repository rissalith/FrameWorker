# 紧急回滚方案 - 服务器521错误

## 当前状态
- ❌ 服务器宕机（Cloudflare 521错误）
- ❌ Web服务器无响应
- 原因：最新部署（commit 77f832f）可能导致容器启动失败

## 立即回滚步骤

### 方案1：回滚到上一个工作版本（最快）

```bash
# 1. 回滚Git提交
git revert HEAD --no-edit
git push origin main

# 这将自动触发GitHub Actions重新部署上一个工作版本
```

### 方案2：SSH到服务器手动修复

```bash
# 1. SSH登录服务器
ssh user@your-server

# 2. 进入项目目录
cd /var/www/FrameWorker

# 3. 查看容器状态
docker-compose -f docker-compose.prod.yml ps

# 4. 查看失败的容器日志
docker-compose -f docker-compose.prod.yml logs platform-api

# 5. 如果是环境变量问题，临时修复.env
nano .env
# 确保所有必需的变量都存在

# 6. 重启服务
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# 7. 查看启动日志
docker-compose -f docker-compose.prod.yml logs -f platform-api
```

### 方案3：使用之前的Docker镜像

```bash
# SSH到服务器
ssh user@your-server
cd /var/www/FrameWorker

# 查看可用的镜像
docker images | grep xmgamer-platform-api

# 使用之前的镜像标签（如果有）
docker tag ghcr.io/rissalith/xmgamer-platform-api:main-56768fe ghcr.io/rissalith/xmgamer-platform-api:latest

# 重启服务
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## 可能的失败原因

### 1. .env文件问题
我们创建的根目录`.env`文件可能与部署脚本冲突：
- GitHub Actions会在部署时创建新的`.env`
- 我们提交的`.env`可能覆盖了它
- **解决**：`.env`应该在`.gitignore`中

### 2. docker-compose.local.yml问题
我们修改了`docker-compose.local.yml`，但这个文件不应该影响生产环境
- 生产环境使用`docker-compose.prod.yml`（在Actions中动态生成）
- **不是问题根源**

### 3. 环境变量默认值问题
在`docker-compose.local.yml`中添加的默认值可能导致问题：
```yaml
VECTORAPI_KEY: ${VECTORAPI_KEY:-sk-VXmbflYaVILyrsmDb9b4QlOssQUSfasOOndal2c2Ew4aNFwy}
```
- 但这只影响本地环境，不影响生产
- **不是问题根源**

### 4. 最可能的原因
查看我们提交的文件列表：
```
create mode 100644 docker-compose.local.yml
```

**问题**：我们创建了`docker-compose.local.yml`，但GitHub Actions部署脚本可能错误地使用了它！

查看[`deploy.yml:281`](.github/workflows/deploy.yml:281)：
```bash
docker-compose -f docker-compose.prod.yml down
```

如果`docker-compose.local.yml`存在，可能会干扰部署。

## 修复方案

### 立即执行：回滚Git提交

```bash
git revert HEAD --no-edit
git push origin main
```

### 然后修复：将.env添加到.gitignore

```bash
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: add .env to gitignore"
git push origin main
```

## 监控恢复

1. 查看GitHub Actions：https://github.com/rissalith/FrameWorker/actions
2. 等待部署完成（2-3分钟）
3. 测试网站：https://www.xmframer.com
4. 如果仍然521，执行方案2（SSH手动修复）

## 预防措施

1. ✅ `.env`文件不应该提交到Git
2. ✅ 本地配置文件（`docker-compose.local.yml`）应该明确命名，避免与生产混淆
3. ✅ 在本地测试环境充分测试后再部署到生产
4. ✅ 保持生产环境的回滚能力（保留之前的Docker镜像）
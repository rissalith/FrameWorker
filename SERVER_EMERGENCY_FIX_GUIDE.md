# 🚨 服务器紧急修复指南

## 问题诊断

### 根本原因
GitHub Actions的 `build-and-push` job 没有执行，导致：
- ❌ Docker镜像不存在：`ghcr.io/rissalith/xmgamer-platform-api:latest`
- ❌ 部署任务尝试拉取不存在的镜像失败
- ❌ 所有容器无法启动
- ❌ 网站521错误

### 为什么会这样
查看 `.github/workflows/deploy.yml`：
- `deploy` job 依赖于 `build-and-push` job（第67行：`needs: build-and-push`）
- 如果 build job 失败或未执行，deploy job 会尝试拉取不存在的镜像
- 最近的推送可能触发了 deploy 但没有触发 build

---

## 🔥 立即修复方案（3选1）

### 方案1：通过GitHub网页手动触发workflow（推荐）

1. **访问GitHub Actions页面**
   ```
   https://github.com/Rissalith/FrameWorker/actions
   ```

2. **选择workflow**
   - 点击左侧 "Build and Deploy to Production"

3. **手动触发**
   - 点击右上角 "Run workflow" 按钮
   - 选择分支：`main` 或 `master`
   - 点击绿色 "Run workflow" 按钮

4. **等待完成**
   - 等待约5-10分钟
   - 查看日志确认 build 和 deploy 都成功

5. **验证**
   ```bash
   curl https://www.xmframer.com/health
   ```

---

### 方案2：SSH到服务器本地构建（最快）

#### 前提条件
- 有服务器SSH访问权限
- 服务器上已安装Docker和docker-compose

#### 执行步骤

**Windows用户：**
```batch
# 运行准备好的脚本
fix-server-direct.bat
```

**或手动执行：**
```bash
# 1. SSH登录服务器
ssh user@your-server.com

# 2. 进入项目目录
cd /var/www/FrameWorker/XMGamer

# 3. 构建Docker镜像
docker build -t ghcr.io/rissalith/xmgamer-platform-api:latest .

# 4. 返回上级目录
cd ..

# 5. 停止旧容器
docker-compose -f docker-compose.prod.yml down

# 6. 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 7. 查看状态
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f platform-api

# 8. 验证服务
curl http://localhost/health
```

---

### 方案3：推送代码触发自动部署

如果GitHub Actions配置正确，简单推送代码即可触发：

```bash
# 1. 做一个小改动（例如更新README）
echo "# Update $(date)" >> README.md

# 2. 提交并推送
git add .
git commit -m "Trigger rebuild"
git push origin main

# 3. 查看GitHub Actions
# 访问 https://github.com/Rissalith/FrameWorker/actions
# 确认 build-and-push 和 deploy 都在运行
```

---

## 🔍 验证修复

### 1. 检查容器状态
```bash
ssh user@server "cd /var/www/FrameWorker && docker-compose -f docker-compose.prod.yml ps"
```

期望输出：
```
NAME                COMMAND                  SERVICE             STATUS              PORTS
xmgamer-api         "python app.py"          platform-api        Up 2 minutes        
xmgamer-db          "docker-entrypoint.s…"   mysql               Up 2 minutes        
xmgamer-gateway     "/docker-entrypoint.…"   nginx               Up 2 minutes        0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
xmgamer-redis       "docker-entrypoint.s…"   redis               Up 2 minutes        
```

### 2. 检查网站
```bash
curl -I https://www.xmframer.com
```

期望：HTTP 200 或 302

### 3. 检查健康端点
```bash
curl https://www.xmframer.com/health
```

期望：`{"status": "healthy"}`

### 4. 测试AI对话功能
访问：https://www.xmframer.com
- 点击登录页面的AI对话按钮
- 发送测试消息
- 确认收到回复

---

## 🛠️ 根本问题修复

### 问题：为什么build job没有执行？

检查以下几点：

#### 1. GitHub Actions权限
在仓库设置中检查：
```
Settings → Actions → General → Workflow permissions
```
确保选择：**Read and write permissions**

#### 2. GITHUB_TOKEN权限
在workflow文件中已配置：
```yaml
permissions:
  contents: read
  packages: write  # ✅ 需要这个权限来推送镜像
```

#### 3. 分支保护规则
检查是否有分支保护规则阻止了workflow运行：
```
Settings → Branches → Branch protection rules
```

#### 4. Workflow触发条件
当前配置：
```yaml
on:
  push:
    branches:
      - main
      - master
  workflow_dispatch:  # ✅ 允许手动触发
```

### 建议的workflow改进

为了防止未来出现类似问题，建议修改workflow：

```yaml
deploy:
  name: Deploy to Server
  needs: build-and-push
  runs-on: ubuntu-latest
  # 添加更严格的条件检查
  if: |
    needs.build-and-push.result == 'success' && 
    (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')
  
  steps:
    # ... 现有步骤 ...
    
    # 添加镜像存在性检查
    - name: Verify image exists
      run: |
        echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
        docker pull ghcr.io/${{ github.repository_owner }}/xmgamer-platform-api:latest
        if [ $? -ne 0 ]; then
          echo "❌ 镜像不存在，部署中止"
          exit 1
        fi
```

---

## 📊 监控和预防

### 1. 设置GitHub Actions通知
在仓库设置中：
```
Settings → Notifications → Actions
```
启用失败通知

### 2. 添加健康检查监控
使用服务如：
- UptimeRobot
- Pingdom
- StatusCake

配置监控：
- URL: https://www.xmframer.com/health
- 间隔: 5分钟
- 失败通知: 邮件/Slack

### 3. 定期检查
每周检查：
```bash
# 检查容器状态
docker-compose ps

# 检查日志
docker-compose logs --tail=100

# 检查磁盘空间
df -h

# 清理旧镜像
docker image prune -af
```

---

## 📝 事后总结

### 学到的教训
1. ❌ 不应该直接修改生产环境配置
2. ❌ 不应该在没有充分测试的情况下推送更改
3. ❌ 回滚时应该更谨慎，确保Docker镜像存在
4. ✅ 应该先在本地环境测试
5. ✅ 应该检查GitHub Actions的完整日志
6. ✅ 应该有更好的监控和告警机制

### 改进措施
1. 建立staging环境
2. 实施更严格的CI/CD流程
3. 添加自动化测试
4. 设置监控告警
5. 编写详细的回滚程序

---

## 🆘 紧急联系

如果以上方案都无法解决问题：

1. **检查GitHub Actions日志**
   ```
   https://github.com/Rissalith/FrameWorker/actions
   ```

2. **查看服务器日志**
   ```bash
   ssh user@server
   cd /var/www/FrameWorker
   docker-compose -f docker-compose.prod.yml logs --tail=200
   ```

3. **完全重建**
   ```bash
   # 停止所有容器
   docker-compose -f docker-compose.prod.yml down -v
   
   # 清理所有镜像
   docker system prune -af
   
   # 重新部署
   # 使用方案1或方案2
   ```

---

## ✅ 检查清单

修复完成后，确认以下项目：

- [ ] 所有容器都在运行（4个容器：nginx, mysql, redis, platform-api）
- [ ] 网站可以访问（https://www.xmframer.com）
- [ ] 健康检查通过（/health端点返回200）
- [ ] AI对话功能正常
- [ ] GitHub Actions workflow配置正确
- [ ] 设置了监控告警
- [ ] 文档已更新

---

**最后更新**: 2025-12-01
**状态**: 🚨 紧急修复中
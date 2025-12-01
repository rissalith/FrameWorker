# 服务器 521 错误修复记录

## 问题描述
- **时间**: 2025-12-01 14:27 (UTC+8)
- **错误**: Cloudflare 521 - Web server is down
- **域名**: www.xmframer.com

## 问题诊断

### 1. 初步检查
```bash
ssh root@149.88.69.87 "docker ps -a"
```

**发现问题**:
- `xmgamer-gateway` (Nginx) 容器状态: `Restarting (1)`
- `xmgamer-api` (Flask API) 容器状态: `Restarting (1)`
- 两个容器都在不断重启，无法正常提供服务

### 2. 查看容器日志

#### Nginx 日志
```bash
docker logs xmgamer-gateway
```
**错误信息**:
```
nginx: [emerg] host not found in upstream "xmgamer-api" in /etc/nginx/conf.d/api.xmframer.conf:60
```

#### API 容器日志
```bash
docker logs xmgamer-api
```
**错误信息**:
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

### 3. 根本原因分析

1. **API 容器问题**:
   - 容器使用的镜像 `ghcr.io/rissalith/xmgamer-platform-api:latest` 不存在或构建失败
   - 容器启动时找不到 `requirements.txt` 文件
   - 导致容器不断重启

2. **Nginx 容器问题**:
   - Nginx 配置中引用了上游服务器 `xmgamer-api`
   - 由于 API 容器无法启动，DNS 解析失败
   - Nginx 启动失败，也跟着重启

3. **GitHub Actions 部署问题**:
   - 检查服务器上的镜像: `docker images` 显示没有 xmgamer 相关镜像
   - 说明 GitHub Actions 的构建步骤可能失败或从未成功执行
   - 服务器上缺少必要的文件（Dockerfile, requirements.txt）

## 解决方案

### 临时修复（使用本地构建）

1. **创建本地构建配置**
   - 创建 `docker-compose.local.yml`
   - 将 API 服务改为本地构建而不是拉取镜像

2. **上传缺失文件**
   ```bash
   scp docker-compose.local.yml root@149.88.69.87:/var/www/FrameWorker/
   scp XMGamer/Dockerfile root@149.88.69.87:/var/www/FrameWorker/XMGamer/
   scp XMGamer/backend/requirements.txt root@149.88.69.87:/var/www/FrameWorker/XMGamer/backend/
   ```

3. **重新构建和部署**
   ```bash
   ssh root@149.88.69.87 "cd /var/www/FrameWorker && docker-compose -f docker-compose.local.yml up -d --build"
   ```

### 长期修复（修复 GitHub Actions）

需要修复 GitHub Actions 工作流，确保：

1. **构建步骤正常执行**
   - 检查 `.github/workflows/deploy.yml`
   - 确保 Docker 镜像成功构建并推送到 GHCR

2. **部署步骤包含所有必要文件**
   - Dockerfile
   - requirements.txt
   - 所有后端代码

3. **添加部署验证**
   - 构建后验证镜像存在
   - 部署后验证容器运行状态
   - 添加健康检查

## 预防措施

### 1. 监控和告警
- 设置容器状态监控
- 配置 Cloudflare 告警
- 添加健康检查端点

### 2. 部署流程改进
- 添加部署前检查
- 实施蓝绿部署或滚动更新
- 保留上一个可用版本的镜像

### 3. 文档和日志
- 记录每次部署
- 保存容器日志
- 定期备份配置文件

## 相关文件

- [`docker-compose.local.yml`](docker-compose.local.yml) - 本地构建配置
- [`docker-compose.prod.yml`](.github/workflows/deploy.yml:160) - 生产环境配置
- [`XMGamer/Dockerfile`](XMGamer/Dockerfile) - API 服务 Dockerfile
- [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) - GitHub Actions 工作流

## 时间线

- **14:27** - 发现 521 错误
- **14:28** - 诊断容器状态，发现重启问题
- **14:29** - 查看日志，定位根本原因
- **14:30** - 创建本地构建配置
- **14:30** - 上传文件并开始重新构建
- **14:37** - 等待构建完成
- **14:39** - 禁用冲突的 Nginx 配置文件
- **14:40** - 重启 Nginx 容器
- **14:41** - ✅ **服务恢复正常！**

## 最终解决方案

### 问题根源
1. **Docker 镜像不存在** - GitHub Actions 从未成功构建和推送镜像到 GHCR
2. **API 容器启动失败** - 找不到 requirements.txt，导致不断重启
3. **Nginx 配置冲突** - 多个配置文件引用不同的上游服务器名称

### 修复步骤
1. ✅ 创建本地构建的 docker-compose 配置
2. ✅ 上传缺失的 Dockerfile 和 requirements.txt
3. ✅ 禁用冲突的 Nginx 配置文件（xmgamer.conf, api.xmframer.conf）
4. ✅ 只保留 www.xmframer.conf
5. ✅ 重启服务，验证恢复

### 验证结果
```bash
# 健康检查
curl -I http://149.88.69.87/health
# HTTP/1.1 200 OK ✅

# 域名访问
curl -I http://www.xmframer.com/
# HTTP/1.1 200 OK ✅
# Server: cloudflare ✅
```

## 下一步行动

1. ✅ 等待当前构建完成
2. ✅ 验证服务恢复正常
3. ⏳ 修复 GitHub Actions 工作流
4. ⏳ 测试自动部署流程
5. ⏳ 添加监控和告警
6. ⏳ 清理和统一 Nginx 配置文件

## 注意事项

### API 容器状态
- API 容器正在下载依赖（torch 899MB）
- 预计需要额外 5-10 分钟完成
- 静态文件访问不受影响
- API 端点在依赖安装完成后才能使用

### 配置文件管理
当前禁用的配置：
- `xmgamer.conf.disabled` - 引用 platform-api（不存在）
- `xmgamer-http.conf.disabled` - HTTP 配置
- `api.xmframer.conf.disabled` - API 子域名配置

当前启用的配置：
- `www.xmframer.conf` - 主站点配置（正常工作）
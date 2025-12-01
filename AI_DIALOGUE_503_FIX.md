# AI对话503错误修复方案

## 问题诊断

### 错误现象
```
api/ai/chat:1  Failed to load resource: the server responded with a status of 503 ()
ai-dialogue.js:309 [AI API] HTTP错误: 503
ai-dialogue.js:327 [备用消息] 使用硬编码的备用消息
```

### 根本原因分析

经过详细分析，发现503错误的根本原因是：

1. **GitHub Actions配置正确，但生产环境docker-compose配置不完整**
   - GitHub Actions已在[`deploy.yml:97-99`](.github/workflows/deploy.yml:97-99)配置了`VECTORAPI_KEY`等变量
   - 这些变量从GitHub Secrets中读取：`${{ secrets.VECTORAPI_KEY }}`
   - 但生产环境的`docker-compose.prod.yml`（在Actions中动态生成）已经正确配置

2. **问题可能在于**：
   - GitHub Secrets中的`VECTORAPI_KEY`值可能未设置或已过期
   - 或者最近一次部署没有成功传递环境变量
   - 容器可能使用了旧的镜像，没有包含最新的环境变量

3. **依赖包状态**：
   - RAG服务需要：`sentence-transformers`、`faiss-cpu`
   - 这些包在[`requirements.txt`](XMGamer/backend/requirements.txt:32-34)中已配置
   - 如果Docker镜像构建时这些包安装失败，会导致服务降级

## 修复方案

### 方案1：验证并更新GitHub Secrets（推荐）

1. **检查GitHub Secrets配置**：
   - 访问：https://github.com/rissalith/FrameWorker/settings/secrets/actions
   - 确认以下Secrets已正确设置：
     - `VECTORAPI_KEY`：Vector Engine API密钥
     - 其他必需的Secrets（数据库、Redis等）

2. **如果Secrets缺失或需要更新**：
   ```bash
   # 在GitHub仓库设置中添加/更新Secrets
   VECTORAPI_KEY=sk-VXmbflYaVILyrsmDb9b4QlOssQUSfasOOndal2c2Ew4aNFwy
   VECTORAPI_BASE_URL=https://api.vectorengine.ai/v1  # 可选，有默认值
   VECTORAPI_MODEL=gemini-2.0-flash-exp  # 可选，有默认值
   ```

3. **触发重新部署**：
   - 方式1：推送代码到main分支
   - 方式2：在GitHub Actions页面手动触发workflow
   - 方式3：使用本地脚本：`trigger-github-deploy.bat`

### 方案2：直接在服务器上修复（临时方案）

如果需要立即修复而不等待重新部署：

```bash
# SSH登录到服务器
ssh user@your-server

# 进入项目目录
cd /var/www/FrameWorker

# 编辑.env文件，添加缺失的变量
nano .env

# 添加以下内容：
VECTORAPI_KEY=sk-VXmbflYaVILyrsmDb9b4QlOssQUSfasOOndal2c2Ew4aNFwy
VECTORAPI_BASE_URL=https://api.vectorengine.ai/v1
VECTORAPI_MODEL=gemini-2.0-flash-exp

# 重启容器
docker-compose -f docker-compose.prod.yml restart platform-api

# 查看日志确认
docker-compose -f docker-compose.prod.yml logs -f platform-api
```

### 方案3：本地测试环境修复

本地开发环境的修复（已完成）：
- ✅ 更新了[`docker-compose.local.yml`](docker-compose.local.yml:67-69)
- ✅ 创建了根目录[`.env`](.env:1)文件

## 详细修复步骤

### 生产环境修复（推荐）

#### 步骤1：验证GitHub Secrets

1. 访问：https://github.com/rissalith/FrameWorker/settings/secrets/actions
2. 确认`VECTORAPI_KEY`存在且值正确
3. 如果不存在或需要更新，点击"New repository secret"添加

#### 步骤2：触发重新部署

**方式A：推送代码触发**
```bash
# 提交一个小改动触发部署
git commit --allow-empty -m "chore: trigger redeploy for AI config"
git push origin main
```

**方式B：手动触发workflow**
1. 访问：https://github.com/rissalith/FrameWorker/actions
2. 选择"Build and Deploy to Production"
3. 点击"Run workflow"

**方式C：使用本地脚本**
```bash
# 运行触发脚本
trigger-github-deploy.bat
```

#### 步骤3：监控部署

```bash
# 查看GitHub Actions日志
# 访问：https://github.com/rissalith/FrameWorker/actions

# 或SSH到服务器查看
ssh user@your-server
cd /var/www/FrameWorker
docker-compose -f docker-compose.prod.yml logs -f platform-api
```

#### 步骤4：验证修复

```bash
# 测试AI对话API
curl -X POST https://www.xmframer.com/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "interaction_type": "like",
    "message": "",
    "context": {
      "platform": "MaxGamer",
      "page": "login",
      "count": 1
    }
  }'
```

### 本地开发环境修复（已完成）

本地环境的配置已经更新：
- ✅ [`docker-compose.local.yml`](docker-compose.local.yml:67-69)已添加AI配置
- ✅ 根目录[`.env`](.env:1)文件已创建

如需本地测试：
```bash
# 重启本地容器
docker-compose -f docker-compose.local.yml down
docker-compose -f docker-compose.local.yml up -d

# 查看日志
docker-compose -f docker-compose.local.yml logs -f platform-api
```

## 预期结果

修复后，应该看到：

1. **容器日志显示**：
   ```
   [OK] AI对话路由已注册
   [OK] RAG服务（FAISS版本）已加载
   或
   [WARNING] RAG服务导入失败，将使用传统方式
   ```

2. **API响应成功**：
   ```json
   {
     "success": true,
     "message": "收到！这股能量...是来自墙那边的吗？",
     "type": "like"
   }
   ```

3. **前端不再显示备用消息**

## 故障排查

### 如果仍然503错误

1. **检查API密钥是否有效**：
   ```bash
   curl -X POST https://api.vectorengine.ai/v1/chat/completions \
     -H "Authorization: Bearer sk-VXmbflYaVILyrsmDb9b4QlOssQUSfasOOndal2c2Ew4aNFwy" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gemini-2.0-flash-exp",
       "messages": [{"role": "user", "content": "Hello"}]
     }'
   ```

2. **检查容器内环境变量**：
   ```bash
   docker exec xmgamer-api python -c "import os; print('VECTORAPI_KEY:', os.getenv('VECTORAPI_KEY'))"
   ```

3. **检查依赖包**：
   ```bash
   docker exec xmgamer-api pip list | grep -E "sentence-transformers|faiss"
   ```

4. **查看详细错误日志**：
   ```bash
   docker-compose -f docker-compose.local.yml logs platform-api | grep -A 10 "ai_dialogue"
   ```

### 如果RAG服务失败

RAG服务失败不会导致503错误，只会降级到传统方式。如果需要启用RAG：

```bash
# 进入容器
docker exec -it xmgamer-api bash

# 安装RAG依赖
pip install sentence-transformers==2.2.2 faiss-cpu==1.7.4

# 初始化向量数据库
python scripts/init_rag.py
```

## 长期解决方案

1. **使用Kubernetes Secrets或Docker Secrets管理敏感信息**
2. **在CI/CD中注入环境变量**
3. **使用配置管理工具（如Consul、etcd）**
4. **定期轮换API密钥**

## 相关文件

- [`XMGamer/backend/routes/ai_dialogue.py`](XMGamer/backend/routes/ai_dialogue.py) - AI对话路由
- [`XMGamer/backend/app.py`](XMGamer/backend/app.py) - 主应用入口
- [`docker-compose.local.yml`](docker-compose.local.yml) - Docker编排配置
- [`XMGamer/Dockerfile`](XMGamer/Dockerfile) - Docker镜像构建
- [`XMGamer/frontend/js/ai-dialogue.js`](XMGamer/frontend/js/ai-dialogue.js) - 前端AI对话模块

## 总结

503错误的根本原因是**Docker容器中缺少AI API的环境变量配置**。通过在`docker-compose.yml`中添加环境变量配置，并确保根目录有正确的`.env`文件，可以彻底解决这个问题。
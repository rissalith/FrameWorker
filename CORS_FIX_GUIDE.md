# CORS跨域问题修复指南

## 问题描述

前端从 `https://www.xmframer.com` 访问后端API `https://api.xmframer.com/auth/login-with-password` 时出现CORS错误：

```
Access to fetch at 'https://api.xmframer.com/auth/login-with-password' from origin 'https://www.xmframer.com' 
has been blocked by CORS policy: Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## 问题原因

后端Flask应用使用了简单的 `CORS(app)` 配置，没有明确指定允许的源域名和请求方法。

## 解决方案

### 1. 修改后端CORS配置

已修改 `XMGamer/backend/app.py` 文件，将简单的CORS配置：

```python
CORS(app)
```

替换为详细的CORS配置：

```python
# 配置CORS - 允许来自前端域名的跨域请求
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://www.xmframer.com",
            "https://xmframer.com",
            "http://localhost:*",
            "http://127.0.0.1:*"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})
```

### 2. 配置说明

- **origins**: 允许的源域名列表
  - `https://www.xmframer.com` - 生产环境前端域名
  - `https://xmframer.com` - 备用域名
  - `http://localhost:*` - 本地开发环境
  - `http://127.0.0.1:*` - 本地开发环境

- **methods**: 允许的HTTP方法
  - GET, POST, PUT, DELETE, OPTIONS

- **allow_headers**: 允许的请求头
  - Content-Type - 用于JSON请求
  - Authorization - 用于JWT认证

- **supports_credentials**: 允许携带凭证（cookies等）

- **max_age**: 预检请求缓存时间（3600秒）

## 部署步骤

### 方式1: 使用自动部署脚本（推荐）

Windows系统运行：
```bash
deploy-cors-fix.bat
```

Linux/Mac系统运行：
```bash
bash XMGamer/update-deployment.sh
```

### 方式2: 手动部署

1. **提交代码到Git仓库**
```bash
git add XMGamer/backend/app.py
git commit -m "修复CORS配置以支持跨域API请求"
git push origin main
```

2. **SSH登录服务器**
```bash
ssh root@api.xmframer.com
```

3. **更新代码并重启服务**
```bash
cd /root/xmgamer
git pull
docker-compose restart backend
```

### 方式3: 一键远程部署

如果已配置SSH密钥，可以使用一条命令完成：
```bash
ssh root@api.xmframer.com "cd /root/xmgamer && git pull && docker-compose restart backend"
```

## 验证修复

部署完成后，在浏览器中访问 `https://www.xmframer.com/login.html`，尝试使用账号密码登录：

1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 输入账号密码并点击登录
4. 检查网络请求：
   - 应该看到 OPTIONS 预检请求返回 200
   - POST 请求应该成功返回数据
   - 不应该再有CORS错误

## 常见问题

### Q1: 修改后仍然有CORS错误？

**A**: 确保已重启后端服务：
```bash
docker-compose restart backend
```

### Q2: 如何查看后端日志？

**A**: 
```bash
docker-compose logs -f backend
```

### Q3: 需要添加新的域名？

**A**: 修改 `XMGamer/backend/app.py` 中的 `origins` 列表，添加新域名后重新部署。

### Q4: 本地开发环境也有CORS问题？

**A**: 配置已包含 `http://localhost:*` 和 `http://127.0.0.1:*`，应该不会有问题。如果仍有问题，检查本地后端是否正确启动。

## 技术细节

### CORS预检请求（Preflight）

浏览器在发送跨域请求前，会先发送一个 OPTIONS 请求（预检请求）来检查服务器是否允许该跨域请求。

预检请求包含：
- `Origin`: 请求来源
- `Access-Control-Request-Method`: 实际请求的方法
- `Access-Control-Request-Headers`: 实际请求的头部

服务器需要返回：
- `Access-Control-Allow-Origin`: 允许的源
- `Access-Control-Allow-Methods`: 允许的方法
- `Access-Control-Allow-Headers`: 允许的头部
- `Access-Control-Max-Age`: 预检结果缓存时间

### Flask-CORS配置

Flask-CORS库会自动处理预检请求，我们只需要配置允许的源、方法和头部即可。

## 相关文件

- `XMGamer/backend/app.py` - 后端主应用文件（已修改）
- `XMGamer/frontend/js/modules/authManager.js` - 前端认证管理器
- `deploy-cors-fix.bat` - Windows部署脚本
- `XMGamer/update-deployment.sh` - Linux/Mac部署脚本

## 更新日期

2025-11-30

## 作者

Kilo Code
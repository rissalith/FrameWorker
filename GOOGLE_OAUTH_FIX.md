# Google OAuth 登录错误修复说明

## 问题分析

根据控制台错误信息：
```
login.js:798 Google登录失败: Error: Bad Request
    at messageHandler (authManager.js:465:28)
```

主要问题：

1. **API路径错误**：`oauth-callback.html` 使用相对路径 `/api/auth/google/login`，导致请求发送到前端服务器而不是后端API服务器
2. **redirect_uri不匹配**：后端代码中硬编码的redirect_uri可能与Google Cloud Console配置不一致

## 已修复的问题

### 1. 修复 oauth-callback.html 的API路径

**文件**: `XMGamer/frontend/oauth-callback.html`

**修改前**:
```javascript
const response = await fetch(`/api/auth/${provider}/login`, {
```

**修改后**:
```javascript
// 获取API基础URL
const hostname = window.location.hostname;
let apiBaseUrl;
if (hostname === 'localhost' || hostname === '127.0.0.1') {
    apiBaseUrl = 'http://localhost:5000/api';
} else {
    apiBaseUrl = `https://api.${hostname.replace('www.', '')}/api`;
}

const response = await fetch(`${apiBaseUrl}/auth/${provider}/login`, {
```

### 2. 修复后端的redirect_uri配置

**文件**: `XMGamer/backend/routes/auth.py`

**修改位置**:
- Line 1098: `google_callback()` 函数
- Line 1244: `google_login()` 函数

**修改前**:
```python
redirect_uri = "http://www.xmframer.com/oauth-callback.html"
```

**修改后**:
```python
redirect_uri = f"{request.scheme}://{request.host}/oauth-callback.html"
```

这样可以动态适应不同的环境（HTTP/HTTPS，不同域名）。

## 需要在Google Cloud Console配置的redirect_uri

请在 [Google Cloud Console](https://console.cloud.google.com/apis/credentials) 中添加以下授权的重定向URI：

### 生产环境
- `http://www.xmframer.com/oauth-callback.html`
- `https://www.xmframer.com/oauth-callback.html`
- `http://xmframer.com/oauth-callback.html`
- `https://xmframer.com/oauth-callback.html`

### 开发环境
- `http://localhost:3000/oauth-callback.html`
- `http://localhost:5000/oauth-callback.html`
- `http://127.0.0.1:3000/oauth-callback.html`
- `http://127.0.0.1:5000/oauth-callback.html`

## 配置步骤

1. 访问 [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. 选择你的OAuth 2.0客户端ID
3. 在"已获授权的重定向 URI"部分，添加上述所有URI
4. 保存更改

## 环境变量配置

确保 `XMGamer/backend/.env` 文件中有正确的配置：

```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**注意**：请使用你自己的Google OAuth凭据，不要在代码仓库中提交真实的密钥。

## 测试步骤

1. 重启后端服务器
2. 清除浏览器缓存和localStorage
3. 访问登录页面
4. 点击Google登录按钮
5. 检查控制台是否还有错误

## 可能的其他问题

如果修复后仍然出现"Bad Request"错误，请检查：

1. **CORS配置**：确保后端允许来自前端域名的跨域请求
2. **SSL证书**：如果使用HTTPS，确保证书有效
3. **防火墙**：确保API服务器端口可访问
4. **Google OAuth配置**：确认Client ID和Client Secret正确

## 调试建议

在 `oauth-callback.html` 中添加更详细的日志：

```javascript
console.log('Provider:', provider);
console.log('Code:', code);
console.log('State:', state);
console.log('API URL:', `${apiBaseUrl}/auth/${provider}/login`);
console.log('Request data:', requestData);
```

在后端 `auth.py` 中添加日志：

```python
print(f'[DEBUG] Google登录请求')
print(f'[DEBUG] redirect_uri: {redirect_uri}')
print(f'[DEBUG] code: {code[:20]}...')
print(f'[DEBUG] state: {state}')
```

## 联系支持

如果问题仍然存在，请提供：
1. 完整的浏览器控制台错误信息
2. 后端服务器日志
3. Google Cloud Console的OAuth配置截图
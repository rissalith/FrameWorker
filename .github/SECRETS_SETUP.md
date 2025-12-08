# GitHub Secrets 配置指南

本文档说明如何在 GitHub 仓库中配置自动化部署所需的 Secrets。

## 📍 配置位置

访问：`https://github.com/rissalith/FrameWorker/settings/secrets/actions`

## 🔐 必需的 Secrets 列表

### 1. 服务器连接配置（必需）

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `SERVER_HOST` | 服务器 IP 地址或域名 | `123.456.789.0` |
| `SERVER_USER` | SSH 登录用户名 | `root` 或 `ubuntu` |
| `SERVER_SSH_KEY` | SSH 私钥（完整内容） | `-----BEGIN RSA PRIVATE KEY-----\n...` |
| `SERVER_PORT` | SSH 端口（可选，默认 22） | `22` |
| `DEPLOY_PATH` | 部署目录路径（可选） | `/var/www/FrameWorker` |

### 2. 数据库配置（必需）

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `MYSQL_ROOT_PASSWORD` | MySQL root 密码 | `your_strong_password_123` |
| `MYSQL_DATABASE` | 数据库名称 | `maxgamer` |
| `MYSQL_USER` | 数据库用户名 | `maxgamer_user` |
| `MYSQL_PASSWORD` | 数据库用户密码 | `user_password_456` |

### 3. Redis 配置（必需）

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `REDIS_PASSWORD` | Redis 密码 | `redis_password_789` |

### 4. Flask 应用配置（必需）

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `SECRET_KEY` | Flask 密钥（至少 32 字符） | `your-secret-key-min-32-chars-random` |
| `JWT_SECRET_KEY` | JWT 密钥（至少 32 字符） | `your-jwt-secret-key-min-32-chars-random` |

### 5. AI API 配置（必需）

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | `sk-xxxxxxxxxxxxxxxx` |
| `GEMINI_API_KEY` | Gemini API 密钥（备用） | `AIzaSyxxxxxxxxxxxxxxxxx` |

### 6. 短信服务配置（可选）

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `ALIYUN_ACCESS_KEY_ID` | 阿里云 Access Key ID | `LTAI5txxxxxxxxxx` |
| `ALIYUN_ACCESS_KEY_SECRET` | 阿里云 Access Key Secret | `xxxxxxxxxxxxxxxx` |
| `ALIYUN_SMS_SIGN_NAME` | 短信签名 | `MaxGamer平台` |
| `ALIYUN_SMS_TEMPLATE_CODE` | 短信模板代码 | `SMS_123456789` |

### 7. 邮件服务配置（可选）

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `SENDGRID_API_KEY` | SendGrid API 密钥 | `SG.xxxxxxxxxxxxxxxx` |
| `SENDGRID_FROM_EMAIL` | 发件人邮箱 | `noreply@maxgamer.com` |

### 8. 微信登录配置（可选）

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `WECHAT_APP_ID` | 微信 App ID | `wx1234567890abcdef` |
| `WECHAT_APP_SECRET` | 微信 App Secret | `xxxxxxxxxxxxxxxx` |

### 9. 支付配置（可选）

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `ALIPAY_APP_ID` | 支付宝 App ID | `2021001234567890` |
| `ALIPAY_PRIVATE_KEY` | 支付宝私钥 | `MIIEvQIBADANBgkqhkiG9w0B...` |
| `ALIPAY_PUBLIC_KEY` | 支付宝公钥 | `MIIBIjANBgkqhkiG9w0B...` |
| `WECHAT_PAY_MCH_ID` | 微信支付商户号 | `1234567890` |
| `WECHAT_PAY_API_KEY` | 微信支付 API 密钥 | `xxxxxxxxxxxxxxxx` |

### 10. 域名配置（必需）

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `DOMAIN` | 主域名 | `maxgamer.com` |
| `API_DOMAIN` | API 域名 | `api.maxgamer.com` |
| `GAME_WITCH_DOMAIN` | 游戏域名 | `play-witch.maxgamer.com` |
| `CORS_ORIGINS` | CORS 允许的源（逗号分隔） | `https://maxgamer.com,https://api.maxgamer.com` |

## 📝 配置步骤

### 步骤 1：生成 SSH 密钥对（如果还没有）

在本地机器上运行：

```bash
# 生成新的 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "github-actions@maxgamer.com" -f ~/.ssh/github_actions_deploy

# 查看公钥（需要添加到服务器）
cat ~/.ssh/github_actions_deploy.pub

# 查看私钥（需要添加到 GitHub Secrets）
cat ~/.ssh/github_actions_deploy
```

### 步骤 2：配置服务器

将公钥添加到服务器的 `~/.ssh/authorized_keys`：

```bash
# 在服务器上执行
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 步骤 3：生成强密钥

使用 Python 生成强随机密钥：

```python
import secrets

# 生成 SECRET_KEY
print("SECRET_KEY:", secrets.token_urlsafe(32))

# 生成 JWT_SECRET_KEY
print("JWT_SECRET_KEY:", secrets.token_urlsafe(32))

# 生成数据库密码
print("MYSQL_ROOT_PASSWORD:", secrets.token_urlsafe(24))
print("MYSQL_PASSWORD:", secrets.token_urlsafe(24))
print("REDIS_PASSWORD:", secrets.token_urlsafe(24))
```

或使用命令行：

```bash
# Linux/Mac
openssl rand -base64 32

# 或使用 Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 步骤 4：在 GitHub 中添加 Secrets

1. 访问仓库设置页面：
   ```
   https://github.com/rissalith/FrameWorker/settings/secrets/actions
   ```

2. 点击 "New repository secret"

3. 逐个添加上述 Secrets：
   - Name: 输入 Secret 名称（如 `SERVER_HOST`）
   - Value: 输入对应的值
   - 点击 "Add secret"

4. 重复步骤 2-3，直到添加完所有必需的 Secrets

## ✅ 验证配置

配置完成后，可以通过以下方式验证：

### 方法 1：手动触发工作流

1. 访问 Actions 页面：
   ```
   https://github.com/rissalith/FrameWorker/actions
   ```

2. 选择 "Build and Deploy to Production" 工作流

3. 点击 "Run workflow" 按钮

4. 选择分支（main 或 master）

5. 点击 "Run workflow" 开始部署

### 方法 2：推送代码触发

```bash
# 提交并推送代码到 main 分支
git add .
git commit -m "test: trigger deployment"
git push origin main
```

## 🔍 故障排查

### 问题 1：SSH 连接失败

**可能原因：**
- SSH 密钥格式不正确
- 服务器防火墙阻止连接
- SSH 端口配置错误

**解决方法：**
```bash
# 在本地测试 SSH 连接
ssh -i ~/.ssh/github_actions_deploy user@server_ip

# 检查服务器 SSH 日志
sudo tail -f /var/log/auth.log
```

### 问题 2：Docker 镜像拉取失败

**可能原因：**
- GitHub Token 权限不足
- 镜像名称不正确

**解决方法：**
- 确保 GitHub Actions 有 `packages: write` 权限
- 检查镜像名称是否与仓库名称匹配

### 问题 3：环境变量未生效

**可能原因：**
- Secret 名称拼写错误
- Secret 值包含特殊字符未正确转义

**解决方法：**
- 仔细检查 Secret 名称
- 对于包含特殊字符的值，使用引号包裹

## 📊 最小配置清单

如果只想快速测试部署，以下是最小必需配置：

### 必需配置（9 个）

- [ ] `SERVER_HOST`
- [ ] `SERVER_USER`
- [ ] `SERVER_SSH_KEY`
- [ ] `MYSQL_ROOT_PASSWORD`
- [ ] `MYSQL_PASSWORD`
- [ ] `REDIS_PASSWORD`
- [ ] `SECRET_KEY`
- [ ] `JWT_SECRET_KEY`
- [ ] `DEEPSEEK_API_KEY`

### 推荐配置（额外 6 个）

- [ ] `MYSQL_DATABASE`
- [ ] `MYSQL_USER`
- [ ] `DOMAIN`
- [ ] `API_DOMAIN`
- [ ] `GAME_WITCH_DOMAIN`
- [ ] `CORS_ORIGINS`

## 🔒 安全建议

1. **定期轮换密钥**：每 3-6 个月更换一次敏感密钥
2. **使用强密码**：所有密码至少 16 字符，包含大小写字母、数字和特殊字符
3. **限制 SSH 访问**：只允许特定 IP 访问服务器
4. **启用 2FA**：为 GitHub 账户启用双因素认证
5. **监控日志**：定期检查部署日志，发现异常及时处理

## 📞 支持

如有问题，请访问：
- GitHub Issues: https://github.com/rissalith/FrameWorker/issues
- 部署文档: [DEPLOYMENT.md](../MaxGamer/DEPLOYMENT.md)
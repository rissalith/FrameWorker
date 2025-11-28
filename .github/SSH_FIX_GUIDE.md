# 🔧 SSH 配置修复指南

## 🎯 问题概述

根据部署日志，SSH 连接失败的原因：

1. **SSH 私钥格式错误**：`ssh.ParsePrivateKey: ssh: no key found`
2. **服务器主机名无法解析**：`dial tcp: lookup ***: no such host`

## ✅ 快速修复步骤

### 步骤 1：检查并修复 SERVER_HOST

访问：https://github.com/rissalith/FrameWorker/settings/secrets/actions

找到 `SERVER_HOST`，点击编辑，确保：

**✅ 正确格式：**
```
123.456.789.0
```
或
```
server.example.com
```

**❌ 错误格式：**
```
http://123.456.789.0    ❌ 不要包含协议
https://server.com      ❌ 不要包含协议
123.456.789.0:22        ❌ 不要包含端口
空值                     ❌ 不能为空
```

---

### 步骤 2：重新生成 SSH 密钥

#### 2.1 在本地生成新密钥

打开终端（PowerShell 或 Git Bash），执行：

```bash
# 生成 ED25519 密钥（推荐）
ssh-keygen -t ed25519 -C "github-actions@frameworker" -f frameworker_deploy -N ""
```

或者使用 RSA 密钥（兼容性更好）：

```bash
# 生成 RSA 密钥
ssh-keygen -t rsa -b 4096 -C "github-actions@frameworker" -f frameworker_deploy -N ""
```

这会生成两个文件：
- `frameworker_deploy` - 私钥（用于 GitHub Secrets）
- `frameworker_deploy.pub` - 公钥（用于服务器）

#### 2.2 查看密钥内容

**查看私钥（用于 GitHub）：**
```bash
# Windows PowerShell
Get-Content frameworker_deploy

# Git Bash / Linux / Mac
cat frameworker_deploy
```

**查看公钥（用于服务器）：**
```bash
# Windows PowerShell
Get-Content frameworker_deploy.pub

# Git Bash / Linux / Mac
cat frameworker_deploy.pub
```

---

### 步骤 3：将公钥添加到服务器

#### 方法 A：使用 ssh-copy-id（推荐）

```bash
ssh-copy-id -i frameworker_deploy.pub user@YOUR_SERVER_IP
```

#### 方法 B：手动添加

1. **登录服务器：**
```bash
ssh user@YOUR_SERVER_IP
```

2. **添加公钥：**
```bash
# 创建 .ssh 目录（如果不存在）
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 添加公钥到 authorized_keys
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

3. **退出服务器**

---

### 步骤 4：测试 SSH 连接

在本地测试新密钥是否工作：

```bash
ssh -i frameworker_deploy user@YOUR_SERVER_IP
```

如果能成功登录，说明密钥配置正确！

---

### 步骤 5：更新 GitHub Secrets

访问：https://github.com/rissalith/FrameWorker/settings/secrets/actions

#### 5.1 更新 SERVER_SSH_KEY

1. 找到 `SERVER_SSH_KEY`
2. 点击 "Update secret"
3. 复制**完整的私钥内容**：
   ```bash
   # Windows PowerShell
   Get-Content frameworker_deploy | clip
   
   # Git Bash / Linux / Mac
   cat frameworker_deploy | pbcopy  # Mac
   cat frameworker_deploy | xclip   # Linux
   ```
4. 粘贴到 Value 字段
5. 点击 "Update secret"

**重要：** 确保包含完整内容，包括：
```
-----BEGIN OPENSSH PRIVATE KEY-----
(密钥内容)
-----END OPENSSH PRIVATE KEY-----
```

#### 5.2 确认 SERVER_HOST

1. 找到 `SERVER_HOST`
2. 确认值是正确的 IP 地址或域名
3. 如果不正确，点击 "Update secret" 修改

#### 5.3 确认 SERVER_USER

1. 找到 `SERVER_USER`
2. 确认值是正确的用户名（如 `root`、`ubuntu`、`admin`）
3. 如果不正确，点击 "Update secret" 修改

---

### 步骤 6：重新触发部署

#### 方法 A：推送代码触发

```bash
git commit --allow-empty -m "fix: 修复 SSH 配置"
git push origin main
```

#### 方法 B：手动触发

1. 访问：https://github.com/rissalith/FrameWorker/actions
2. 点击左侧 "Build and Deploy to Production"
3. 点击右侧 "Run workflow"
4. 选择 `main` 分支
5. 点击绿色的 "Run workflow" 按钮

---

## 📋 配置检查清单

在修复前，请确认以下信息：

### 服务器信息
- [ ] 服务器 IP 地址或域名
- [ ] SSH 用户名（通常是 `root`、`ubuntu`、`admin`）
- [ ] SSH 端口（默认 22，如果不是需要配置 `SERVER_PORT`）
- [ ] 能否从本地 SSH 连接到服务器

### GitHub Secrets
- [ ] `SERVER_HOST` - 格式正确（不含协议和端口）
- [ ] `SERVER_USER` - 用户名正确
- [ ] `SERVER_SSH_KEY` - 包含完整的私钥（含 BEGIN/END 标记）
- [ ] `SERVER_PORT` - 如果不是 22，需要配置

---

## 🔍 验证配置

### 1. 验证 SERVER_HOST

```bash
# 测试 IP 是否可达
ping YOUR_SERVER_IP

# 测试 SSH 端口是否开放
telnet YOUR_SERVER_IP 22
# 或
nc -zv YOUR_SERVER_IP 22
```

### 2. 验证 SSH 密钥

```bash
# 测试密钥连接
ssh -i frameworker_deploy user@YOUR_SERVER_IP

# 如果成功，应该能直接登录
```

### 3. 验证密钥格式

私钥应该是以下格式之一：

**ED25519 格式：**
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
...
-----END OPENSSH PRIVATE KEY-----
```

**RSA 格式：**
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
...
-----END RSA PRIVATE KEY-----
```

或

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
...
-----END OPENSSH PRIVATE KEY-----
```

---

## 🚨 常见错误

### 错误 1：密钥格式不完整

**症状：** `ssh: no key found`

**原因：** 缺少 BEGIN/END 标记或内容不完整

**解决：** 确保复制完整的私钥内容

### 错误 2：主机名无法解析

**症状：** `no such host`

**原因：** SERVER_HOST 配置错误或为空

**解决：** 使用正确的 IP 地址或域名

### 错误 3：权限被拒绝

**症状：** `Permission denied (publickey)`

**原因：** 公钥未正确添加到服务器

**解决：** 重新添加公钥到服务器的 `~/.ssh/authorized_keys`

### 错误 4：连接超时

**症状：** `Connection timed out`

**原因：** 防火墙阻止或 SSH 端口不正确

**解决：** 
- 检查服务器防火墙设置
- 确认 SSH 端口（默认 22）
- 如果使用非标准端口，配置 `SERVER_PORT`

---

## 💡 最佳实践

1. **使用 ED25519 密钥**
   - 更安全
   - 更快
   - 密钥更短

2. **不要使用密码保护的密钥**
   - GitHub Actions 不支持交互式密码输入
   - 生成时使用 `-N ""` 参数

3. **定期更换密钥**
   - 建议每 3-6 个月更换一次
   - 旧密钥失效后立即从服务器删除

4. **限制 SSH 访问**
   - 使用防火墙规则
   - 只允许必要的 IP 访问
   - 禁用密码登录，只使用密钥

---

## 📞 需要帮助？

如果按照以上步骤仍然无法解决，请提供：

1. 服务器类型和操作系统
2. 是否能从本地 SSH 连接
3. GitHub Actions 的完整错误日志
4. 使用的密钥类型（ED25519 或 RSA）

参考文档：
- [SSH_TROUBLESHOOTING.md](SSH_TROUBLESHOOTING.md) - 详细故障排除
- [HOW_TO_DEPLOY.md](HOW_TO_DEPLOY.md) - 完整部署指南
- [QUICK_DEPLOY.md](QUICK_DEPLOY.md) - 快速部署指南

---

## ✅ 修复完成后

配置修复后，您应该能看到：

1. ✅ GitHub Actions 部署成功
2. ✅ SSH 连接成功
3. ✅ 服务正常启动
4. ✅ 健康检查通过

访问您的服务器 IP 应该能看到网站运行！

---

**祝您配置顺利！🚀**
# 🔧 SSH 连接失败问题排查指南

## 🚨 当前错误

```
ssh.ParsePrivateKey: ssh: no key found
dial tcp: lookup ***: no such host
```

## 🔍 问题诊断

根据错误信息，有两个主要问题：

### 问题 1：SSH 私钥格式错误
**错误：** `ssh.ParsePrivateKey: ssh: no key found`

**可能原因：**
1. SSH 私钥格式不正确
2. 私钥缺少 BEGIN/END 标记
3. 私钥包含额外的空格或换行符
4. 使用了错误的密钥类型

### 问题 2：无法解析服务器主机名
**错误：** `dial tcp: lookup ***: no such host`

**可能原因：**
1. `SERVER_HOST` 配置为空或格式错误
2. 主机名拼写错误
3. 使用了域名但 DNS 无法解析

---

## ✅ 解决方案

### 步骤 1：检查 SERVER_HOST 配置

访问：https://github.com/rissalith/FrameWorker/settings/secrets/actions

**检查 `SERVER_HOST`：**
- ✅ 应该是 IP 地址（如 `123.456.789.0`）或域名（如 `server.example.com`）
- ❌ 不应该包含 `http://` 或 `https://`
- ❌ 不应该包含端口号（端口在 `SERVER_PORT` 中配置）
- ❌ 不应该为空

**正确示例：**
```
123.456.789.0
```
或
```
server.example.com
```

**错误示例：**
```
http://123.456.789.0    ❌ 不要包含协议
123.456.789.0:22        ❌ 不要包含端口
```

---

### 步骤 2：检查 SSH 私钥格式

**正确的 SSH 私钥格式应该是：**

#### RSA 密钥格式：
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
(多行密钥内容)
...
-----END RSA PRIVATE KEY-----
```

#### OpenSSH 格式（推荐）：
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
(多行密钥内容)
...
-----END OPENSSH PRIVATE KEY-----
```

#### ED25519 格式：
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
(多行密钥内容)
...
-----END OPENSSH PRIVATE KEY-----
```

**重要提示：**
- ✅ 必须包含完整的 `-----BEGIN` 和 `-----END` 标记
- ✅ 密钥内容应该是多行的
- ✅ 不要在开头或结尾添加额外的空行
- ✅ 确保没有额外的空格

---

### 步骤 3：重新生成并配置 SSH 密钥

如果您的密钥格式有问题，请重新生成：

#### 3.1 在本地生成新的 SSH 密钥对

```bash
# 生成 ED25519 密钥（推荐，更安全更快）
ssh-keygen -t ed25519 -C "github-actions@frameworker" -f ~/.ssh/frameworker_deploy

# 或生成 RSA 密钥（兼容性更好）
ssh-keygen -t rsa -b 4096 -C "github-actions@frameworker" -f ~/.ssh/frameworker_deploy
```

**提示：** 按 Enter 跳过密码设置（GitHub Actions 不支持带密码的密钥）

#### 3.2 查看私钥内容

```bash
# 查看私钥（需要添加到 GitHub Secrets）
cat ~/.ssh/frameworker_deploy

# 查看公钥（需要添加到服务器）
cat ~/.ssh/frameworker_deploy.pub
```

#### 3.3 将公钥添加到服务器

```bash
# 方法 1：使用 ssh-copy-id（推荐）
ssh-copy-id -i ~/.ssh/frameworker_deploy.pub user@YOUR_SERVER_IP

# 方法 2：手动添加
# 登录服务器后执行：
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### 3.4 测试 SSH 连接

```bash
# 测试连接
ssh -i ~/.ssh/frameworker_deploy user@YOUR_SERVER_IP

# 如果成功，应该能直接登录服务器
```

#### 3.5 更新 GitHub Secrets

访问：https://github.com/rissalith/FrameWorker/settings/secrets/actions

1. 点击 `SERVER_SSH_KEY`
2. 点击 "Update secret"
3. 复制**完整的私钥内容**（包括 BEGIN 和 END 行）
4. 粘贴到 Value 字段
5. 点击 "Update secret"

---

### 步骤 4：验证配置

#### 4.1 检查 SERVER_HOST

确保 `SERVER_HOST` 是有效的：

```bash
# 测试 IP 地址是否可达
ping YOUR_SERVER_IP

# 测试 SSH 端口是否开放
telnet YOUR_SERVER_IP 22
# 或
nc -zv YOUR_SERVER_IP 22
```

#### 4.2 检查 SERVER_USER

确保用户名正确：
- 通常是 `root`、`ubuntu`、`admin` 等
- 必须是服务器上存在的用户
- 该用户必须有 SSH 登录权限

#### 4.3 检查 SERVER_PORT（可选）

如果 SSH 端口不是默认的 22，需要配置 `SERVER_PORT`：

```bash
# 查看服务器 SSH 端口
sudo netstat -tulpn | grep ssh
```

---

## 🔄 重新触发部署

配置修复后，重新触发部署：

### 方法 1：推送代码
```bash
git commit --allow-empty -m "test: 重新触发部署"
git push origin main
```

### 方法 2：手动触发
访问：https://github.com/rissalith/FrameWorker/actions
点击 "Run workflow"

---

## 📋 完整配置检查清单

在 GitHub Secrets 中检查以下配置：

- [ ] `SERVER_HOST` - 服务器 IP 或域名（不含协议和端口）
- [ ] `SERVER_USER` - SSH 用户名（如 `root`）
- [ ] `SERVER_SSH_KEY` - 完整的 SSH 私钥（包含 BEGIN/END 标记）
- [ ] `SERVER_PORT` - SSH 端口（可选，默认 22）
- [ ] `DEPLOY_PATH` - 部署路径（可选，默认 `/var/www/FrameWorker`）

---

## 🎯 快速修复步骤

如果您想快速修复，按以下步骤操作：

### 1. 确认服务器信息
```bash
# 您的服务器 IP 地址是什么？
# 您的 SSH 用户名是什么？
# SSH 端口是 22 吗？
```

### 2. 生成新密钥
```bash
ssh-keygen -t ed25519 -f ~/.ssh/frameworker_deploy -N ""
```

### 3. 添加公钥到服务器
```bash
ssh-copy-id -i ~/.ssh/frameworker_deploy.pub user@server_ip
```

### 4. 测试连接
```bash
ssh -i ~/.ssh/frameworker_deploy user@server_ip
```

### 5. 更新 GitHub Secrets
- 复制私钥：`cat ~/.ssh/frameworker_deploy`
- 更新 `SERVER_SSH_KEY`
- 确认 `SERVER_HOST` 正确

### 6. 重新部署
```bash
git commit --allow-empty -m "test: 修复 SSH 配置"
git push origin main
```

---

## 📞 需要帮助？

如果问题仍然存在，请提供以下信息：

1. 您的服务器类型（云服务商、操作系统）
2. SSH 密钥类型（RSA、ED25519 等）
3. 是否能从本地 SSH 连接到服务器
4. GitHub Actions 的完整错误日志

---

## 🔒 安全提醒

- ✅ 私钥只存储在 GitHub Secrets 中
- ✅ 不要将私钥提交到代码仓库
- ✅ 定期更换 SSH 密钥
- ✅ 使用强密钥类型（ED25519 或 RSA 4096）
- ✅ 限制服务器 SSH 访问（使用防火墙规则）

---

**祝您配置顺利！🚀**
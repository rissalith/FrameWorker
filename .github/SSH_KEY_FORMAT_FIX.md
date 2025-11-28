# 🔧 SSH 密钥格式问题修复

## 🚨 当前错误

```
ssh.ParsePrivateKey: ssh: no key found
ssh: unable to authenticate, attempted methods [none], no supported methods remain
```

## 🔍 问题根源

`SERVER_SSH_KEY` 的格式不正确，导致 GitHub Actions 无法解析私钥。

---

## ✅ 正确的密钥格式

### 方法 1：使用 OpenSSH 格式（推荐）

**完整的私钥应该是这样的：**

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAYEAyxz1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN
OPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV
... (更多行)
WXYZ1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234
567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ==
-----END OPENSSH PRIVATE KEY-----
```

### 方法 2：使用 RSA 格式

```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAyxz1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN
OPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV
... (更多行)
WXYZ1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234
567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ==
-----END RSA PRIVATE KEY-----
```

---

## 🛠️ 修复步骤

### 步骤 1：重新生成 SSH 密钥对

在本地终端执行：

```bash
# 生成新的 ED25519 密钥（推荐）
ssh-keygen -t ed25519 -C "github-actions@frameworker" -f frameworker_key -N ""

# 或生成 RSA 密钥（兼容性更好）
ssh-keygen -t rsa -b 4096 -C "github-actions@frameworker" -f frameworker_key -N ""
```

**重要：** `-N ""` 表示不设置密码（GitHub Actions 不支持带密码的密钥）

---

### 步骤 2：查看并复制私钥

#### Windows PowerShell:
```powershell
# 查看私钥
Get-Content frameworker_key

# 复制到剪贴板
Get-Content frameworker_key | Set-Clipboard
```

#### Git Bash / Linux / Mac:
```bash
# 查看私钥
cat frameworker_key

# 复制到剪贴板 (Mac)
cat frameworker_key | pbcopy

# 复制到剪贴板 (Linux)
cat frameworker_key | xclip -selection clipboard
```

**确保复制的内容包括：**
- ✅ `-----BEGIN` 开头行
- ✅ 所有中间的密钥内容（多行）
- ✅ `-----END` 结尾行
- ✅ 没有额外的空行或空格

---

### 步骤 3：将公钥添加到服务器

#### 查看公钥：
```bash
# Windows PowerShell
Get-Content frameworker_key.pub

# Git Bash / Linux / Mac
cat frameworker_key.pub
```

#### 添加到服务器：

**方法 A：使用 ssh-copy-id（推荐）**
```bash
ssh-copy-id -i frameworker_key.pub user@YOUR_SERVER_IP
```

**方法 B：手动添加**
```bash
# 1. 登录服务器
ssh user@YOUR_SERVER_IP

# 2. 创建 .ssh 目录（如果不存在）
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 3. 添加公钥
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 4. 退出服务器
exit
```

---

### 步骤 4：测试 SSH 连接

```bash
# 测试新密钥
ssh -i frameworker_key user@YOUR_SERVER_IP

# 如果成功，应该能直接登录服务器
```

**如果测试失败，检查：**
1. 服务器 IP 是否正确
2. 用户名是否正确
3. SSH 端口是否是 22（如果不是，使用 `-p 端口号`）
4. 服务器防火墙是否允许 SSH 连接

---

### 步骤 5：更新 GitHub Secrets

访问：https://github.com/rissalith/FrameWorker/settings/secrets/actions

#### 更新 SERVER_SSH_KEY：

1. 找到 `SERVER_SSH_KEY`
2. 点击 "Update secret"
3. **完整复制私钥内容**（包括 BEGIN/END 行）
4. 粘贴到 Value 字段
5. 点击 "Update secret"

**检查清单：**
- [ ] 包含 `-----BEGIN` 行
- [ ] 包含所有密钥内容（多行）
- [ ] 包含 `-----END` 行
- [ ] 没有额外的空行
- [ ] 没有额外的空格
- [ ] 没有截断或省略

---

### 步骤 6：验证其他 Secrets

#### 检查 SERVER_HOST：
- ✅ 应该是纯 IP 地址：`123.456.789.0`
- ❌ 不要包含：`http://`、`https://`、端口号

#### 检查 SERVER_USER：
- ✅ 应该是有效的用户名：`root`、`ubuntu`、`admin` 等
- ❌ 不要包含：`@`、空格

#### 检查 SERVER_PORT（可选）：
- 如果 SSH 端口是 22，可以不设置
- 如果不是 22，设置为实际端口号（如 `2222`）

---

### 步骤 7：重新触发部署

```bash
# 创建空提交触发部署
git commit --allow-empty -m "fix: 重新配置 SSH 密钥"
git push origin main
```

或手动触发：
1. 访问：https://github.com/rissalith/FrameWorker/actions
2. 点击 "Build and Deploy to Production"
3. 点击 "Run workflow"
4. 选择 `main` 分支
5. 点击 "Run workflow"

---

## 🔍 常见错误及解决方案

### 错误 1：`ssh: no key found`

**原因：** 私钥格式不完整或损坏

**解决：**
1. 重新复制完整的私钥
2. 确保包含 BEGIN/END 标记
3. 确保没有额外的空格或换行

### 错误 2：`unable to authenticate`

**原因：** 公钥未正确添加到服务器

**解决：**
1. 检查服务器的 `~/.ssh/authorized_keys` 文件
2. 确保公钥完整且格式正确
3. 检查文件权限：
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

### 错误 3：`Permission denied (publickey)`

**原因：** SSH 配置或权限问题

**解决：**
1. 检查服务器 SSH 配置：
   ```bash
   sudo nano /etc/ssh/sshd_config
   ```
2. 确保以下设置：
   ```
   PubkeyAuthentication yes
   AuthorizedKeysFile .ssh/authorized_keys
   ```
3. 重启 SSH 服务：
   ```bash
   sudo systemctl restart sshd
   ```

### 错误 4：`Connection timed out`

**原因：** 网络或防火墙问题

**解决：**
1. 检查服务器防火墙：
   ```bash
   sudo ufw status
   sudo ufw allow 22/tcp
   ```
2. 检查云服务商的安全组规则
3. 确认 SSH 端口是否正确

---

## 📋 完整检查清单

在重新部署前，确认：

- [ ] 已生成新的 SSH 密钥对（无密码）
- [ ] 私钥格式完整（包含 BEGIN/END 标记）
- [ ] 公钥已添加到服务器 `~/.ssh/authorized_keys`
- [ ] 服务器文件权限正确（700 for .ssh, 600 for authorized_keys）
- [ ] 本地测试 SSH 连接成功
- [ ] `SERVER_SSH_KEY` 已更新（完整私钥）
- [ ] `SERVER_HOST` 格式正确（纯 IP 或域名）
- [ ] `SERVER_USER` 正确
- [ ] `SERVER_PORT` 正确（如果不是 22）

---

## 🎯 快速验证命令

```bash
# 1. 生成密钥
ssh-keygen -t ed25519 -f frameworker_key -N ""

# 2. 添加公钥到服务器
ssh-copy-id -i frameworker_key.pub user@SERVER_IP

# 3. 测试连接
ssh -i frameworker_key user@SERVER_IP

# 4. 如果成功，复制私钥
cat frameworker_key

# 5. 更新 GitHub Secret
# 访问 https://github.com/rissalith/FrameWorker/settings/secrets/actions
# 更新 SERVER_SSH_KEY

# 6. 触发部署
git commit --allow-empty -m "fix: 更新 SSH 密钥"
git push origin main
```

---

## 💡 提示

1. **密钥类型选择：**
   - ED25519：更安全、更快、密钥更短（推荐）
   - RSA 4096：兼容性更好、更通用

2. **不要使用密码：**
   - GitHub Actions 不支持交互式密码输入
   - 生成时必须使用 `-N ""` 参数

3. **保护私钥：**
   - 只存储在 GitHub Secrets 中
   - 不要提交到代码仓库
   - 不要分享给他人

4. **定期更换：**
   - 建议每 3-6 个月更换一次
   - 旧密钥失效后立即从服务器删除

---

**如果按照以上步骤操作后仍然失败，请提供：**
1. 密钥生成命令的输出
2. 本地 SSH 测试的结果
3. GitHub Actions 的完整错误日志
4. 服务器类型和操作系统版本

---

**祝您配置顺利！🚀**
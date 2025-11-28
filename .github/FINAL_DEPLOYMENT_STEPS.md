# 🚀 最终部署步骤

## ✅ 已完成的工作

1. ✅ SSH 密钥已生成（`frameworker_key` 和 `frameworker_key.pub`）
2. ✅ 公钥已添加到服务器（root@149.88.69.87）
3. ✅ 服务器信息已确认：
   - 服务器 IP: `149.88.69.87`
   - 用户名: `root`
   - SSH 端口: `22`（默认）

---

## 📝 最后 3 步操作

### 步骤 1：更新 GitHub Secrets

访问：https://github.com/rissalith/FrameWorker/settings/secrets/actions

#### 1.1 更新 SERVER_SSH_KEY

1. 找到 `SERVER_SSH_KEY`
2. 点击 "Update secret"
3. 复制以下完整的私钥内容：

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACD8cnO5VtfJJe0fm+cU/tbb3dei7tqxCZcmCmCe8DySewAAAKDSvPlb0rz5
WwAAAAtzc2gtZWQyNTUxOQAAACD8cnO5VtfJJe0fm+cU/tbb3dei7tqxCZcmCmCe8DySew
AAAEAL4WTqdntxV70Of0KXhy7MBuEZF7FSI2k2nC5iKVicpPxyc7lW18kl7R+b5xT+1tvd
16Lu2rEJlyYKYJ7wPJJ7AAAAGmdpdGh1Yi1hY3Rpb25zQGZyYW1ld29ya2VyAQID
-----END OPENSSH PRIVATE KEY-----
```

4. 粘贴到 Value 字段
5. 点击 "Update secret"

#### 1.2 确认 SERVER_HOST

1. 找到 `SERVER_HOST`
2. 确认值为：`149.88.69.87`
3. 如果不正确，点击 "Update secret" 修改

#### 1.3 确认 SERVER_USER

1. 找到 `SERVER_USER`
2. 确认值为：`root`
3. 如果不正确，点击 "Update secret" 修改

---

### 步骤 2：测试 SSH 连接（可选）

在项目目录（`c:\巫女上上签`）打开 PowerShell，执行：

```powershell
ssh -i frameworker_key root@149.88.69.87 "echo 'SSH测试成功'"
```

如果看到 "SSH测试成功"，说明配置正确！

---

### 步骤 3：触发部署

#### 方法 A：推送代码触发（推荐）

在项目目录执行：

```bash
git add .
git commit -m "fix: 更新 SSH 配置，使用 root 用户"
git push origin main
```

#### 方法 B：手动触发

1. 访问：https://github.com/rissalith/FrameWorker/actions
2. 点击左侧 "Build and Deploy to Production"
3. 点击右侧 "Run workflow"
4. 选择 `main` 分支
5. 点击绿色的 "Run workflow" 按钮

---

## 📊 监控部署

### 查看部署进度

访问：https://github.com/rissalith/FrameWorker/actions

您应该看到：
1. ✅ Build and Push Docker Images - 构建镜像
2. ✅ Copy files to server - 复制文件（应该不再报错）
3. ✅ Deploy to server via SSH - SSH 部署（应该不再报错）
4. ✅ Health check - 健康检查

### 预期结果

如果一切正常，您应该看到：
- ✅ 所有步骤都显示绿色对勾
- ✅ 没有 "ssh: no key found" 错误
- ✅ 没有 "unable to authenticate" 错误
- ✅ 服务成功部署到服务器

---

## 🎯 部署成功后

### 验证服务

1. **访问网站**
   ```
   http://149.88.69.87
   ```

2. **检查 API**
   ```
   http://149.88.69.87:5000
   ```

3. **检查游戏服务**
   ```
   http://149.88.69.87:5001
   ```

### SSH 登录服务器检查

```bash
ssh root@149.88.69.87

# 查看 Docker 容器
cd /var/www/FrameWorker
docker-compose -f docker-compose.prod.yml ps

# 查看服务日志
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🔧 如果部署失败

### 检查 GitHub Actions 日志

1. 访问：https://github.com/rissalith/FrameWorker/actions
2. 点击失败的工作流
3. 查看错误信息

### 常见问题

#### 问题 1：仍然提示 "ssh: no key found"

**解决：** 确保私钥完整复制，包括：
- `-----BEGIN OPENSSH PRIVATE KEY-----`
- 所有中间内容
- `-----END OPENSSH PRIVATE KEY-----`

#### 问题 2：提示 "Permission denied"

**解决：** 
1. 确认 `SERVER_USER` 是 `root`
2. 确认公钥已添加到服务器
3. 检查服务器 `~/.ssh/authorized_keys` 文件权限

#### 问题 3：提示 "Connection refused"

**解决：**
1. 确认服务器 IP 正确
2. 检查服务器防火墙设置
3. 确认 SSH 服务正在运行

---

## 📚 相关文档

- [SSH_KEY_FORMAT_FIX.md](SSH_KEY_FORMAT_FIX.md) - SSH 密钥格式修复
- [SSH_FIX_GUIDE.md](SSH_FIX_GUIDE.md) - SSH 配置快速修复
- [SSH_TROUBLESHOOTING.md](SSH_TROUBLESHOOTING.md) - SSH 故障排除
- [HOW_TO_DEPLOY.md](HOW_TO_DEPLOY.md) - 完整部署指南

---

## ✅ 配置总结

| 配置项 | 值 | 状态 |
|--------|-----|------|
| SERVER_HOST | 149.88.69.87 | ✅ 已确认 |
| SERVER_USER | root | ✅ 已确认 |
| SERVER_SSH_KEY | ED25519 私钥 | ⚠️ 需要更新 |
| SERVER_PORT | 22 | ✅ 默认值 |
| 公钥位置 | ~/.ssh/authorized_keys | ✅ 已添加 |

---

## 🎉 完成清单

在触发部署前，确认：

- [ ] 已复制完整私钥到 GitHub `SERVER_SSH_KEY`
- [ ] 已确认 `SERVER_HOST` 为 `149.88.69.87`
- [ ] 已确认 `SERVER_USER` 为 `root`
- [ ] 公钥已在服务器上（已完成）
- [ ] 本地可以使用密钥登录（可选测试）

**完成以上步骤后，执行步骤 3 触发部署！** 🚀

---

## 📞 需要帮助？

如果遇到问题：
1. 查看 GitHub Actions 日志
2. 参考相关文档
3. 检查服务器日志

**祝您部署顺利！** ✨
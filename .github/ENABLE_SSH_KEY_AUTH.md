# 启用服务器 SSH 密钥认证

## 问题诊断

服务器当前配置：
```
PubkeyAuthentication no  ← 禁用了公钥认证
PasswordAuthentication yes
PermitRootLogin yes
```

这导致 GitHub Actions 无法使用 SSH 密钥连接服务器。

## 解决方案

### 方法 1：通过 SSH 修改配置（推荐）

1. **连接到服务器**（使用密码）：
```bash
ssh root@149.88.69.87
```

2. **备份 SSH 配置**：
```bash
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
```

3. **启用公钥认证**：
```bash
sed -i 's/^PubkeyAuthentication no/PubkeyAuthentication yes/' /etc/ssh/sshd_config
```

4. **验证修改**：
```bash
grep PubkeyAuthentication /etc/ssh/sshd_config
```
应该显示：`PubkeyAuthentication yes`

5. **重启 SSH 服务**：
```bash
# Ubuntu/Debian
systemctl restart sshd

# 或者
service sshd restart
```

6. **测试 SSH 密钥连接**（在本地执行）：
```bash
cd c:\巫女上上签
ssh -i frameworker_key root@149.88.69.87 "echo 'SSH密钥认证成功！'"
```

### 方法 2：一键修复脚本

在服务器上执行：
```bash
ssh root@149.88.69.87 << 'ENDSSH'
# 备份配置
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# 启用公钥认证
sed -i 's/^PubkeyAuthentication no/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# 确保 authorized_keys 文件权限正确
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 重启 SSH 服务
systemctl restart sshd || service sshd restart

# 显示当前配置
echo "=== 当前 SSH 配置 ==="
grep -E '(PubkeyAuthentication|PasswordAuthentication|PermitRootLogin)' /etc/ssh/sshd_config

echo "=== SSH 服务状态 ==="
systemctl status sshd | head -5
ENDSSH
```

### 方法 3：手动编辑配置文件

1. 连接服务器：
```bash
ssh root@149.88.69.87
```

2. 编辑配置文件：
```bash
nano /etc/ssh/sshd_config
```

3. 找到并修改：
```
PubkeyAuthentication no
```
改为：
```
PubkeyAuthentication yes
```

4. 保存并退出（Ctrl+X, Y, Enter）

5. 重启 SSH：
```bash
systemctl restart sshd
```

## 验证步骤

### 1. 检查服务器配置
```bash
ssh root@149.88.69.87 "grep PubkeyAuthentication /etc/ssh/sshd_config"
```
应该显示：`PubkeyAuthentication yes`

### 2. 测试本地 SSH 密钥连接
```bash
cd c:\巫女上上签
ssh -i frameworker_key root@149.88.69.87 "echo '测试成功'"
```
应该**不需要输入密码**就能连接成功

### 3. 重新触发 GitHub Actions 部署
```bash
git commit --allow-empty -m "test: 重新测试部署 - 已启用公钥认证"
git push origin main
```

## 安全建议

启用公钥认证后，建议：

1. **禁用密码认证**（更安全）：
```bash
sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd
```

2. **确保只有授权的公钥可以访问**：
```bash
cat ~/.ssh/authorized_keys
```

3. **设置防火墙规则**（如果需要）：
```bash
# 只允许特定 IP 访问 SSH
ufw allow from YOUR_IP to any port 22
```

## 常见问题

### Q: 修改后仍然无法连接？
A: 检查以下几点：
1. SSH 服务是否成功重启
2. authorized_keys 文件权限是否正确（600）
3. .ssh 目录权限是否正确（700）
4. 公钥是否正确添加到 authorized_keys

### Q: 如何回滚配置？
A: 使用备份文件：
```bash
cp /etc/ssh/sshd_config.backup /etc/ssh/sshd_config
systemctl restart sshd
```

### Q: 为什么之前公钥认证被禁用？
A: 可能是：
- 服务器默认配置
- 安全策略要求
- 之前的管理员手动禁用

## 下一步

修复后，GitHub Actions 部署应该能够成功：
1. ✅ 启用公钥认证
2. ✅ 测试本地 SSH 连接
3. ✅ 重新触发部署
4. ✅ 监控部署状态

---

**立即执行方法 2 的一键修复脚本！**
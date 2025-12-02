# 🚨 需要手动SSH修复 - 自动化方案失败

## 当前状态 (2025-12-01 17:32 CST)

### ✅ 已完成的工作
1. ✅ 修复了GitHub Actions workflow配置
2. ✅ 成功推送到远程仓库
3. ✅ GitHub Actions成功构建Docker镜像
4. ✅ Docker镜像已成功拉取到服务器

### ❌ 当前问题
- **所有SSH自动化命令都卡住无响应**
- Terminal 3, 5, 6 的SSH命令已运行5+分钟无输出
- 自动化部署脚本无法完成
- 网站仍然处于521错误状态

### 🔍 问题根源
SSH命令在Windows PowerShell中执行时遇到以下问题:
1. 首次连接需要手动确认主机指纹
2. 即使使用`-o StrictHostKeyChecking=no`参数仍然卡住
3. `docker-compose down`命令在服务器上可能挂起

---

## 🛠️ 立即修复方案 (需要手动操作)

### 方案A: 使用PuTTY或其他SSH客户端 (推荐)

**步骤1: 使用SSH客户端登录**
```
主机: 8.138.115.175
用户: root
密码: [您的密码]
```

**步骤2: 执行修复命令**
```bash
# 进入项目目录
cd /var/www/FrameWorker

# 强制停止所有容器
docker kill $(docker ps -q) 2>/dev/null || true
docker rm -f $(docker ps -aq) 2>/dev/null || true

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 查看状态
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f platform-api
```

**预期结果:**
```
NAME                          IMAGE                                                    COMMAND                  SERVICE        CREATED         STATUS         PORTS
frameworker-platform-api-1    ghcr.io/rissalith/xmgamer-platform-api:latest           "python app.py"          platform-api   X seconds ago   Up X seconds   0.0.0.0:5000->5000/tcp
```

---

### 方案B: 在PowerShell中手动交互式SSH

**步骤1: 打开新的PowerShell窗口**

**步骤2: 执行SSH登录**
```powershell
ssh root@8.138.115.175
```

**步骤3: 当提示确认主机指纹时,输入 `yes`**
```
The authenticity of host '8.138.115.175 (8.138.115.175)' can't be established.
ED25519 key fingerprint is SHA256:iaLARCzLFw7VhepdfC/mOizjqJkV1Rt9R4gkJtsIU6I.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

**步骤4: 输入密码登录**

**步骤5: 执行修复命令** (同方案A的步骤2)

---

### 方案C: 使用Windows Terminal (如果已安装)

Windows Terminal对SSH支持更好,可以尝试:

```powershell
wt ssh root@8.138.115.175
```

然后执行修复命令。

---

## 📋 验证服务恢复

修复完成后,执行以下验证:

### 1. 检查容器状态
```bash
docker-compose -f docker-compose.prod.yml ps
```

应该看到:
- `platform-api` 容器状态为 `Up`
- 端口映射 `0.0.0.0:5000->5000/tcp`

### 2. 检查容器日志
```bash
docker-compose -f docker-compose.prod.yml logs -f platform-api
```

应该看到:
```
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

### 3. 测试网站访问
在浏览器中访问: https://www.xmframer.com

应该看到:
- ✅ 网站正常加载 (不再是521错误)
- ✅ 可以正常浏览内容

### 4. 测试AI对话功能
访问: https://www.xmframer.com/ai-dialogue

应该看到:
- ✅ AI对话界面正常加载
- ✅ 可以发送消息并收到回复 (不再是503错误)

---

## 🔧 如果仍然有问题

### 问题1: 容器无法启动
```bash
# 查看详细错误日志
docker-compose -f docker-compose.prod.yml logs platform-api

# 检查镜像是否存在
docker images | grep platform-api

# 如果镜像不存在,手动拉取
docker pull ghcr.io/rissalith/xmgamer-platform-api:latest
```

### 问题2: 端口被占用
```bash
# 检查端口占用
netstat -tlnp | grep 5000

# 如果有其他进程占用,停止它
kill -9 <PID>
```

### 问题3: 权限问题
```bash
# 确保有执行权限
chmod +x /var/www/FrameWorker/docker-compose.prod.yml

# 检查Docker服务状态
systemctl status docker
```

---

## 📝 后续改进建议

1. **配置SSH密钥认证**
   - 避免每次都需要输入密码
   - 提高自动化脚本的可靠性

2. **增加GitHub Actions超时时间**
   - 修改workflow中的timeout设置
   - 避免部署过程中超时

3. **改进部署脚本**
   - 使用`docker kill`代替`docker-compose down`
   - 添加更多错误处理和重试逻辑

4. **设置监控告警**
   - 配置服务器监控
   - 容器异常时自动告警

---

## 📞 需要帮助?

如果遇到任何问题:
1. 检查容器日志: `docker-compose logs -f`
2. 检查系统日志: `journalctl -xe`
3. 检查磁盘空间: `df -h`
4. 检查内存使用: `free -h`

---

## ✅ 修复完成检查清单

- [ ] SSH成功登录到服务器
- [ ] 成功停止旧容器
- [ ] 成功启动新容器
- [ ] 容器状态显示为 `Up`
- [ ] 网站可以正常访问 (不再521错误)
- [ ] AI对话功能正常工作 (不再503错误)
- [ ] 容器日志没有错误信息

---

**最后更新**: 2025-12-01 17:32 CST
**状态**: 等待手动SSH修复
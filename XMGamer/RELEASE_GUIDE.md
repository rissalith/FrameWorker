# FrameWorker v1.0.0 发版指南

## 📦 发版内容

本次发版包含以下主要功能和改进：

### 主要功能
- ✅ 用户认证系统（邮箱登录、密码登录、Google OAuth）
- ✅ 图片处理和切割功能
- ✅ GIF动画生成
- ✅ 历史记录同步
- ✅ 精灵图动画系统
- ✅ 粒子爆炸特效

### 技术改进
- ✅ 模块化前端架构
- ✅ RESTful API设计
- ✅ JWT认证
- ✅ SQLite数据库
- ✅ 响应式UI设计

### 部署支持
- ✅ 完整的部署文档 (DEPLOYMENT.md)
- ✅ 快速部署脚本 (deploy.sh)
- ✅ 环境变量配置示例
- ✅ 服务器配置指南

## 🚀 GitHub 发版步骤

### 1. 推送代码到GitHub

由于网络问题，如果 `git push` 失败，可以尝试以下方法：

#### 方法 A: 使用代理
```bash
# 设置 Git 代理（如果你有代理）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 推送代码
git push origin master

# 推送标签
git push origin v1.0.0

# 推送完成后取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

#### 方法 B: 使用 SSH
```bash
# 如果还没有配置 SSH，先配置
# 1. 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 将公钥添加到 GitHub
# 复制 ~/.ssh/id_ed25519.pub 的内容到 GitHub Settings > SSH Keys

# 3. 修改远程仓库地址为 SSH
git remote set-url origin git@github.com:rissalith/FrameWorker.git

# 4. 推送代码
git push origin master
git push origin v1.0.0
```

#### 方法 C: 手动上传（最后的选择）
如果以上方法都不行，可以：
1. 访问 https://github.com/rissalith/FrameWorker
2. 使用 GitHub 网页界面上传文件
3. 或者等待网络恢复后再推送

### 2. 创建 GitHub Release

推送成功后，在 GitHub 上创建 Release：

1. 访问 https://github.com/rissalith/FrameWorker/releases
2. 点击 "Create a new release"
3. 选择标签 `v1.0.0`
4. 填写 Release 标题：`v1.0.0 - 完整功能版本`
5. 填写 Release 说明：

```markdown
# FrameWorker v1.0.0

## 🎉 首个正式版本发布

这是 FrameWorker 的第一个正式版本，包含完整的图片处理和动画生成功能。

## ✨ 主要功能

### 用户系统
- 邮箱验证码登录
- 密码登录
- Google OAuth 登录
- 用户注册和认证

### 图片处理
- 图片上传和预览
- 图片切割和裁剪
- 背景去除
- 批量处理

### 动画生成
- GIF 动画生成
- WebP 帧导出
- 精灵图导出
- 帧插值功能

### 其他功能
- 历史记录同步
- 精灵图动画系统
- 粒子爆炸特效
- 响应式设计

## 🛠️ 技术栈

- **后端**: Python Flask
- **前端**: HTML5, CSS3, JavaScript (原生)
- **数据库**: SQLite
- **认证**: JWT, OAuth 2.0

## 📦 部署

详细部署说明请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

### 快速部署（Linux）
```bash
sudo bash deploy.sh
```

### 手动部署
请参考 DEPLOYMENT.md 中的详细步骤。

## 📝 更新日志

### 新增
- 完整的用户认证系统
- 图片处理核心功能
- GIF 动画生成
- 历史记录管理
- 精灵图动画系统
- 粒子特效系统

### 改进
- 模块化代码架构
- RESTful API 设计
- 响应式 UI
- 完善的错误处理

### 文档
- 添加部署文档
- 添加快速部署脚本
- 添加环境变量配置示例

## 🔗 相关链接

- [项目主页](https://github.com/rissalith/FrameWorker)
- [部署文档](./DEPLOYMENT.md)
- [问题反馈](https://github.com/rissalith/FrameWorker/issues)

## 📄 许可证

MIT License
```

6. 点击 "Publish release"

## 🌐 云服务器部署

### 前置准备

1. **准备云服务器**
   - 推荐配置：2核4G内存，40G硬盘
   - 操作系统：Ubuntu 20.04 或更高版本
   - 开放端口：80, 443, 22

2. **域名配置（可选）**
   - 如果有域名，将 A 记录指向服务器 IP
   - 如果没有域名，可以直接使用 IP 访问

### 快速部署

#### 方法 1: 使用自动部署脚本

```bash
# 1. 连接到服务器
ssh root@your-server-ip

# 2. 下载部署脚本
wget https://raw.githubusercontent.com/rissalith/FrameWorker/master/deploy.sh

# 3. 运行部署脚本
sudo bash deploy.sh

# 4. 按照提示配置环境变量
nano /var/www/FrameWorker/backend/.env
```

#### 方法 2: 手动部署

详细步骤请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

### 部署后配置

1. **配置环境变量**
```bash
cd /var/www/FrameWorker/backend
nano .env
```

必须配置的项：
- `SECRET_KEY`: 生成强随机密钥
- `JWT_SECRET_KEY`: 生成另一个强随机密钥
- `FLASK_ENV`: 设置为 `production`

可选配置：
- Google OAuth 配置
- 邮件服务配置
- 短信服务配置

2. **配置 HTTPS（强烈推荐）**
```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书（替换为你的域名）
sudo certbot --nginx -d your-domain.com

# 测试自动续期
sudo certbot renew --dry-run
```

3. **设置防火墙**
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### 验证部署

1. **检查服务状态**
```bash
sudo systemctl status frameworker
sudo systemctl status nginx
```

2. **查看日志**
```bash
# 应用日志
sudo journalctl -u frameworker -f

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

3. **访问应用**
- 浏览器访问：`http://your-server-ip` 或 `https://your-domain.com`
- 测试登录功能
- 测试图片上传和处理功能

### 常见问题

#### 1. 服务无法启动
```bash
# 查看详细错误
sudo journalctl -u frameworker -n 50

# 检查 Python 环境
cd /var/www/FrameWorker/backend
source venv/bin/activate
python app.py
```

#### 2. 502 Bad Gateway
- 检查 Flask 应用是否运行
- 检查端口 3000 是否被占用
- 查看 Nginx 错误日志

#### 3. 数据库权限问题
```bash
sudo chown www-data:www-data /var/www/FrameWorker/backend/frameworker.db
sudo chmod 664 /var/www/FrameWorker/backend/frameworker.db
```

### 更新部署

当有新版本时：

```bash
cd /var/www/FrameWorker
git pull origin master
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart frameworker
```

### 备份策略

建议设置定期备份：

```bash
# 创建备份脚本
sudo nano /usr/local/bin/backup-frameworker.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/frameworker"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp /var/www/FrameWorker/backend/frameworker.db $BACKUP_DIR/frameworker_$DATE.db
find $BACKUP_DIR -name "frameworker_*.db" -mtime +30 -delete
```

```bash
# 添加执行权限
sudo chmod +x /usr/local/bin/backup-frameworker.sh

# 添加到 crontab（每天凌晨 2 点备份）
sudo crontab -e
# 添加：0 2 * * * /usr/local/bin/backup-frameworker.sh
```

## 📊 监控和维护

### 性能监控

建议使用以下工具：
- Prometheus + Grafana
- New Relic
- Datadog

### 日志管理

```bash
# 查看实时日志
sudo journalctl -u frameworker -f

# 查看最近的错误
sudo journalctl -u frameworker -p err -n 50

# 清理旧日志
sudo journalctl --vacuum-time=7d
```

### 安全建议

1. 定期更新系统和依赖包
2. 使用强密码和密钥
3. 启用 HTTPS
4. 配置防火墙规则
5. 定期备份数据库
6. 限制文件上传大小
7. 实施速率限制
8. 监控异常访问

## 🆘 获取帮助

如果遇到问题：

1. 查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 详细文档
2. 查看 [GitHub Issues](https://github.com/rissalith/FrameWorker/issues)
3. 提交新的 Issue 描述问题

## 📞 联系方式

- GitHub: https://github.com/rissalith/FrameWorker
- Issues: https://github.com/rissalith/FrameWorker/issues

---

**祝部署顺利！** 🎉
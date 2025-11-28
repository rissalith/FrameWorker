# 自动化部署配置检查清单

## ✅ 我已经完成的工作

- [x] 创建 GitHub Actions 工作流文件
- [x] 创建配置文档和工具
- [x] 设置项目结构

## 🔧 您需要完成的配置

### 步骤 1：生成密钥（5 分钟）

在本地项目目录运行：

```bash
python3 .github/generate-secrets.py
```

这会生成所有需要的随机密钥，并显示在终端。**请保存这些密钥！**

### 步骤 2：配置 GitHub Secrets（10 分钟）

#### 2.1 访问 Secrets 设置页面

打开浏览器，访问：
```
https://github.com/rissalith/FrameWorker/settings/secrets/actions
```

#### 2.2 添加必需的 Secrets

点击 **"New repository secret"** 按钮，逐个添加以下 9 个必需配置：

| # | Secret 名称 | 从哪里获取 | 示例 |
|---|------------|-----------|------|
| 1 | `SERVER_HOST` | 您的服务器 IP 地址 | `123.456.789.0` |
| 2 | `SERVER_USER` | SSH 登录用户名 | `root` 或 `ubuntu` |
| 3 | `SERVER_SSH_KEY` | SSH 私钥（见下方说明） | `-----BEGIN RSA...` |
| 4 | `MYSQL_ROOT_PASSWORD` | 从步骤 1 生成的密钥复制 | 自动生成的密码 |
| 5 | `MYSQL_PASSWORD` | 从步骤 1 生成的密钥复制 | 自动生成的密码 |
| 6 | `REDIS_PASSWORD` | 从步骤 1 生成的密钥复制 | 自动生成的密码 |
| 7 | `SECRET_KEY` | 从步骤 1 生成的密钥复制 | 自动生成的密钥 |
| 8 | `JWT_SECRET_KEY` | 从步骤 1 生成的密钥复制 | 自动生成的密钥 |
| 9 | `DEEPSEEK_API_KEY` | 从 DeepSeek 官网获取 | `sk-xxxxx` |

#### 2.3 如何获取 SSH 私钥

**如果您已有 SSH 密钥：**

```bash
# 查看现有私钥
cat ~/.ssh/id_rsa
```

**如果需要生成新的 SSH 密钥：**

```bash
# 生成新密钥对
ssh-keygen -t rsa -b 4096 -C "github-actions@deploy" -f ~/.ssh/github_deploy

# 查看私钥（复制到 GitHub Secrets）
cat ~/.ssh/github_deploy

# 查看公钥（需要添加到服务器）
cat ~/.ssh/github_deploy.pub
```

### 步骤 3：配置服务器（15 分钟）

#### 3.1 添加 SSH 公钥到服务器

```bash
# SSH 登录到服务器
ssh root@YOUR_SERVER_IP

# 添加公钥
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### 3.2 安装 Docker

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

#### 3.3 准备部署目录

```bash
# 创建目录
sudo mkdir -p /var/www/FrameWorker
sudo chown -R $USER:$USER /var/www/FrameWorker

# 克隆仓库
cd /var/www
git clone https://github.com/rissalith/FrameWorker.git
cd FrameWorker

# 创建必要的目录
mkdir -p data/mysql data/redis logs/nginx logs/platform logs/game-witch nginx/ssl backups
```

### 步骤 4：测试部署（5 分钟）

#### 4.1 手动触发部署

1. 访问：https://github.com/rissalith/FrameWorker/actions
2. 点击左侧 **"Build and Deploy to Production"**
3. 点击右侧 **"Run workflow"** 按钮
4. 选择 `main` 分支
5. 点击绿色的 **"Run workflow"** 按钮

#### 4.2 查看部署进度

- 在 Actions 页面可以实时查看部署日志
- 整个过程大约需要 5-10 分钟

#### 4.3 验证部署成功

部署完成后，访问：
```
http://YOUR_SERVER_IP
```

应该能看到网站首页。

## 📋 配置进度追踪

请在完成每个步骤后打勾：

### 本地准备
- [ ] 已运行 `generate-secrets.py` 生成密钥
- [ ] 已保存生成的所有密钥

### GitHub Secrets 配置
- [ ] `SERVER_HOST` 已添加
- [ ] `SERVER_USER` 已添加
- [ ] `SERVER_SSH_KEY` 已添加
- [ ] `MYSQL_ROOT_PASSWORD` 已添加
- [ ] `MYSQL_PASSWORD` 已添加
- [ ] `REDIS_PASSWORD` 已添加
- [ ] `SECRET_KEY` 已添加
- [ ] `JWT_SECRET_KEY` 已添加
- [ ] `DEEPSEEK_API_KEY` 已添加

### 服务器配置
- [ ] SSH 公钥已添加到服务器
- [ ] Docker 已安装
- [ ] Docker Compose 已安装
- [ ] 部署目录已创建
- [ ] 仓库已克隆到服务器

### 部署测试
- [ ] 已手动触发第一次部署
- [ ] 部署成功完成
- [ ] 网站可以正常访问

## 🎯 可选配置（推荐）

完成基本配置后，建议添加以下可选配置以获得完整功能：

### 域名配置（如果有域名）

在 GitHub Secrets 中添加：
- `DOMAIN` - 主域名（如 `xmgamer.com`）
- `API_DOMAIN` - API 域名（如 `api.xmgamer.com`）
- `GAME_WITCH_DOMAIN` - 游戏域名（如 `play-witch.xmgamer.com`）
- `CORS_ORIGINS` - CORS 允许的源

### 数据库配置

在 GitHub Secrets 中添加：
- `MYSQL_DATABASE` - 数据库名称（默认：`xmgamer`）
- `MYSQL_USER` - 数据库用户名（默认：`xmgamer_user`）

## ❓ 常见问题

### Q1: 我没有服务器怎么办？

**答：** 您需要先购买一台云服务器。推荐：
- 阿里云 ECS
- 腾讯云 CVM
- AWS EC2
- DigitalOcean Droplet

最低配置：2核4G，推荐：4核8G

### Q2: 我没有 DeepSeek API Key 怎么办？

**答：** 访问 https://platform.deepseek.com/ 注册并获取 API Key

### Q3: SSH 连接失败怎么办？

**答：** 检查：
1. 服务器 IP 是否正确
2. SSH 端口是否开放（默认 22）
3. 防火墙是否允许 SSH 连接
4. SSH 密钥格式是否正确（包含完整的 BEGIN 和 END 标记）

### Q4: 部署失败怎么办？

**答：** 
1. 查看 GitHub Actions 日志找到具体错误
2. 检查所有 Secrets 是否正确配置
3. 确认服务器可以正常访问
4. 查看 [SECRETS_SETUP.md](SECRETS_SETUP.md) 故障排查部分

## 📞 需要帮助？

- 详细配置指南：[SECRETS_SETUP.md](SECRETS_SETUP.md)
- 快速开始：[README.md](README.md)
- 提交问题：https://github.com/rissalith/FrameWorker/issues

## 🎉 完成后

配置完成后，每次推送代码到 `main` 分支都会自动触发部署：

```bash
git add .
git commit -m "feat: new feature"
git push origin main
```

部署过程会自动：
1. 构建 Docker 镜像
2. 推送到 GitHub Container Registry
3. SSH 到服务器
4. 拉取最新镜像
5. 重启服务
6. 进行健康检查

整个过程无需人工干预！🚀
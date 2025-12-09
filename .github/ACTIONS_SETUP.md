# GitHub Actions 设置指南

本文档说明如何配置 GitHub Actions 以实现自动化部署。

## 前置要求

1. 有一台远端服务器（Linux）
2. 服务器上已安装 Docker 和 Docker Compose
3. 服务器上已经 clone 了项目代码

## 配置步骤

### 1. 生成 SSH 密钥对

在**本地电脑**上生成 SSH 密钥对：

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/maxgamer_deploy

# 会生成两个文件：
# - maxgamer_deploy (私钥，用于 GitHub Secrets)
# - maxgamer_deploy.pub (公钥，添加到服务器)
```

### 2. 将公钥添加到服务器

将公钥内容复制到服务器：

```bash
# 查看公钥内容
cat ~/.ssh/maxgamer_deploy.pub

# 在服务器上执行
mkdir -p ~/.ssh
echo "公钥内容粘贴到这里" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. 配置 GitHub Secrets

进入 GitHub 仓库页面：

1. 点击 **Settings** (设置)
2. 在左侧菜单点击 **Secrets and variables** → **Actions**
3. 点击 **New repository secret** 添加以下密钥：

#### 必须配置的 Secrets

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `SSH_PRIVATE_KEY` | SSH 私钥内容 | 完整的私钥文件内容（包括 BEGIN 和 END 行） |
| `SERVER_HOST` | 服务器 IP 或域名 | `123.456.789.0` 或 `server.example.com` |
| `SERVER_USER` | SSH 登录用户名 | `root` 或 `ubuntu` |
| `DEPLOY_PATH` | 项目在服务器上的路径 | `/root/MaxGamer` 或 `/home/ubuntu/MaxGamer` |

#### 添加 SSH_PRIVATE_KEY

```bash
# 查看私钥内容
cat ~/.ssh/maxgamer_deploy

# 复制完整输出（包括 BEGIN 和 END 行）到 GitHub Secret
```

### 4. 测试 SSH 连接

在添加 Secrets 之前，先测试 SSH 连接是否正常：

```bash
ssh -i ~/.ssh/maxgamer_deploy SERVER_USER@SERVER_HOST

# 如果连接成功，说明配置正确
```

### 5. 启用 GitHub Actions

1. 在仓库页面点击 **Actions** 标签
2. 如果看到提示，点击 **I understand my workflows, go ahead and enable them**
3. 选择 **Enable workflows**

## Workflow 说明

### 1. Deploy to Production (deploy.yml)

**触发条件：**
- 推送到 `main` 分支时自动触发
- 可在 Actions 页面手动触发

**执行步骤：**
1. ✅ 拉取代码
2. ✅ 连接到服务器
3. ✅ 在服务器上执行 `git pull`
4. ✅ 运行 `./deploy.sh --skip-backup`
5. ✅ 验证部署（检查 Docker 容器状态）
6. ✅ 健康检查（访问 API health 端点）

### 2. CI Tests (ci.yml)

**触发条件：**
- 推送到 `main` 或 `develop` 分支
- Pull Request 到 `main` 或 `develop` 分支

**执行步骤：**
1. ✅ 运行 Python 单元测试
2. ✅ 代码质量检查（flake8）
3. ✅ 构建 Docker 镜像
4. ✅ 验证 docker-compose 配置
5. ✅ 前端代码检查

## 手动触发部署

### 方式一：通过 GitHub 网页

1. 访问仓库的 **Actions** 页面
2. 在左侧选择 **Deploy to Production**
3. 点击右侧的 **Run workflow** 按钮
4. 选择分支（通常是 `main`）
5. 点击绿色的 **Run workflow** 按钮

### 方式二：通过 Git 推送

```bash
# 推送到 main 分支会自动触发部署
git push origin main
```

## 查看部署日志

1. 访问仓库的 **Actions** 页面
2. 点击最近的 workflow 运行
3. 点击具体的 job 查看详细日志

## 故障排查

### 问题 1: SSH 连接失败

**错误信息：** `Permission denied (publickey)`

**解决方案：**
1. 检查 `SSH_PRIVATE_KEY` 是否完整（包括 BEGIN 和 END 行）
2. 确认公钥已添加到服务器 `~/.ssh/authorized_keys`
3. 检查服务器上的权限：`chmod 600 ~/.ssh/authorized_keys`

### 问题 2: Git pull 失败

**错误信息：** `fatal: detected dubious ownership`

**解决方案：**

在服务器上执行：
```bash
cd /path/to/MaxGamer
git config --global --add safe.directory $(pwd)
```

### 问题 3: Docker 命令权限不足

**错误信息：** `Got permission denied while trying to connect to the Docker daemon`

**解决方案：**

将部署用户添加到 docker 组：
```bash
sudo usermod -aG docker $USER
# 重新登录或执行
newgrp docker
```

### 问题 4: 部署脚本执行失败

**解决方案：**

确保部署脚本有执行权限：
```bash
chmod +x deploy.sh
```

## 安全建议

1. ✅ **使用专用 SSH 密钥**：不要使用个人 SSH 密钥
2. ✅ **限制 SSH 密钥权限**：配置服务器只允许该密钥执行部署操作
3. ✅ **定期轮换密钥**：每 3-6 个月更换一次 SSH 密钥
4. ✅ **保护 GitHub Secrets**：不要在代码中硬编码任何敏感信息
5. ✅ **审查 workflow 日志**：定期检查部署日志，确保没有异常

## 高级配置

### 配置部署通知

可以添加 Slack、Discord 或邮件通知：

```yaml
- name: Send Slack notification
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 配置多环境部署

可以为不同分支配置不同的部署环境：

```yaml
on:
  push:
    branches:
      - main        # 生产环境
      - staging     # 预发布环境
      - develop     # 开发环境
```

## 禁用自动部署

如果需要暂时禁用自动部署：

1. 访问 **Settings** → **Actions** → **General**
2. 选择 **Disable Actions for this repository**
3. 或者编辑 `.github/workflows/deploy.yml`，在文件顶部添加注释禁用

## 参考资料

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [SSH Agent Action](https://github.com/webfactory/ssh-agent)
- [Docker Build Push Action](https://github.com/docker/build-push-action)

@echo off
chcp 65001 >nul
echo ========================================
echo 🚨 服务器紧急修复 - 中国镜像站版本
echo ========================================
echo.
echo 📋 修复步骤：
echo 1. SSH连接到服务器
echo 2. 配置Docker使用国内镜像站
echo 3. 本地构建Docker镜像
echo 4. 启动所有服务
echo.
echo ⚠️  重要提示：
echo - 使用阿里云/腾讯云/网易云等国内镜像站
echo - 避免从docker.io拉取镜像
echo - 本地构建所有镜像
echo.
pause
echo.

echo 📝 请复制以下命令到SSH终端执行：
echo.
echo ========================================
echo # 步骤1：SSH登录服务器
echo ssh user@your-server
echo.
echo # 步骤2：配置Docker国内镜像（选择一个）
echo.
echo ## 方案A：阿里云镜像
echo sudo mkdir -p /etc/docker
echo sudo tee /etc/docker/daemon.json ^<^<-'EOF'
echo {
echo   "registry-mirrors": [
echo     "https://registry.cn-hangzhou.aliyuncs.com",
echo     "https://docker.mirrors.ustc.edu.cn",
echo     "https://hub-mirror.c.163.com"
echo   ]
echo }
echo EOF
echo sudo systemctl daemon-reload
echo sudo systemctl restart docker
echo.
echo ## 方案B：腾讯云镜像
echo sudo tee /etc/docker/daemon.json ^<^<-'EOF'
echo {
echo   "registry-mirrors": [
echo     "https://mirror.ccs.tencentyun.com"
echo   ]
echo }
echo EOF
echo sudo systemctl daemon-reload
echo sudo systemctl restart docker
echo.
echo # 步骤3：进入项目目录
echo cd /var/www/FrameWorker/XMGamer
echo.
echo # 步骤4：本地构建镜像（不从远程拉取）
echo docker build -t ghcr.io/rissalith/xmgamer-platform-api:latest .
echo.
echo # 步骤5：返回上级目录
echo cd ..
echo.
echo # 步骤6：停止现有容器
echo docker-compose -f docker-compose.prod.yml down
echo.
echo # 步骤7：启动所有服务
echo docker-compose -f docker-compose.prod.yml up -d
echo.
echo # 步骤8：查看容器状态
echo docker-compose -f docker-compose.prod.yml ps
echo.
echo # 步骤9：查看日志
echo docker-compose -f docker-compose.prod.yml logs -f platform-api
echo.
echo # 步骤10：测试服务
echo curl http://localhost:5000/health
echo curl https://www.xmframer.com
echo ========================================
echo.
echo 💡 提示：
echo - 如果构建失败，检查Dockerfile中的基础镜像
echo - 可能需要修改Dockerfile使用国内镜像
echo - 例如：FROM python:3.9 改为 FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.9
echo.
echo 📄 详细文档请查看：FINAL_EMERGENCY_FIX.md
echo.
pause
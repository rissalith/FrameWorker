@echo off
chcp 65001 >nul
echo ==========================================
echo 🚨 紧急修复服务器 - 直接SSH方案
echo ==========================================
echo.
echo 此脚本将连接到服务器并执行以下操作：
echo 1. 在服务器上本地构建Docker镜像
echo 2. 启动所有容器
echo 3. 验证服务状态
echo.
echo ⚠️  请确保您有服务器的SSH访问权限
echo.
pause

REM 服务器信息（从GitHub Secrets获取）
REM 您需要手动输入这些信息
set /p SERVER_HOST=请输入服务器地址（例如：your-server.com）: 
set /p SERVER_USER=请输入SSH用户名（例如：root）: 
set /p SSH_KEY_PATH=请输入SSH密钥路径（留空使用密码认证）: 

echo.
echo ==========================================
echo 开始执行修复...
echo ==========================================
echo.

REM 构建SSH命令
set "SSH_CMD=ssh"
if not "%SSH_KEY_PATH%"=="" (
    set "SSH_CMD=ssh -i "%SSH_KEY_PATH%""
)

echo 步骤 1/5: 连接到服务器...
%SSH_CMD% %SERVER_USER%@%SERVER_HOST% "echo '✅ SSH连接成功'"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ SSH连接失败！
    echo 请检查：
    echo - 服务器地址是否正确
    echo - SSH密钥是否有效
    echo - 网络连接是否正常
    pause
    exit /b 1
)

echo.
echo 步骤 2/5: 进入项目目录并构建Docker镜像...
%SSH_CMD% %SERVER_USER%@%SERVER_HOST% "cd /var/www/FrameWorker/XMGamer && docker build -t ghcr.io/rissalith/xmgamer-platform-api:latest ."
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker镜像构建失败！
    pause
    exit /b 1
)

echo.
echo 步骤 3/5: 停止旧容器...
%SSH_CMD% %SERVER_USER%@%SERVER_HOST% "cd /var/www/FrameWorker && docker-compose -f docker-compose.prod.yml down"

echo.
echo 步骤 4/5: 启动所有服务...
%SSH_CMD% %SERVER_USER%@%SERVER_HOST% "cd /var/www/FrameWorker && docker-compose -f docker-compose.prod.yml up -d"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 容器启动失败！
    pause
    exit /b 1
)

echo.
echo 步骤 5/5: 检查服务状态...
%SSH_CMD% %SERVER_USER%@%SERVER_HOST% "cd /var/www/FrameWorker && docker-compose -f docker-compose.prod.yml ps && docker-compose -f docker-compose.prod.yml logs --tail=50 platform-api"

echo.
echo ==========================================
echo ✅ 修复完成！
echo ==========================================
echo.
echo 等待10秒后测试网站...
timeout /t 10 /nobreak >nul

echo.
echo 测试网站健康状态...
curl -f https://www.xmframer.com/health
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 网站已恢复正常！
) else (
    echo.
    echo ⚠️  网站可能还在启动中，请稍后手动检查
)

echo.
echo ==========================================
echo 后续步骤：
echo 1. 访问 https://www.xmframer.com 验证网站
echo 2. 检查 GitHub Actions 为什么没有构建镜像
echo 3. 修复 workflow 配置防止未来问题
echo ==========================================
echo.
pause
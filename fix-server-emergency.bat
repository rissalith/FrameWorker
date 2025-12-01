@echo off
chcp 65001 >nul
echo ==========================================
echo 紧急修复服务器 - SSH自动化脚本
echo ==========================================
echo.
echo 此脚本将通过SSH连接到服务器并执行修复
echo.
echo 需要的信息（从GitHub Secrets获取）：
echo - SERVER_HOST
echo - SERVER_USER  
echo - SERVER_SSH_KEY（需要保存为文件）
echo.
echo ==========================================
echo.

REM 检查是否安装了ssh
where ssh >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 错误：未找到SSH客户端
    echo 请安装OpenSSH或使用Git Bash
    pause
    exit /b 1
)

echo 请输入服务器信息：
echo.
set /p SERVER_HOST=服务器地址: 
set /p SERVER_USER=用户名: 
set /p SSH_KEY_PATH=SSH密钥文件路径（留空使用密码）: 

echo.
echo ==========================================
echo 开始修复...
echo ==========================================
echo.

REM 构建SSH命令
if "%SSH_KEY_PATH%"=="" (
    REM 使用密码认证
    ssh %SERVER_USER%@%SERVER_HOST% "cd /var/www/FrameWorker && cd XMGamer && docker build -t ghcr.io/rissalith/xmgamer-platform-api:latest . && cd .. && docker-compose -f docker-compose.prod.yml up -d && docker-compose -f docker-compose.prod.yml ps"
) else (
    REM 使用密钥认证
    ssh -i "%SSH_KEY_PATH%" %SERVER_USER%@%SERVER_HOST% "cd /var/www/FrameWorker && cd XMGamer && docker build -t ghcr.io/rissalith/xmgamer-platform-api:latest . && cd .. && docker-compose -f docker-compose.prod.yml up -d && docker-compose -f docker-compose.prod.yml ps"
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo ✅ 修复完成！
    echo ==========================================
    echo.
    echo 正在测试服务...
    timeout /t 5 /nobreak >nul
    curl -f https://www.xmframer.com/health
    echo.
) else (
    echo.
    echo ==========================================
    echo ❌ 修复失败
    echo ==========================================
    echo.
    echo 请检查：
    echo 1. SSH连接是否正常
    echo 2. 服务器上是否有Docker
    echo 3. 项目目录是否正确
    echo.
)

pause
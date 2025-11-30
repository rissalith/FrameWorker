@echo off
chcp 65001 >nul
echo ==========================================
echo XMGamer CORS修复部署
echo ==========================================
echo.

echo 📦 步骤1: 提交代码更改...
git add XMGamer/backend/app.py
git commit -m "修复CORS配置以支持跨域API请求"
if errorlevel 1 (
    echo ⚠️  没有新的更改需要提交
) else (
    echo ✅ 代码已提交
)

echo.
echo 📤 步骤2: 推送到远程仓库...
git push origin main
if errorlevel 1 (
    git push origin master
)

echo.
echo ✅ 代码已推送到远程仓库
echo.
echo ==========================================
echo 🚀 接下来需要在服务器上执行以下操作：
echo ==========================================
echo.
echo 方式1: 手动SSH登录服务器
echo   ssh root@api.xmframer.com
echo   cd /root/xmgamer
echo   git pull
echo   docker-compose restart backend
echo.
echo 方式2: 一键远程部署（如果已配置SSH密钥）
echo   ssh root@api.xmframer.com "cd /root/xmgamer && git pull && docker-compose restart backend"
echo.
echo ==========================================
echo.
pause
@echo off
chcp 65001 >nul
echo ==========================================
echo 🔄 触发GitHub Actions重新构建
echo ==========================================
echo.
echo 此脚本将：
echo 1. 创建一个小的提交来触发workflow
echo 2. 推送到GitHub
echo 3. 自动触发 build-and-push 和 deploy
echo.
pause

echo.
echo 步骤 1/3: 创建触发提交...
echo # Rebuild triggered at %date% %time% >> .rebuild-trigger

git add .rebuild-trigger
git commit -m "chore: trigger rebuild - fix missing Docker image"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git提交失败
    pause
    exit /b 1
)

echo.
echo 步骤 2/3: 推送到GitHub...
git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git推送失败
    echo 尝试推送到master分支...
    git push origin master
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ 推送失败，请检查Git配置
        pause
        exit /b 1
    )
)

echo.
echo ✅ 推送成功！
echo.
echo 步骤 3/3: 查看GitHub Actions状态...
echo.
echo 请访问以下链接查看构建进度：
echo https://github.com/Rissalith/FrameWorker/actions
echo.
echo 预计需要5-10分钟完成构建和部署
echo.
echo ==========================================
echo 后续步骤：
echo 1. 在浏览器中打开上述链接
echo 2. 确认 "Build and Deploy to Production" workflow正在运行
echo 3. 等待两个job都完成（build-and-push 和 deploy）
echo 4. 验证网站恢复：https://www.xmframer.com
echo ==========================================
echo.

REM 尝试在浏览器中打开GitHub Actions页面
start https://github.com/Rissalith/FrameWorker/actions

pause
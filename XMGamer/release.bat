@echo off
chcp 65001 >nul
echo ================================
echo 快速版本发布脚本
echo ================================
echo.

REM 检查Git状态
git status --short >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：Git仓库有问题
    pause
    exit /b 1
)

echo 📋 当前未提交的更改：
git status --short
echo.

REM 获取当前版本
for /f "tokens=*" %%i in ('git describe --tags --abbrev=0 2^>nul') do set current_version=%%i
if "%current_version%"=="" set current_version=v1.0.0

echo 📌 当前版本: %current_version%
echo.
echo 请选择版本类型：
echo   1. 修订版本 (v1.0.X) - Bug修复、小优化
echo   2. 次版本 (v1.X.0) - 新功能、功能增强
echo   3. 主版本 (vX.0.0) - 重大更新、不兼容改动
echo.
set /p choice=请输入选择 (1/2/3): 

echo.
set /p new_version=请输入新版本号 (例如 v1.0.1): 
set /p message=请输入版本说明: 

echo.
echo ================================
echo 📦 准备发布版本
echo ================================
echo 当前版本: %current_version%
echo 新版本: %new_version%
echo 说明: %message%
echo.
set /p confirm=确认发布? (y/n): 

if /i not "%confirm%"=="y" (
    echo ❌ 已取消发布
    pause
    exit /b 0
)

echo.
echo 🔄 正在提交代码...
git add .
git commit -m "%message%"
if errorlevel 1 (
    echo ⚠️  没有新的更改需要提交
)

echo.
echo 🏷️  正在创建标签...
git tag -a %new_version% -m "%message%"
if errorlevel 1 (
    echo ❌ 创建标签失败
    pause
    exit /b 1
)

echo.
echo 📤 正在推送到GitHub...
git push origin master
if errorlevel 1 (
    echo ❌ 推送代码失败
    pause
    exit /b 1
)

git push origin --tags
if errorlevel 1 (
    echo ❌ 推送标签失败
    pause
    exit /b 1
)

echo.
echo ================================
echo ✅ 版本发布成功！
echo ================================
echo 📌 版本: %new_version%
echo 📝 说明: %message%
echo 🌐 GitHub: https://github.com/rissalith/FrameWorker
echo 🏷️  标签: https://github.com/rissalith/FrameWorker/tags
echo 📦 Release: https://github.com/rissalith/FrameWorker/releases
echo.
echo 📋 下一步操作：
echo   1. 访问 GitHub 创建 Release（推荐）
echo   2. 运行 deploy-final.bat 部署到服务器
echo   3. 访问 https://www.xmframer.com 验证功能
echo.
pause
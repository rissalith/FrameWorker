@echo off
chcp 65001 >nul
echo ========================================
echo    MaxGamer 版本号更新工具
echo ========================================
echo.

cd /d "%~dp0"

node update-version.js

echo.
echo ========================================
pause
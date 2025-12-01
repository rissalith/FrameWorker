@echo off
chcp 65001 >nul
echo ========================================
echo 检查GitHub Actions Workflow状态
echo ========================================
echo.

echo 📋 获取最新的workflow运行记录...
echo.

powershell -Command "gh run list --repo rissalith/FrameWorker --limit 5 --json databaseId,status,conclusion,name,createdAt,headBranch | ConvertFrom-Json | ForEach-Object { Write-Host ('ID: ' + $_.databaseId + ' | 状态: ' + $_.status + ' | 结果: ' + $_.conclusion + ' | 分支: ' + $_.headBranch + ' | 时间: ' + $_.createdAt) }"

echo.
echo ========================================
echo 检查最新运行的详细信息
echo ========================================
echo.

powershell -Command "gh run view --repo rissalith/FrameWorker"

echo.
echo 按任意键退出...
pause >nul
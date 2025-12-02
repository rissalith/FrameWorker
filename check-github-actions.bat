@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   GitHub Actions 状态检查
echo ========================================
echo.
echo 📋 最近的提交:
echo    Commit: 049d17c
echo    Message: fix: 简化workflow build job配置,移除matrix strategy
echo    Time: 刚刚推送
echo.
echo 🔗 查看GitHub Actions执行状态:
echo    https://github.com/rissalith/FrameWorker/actions
echo.
echo 📊 预期执行流程:
echo    1. ⏳ GitHub检测到push事件
echo    2. ⏳ 触发deploy.yml workflow
echo    3. ⏳ Build and Push Docker Images job 执行
echo    4. ⏳ Deploy to Server job 执行
echo    5. ✅ 服务恢复
echo.
echo ⏱️  预计总时间: 5-8分钟
echo.
echo 💡 提示:
echo    - 请在浏览器中打开上述链接查看实时进度
echo    - 如果5分钟后build job仍未执行,请使用备用方案
echo    - 备用方案: 运行 fix-server-china-mirror.bat
echo.
echo ========================================
echo.
pause
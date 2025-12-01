@echo off
chcp 65001 >nul
echo ==========================================
echo 监控部署进度
echo ==========================================
echo.
echo GitHub Actions: https://github.com/Rissalith/FrameWorker/actions
echo.
echo 正在检查服务器状态...
echo.

:loop
echo [%time%] 检查中...

REM 检查网站健康状态
curl -s -o nul -w "HTTP状态码: %%{http_code}\n" https://www.xmframer.com/health

if %ERRORLEVEL% EQU 0 (
    echo ✅ 服务器响应正常！
    echo.
    echo 测试完整响应...
    curl -s https://www.xmframer.com/health
    echo.
    echo.
    echo ==========================================
    echo ✅ 部署成功！服务已恢复！
    echo ==========================================
    echo.
    echo 请验证以下功能：
    echo 1. 访问 https://www.xmframer.com
    echo 2. 测试登录功能
    echo 3. 测试AI对话功能
    echo.
    goto end
) else (
    echo ⏳ 服务器还在启动中...
    echo 等待30秒后重试...
    timeout /t 30 /nobreak >nul
    goto loop
)

:end
pause
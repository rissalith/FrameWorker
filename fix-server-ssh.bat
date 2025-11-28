@echo off
chcp 65001 >nul
echo ========================================
echo 修复服务器 SSH 公钥认证配置
echo ========================================
echo.

echo [1/4] 连接到服务器并启用公钥认证...
ssh root@149.88.69.87 "cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup && sed -i 's/^PubkeyAuthentication no/PubkeyAuthentication yes/' /etc/ssh/sshd_config && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys && systemctl restart sshd"

if %errorlevel% neq 0 (
    echo ❌ 修复失败！请检查网络连接或手动修复。
    pause
    exit /b 1
)

echo ✅ 配置已更新
echo.

echo [2/4] 验证配置...
ssh root@149.88.69.87 "grep PubkeyAuthentication /etc/ssh/sshd_config"
echo.

echo [3/4] 测试 SSH 密钥连接...
cd /d "%~dp0"
ssh -i frameworker_key root@149.88.69.87 "echo '✅ SSH 密钥认证成功！'"

if %errorlevel% neq 0 (
    echo ❌ SSH 密钥测试失败！
    echo 请检查：
    echo 1. 公钥是否正确添加到服务器
    echo 2. 私钥文件是否存在：frameworker_key
    echo 3. SSH 服务是否正常运行
    pause
    exit /b 1
)

echo.
echo [4/4] 显示服务器 SSH 状态...
ssh root@149.88.69.87 "systemctl status sshd | head -5"
echo.

echo ========================================
echo ✅ 修复完成！
echo ========================================
echo.
echo 下一步：
echo 1. 重新触发 GitHub Actions 部署
echo 2. 监控部署状态
echo.
echo 执行以下命令重新部署：
echo   git commit --allow-empty -m "test: 重新部署 - 已启用公钥认证"
echo   git push origin main
echo.
pause
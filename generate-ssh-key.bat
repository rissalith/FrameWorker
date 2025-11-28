@echo off
echo ========================================
echo 生成 GitHub Actions SSH 密钥
echo ========================================
echo.

echo [1/4] 生成 ED25519 密钥对...
ssh-keygen -t ed25519 -C "github-actions@frameworker" -f frameworker_key -N ""

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [警告] ED25519 生成失败，尝试使用 RSA...
    ssh-keygen -t rsa -b 4096 -C "github-actions@frameworker" -f frameworker_key -N ""
)

echo.
echo [2/4] 密钥生成成功！
echo.

echo ========================================
echo 私钥内容（用于 GitHub Secrets）
echo ========================================
type frameworker_key
echo.
echo ========================================

echo.
echo [3/4] 公钥内容（用于服务器）
echo ========================================
type frameworker_key.pub
echo.
echo ========================================

echo.
echo [4/4] 下一步操作：
echo.
echo 1. 复制上面的私钥内容（从 -----BEGIN 到 -----END）
echo 2. 访问: https://github.com/rissalith/FrameWorker/settings/secrets/actions
echo 3. 更新 SERVER_SSH_KEY，粘贴完整的私钥
echo.
echo 4. 将公钥添加到服务器：
echo    ssh user@YOUR_SERVER_IP
echo    mkdir -p ~/.ssh
echo    echo "公钥内容" ^>^> ~/.ssh/authorized_keys
echo    chmod 600 ~/.ssh/authorized_keys
echo.
echo 5. 测试连接：
echo    ssh -i frameworker_key user@YOUR_SERVER_IP
echo.
echo ========================================
pause
@echo off
chcp 65001 >nul
echo ========================================
echo 🔧 服务器紧急修复脚本
echo ========================================
echo.
echo 服务器: 149.88.69.87
echo 用户: root
echo.
echo 正在连接服务器并执行修复...
echo.

sshpass -p "pXw1995" ssh -o StrictHostKeyChecking=no root@149.88.69.87 "cd /var/www/FrameWorker && echo '=== 当前目录 ===' && pwd && echo '=== 停止所有容器 ===' && docker kill $(docker ps -q) 2>/dev/null || true && docker rm -f $(docker ps -aq) 2>/dev/null || true && echo '=== 启动服务 ===' && docker-compose -f docker-compose.prod.yml up -d && echo '=== 查看容器状态 ===' && docker-compose -f docker-compose.prod.yml ps && echo '=== 查看日志 ===' && docker-compose -f docker-compose.prod.yml logs --tail=50 platform-api"

echo.
echo ========================================
echo 修复完成!
echo ========================================
pause
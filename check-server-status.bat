@echo off
echo ========================================
echo 检查服务器状态
echo ========================================
echo.

echo [1] 检查容器状态...
ssh root@149.88.69.87 "docker ps -a | grep xmgamer"
echo.

echo [2] 检查端口监听...
ssh root@149.88.69.87 "netstat -tlnp | grep -E '80|5000'"
echo.

echo [3] 测试健康检查端点...
curl -I http://149.88.69.87/health
echo.

echo [4] 检查最新日志...
echo --- Nginx 日志 ---
ssh root@149.88.69.87 "docker logs --tail 10 xmgamer-gateway 2>&1"
echo.
echo --- API 日志 ---
ssh root@149.88.69.87 "docker logs --tail 10 xmgamer-api 2>&1"
echo.

echo ========================================
echo 检查完成
echo ========================================
pause
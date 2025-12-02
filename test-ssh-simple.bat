@echo off
echo ========================================
echo 测试SSH连接
echo ========================================
echo.

echo 尝试简单的SSH命令...
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@8.138.115.175 "echo 'SSH连接成功'"

echo.
echo 如果上面显示"SSH连接成功",说明SSH工作正常
echo 如果卡住或超时,说明SSH连接有问题
pause
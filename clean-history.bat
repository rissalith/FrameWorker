@echo off
echo ========================================
echo 警告：这将彻底重写Git历史！
echo ========================================
echo.
echo 这个操作将：
echo 1. 删除所有历史记录
echo 2. 创建一个全新的初始提交
echo 3. 强制推送到GitHub
echo.
echo 敏感信息将被完全清除，但：
echo - 所有提交历史将丢失
echo - 版本标签将丢失
echo - 需要重新创建标签
echo.
set /p confirm=确认执行？这个操作不可逆！(yes/no): 

if /i not "%confirm%"=="yes" (
    echo 已取消操作
    pause
    exit /b 0
)

echo.
echo 正在清理历史...
echo.

REM 1. 删除所有远程分支和标签
git push origin --delete v1.0.0 2>nul

REM 2. 删除本地标签
git tag -d v1.0.0 2>nul

REM 3. 创建孤立分支（没有历史）
git checkout --orphan latest_branch

REM 4. 添加所有文件
git add -A

REM 5. 创建新的初始提交
git commit -m "feat: FrameWorker v1.0.0 - 初始版本（安全清理后）

主要功能：
- AI生成动画精灵图
- 帧插值功能
- 历史记录管理
- GIF导出功能
- 自定义Prompt模板系统

安全说明：
- 所有敏感信息已移除
- API密钥通过.env文件管理
- 部署脚本已从仓库中排除"

REM 6. 删除旧的master分支
git branch -D master

REM 7. 重命名当前分支为master
git branch -m master

REM 8. 强制推送到远程
echo.
echo 正在强制推送到GitHub...
git push -f origin master

REM 9. 重新创建标签
git tag -a v1.0.0 -m "FrameWorker v1.0.0 - 首个正式版本（安全清理后）"
git push origin v1.0.0

echo.
echo ========================================
echo 历史清理完成！
echo ========================================
echo.
echo 下一步：
echo 1. 访问 GitHub 检查历史是否已清理
echo 2. 立即撤销泄露的API密钥
echo 3. 修改服务器密码
echo.
pause
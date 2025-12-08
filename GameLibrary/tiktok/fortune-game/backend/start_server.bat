@echo off
echo ========================================
echo 启动抖音直播间监控服务器
echo ========================================
cd /d %~dp0

REM 优先使用Python 3.12或更低版本（避免3.14兼容性问题）

REM 尝试Python 3.12路径
if exist "C:\Python313\python.exe" (
    echo 找到Python 3.13
    C:\Python313\python.exe app.py
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    echo 找到Python 3.13
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" app.py
    goto :end
)

REM 尝试Python 3.12路径
if exist "C:\Python312\python.exe" (
    echo 找到Python 3.12
    C:\Python312\python.exe app.py
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    echo 找到Python 3.12
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" app.py
    goto :end
)

REM 尝试Python 3.13路径
if exist "C:\Python313\python.exe" (
    echo 找到Python 3.13
    C:\Python313\python.exe app.py
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    echo 找到Python 3.13
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" app.py
    goto :end
)

REM 尝试Python 3.11路径
if exist "C:\Python311\python.exe" (
    echo 找到Python 3.11
    C:\Python311\python.exe app.py
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    echo 找到Python 3.11
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" app.py
    goto :end
)

REM 尝试Python 3.10路径
if exist "C:\Python310\python.exe" (
    echo 找到Python 3.10
    C:\Python310\python.exe app.py
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    echo 找到Python 3.10
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" app.py
    goto :end
)

REM 尝试Python 3.9路径
if exist "C:\Python39\python.exe" (
    echo 找到Python 3.9
    C:\Python39\python.exe app.py
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
    echo 找到Python 3.9
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" app.py
    goto :end
)

REM 尝试使用系统PATH中的python（最后尝试）
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo 使用系统Python环境
    python app.py
    goto :end
)

REM 尝试使用py启动器
where py >nul 2>nul
if %errorlevel% equ 0 (
    echo 使用py启动器
    py -3.12 app.py
    if %errorlevel% neq 0 (
        py app.py
    )
    goto :end
)

REM 尝试Python 3.14路径（最后选择）
if exist "C:\Python314\python.exe" (
    echo 找到Python 3.14（可能存在兼容性问题）
    C:\Python314\python.exe app.py
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    echo 找到Python 3.14（可能存在兼容性问题）
    "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" app.py
    goto :end
)

echo.
echo ========================================
echo 错误: 未找到合适的Python环境！
echo ========================================
echo 推荐使用Python 3.9-3.12版本
echo Python 3.14可能存在兼容性问题
echo.
echo 安装方法：
echo 1. 访问 https://www.python.org/downloads/
echo 2. 下载并安装Python 3.12
echo 3. 安装时勾选 "Add Python to PATH"
echo ========================================

:end
pause
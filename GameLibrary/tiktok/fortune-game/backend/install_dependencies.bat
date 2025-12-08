@echo off
echo ========================================
echo 安装Python依赖包
echo ========================================
cd /d %~dp0

REM 优先使用Python 3.12（最佳兼容性）
REM 尝试Python 3.12路径
if exist "C:\Python312\python.exe" (
    echo 使用Python 3.12安装依赖
    C:\Python312\python.exe -m pip install -r ../requirements.txt
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    echo 使用Python 3.12安装依赖
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -m pip install -r ../requirements.txt
    goto :end
)

REM 尝试Python 3.13路径
if exist "C:\Python313\python.exe" (
    echo 使用Python 3.13安装依赖
    C:\Python313\python.exe -m pip install -r ../requirements.txt
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    echo 使用Python 3.13安装依赖
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" -m pip install -r ../requirements.txt
    goto :end
)

REM 尝试Python 3.11路径
if exist "C:\Python311\python.exe" (
    echo 使用Python 3.11安装依赖
    C:\Python311\python.exe -m pip install -r ../requirements.txt
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    echo 使用Python 3.11安装依赖
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" -m pip install -r ../requirements.txt
    goto :end
)

REM 尝试Python 3.10路径
if exist "C:\Python310\python.exe" (
    echo 使用Python 3.10安装依赖
    C:\Python310\python.exe -m pip install -r ../requirements.txt
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    echo 使用Python 3.10安装依赖
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" -m pip install -r ../requirements.txt
    goto :end
)

REM 尝试Python 3.9路径
if exist "C:\Python39\python.exe" (
    echo 使用Python 3.9安装依赖
    C:\Python39\python.exe -m pip install -r ../requirements.txt
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
    echo 使用Python 3.9安装依赖
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" -m pip install -r ../requirements.txt
    goto :end
)

REM 尝试使用系统PATH中的python（最后尝试）
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo 使用系统Python环境安装依赖
    python -m pip install -r ../requirements.txt
    goto :end
)

REM 尝试使用py启动器
where py >nul 2>nul
if %errorlevel% equ 0 (
    echo 使用py启动器安装依赖
    py -3.12 -m pip install -r ../requirements.txt
    if %errorlevel% neq 0 (
        py -m pip install -r ../requirements.txt
    )
    goto :end
)

REM 尝试Python 3.14路径（最后选择，可能有兼容性问题）
if exist "C:\Python314\python.exe" (
    echo 使用Python 3.14安装依赖（可能存在兼容性问题）
    C:\Python314\python.exe -m pip install -r ../requirements.txt
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    echo 使用Python 3.14安装依赖（可能存在兼容性问题）
    "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" -m pip install -r ../requirements.txt
    goto :end
)

echo.
echo ========================================
echo 错误: 未找到合适的Python环境！
echo ========================================
echo 推荐使用Python 3.9-3.12版本
echo Python 3.14可能存在兼容性问题
echo.

:end
echo.
echo ========================================
echo 依赖安装完成！
echo ========================================
pause
# ========================================
# FrameWorker 一键部署脚本
# 使用 plink 自动输入密码
# ========================================

param(
    [string]$Password = "pXw1995"
)

$SERVER_IP = "149.88.69.87"
$SERVER_USER = "root"
$PROJECT_DIR = "/var/www/xmframer"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FrameWorker 一键自动部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否安装了 plink
$plinkInstalled = Get-Command plink -ErrorAction SilentlyContinue

if (-not $plinkInstalled) {
    Write-Host "正在下载 PuTTY 工具..." -ForegroundColor Yellow
    $puttyUrl = "https://the.earth.li/~sgtatham/putty/latest/w64/plink.exe"
    $plinkPath = "$env:TEMP\plink.exe"
    
    try {
        Invoke-WebRequest -Uri $puttyUrl -OutFile $plinkPath -UseBasicParsing
        Write-Host "✓ PuTTY 下载完成" -ForegroundColor Green
        $plink = $plinkPath
    } catch {
        Write-Host "✗ 下载失败，将使用标准 SSH（需要手动输入密码）" -ForegroundColor Red
        $plink = $null
    }
} else {
    $plink = "plink"
    Write-Host "✓ 检测到 PuTTY 工具" -ForegroundColor Green
}

Write-Host ""

# ========================================
# 函数：执行远程命令
# ========================================
function Invoke-RemoteCommand {
    param(
        [string]$Command
    )
    
    if ($plink) {
        & $plink -batch -pw $Password ${SERVER_USER}@${SERVER_IP} $Command
    } else {
        Write-Host "执行: $Command" -ForegroundColor Gray
        ssh ${SERVER_USER}@${SERVER_IP} $Command
    }
}

# ========================================
# 函数：上传文件
# ========================================
function Upload-File {
    param(
        [string]$LocalPath,
        [string]$RemotePath
    )
    
    if ($plink) {
        $pscp = $plink -replace "plink", "pscp"
        if (Test-Path $pscp) {
            & $pscp -batch -pw $Password $LocalPath ${SERVER_USER}@${SERVER_IP}:${RemotePath}
        } else {
            # 下载 pscp
            $pscpUrl = "https://the.earth.li/~sgtatham/putty/latest/w64/pscp.exe"
            $pscpPath = "$env:TEMP\pscp.exe"
            Invoke-WebRequest -Uri $pscpUrl -OutFile $pscpPath -UseBasicParsing
            & $pscpPath -batch -pw $Password $LocalPath ${SERVER_USER}@${SERVER_IP}:${RemotePath}
        }
    } else {
        scp $LocalPath ${SERVER_USER}@${SERVER_IP}:${RemotePath}
    }
}

# ========================================
# 步骤 1: 创建远程目录
# ========================================
Write-Host "步骤 1/5: 创建远程目录..." -ForegroundColor Cyan
Invoke-RemoteCommand "mkdir -p $PROJECT_DIR/frontend $PROJECT_DIR/backend $PROJECT_DIR/prompts"
Write-Host "✓ 目录创建完成" -ForegroundColor Green

# ========================================
# 步骤 2: 上传后端文件
# ========================================
Write-Host ""
Write-Host "步骤 2/5: 上传后端文件..." -ForegroundColor Cyan

$backendFiles = @(
    @{Local="backend/app.py"; Remote="$PROJECT_DIR/backend/app.py"},
    @{Local="backend/image_processor.py"; Remote="$PROJECT_DIR/backend/image_processor.py"},
    @{Local="backend/requirements.txt"; Remote="$PROJECT_DIR/backend/requirements.txt"},
    @{Local="backend/.env.example"; Remote="$PROJECT_DIR/backend/.env.example"}
)

foreach ($file in $backendFiles) {
    if (Test-Path $file.Local) {
        $fileName = Split-Path $file.Local -Leaf
        Write-Host "  上传 $fileName..." -ForegroundColor Gray
        Upload-File -LocalPath $file.Local -RemotePath $file.Remote
        Write-Host "  ✓ $fileName" -ForegroundColor Green
    }
}

# 上传 .env 文件
if (Test-Path "backend\.env") {
    Write-Host "  上传 .env 配置..." -ForegroundColor Gray
    Upload-File -LocalPath "backend\.env" -RemotePath "$PROJECT_DIR/backend/.env"
    Write-Host "  ✓ .env 文件" -ForegroundColor Green
}

# ========================================
# 步骤 3: 打包并上传前端
# ========================================
Write-Host ""
Write-Host "步骤 3/5: 上传前端文件..." -ForegroundColor Cyan

# 创建临时压缩包
$tempZip = "$env:TEMP\frontend.zip"
if (Test-Path $tempZip) { Remove-Item $tempZip -Force }

Write-Host "  正在打包前端..." -ForegroundColor Gray
Compress-Archive -Path "frontend\*" -DestinationPath $tempZip -Force

Write-Host "  正在上传..." -ForegroundColor Gray
Upload-File -LocalPath $tempZip -RemotePath "$PROJECT_DIR/frontend.zip"

Write-Host "  正在解压..." -ForegroundColor Gray
Invoke-RemoteCommand "cd $PROJECT_DIR; unzip -o frontend.zip -d frontend/; rm -f frontend.zip"

Remove-Item $tempZip -Force
Write-Host "✓ 前端文件上传完成" -ForegroundColor Green

# ========================================
# 步骤 4: 上传部署脚本
# ========================================
Write-Host ""
Write-Host "步骤 4/5: 上传部署脚本..." -ForegroundColor Cyan
Upload-File -LocalPath "deploy-python.sh" -RemotePath "$PROJECT_DIR/deploy-python.sh"
Invoke-RemoteCommand "chmod +x $PROJECT_DIR/deploy-python.sh"
Write-Host "✓ 部署脚本上传完成" -ForegroundColor Green

# ========================================
# 步骤 5: 执行部署
# ========================================
Write-Host ""
Write-Host "步骤 5/5: 执行远程部署..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

if ($plink) {
    # 使用 plink 执行，可以看到实时输出
    & $plink -batch -pw $Password -t ${SERVER_USER}@${SERVER_IP} "cd $PROJECT_DIR; ./deploy-python.sh"
} else {
    # 使用标准 SSH
    ssh -t ${SERVER_USER}@${SERVER_IP} "cd $PROJECT_DIR; ./deploy-python.sh"
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# ========================================
# 完成
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "🎉 部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 访问地址:" -ForegroundColor Cyan
Write-Host "  • 前端: http://$SERVER_IP" -ForegroundColor White
Write-Host "  • API: http://$SERVER_IP/api/health" -ForegroundColor White
Write-Host ""
Write-Host "📊 管理命令:" -ForegroundColor Cyan
if ($plink) {
    Write-Host "  • 查看日志: " -NoNewline -ForegroundColor White
    Write-Host "$plink -batch -pw $Password ${SERVER_USER}@${SERVER_IP} 'sudo journalctl -u frameworker -f'" -ForegroundColor Gray
    Write-Host "  • 重启服务: " -NoNewline -ForegroundColor White
    Write-Host "$plink -batch -pw $Password ${SERVER_USER}@${SERVER_IP} 'sudo systemctl restart frameworker'" -ForegroundColor Gray
} else {
    Write-Host "  • 查看日志: ssh ${SERVER_USER}@${SERVER_IP} 'sudo journalctl -u frameworker -f'" -ForegroundColor White
    Write-Host "  • 重启服务: ssh ${SERVER_USER}@${SERVER_IP} 'sudo systemctl restart frameworker'" -ForegroundColor White
}
Write-Host ""
Write-Host "⚠️  重要提示:" -ForegroundColor Yellow
Write-Host "  请确保服务器上的 .env 文件包含正确的 API 密钥" -ForegroundColor Yellow
Write-Host "  编辑命令: " -NoNewline -ForegroundColor Yellow
if ($plink) {
    Write-Host "$plink -batch -pw $Password ${SERVER_USER}@${SERVER_IP} 'nano $PROJECT_DIR/backend/.env'" -ForegroundColor Gray
} else {
    Write-Host "ssh ${SERVER_USER}@${SERVER_IP} 'nano $PROJECT_DIR/backend/.env'" -ForegroundColor Gray
}
Write-Host ""
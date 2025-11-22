# ========================================
# FrameWorker 一键自动部署脚本
# 自动输入密码完成部署
# ========================================

$SERVER_IP = "149.88.69.87"
$SERVER_USER = "root"
$SERVER_PASSWORD = "pXw1995"
$PROJECT_DIR = "/var/www/xmframer"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FrameWorker 一键自动部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 plink 是否可用（PuTTY 工具）
$plinkPath = "plink"
if (-not (Get-Command plink -ErrorAction SilentlyContinue)) {
    Write-Host "正在检查部署工具..." -ForegroundColor Yellow
    Write-Host "提示: 如果需要更好的自动化体验，可以安装 PuTTY" -ForegroundColor Gray
}

# ========================================
# 步骤 1: 创建远程目录
# ========================================
Write-Host "步骤 1/4: 创建远程目录..." -ForegroundColor Cyan

$createDirCmd = @"
echo $SERVER_PASSWORD | ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "mkdir -p $PROJECT_DIR/frontend $PROJECT_DIR/backend $PROJECT_DIR/prompts"
"@

# 使用 echo 管道密码的方式
$process = Start-Process powershell -ArgumentList "-Command", "echo $SERVER_PASSWORD | ssh -o StrictHostKeyChecking=no -o PubkeyAuthentication=no $SERVER_USER@$SERVER_IP 'mkdir -p $PROJECT_DIR/frontend $PROJECT_DIR/backend $PROJECT_DIR/prompts'" -Wait -NoNewWindow -PassThru

if ($process.ExitCode -eq 0) {
    Write-Host "✓ 远程目录创建成功" -ForegroundColor Green
} else {
    Write-Host "✗ 目录创建失败，尝试继续..." -ForegroundColor Yellow
}

# ========================================
# 步骤 2: 上传后端文件
# ========================================
Write-Host ""
Write-Host "步骤 2/4: 上传后端文件..." -ForegroundColor Cyan

$backendFiles = @(
    "backend/app.py",
    "backend/image_processor.py",
    "backend/requirements.txt",
    "backend/.env.example"
)

foreach ($file in $backendFiles) {
    if (Test-Path $file) {
        $fileName = Split-Path $file -Leaf
        Write-Host "  上传 $fileName..." -ForegroundColor Gray
        
        # 使用 pscp (PuTTY) 如果可用，否则使用 scp with expect-like behavior
        $remotePath = "$PROJECT_DIR/$($file -replace '\\', '/')"
        
        # 创建临时批处理文件来自动输入密码
        $tempBatch = [System.IO.Path]::GetTempFileName() + ".bat"
        @"
@echo off
echo $SERVER_PASSWORD
"@ | Out-File -FilePath $tempBatch -Encoding ASCII
        
        # 使用管道输入密码
        cmd /c "type `"$tempBatch`" | scp -o StrictHostKeyChecking=no -o PubkeyAuthentication=no `"$file`" ${SERVER_USER}@${SERVER_IP}:${remotePath}" 2>$null
        
        Remove-Item $tempBatch -Force
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $fileName 上传成功" -ForegroundColor Green
        }
    }
}

# 上传 .env 文件（如果存在）
if (Test-Path "backend\.env") {
    Write-Host "  上传 .env 配置..." -ForegroundColor Gray
    $tempBatch = [System.IO.Path]::GetTempFileName() + ".bat"
    @"
@echo off
echo $SERVER_PASSWORD
"@ | Out-File -FilePath $tempBatch -Encoding ASCII
    
    cmd /c "type `"$tempBatch`" | scp -o StrictHostKeyChecking=no -o PubkeyAuthentication=no `"backend\.env`" ${SERVER_USER}@${SERVER_IP}:${PROJECT_DIR}/backend/.env" 2>$null
    Remove-Item $tempBatch -Force
    Write-Host "  ✓ .env 文件上传成功" -ForegroundColor Green
}

# ========================================
# 步骤 3: 上传前端和其他文件
# ========================================
Write-Host ""
Write-Host "步骤 3/4: 上传前端文件..." -ForegroundColor Cyan

# 使用 WinSCP 或创建压缩包的方式
Write-Host "  正在打包前端文件..." -ForegroundColor Gray

# 创建临时压缩包
$tempZip = [System.IO.Path]::GetTempFileName() + ".zip"
Compress-Archive -Path "frontend\*" -DestinationPath $tempZip -Force

# 上传压缩包
$tempBatch = [System.IO.Path]::GetTempFileName() + ".bat"
@"
@echo off
echo $SERVER_PASSWORD
"@ | Out-File -FilePath $tempBatch -Encoding ASCII

cmd /c "type `"$tempBatch`" | scp -o StrictHostKeyChecking=no -o PubkeyAuthentication=no `"$tempZip`" ${SERVER_USER}@${SERVER_IP}:${PROJECT_DIR}/frontend.zip" 2>$null
Remove-Item $tempBatch -Force
Remove-Item $tempZip -Force

Write-Host "  ✓ 前端文件上传成功" -ForegroundColor Green

# 上传部署脚本
Write-Host "  上传部署脚本..." -ForegroundColor Gray
$tempBatch = [System.IO.Path]::GetTempFileName() + ".bat"
@"
@echo off
echo $SERVER_PASSWORD
"@ | Out-File -FilePath $tempBatch -Encoding ASCII

cmd /c "type `"$tempBatch`" | scp -o StrictHostKeyChecking=no -o PubkeyAuthentication=no `"deploy-python.sh`" ${SERVER_USER}@${SERVER_IP}:${PROJECT_DIR}/" 2>$null
Remove-Item $tempBatch -Force

# ========================================
# 步骤 4: 执行远程部署
# ========================================
Write-Host ""
Write-Host "步骤 4/4: 执行远程部署..." -ForegroundColor Cyan
Write-Host "  这可能需要几分钟时间..." -ForegroundColor Yellow

# 创建远程执行脚本
$remoteScript = @"
cd $PROJECT_DIR
unzip -o frontend.zip -d frontend/
rm -f frontend.zip
chmod +x deploy-python.sh
./deploy-python.sh
"@

# 保存到临时文件
$tempScript = [System.IO.Path]::GetTempFileName()
$remoteScript | Out-File -FilePath $tempScript -Encoding UTF8

# 上传并执行
$tempBatch = [System.IO.Path]::GetTempFileName() + ".bat"
@"
@echo off
echo $SERVER_PASSWORD
"@ | Out-File -FilePath $tempBatch -Encoding ASCII

cmd /c "type `"$tempBatch`" | scp -o StrictHostKeyChecking=no -o PubkeyAuthentication=no `"$tempScript`" ${SERVER_USER}@${SERVER_IP}:/tmp/deploy_script.sh" 2>$null
Remove-Item $tempBatch -Force
Remove-Item $tempScript -Force

# 执行部署脚本
Write-Host ""
Write-Host "正在服务器上执行部署..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# 使用 plink 或 ssh 执行
$deployCmd = "bash /tmp/deploy_script.sh"
$tempBatch = [System.IO.Path]::GetTempFileName() + ".bat"
@"
@echo off
echo $SERVER_PASSWORD
"@ | Out-File -FilePath $tempBatch -Encoding ASCII

# 直接显示输出
$pinfo = New-Object System.Diagnostics.ProcessStartInfo
$pinfo.FileName = "cmd.exe"
$pinfo.Arguments = "/c type `"$tempBatch`" | ssh -o StrictHostKeyChecking=no -o PubkeyAuthentication=no -tt ${SERVER_USER}@${SERVER_IP} `"$deployCmd`""
$pinfo.UseShellExecute = $false
$pinfo.RedirectStandardOutput = $false
$pinfo.RedirectStandardError = $false

$p = New-Object System.Diagnostics.Process
$p.StartInfo = $pinfo
$p.Start() | Out-Null
$p.WaitForExit()

Remove-Item $tempBatch -Force

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
Write-Host "访问地址:" -ForegroundColor Cyan
Write-Host "  • 前端: http://$SERVER_IP" -ForegroundColor White
Write-Host "  • API: http://$SERVER_IP/api/health" -ForegroundColor White
Write-Host ""
Write-Host "管理命令:" -ForegroundColor Cyan
Write-Host "  • 查看日志: ssh ${SERVER_USER}@${SERVER_IP} 'sudo journalctl -u frameworker -f'" -ForegroundColor White
Write-Host "  • 重启服务: ssh ${SERVER_USER}@${SERVER_IP} 'sudo systemctl restart frameworker'" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  重要提示:" -ForegroundColor Yellow
Write-Host "  请确保服务器上的 .env 文件包含正确的 API 密钥" -ForegroundColor Yellow
Write-Host ""
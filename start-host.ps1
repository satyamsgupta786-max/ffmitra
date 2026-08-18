# FFMitra local hosted build (production-style, single URL: http://localhost:8000)
# Requires Node.js + the backend venv (created automatically on first run).

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "[FFMitra] Building the frontend..." -ForegroundColor Cyan
Push-Location (Join-Path $root "frontend")
npm run build
Pop-Location

$backend = Join-Path $root "backend"
if (-not (Test-Path (Join-Path $backend ".venv"))) {
    Write-Host "[FFMitra] Creating backend venv..." -ForegroundColor Cyan
    python -m venv (Join-Path $backend ".venv")
    & (Join-Path $backend ".venv\Scripts\python.exe") -m pip install -q -r (Join-Path $backend "requirements.txt")
}

$inUse = [bool](Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue)
if ($inUse) {
    Write-Host "[FFMitra] Port 8000 already in use - stopping existing backend..." -ForegroundColor Yellow
    Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
}

Write-Host "[FFMitra] Starting hosted app on http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process -FilePath (Join-Path $backend ".venv\Scripts\python.exe") `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8000" `
    -WorkingDirectory $backend -WindowStyle Normal

Start-Sleep -Seconds 8
Start-Process "http://localhost:8000"
Write-Host "[FFMitra] Live at http://localhost:8000  (chat: /victim)" -ForegroundColor Green

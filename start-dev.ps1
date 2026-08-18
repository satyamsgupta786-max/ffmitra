# FFMitra one-click local startup: backend (8000) + frontend (5173)
# Run:  powershell -ExecutionPolicy Bypass -File start-dev.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Port-In-Use($port) {
    return [bool](Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue)
}

$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

if (-not (Test-Path (Join-Path $backend ".venv"))) {
    Write-Host "[FFMitra] Creating backend venv..." -ForegroundColor Cyan
    python -m venv (Join-Path $backend ".venv")
    & (Join-Path $backend ".venv\Scripts\python.exe") -m pip install -q -r (Join-Path $backend "requirements.txt")
}

if (-not (Port-In-Use 8000)) {
    Write-Host "[FFMitra] Starting backend on http://localhost:8000 ..." -ForegroundColor Cyan
    Start-Process -FilePath (Join-Path $backend ".venv\Scripts\python.exe") `
        -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8000" `
        -WorkingDirectory $backend -WindowStyle Normal
} else {
    Write-Host "[FFMitra] Backend already running on :8000" -ForegroundColor Yellow
}

if (-not (Port-In-Use 5173)) {
    Write-Host "[FFMitra] Starting frontend on http://localhost:5173 ..." -ForegroundColor Cyan
    Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev" `
        -WorkingDirectory $frontend -WindowStyle Normal
} else {
    Write-Host "[FFMitra] Frontend already running on :5173" -ForegroundColor Yellow
}

Start-Sleep -Seconds 6
Start-Process "http://localhost:5173"
Write-Host "[FFMitra] Ready. Open http://localhost:5173 (chat at /victim)" -ForegroundColor Green

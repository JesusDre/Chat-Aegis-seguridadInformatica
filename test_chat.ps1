# Script simple para testear paso a paso
# Ejecuta: .\test_chat.ps1

$projectPath = (Get-Location).Path

Write-Host "Chat Aegis - Test Simple" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "[1/3] Python check..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python no esta instalado" -ForegroundColor Red
    exit 1
}
Write-Host "OK: $pythonVersion" -ForegroundColor Green
Write-Host ""

# 2. Activar venv e instalar deps
Write-Host "[2/3] Instalando dependencias..." -ForegroundColor Yellow
if (!(Test-Path ".\.venv")) {
    python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
pip install -q websockets 2>$null
Write-Host "OK: Dependencias listas" -ForegroundColor Green
Write-Host ""

# 3. Lanzar servidor
Write-Host "[3/3] Lanzando servidor y proxy..." -ForegroundColor Yellow
Write-Host ""
Write-Host "=== TERMINAL 1: SERVIDOR ===" -ForegroundColor Magenta
Write-Host "Ejecutando: python .\servidor.py" -ForegroundColor Gray
Write-Host ""

$cmd1 = "cd `"$projectPath`"; `& .\.venv\Scripts\Activate.ps1; python .\servidor.py"
Start-Process powershell -ArgumentList "-NoExit","-Command",$cmd1

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "=== TERMINAL 2: PROXY ===" -ForegroundColor Magenta
Write-Host "Ejecutando: python .\ws_proxy.py" -ForegroundColor Gray
Write-Host ""

$cmd2 = "cd `"$projectPath`"; `& .\.venv\Scripts\Activate.ps1; python .\ws_proxy.py"
Start-Process powershell -ArgumentList "-NoExit","-Command",$cmd2

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Servidor y proxy estan corriendo." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Abriendo http://localhost:8000/ en Chrome..." -ForegroundColor Cyan
Write-Host ""
Start-Process "chrome.exe" -ArgumentList "http://localhost:8000/"

Write-Host "Abriendo segunda ventana de Chrome..." -ForegroundColor Cyan
Write-Host ""
Start-Sleep -Milliseconds 500
Start-Process "chrome.exe" -ArgumentList "http://localhost:8000/"

Write-Host ""
Write-Host "Listo! Ambas ventanas deberian mostrar Conectado en el status." -ForegroundColor Green
Write-Host "Escribe en una ventana y deberia ver el mensaje en la otra." -ForegroundColor Cyan
Write-Host ""

Write-Host "Para cerrar todo: cierra las ventanas de Chrome y las terminales." -ForegroundColor Yellow

# Script para lanzar el Chat Aegis web con dos clientes automáticamente
# Ejecuta: .\run_chat.ps1
# (Si da error de ejecución, ve a Settings > Update & Security > For developers > modo de desarrollador activado, 
# o ejecuta: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser)

# Cambiar a la carpeta del proyecto
$projectPath = (Get-Location).Path
Write-Host "Chat Aegis - Lanzador Automático" -ForegroundColor Cyan -BackgroundColor Black
Write-Host "================================`n" -ForegroundColor Cyan

# Verificar que Python está instalado
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Descargalo desde: https://www.python.org/downloads/windows/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Python encontrado: $pythonVersion`n" -ForegroundColor Green

# Verificar/crear virtualenv
Write-Host "[2/5] Configurando entorno virtual..." -ForegroundColor Yellow
if (!(Test-Path ".\.venv")) {
    Write-Host "Creando virtualenv..." -ForegroundColor Cyan
    python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
Write-Host "✓ Virtualenv listo`n" -ForegroundColor Green

# Instalar dependencias
Write-Host "[3/5] Instalando dependencias..." -ForegroundColor Yellow
pip install -q -r .\requirements.txt 2>$null
Write-Host "✓ Dependencias procesadas`n" -ForegroundColor Green

# Lanzar servidor y proxy en ventanas nuevas
Write-Host "[4/5] Lanzando servidor y proxy..." -ForegroundColor Yellow
Write-Host "Terminal 1: Servidor TCP" -ForegroundColor Cyan
Start-Process powershell -ArgumentList '-NoExit','-Command','cd "' + $projectPath + '"; & .\.venv\Scripts\Activate.ps1; python .\servidor.py'

Start-Sleep -Milliseconds 1500
Write-Host "Terminal 2: Proxy WebSocket" -ForegroundColor Cyan
Start-Process powershell -ArgumentList '-NoExit','-Command','cd "' + $projectPath + '"; & .\.venv\Scripts\Activate.ps1; python .\ws_proxy.py'

Write-Host "`n[5/5] Abriendo Chrome con dos clientes de chat..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Abrir Chrome con la página (Usuario 1)
Write-Host "Abriendo Cliente 1..." -ForegroundColor Cyan
Start-Process "chrome.exe" -ArgumentList "http://localhost:8000/"

Start-Sleep -Milliseconds 500

# Abrir Chrome con la página (Usuario 2)
Write-Host "Abriendo Cliente 2..." -ForegroundColor Cyan
Start-Process "chrome.exe" -ArgumentList "http://localhost:8000/"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✓ ¡Chat Aegis iniciado correctamente!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Dos ventanas de Chrome se abrieron automáticamente." -ForegroundColor Cyan
Write-Host "En cada ventana, haz clic en 'Conectar' para conectarse al WebSocket." -ForegroundColor Cyan
Write-Host "¡Luego ya puedes chatear entre los dos usuarios!`n" -ForegroundColor Cyan

Write-Host "Ventanas que se ejecutan en background:" -ForegroundColor Yellow
Write-Host "  - Terminal 1: Servidor TCP (puerto 5000)" -ForegroundColor Gray
Write-Host "  - Terminal 2: Proxy WebSocket (puertos 8000 HTTP, 8765 WS)" -ForegroundColor Gray
Write-Host "`nPara cerrar todo: cierra las tres ventanas (Chrome y las 2 terminales)" -ForegroundColor Yellow

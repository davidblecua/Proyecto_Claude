# start_demo.ps1 — Arranca el entorno demo de RentaMaq
# Uso: .\start_demo.ps1 [dev|pre|pro]

param(
    [ValidateSet("dev","pre","pro")]
    [string]$Env = "dev"
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

$BackendDir = Join-Path $PSScriptRoot "backend"

Write-Host ""
Write-Host "=== RentaMaq Demo — entorno: $($Env.ToUpper()) ===" -ForegroundColor Cyan
Write-Host ""

# 1. Fotos de maquinaria (descarga una sola vez, ~2 min si es la primera vez)
Write-Host "[1/3] Comprobando fotos de maquinaria..." -ForegroundColor Yellow
Push-Location $BackendDir
try {
    python seeds/download_demo_photos.py
} finally {
    Pop-Location
}

# 2. Seed de datos demo
Write-Host ""
Write-Host "[2/3] Cargando datos demo..." -ForegroundColor Yellow
Push-Location $BackendDir
try {
    python seeds/seed_demo.py --env $Env
    if ($LASTEXITCODE -ne 0) { throw "Seed fallo con codigo $LASTEXITCODE" }
} finally {
    Pop-Location
}

# Puerto por entorno
$Port = switch ($Env) {
    "dev" { 8080 }
    "pre" { 8001 }
    "pro" { 8002 }
}

Write-Host ""
Write-Host "[3/3] Arrancando servidor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Servidor disponible en  http://localhost:$Port" -ForegroundColor Green
Write-Host ""
Write-Host "Credenciales demo:" -ForegroundColor Cyan
Write-Host "  Propietario : david@demo.com   / Demo1234!"
Write-Host "  Cliente     : cliente@demo.com / Demo1234!"
Write-Host "  Admin       : admin@demo.com   / Demo1234!"
Write-Host ""
Write-Host "Pulsa Ctrl+C para detener."
Write-Host ""

Push-Location $BackendDir
try {
    $env:APP_ENV = $Env
    python -m uvicorn app.main:app --host 0.0.0.0 --port $Port --reload
} finally {
    Pop-Location
}

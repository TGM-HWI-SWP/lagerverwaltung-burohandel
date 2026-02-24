# Quick Start Script für Lagerverwaltung Flask App (PowerShell)

Write-Host ""
Write-Host "========================================"
Write-Host "  Lagerverwaltung - Flask App Starter" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python gefunden: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Fehler: Python 3.10+ nicht gefunden" -ForegroundColor Red
    Write-Host "Bitte Python von https://www.python.org installieren" -ForegroundColor Yellow
    Read-Host "Drücke Enter zum Beenden"
    exit
}

Write-Host ""
Write-Host "[1/4] Installing dependencies..." -ForegroundColor Cyan
pip install -e . --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "Fehler beim Installieren der Dependencies" -ForegroundColor Red
    Read-Host "Drücke Enter zum Beenden"
    exit
}
Write-Host "[OK] Dependencies installiert" -ForegroundColor Green

Write-Host ""
Write-Host "[2/4] Initializing database..." -ForegroundColor Cyan
python init_db.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Fehler beim Initialisieren der Datenbank" -ForegroundColor Red
    Read-Host "Drücke Enter zum Beenden"
    exit
}
Write-Host "[OK] Datenbank initialisiert" -ForegroundColor Green

Write-Host ""
Write-Host "========================================"
Write-Host "[3/4] Starting Flask App..." -ForegroundColor Cyan
Write-Host "========================================"
Write-Host ""
Write-Host "App läuft auf: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "Drücke Ctrl+C zum Beenden" -ForegroundColor Yellow
Write-Host ""

python app.py

Write-Host ""
Write-Host "Flask App wurde beendet." -ForegroundColor Yellow

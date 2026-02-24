@echo off
REM Quick Start Script für Lagerverwaltung Flask App

echo.
echo ========================================
echo  Lagerverwaltung - Flask App Starter
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Fehler: Python 3.10+ nicht gefunden. Bitte Python installieren.
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -e . --quiet
if errorlevel 1 (
    echo Fehler beim Installieren der Dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installiert

echo.
echo [2/4] Initializing database...
python init_db.py
if errorlevel 1 (
    echo Fehler beim Initialisieren der Datenbank
    pause
    exit /b 1
)
echo [OK] Datenbank initialisiert

echo.
echo ========================================
echo [3/4] Starting Flask App...
echo ========================================
echo.
echo WICHTIG:
echo - App läuft auf http://127.0.0.1:5000
echo - Drücke Ctrl+C zum Beenden
echo.

python app.py

REM Cleanup wenn beendet
echo.
echo Flask App wurde beendet.
pause

@echo off
REM ============================================================================
REM DC-Intel Dashboard Snapshot Capture
REM ============================================================================
REM This script captures screenshots of all dashboard pages automatically
REM ============================================================================

echo ============================================================================
echo DC-INTEL DASHBOARD SNAPSHOT TOOL
echo ============================================================================
echo.

REM Check if Playwright is installed
echo Checking for Playwright installation...
python -c "import playwright" 2>nul
if errorlevel 1 (
    echo.
    echo Playwright is not installed. Installing now...
    echo.
    pip install playwright
    echo.
    echo Installing Chromium browser...
    playwright install chromium
    echo.
)

REM Check if dashboard server is running
echo.
echo IMPORTANT: The dashboard server must be running for this to work!
echo.
echo Please make sure you have started the dashboard server by running:
echo   START_DASHBOARD.bat
echo.
echo Press Ctrl+C to cancel if the server is not running.
echo Press any other key to continue...
pause >nul

echo.
echo Starting snapshot capture...
echo.

REM Run the snapshot script
cd /d C:\Users\Yaseen\dc-intel\site
python capture_dashboard_snapshots.py

echo.
echo ============================================================================
echo Done! Check the 'snapshots' folder for your screenshots.
echo ============================================================================
pause

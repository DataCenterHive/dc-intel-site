@echo off
REM ============================================================================
REM DC-Intel Dashboard - Local Web Server
REM ============================================================================
REM This starts a simple Python web server to serve the dashboard files
REM without CORS restrictions. The dashboard will open in your browser.
REM ============================================================================

echo ============================================================================
echo DC-INTEL DASHBOARD - STARTING LOCAL WEB SERVER
echo ============================================================================
echo.

REM Change to the dc-intel ROOT directory (so we can serve both site/ and knowledge/)
cd /d C:\Users\Yaseen\dc-intel

echo Starting web server on http://localhost:8080
echo Serving from: C:\Users\Yaseen\dc-intel
echo.
echo The dashboard will open automatically in your browser.
echo.
echo IMPORTANT: Keep this window open while using the dashboard.
echo            Press Ctrl+C to stop the server when done.
echo.
echo ============================================================================
echo.

REM Start the browser after a 2 second delay (in background)
timeout /t 2 /nobreak >nul
start http://localhost:8080/site/dashboard_v2.html

REM Start Python web server (this will block)
python -m http.server 8080

@echo off
echo ================================================================================
echo DC Intel Dashboard - Local Server
echo ================================================================================
echo.
echo Starting local web server...
echo Dashboard will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================================================================
echo.

cd /d "%~dp0"
python -m http.server 8000

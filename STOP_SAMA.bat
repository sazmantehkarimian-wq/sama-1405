@echo off
setlocal
cd /d "%~dp0"
if not defined SAMA_PORT set SAMA_PORT=8765
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R /C:":%SAMA_PORT% .*LISTENING"') do taskkill /PID %%a /F

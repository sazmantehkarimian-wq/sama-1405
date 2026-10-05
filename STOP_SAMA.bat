@echo off
if not defined SAMA_PORT set SAMA_PORT=8765
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%SAMA_PORT%" ^| findstr "LISTENING"') do taskkill /PID %%a /F

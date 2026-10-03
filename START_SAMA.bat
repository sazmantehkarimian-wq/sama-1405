@echo off
setlocal
if not defined SAMA_PORT set SAMA_PORT=8765
set "PYTHON=python"
if exist "runtime\python.exe" set "PYTHON=runtime\python.exe"

echo ============================================================
echo SAMA Zero-Data UAT
echo ============================================================
echo [1/2] Preparing application...
%PYTHON% scripts\first_start.py
if errorlevel 1 (
  echo.
  echo [ERROR] SAMA startup preparation failed.
  pause
  exit /b 1
)

echo [2/2] Starting server on http://127.0.0.1:%SAMA_PORT%/
echo Keep this window open while SAMA is running.
start "SAMA" http://127.0.0.1:%SAMA_PORT%/
%PYTHON% scripts\run_server.py

if errorlevel 1 (
  echo.
  echo [ERROR] SAMA server stopped unexpectedly.
  pause
)

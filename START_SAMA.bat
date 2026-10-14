@echo off
setlocal
if not defined SAMA_PORT set SAMA_PORT=8765
set "PYTHON=python"
if exist "runtime\python.exe" set "PYTHON=runtime\python.exe"
%PYTHON% scripts\first_start.py
if errorlevel 1 (
  echo SAMA startup preparation failed.
  pause
  exit /b 1
)
start "SAMA" http://127.0.0.1:%SAMA_PORT%/
%PYTHON% scripts\run_server.py

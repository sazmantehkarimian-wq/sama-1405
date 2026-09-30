@echo off
setlocal
if not defined SAMA_PORT set SAMA_PORT=8765
start "SAMA" http://127.0.0.1:%SAMA_PORT%/
python scripts\run_server.py

@echo off
powershell -WindowStyle Hidden -Command "Start-Process python -ArgumentList 'app.py' -NoNewWindow"
timeout /t 1 >nul
start "" "http://127.0.0.1:5000/"

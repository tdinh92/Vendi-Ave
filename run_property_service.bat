@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo Starting Property API Service...
python property_api_service.py
pause

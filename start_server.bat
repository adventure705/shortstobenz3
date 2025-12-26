@echo off
echo Starting local web server...
echo Please open your browser to http://localhost:8000/index.html
cd /d "%~dp0"
python -m http.server 8000
pause

@echo off
cd /d "%~dp0"
python -c "import flask" 2>nul || python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Could not install the required Python package.
  echo Check your internet connection, then run this file again.
  pause
  exit /b 1
)
python app.py
if errorlevel 1 pause

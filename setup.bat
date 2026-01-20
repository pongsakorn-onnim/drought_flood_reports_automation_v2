@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Developer Setup (v2)

echo =======================================================
echo  [DEV SETUP] HII Report Generator v2
echo =======================================================
echo.

rem 1. Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python first.
    pause
    exit /b 1
)

rem 2. Create/Recreate .venv
if exist .venv (
    echo [INFO] Found existing .venv...
) else (
    echo [INFO] Creating new .venv...
    python -m venv .venv
)

rem 3. Activate & Install
echo [INFO] Installing libraries...
call .venv\Scripts\activate

rem อัปเกรด pip ก่อน
python -m pip install --upgrade pip

rem ลง library หลัก (rich, requests, etc.)
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt not found! Installing basics...
    pip install rich requests python-pptx pyinstaller
)

rem ลง PyInstaller แยกต่างหาก (เผื่อใน req ไม่มี)
pip install pyinstaller

echo.
echo =======================================================
echo  [SUCCESS] Environment Ready!
echo =======================================================
echo.
echo Now you can run:
echo  1. 'python -m src.main' to test your code.
echo  2. 'build.bat' to create the .exe for users.
echo.
pause
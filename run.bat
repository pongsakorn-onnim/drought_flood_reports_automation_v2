@echo off
chcp 65001 >nul
setlocal
title HII Report Generator
cd /d "%~dp0"

rem --- Check venv ---
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo [ERROR] Python environment not found.
    pause
    exit /b 1
)

rem --- Run Python in Interactive Mode ---
rem เราไม่ส่ง argument อะไรไปเลย เพื่อให้ main.py รู้ว่าต้องถาม User เอง
"%~dp0.venv\Scripts\python.exe" -m src.main

if errorlevel 1 (
    echo.
    echo [ERROR] Program exited with errors.
    pause
) else (
    echo.
    echo Press any key to close...
    pause >nul
)
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

rem --- Run Python ---
"%~dp0.venv\Scripts\python.exe" -m src.main

rem --- Check Error Level ---
rem เช็คเฉพาะถ้ามี Error (Level 1) ถึงจะ Pause
if errorlevel 1 (
    echo.
    echo [ERROR] Program exited with errors.
    pause
)

rem ถ้าไม่มี Error (Level 0) สคริปต์จะจบตรงนี้และปิดหน้าต่างทันที
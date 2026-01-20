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

rem --- Run Python (application controls UX) ---
"%~dp0.venv\Scripts\python.exe" -m src.main

rem --- Exit immediately (pure launcher) ---
exit /b %ERRORLEVEL%

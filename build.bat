@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"

echo =======================================================
echo  [BUILD] Packing Drought Flood Report Generator
echo =======================================================
echo.

rem ---------- CONFIG ----------
set "EXE_NAME=report_generator"
set "DIST_ROOT=dist"
set "OUT_FOLDER_NAME=drought_flood_report_generator"
set "OUT_DIR=%DIST_ROOT%\%OUT_FOLDER_NAME%"

rem Anaconda DLL source (optional patch)
set "CONDA_BIN=C:\Users\cws12345\anaconda3\Library\bin"
rem ----------------------------

rem 1) Activate Environment
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] .venv not found! Please run setup.bat first.
    pause
    exit /b 1
)
call ".venv\Scripts\activate.bat"

rem 2) Build EXE (onedir)
echo [INFO] Building executable...
pyinstaller --noconfirm --onedir --clean ^
 --name "%EXE_NAME%" ^
 --distpath "%DIST_ROOT%" ^
 --workpath "build" ^
 entry_point.py

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

rem 3) Normalize output folder name:
rem    PyInstaller creates: dist\%EXE_NAME%\
rem    You want:           dist\drought_flood_report_generator\
if exist "%OUT_DIR%" rmdir /s /q "%OUT_DIR%"
if exist "%DIST_ROOT%\%EXE_NAME%" (
    ren "%DIST_ROOT%\%EXE_NAME%" "%OUT_FOLDER_NAME%"
) else (
    echo [ERROR] Expected output folder not found: %DIST_ROOT%\%EXE_NAME%
    pause
    exit /b 1
)

rem 4) Patch Anaconda DLLs (optional but kept as your workflow)
echo.
echo [AUTO-FIX] Patching Anaconda DLLs...
if not exist "%CONDA_BIN%" (
    echo [WARN] Anaconda bin not found: %CONDA_BIN%
    echo [WARN] Skipping DLL patch.
) else (
    xcopy "%CONDA_BIN%\ffi*.dll"      "%OUT_DIR%\_internal\" /Y /I >nul
    xcopy "%CONDA_BIN%\libcrypto*.dll" "%OUT_DIR%\_internal\" /Y /I >nul
    xcopy "%CONDA_BIN%\libssl*.dll"    "%OUT_DIR%\_internal\" /Y /I >nul
    echo - DLLs patched successfully.
)

rem 5) Copy user resources
echo.
echo [INFO] Copying User Resources...
xcopy "templates" "%OUT_DIR%\templates\" /E /I /Y >nul
echo f | xcopy "config.yaml" "%OUT_DIR%\config.yaml" /Y >nul

echo.
echo =======================================================
echo  [SUCCESS] Build Finished!
echo =======================================================
echo.
echo Your app is ready in:
echo   %OUT_DIR%
echo.
pause

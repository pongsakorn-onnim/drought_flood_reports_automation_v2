@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo =======================================================
echo  [BUILD] Packing Drought & Flood Report Generator v2
echo =======================================================
echo.

rem 1. Activate Environment
if not exist .venv\Scripts\activate.bat (
    echo [ERROR] .venv not found! Please run setup.bat first.
    pause
    exit /b
)
call .venv\Scripts\activate

echo [INFO] Building executable...
rem ตั้งชื่อใหม่ตรงนี้ครับ
pyinstaller --noconfirm --onedir --clean ^
 --name "Drought&Flood_report_generator_v2" ^
 run_app.py

echo.
echo [AUTO-FIX] Patching Anaconda DLLs...
rem ---------------------------------------------------------
rem ก๊อปปี้ DLL ไปใส่ในโฟลเดอร์ชื่อใหม่
rem ---------------------------------------------------------

rem 1. กวาดตระกูล ffi ทั้งหมด
xcopy "C:\Users\cws12345\anaconda3\Library\bin\ffi*.dll" "dist\Drought&Flood_report_generator_v2\_internal\" /Y /I >nul

rem 2. กวาดตระกูล SSL/Crypto
xcopy "C:\Users\cws12345\anaconda3\Library\bin\libcrypto*.dll" "dist\Drought&Flood_report_generator_v2\_internal\" /Y /I >nul
xcopy "C:\Users\cws12345\anaconda3\Library\bin\libssl*.dll" "dist\Drought&Flood_report_generator_v2\_internal\" /Y /I >nul

echo - DLLs patched successfully.

echo.
echo [INFO] Copying User Resources...
rem ก๊อปปี้ Template/Config ไปที่โฟลเดอร์ชื่อใหม่
xcopy "templates" "dist\Drought&Flood_report_generator_v2\templates\" /E /I /Y >nul
echo f | xcopy "config.yaml" "dist\Drought&Flood_report_generator_v2\config.yaml" /Y >nul

echo.
echo =======================================================
echo  [SUCCESS] Build Finished! 🍱
echo =======================================================
echo.
echo Your app is ready in:
echo   dist\Drought&Flood_report_generator_v2
echo.
echo [TEST] Run this file:
echo dist\Drought&Flood_report_generator_v2\Drought&Flood_report_generator_v2.exe
echo.
pause
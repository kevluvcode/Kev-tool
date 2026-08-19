@echo off
title KevTool Installer
color 0F
chcp 65001 >nul 2>&1

echo.
echo  ============================================
echo     KevTool - KevBin Educational Suite
echo            Installer v1.0.0
echo  ============================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  [X] Python not found. install it from python.org
    echo      make sure to check "Add Python to PATH" during install
    echo.
    pause
    exit /b 1
)

echo  Python found:
python --version
echo.

python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [X] pip not found, trying to install it...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo  [X] couldnt install pip. try reinstalling python with pip enabled
        pause
        exit /b 1
    )
)

echo  installing packages from requirements.txt...
echo.
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo  [!] something broke. try running this as admin
    echo      or check if you have internet
    echo.
    pause
    exit /b 1
)

echo.
echo  done. all packages installed.
echo  run kevtool with: python kevtool.py
echo  or just double-click kevtool.bat
echo.
pause

@echo off
title KevTool - KevBin Educational Suite
color 0F
chcp 65001 >nul 2>&1
mode con: cols=90 lines=45

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [X] Python is required to run KevTool.
    echo  Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python kevtool.py %*
if %errorlevel% neq 0 (
    echo.
    echo  [!] Error occurred. Ensure Python 3.8+ is installed.
    pause
)

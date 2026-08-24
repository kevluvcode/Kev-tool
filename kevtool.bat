@echo off
title KevTool v2.0
color 0B
setlocal enabledelayedexpansion

set "APPDATA_KV=%APPDATA%\KevTool"
set "BAT_DIR=%~dp0"
set "ENGINE_DIR=%BAT_DIR%_engine"
set "CACHE_DIR=%BAT_DIR%_cache"
set "ENGINE_PY=%ENGINE_DIR%\launcher.py"
set "KEVTOOL_PY=%CACHE_DIR%\kevtool.py"

if not exist "%APPDATA_KV%" mkdir "%APPDATA_KV%"

if "%~1"=="/c" goto :cleanup
if "%~1"=="/clean" goto :cleanup
if "%~1"=="/h" goto :help
if "%~1"=="/help" goto :help
if "%~1"=="/u" goto :force_update
if "%~1"=="/update" goto :force_update
if "%~1"=="/v" goto :version
if "%~1"=="/version" goto :version
if "%~1"=="/r" goto :run_direct
if "%~1"=="/run" goto :run_direct
goto :main

:help
echo.
echo  +------------------------------------------+
echo  ^|  KevTool Loader v2.0 - Help              ^|
echo  +------------------------------------------+
echo  ^|  (none)   Launch KevTool                 ^|
echo  ^|  /h       Show this help                 ^|
echo  ^|  /c       Clean cached files             ^|
echo  ^|  /u       Force re-download              ^|
echo  ^|  /v       Show version info              ^|
echo  ^|  /r       Skip sync, run cache           ^|
echo  +------------------------------------------+
echo  ^|  Data: %APPDATA_KV%
echo  +------------------------------------------+
echo.
exit /b 0

:version
echo.
echo  KevTool v2.0
if exist "%CACHE_DIR%\modules\version.txt" (
    set /p KV_LOCAL=<"%CACHE_DIR%\modules\version.txt"
    echo  Version: !KV_LOCAL!
) else (echo  Version: not downloaded)
echo  Data:   %APPDATA_KV%
echo  Cache:  %CACHE_DIR%
echo.
exit /b 0

:force_update
if exist "%CACHE_DIR%" rmdir /s /q "%CACHE_DIR%" 2>nul
goto :main

:cleanup
echo.
if exist "%ENGINE_PY%" python "%ENGINE_PY%" cleanup 2>nul
if exist "%CACHE_DIR%" rmdir /s /q "%CACHE_DIR%" 2>nul
if exist "%ENGINE_DIR%" rmdir /s /q "%ENGINE_DIR%" 2>nul
python -c "import gc,sys;[sys.modules.pop(k,None) for k in list(sys.modules) if 'kevtool' in k or k.startswith('modules')];gc.collect()" 2>nul
echo  [V] Cache wiped.
echo.
exit /b 0

:run_direct
if not exist "%KEVTOOL_PY%" (
    echo  [X] No cache. Run without /r first.
    pause
    exit /b 1
)
goto :launch

:main
echo.
echo   ==============================
echo      K E V T O O L   v2.0
echo   ==============================
echo.

:: CHECK PYTHON
python --version >nul 2>&1
if errorlevel 1 (
    echo  [X] Python not found.
    echo  [?] Would you like to auto-install Python 3.11? ^(Y/N^)
    set /p "PYCHOICE=  > "
    if /i "!PYCHOICE!"=="Y" (
        call :install_python
        if errorlevel 1 goto :pyfail
    ) else (
        echo  Get it: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYVER=%%i"
echo  [V] !PYVER!

:: DOWNLOAD ENGINE (always fresh)
echo  [*] Updating engine...
if not exist "%ENGINE_DIR%" mkdir "%ENGINE_DIR%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12;" ^
    "$progressPreference='SilentlyContinue';" ^
    "try{Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/kevluvcode/kevtoolsource/master/_engine/launcher.py'" ^
    "-OutFile '%ENGINE_PY%' -UseBasicParsing -TimeoutSec 30;Write-Host '  [V] Engine ready'}catch{Write-Host '  [X] Failed';exit 1}"
if not exist "%ENGINE_PY%" (
    echo  [X] Engine download failed.
    pause
    exit /b 1
)

:: SYNC
echo  [*] Syncing...
python "%ENGINE_PY%" sync
if errorlevel 1 (
    if not exist "%KEVTOOL_PY%" (
        echo  [X] Sync failed AND no cache.
        pause
        exit /b 1
    )
    echo  [!] Sync had issues, using cache...
) else (echo  [V] Sync OK)

:: PRE-FLIGHT CHECK
echo.
echo  [*] Pre-flight checks...
set "KVERRORS=0"
if not exist "%KEVTOOL_PY%" (
    echo  [X] kevtool.py missing
    set /a "KVERRORS+=1"
)
if not exist "%CACHE_DIR%\modules\version.txt" (
    echo  [X] version.txt missing
    set /a "KVERRORS+=1"
)
python -c "import json,os,sys,importlib" 2>nul
if errorlevel 1 (
    echo  [X] Python modules broken
    set /a "KVERRORS+=1"
)
if !KVERRORS! gtr 0 (
    echo.
    echo  [X] !KVERRORS! error^(s^). Run with /u to re-download.
    pause
    exit /b 1
)
echo  [V] All checks passed.
echo.
echo  Press Enter to start...
pause >nul

:: LAUNCH
:launch
cd /d "%CACHE_DIR%"
python kevtool.py %*
set KEV_EXIT=%errorlevel%
cd /d "%BAT_DIR%"

:: SAVE STATE
python "%ENGINE_PY%" sync_state 2>nul
python -c "import gc,sys;[sys.modules.pop(k,None) for k in list(sys.modules) if 'kevtool' in k or k.startswith('modules')];gc.collect();gc.collect();gc.collect()" 2>nul
echo  [V] Done. Cache kept.
exit /b %KEV_EXIT%

:: PYTHON INSTALL SUBROUTINE
:install_python
echo  [*] Downloading Python 3.11.9...
set "PYINSTALLER=%TEMP%\python-installer.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12;" ^
    "$progressPreference='SilentlyContinue';" ^
    "try{Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe'" ^
    "-OutFile '%PYINSTALLER%' -UseBasicParsing -TimeoutSec 120;Write-Host '  [V] Downloaded'}catch{Write-Host '  [X] Failed';exit 1}"
if not exist "%PYINSTALLER%" (
    echo  [X] Download failed.
    exit /b 1
)
echo  [*] Installing Python 3.11.9...
"%PYINSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0
set /a "PW=0"
:waitpy
if !PW! geq 180 (
    echo  [X] Install timed out.
    exit /b 1
)
timeout /t 3 /nobreak >nul
set /a "PW+=3"
tasklist /fi "imagename eq python-3.11.9-amd64.exe" 2>nul | find /i "python-3.11" >nul
if not errorlevel 1 goto :waitpy
:: Refresh PATH from registry
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "PATH=%%B;%PATH%"
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "PATH=%%B;%PATH%"
del /f /q "%PYINSTALLER%" 2>nul
python --version >nul 2>&1
if errorlevel 1 (
    echo  [X] Installed but not in PATH.
    echo  [!] Close this window and open a NEW terminal.
    exit /b 1
)
echo  [V] Python installed!
exit /b 0

:pyfail
echo  Manual: https://www.python.org/downloads/
pause
exit /b 1

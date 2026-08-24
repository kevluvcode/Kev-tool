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
echo  +-------------------------------------------+
echo  |  KevTool Loader v2.0 - Help               |
echo  +-------------------------------------------+
echo  |  (none)   Launch KevTool                  |
echo  |  /h       Show this help                  |
echo  |  /c       Clean cached files              |
echo  |  /u       Force re-download               |
echo  |  /v       Show version info               |
echo  |  /r       Skip sync, run cache            |
echo  +-------------------------------------------+
echo  |  Data:   %APPDATA_KV%
echo  |  Cache persists. Wipe only with /c        |
echo  |  Updates: delta - changed files only      |
echo  +-------------------------------------------+
echo.
exit /b 0

:version
echo.
echo  KevTool v2.0 | kevtoolsource
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
echo  [V] Cache wiped. Rebuilds on next launch.
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
echo    _  __           __  ___      __
echo   | |/ /__ _    __/  |/ (_)__  / /_
echo   |   / -| | | / / / _/ / / _ \/ __/
echo   |_|\_\ |_|__/ /\__/_/_/_//_/\__/
echo              Loader v2.0
echo.

:: CHECK PYTHON
python --version >nul 2>&1
if errorlevel 1 (
    echo  [X] Python not found. Install? (Y/N)
    set /p "PYCHOICE=  > "
    if /i "!PYCHOICE!"=="Y" (goto :install_python)
    echo  Get it: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYVER=%%i"
echo  [V] !PYVER!

:: DOWNLOAD ENGINE
if not exist "%ENGINE_PY%" (
    echo  [*] Downloading engine...
    if not exist "%ENGINE_DIR%" mkdir "%ENGINE_DIR%"
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12;" ^
        "$progressPreference='SilentlyContinue';" ^
        "try{Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/kevluvcode/kevtoolsource/master/_engine/launcher.py'" ^
        "-OutFile '%ENGINE_PY%' -UseBasicParsing -TimeoutSec 30;Write-Host '  [V] Engine ready'}catch{Write-Host '  [X] Download failed';exit 1}"
    if not exist "%ENGINE_PY%" (echo  [X] No internet. & pause & exit /b 1)
) else (echo  [V] Engine ready)

:: SYNC
echo  [*] Syncing...
python "%ENGINE_PY%" sync
if errorlevel 1 (
    if not exist "%KEVTOOL_PY%" (echo  [X] Sync failed, no cache. & pause & exit /b 1)
    echo  [!] Issues, using cache...
)

:: LAUNCH
:launch
echo  [*] Starting...
cd /d "%CACHE_DIR%"
python kevtool.py %*
set KEV_EXIT=%errorlevel%
cd /d "%BAT_DIR%"

:: SAVE STATE
python "%ENGINE_PY%" sync_state 2>nul
python -c "import gc,sys;[sys.modules.pop(k,None) for k in list(sys.modules) if 'kevtool' in k or k.startswith('modules')];gc.collect();gc.collect();gc.collect()" 2>nul
echo  [V] Saved. Cache kept.
exit /b %KEV_EXIT%

:: PYTHON INSTALL
:install_python
echo  [*] Downloading Python 3.11.9...
set "PYINSTALLER=%TEMP%\python-installer.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12;" ^
    "$progressPreference='SilentlyContinue';" ^
    "try{Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe'" ^
    "-OutFile '%PYINSTALLER%' -UseBasicParsing -TimeoutSec 120;Write-Host '  [V] Downloaded'}catch{Write-Host '  [X] Failed';exit 1}"
if not exist "%PYINSTALLER%" (echo  [X] Failed. & pause & exit /b 1)
echo  [*] Installing...
"%PYINSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0
set /a "PW=0"
:waitpy
if %PW% geq 180 (echo  [X] Timeout. & goto :pyfail)
timeout /t 2 /nobreak >nul
set /a "PW+=2"
tasklist /fi "imagename eq python-3.11.9-amd64.exe" 2>nul | find /i "python-3.11" >nul
if not errorlevel 1 goto :waitpy
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "PATH=%%B;%PATH%"
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "PATH=%%B;%PATH%"
del /f /q "%PYINSTALLER%" 2>nul
python --version >nul 2>&1
if errorlevel 1 (echo  [X] Installed but not in PATH. Restart terminal. & goto :pyfail)
echo  [V] Python installed!
goto :main

:pyfail
echo  Manual: https://www.python.org/downloads/
pause
exit /b 1

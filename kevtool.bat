@echo off
chcp 65001 >nul 2>&1
title KevTool v2.0
color 0B

:: ============================================================
:: KevTool Loader v2.0
:: Single-file launcher — everything downloaded from kevtoolsource
:: Persistent data stored in %APPDATA%\KevTool\
:: Cache persists between runs (delta updates only)
:: Only wipes with /c flag
:: ============================================================

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
echo  ╔══════════════════════════════════════════════════╗
echo  ║           KevTool Loader v2.0 - Help            ║
echo  ╠══════════════════════════════════════════════════╣
echo  ║                                                  ║
echo  ║  kevtool.bat              Launch KevTool         ║
echo  ║  kevtool.bat /h           Show this help         ║
echo  ║  kevtool.bat /c           Clean cached files     ║
echo  ║  kevtool.bat /u           Force re-download      ║
echo  ║  kevtool.bat /v           Show version info      ║
echo  ║  kevtool.bat /r           Skip sync, run cache   ║
echo  ║                                                  ║
echo  ║  Data: %%APPDATA%%\KevTool\                        ║
echo  ║  Settings, proxies, version tracking             ║
echo  ║                                                  ║
echo  ║  Cache persists between runs. Only wipe with /c  ║
echo  ║  Updates are delta — only changed files redownl  ║
echo  ╚══════════════════════════════════════════════════╝
echo.
exit /b 0

:version
echo.
echo  KevTool Loader v2.0
echo  Source: https://github.com/kevluvcode/kevtoolsource
if exist "%CACHE_DIR%\modules\version.txt" (
    set /p KV_LOCAL=<"%CACHE_DIR%\modules\version.txt"
    echo  Local version:  !KV_LOCAL!
) else (
    echo  Local version:  not downloaded
)
echo  Data folder: %APPDATA_KV%
echo  Cache folder: %CACHE_DIR%
echo.
exit /b 0

:force_update
echo.
echo  [*] Forcing full re-download...
if exist "%CACHE_DIR%" rmdir /s /q "%CACHE_DIR%" 2>nul
goto :main

:cleanup
echo.
echo  ╔══════════════════════════════════════╗
echo  ║     KevTool — Cleaning Up            ║
echo  ╚══════════════════════════════════════╝
echo.
if exist "%ENGINE_PY%" (
    python "%ENGINE_PY%" cleanup 2>nul
)
if exist "%CACHE_DIR%" (
    echo  [*] Removing cache...
    rmdir /s /q "%CACHE_DIR%" 2>nul
)
if exist "%ENGINE_DIR%" (
    echo  [*] Removing engine...
    rmdir /s /q "%ENGINE_DIR%" 2>nul
)
python -c "import gc,sys;[sys.modules.pop(k,None) for k in list(sys.modules) if 'kevtool' in k or k.startswith('modules')];gc.collect()" 2>nul
echo  [V] Cleanup complete. Cache will rebuild on next launch.
echo.
exit /b 0

:run_direct
if not exist "%KEVTOOL_PY%" (
    echo  [X] No cached version found. Run without /r first.
    pause
    exit /b 1
)
goto :launch

:main
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║                                                  ║
echo  ║     ██╗  ██╗██╗███████╗████████╗██╗   ██╗██╗    ║
echo  ║     ██║ ██╔╝██║██╔════╝╚══██╔══╝██║   ██║██║    ║
echo  ║     █████╔╝ ██║███████╗   ██║   ██║   ██║██║    ║
echo  ║     ██╔═██╗ ██║╚════██║   ██║   ██║   ██║██║    ║
echo  ║     ██║  ██╗██║███████║   ██║   ╚██████╔╝██║    ║
echo  ║     ╚═╝  ╚═╝╚═╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝    ║
echo  ║                                                  ║
echo  ║              Loader v2.0                         ║
echo  ╚══════════════════════════════════════════════════╝
echo.

:: ============================================================
:: CHECK PYTHON
:: ============================================================
echo  [*] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [X] Python not found.
    echo.
    echo  Would you like to auto-install Python 3.11? (Y/N)
    set /p PYCHOICE="  > "
    if /i "%PYCHOICE%"=="Y" (
        goto :install_python
    ) else (
        echo.
        echo  [X] Python is required. Download from:
        echo      https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYVER=%%i"
echo  [V] %PYVER%
echo.

:: ============================================================
:: DOWNLOAD ENGINE (only if missing)
:: ============================================================
if not exist "%ENGINE_PY%" (
    echo  [*] Downloading engine from kevtoolsource...
    if not exist "%ENGINE_DIR%" mkdir "%ENGINE_DIR%"
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; " ^
        "$progressPreference='SilentlyContinue'; " ^
        "try { " ^
        "  Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/kevluvcode/kevtoolsource/master/_engine/launcher.py' " ^
        "  -OutFile '%ENGINE_PY%' -UseBasicParsing -TimeoutSec 30; " ^
        "  Write-Host '  [V] Engine downloaded'" ^
        "} catch { " ^
        "  Write-Host '  [X] Failed to download engine.'; " ^
        "  exit 1 " ^
        "}"
    if not exist "%ENGINE_PY%" (
        echo.
        echo  [X] Engine download failed.
        echo      Check internet: ping github.com
        echo.
        pause
        exit /b 1
    )
) else (
    echo  [V] Engine found
)
echo.

:: ============================================================
:: SYNC — delta update (only downloads changed files)
:: ============================================================
echo  [*] Checking for updates...
python "%ENGINE_PY%" sync
if errorlevel 1 (
    if not exist "%KEVTOOL_PY%" (
        echo.
        echo  [X] Sync failed and no cached version.
        echo      Check internet and try again.
        echo.
        pause
        exit /b 1
    )
    echo  [!] Sync issues, using cache...
)
echo.

:: ============================================================
:: LAUNCH
:: ============================================================
:launch
echo  [*] Launching KevTool...
echo.
cd /d "%CACHE_DIR%"
python kevtool.py %*
set KEV_EXIT=%errorlevel%
cd /d "%BAT_DIR%"

:: ============================================================
:: SAVE STATE — sync settings/proxies back to AppData, NO wipe
:: ============================================================
echo.
echo  [*] Saving state...
python "%ENGINE_PY%" sync_state 2>nul
python -c "import gc,sys;[sys.modules.pop(k,None) for k in list(sys.modules) if 'kevtool' in k or k.startswith('modules')];gc.collect();gc.collect();gc.collect()" 2>nul
echo  [V] Done. Cache kept for next launch.
exit /b %KEV_EXIT%

:: ============================================================
:: PYTHON INSTALL
:: ============================================================
:install_python
echo.
echo  [*] Downloading Python 3.11.9...
set "PYINSTALLER=%TEMP%\python-installer.exe"
set "PYURL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; " ^
    "$progressPreference='SilentlyContinue'; " ^
    "Write-Host '  [*] Connecting to python.org...'; " ^
    "try { " ^
    "  Invoke-WebRequest -Uri '%PYURL%' -OutFile '%PYINSTALLER%' -UseBasicParsing -TimeoutSec 120; " ^
    "  Write-Host '  [V] Downloaded'" ^
    "} catch { " ^
    "  Write-Host '  [X] Download failed:' $_.Exception.Message; " ^
    "  exit 1 " ^
    "}"
if not exist "%PYINSTALLER%" (
    echo  [X] Download failed.
    echo  Manual install: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo  [*] Installing Python 3.11.9 (this may take a minute)...
"%PYINSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0
set /a "PYWAIT=0"
:wait_install
if %PYWAIT% geq 180 (
    echo  [X] Install timed out
    goto :py_fail
)
timeout /t 2 /nobreak >nul
set /a "PYWAIT+=2"
tasklist /fi "imagename eq python-3.11.9-amd64.exe" 2>nul | find /i "python-3.11" >nul
if not errorlevel 1 goto :wait_install
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "PATH=%%B;%PATH%"
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "PATH=%%B;%PATH%"
del /f /q "%PYINSTALLER%" 2>nul
python --version >nul 2>&1
if errorlevel 1 (
    echo  [X] Python installed but not in PATH.
    echo  Restart your terminal or computer.
    goto :py_fail
)
echo  [V] Python installed!
echo.
goto :main

:py_fail
echo  [X] Python install failed.
echo  Manual: https://www.python.org/downloads/
pause
exit /b 1

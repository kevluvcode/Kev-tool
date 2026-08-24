@echo off
title KevTool
cd /d "%~dp0"
color 0B

:: ============================================================
:: KevTool Loader v2.0
:: ONLY kevtool.bat persists — everything else downloaded from
:: https://github.com/kevluvcode/kevtoolsource
:: On exit: secure wipe all files + memory flush
:: ============================================================

if "%~1"=="/c" goto :cleanup

:: ============================================================
:: CHECK PYTHON — auto-install if missing
:: ============================================================
python --version >nul 2>&1
if errorlevel 1 goto :install_python
goto :python_ok

:install_python
echo.
echo  ==========================================
echo       Python not found - auto-installing
echo  ==========================================
echo.
set "PYINSTALLER=%~dp0python-installer.exe"
set "PYURL=https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
echo  [*] Downloading Python 3.11.0...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; " ^
    "Write-Host '  [*] Connecting to python.org...'; " ^
    "$progressPreference='SilentlyContinue'; " ^
    "Invoke-WebRequest -Uri '%PYURL%' -OutFile '%PYINSTALLER%' -UseBasicParsing; " ^
    "Write-Host '  [V] Downloaded'"
if not exist "%PYINSTALLER%" (
    echo  [X] Download failed. Manual: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo  [*] Installing Python 3.11.0 (this may take a minute)...
"%PYINSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0
set /a "PYWAIT=0"
:wait_install
if %PYWAIT% geq 120 (
    echo  [X] Install timed out
    goto :py_fail
)
timeout /t 2 /nobreak >nul
set /a "PYWAIT+=2"
tasklist /fi "imagename eq python-3.11.0-amd64.exe" 2>nul | find /i "python-3.11" >nul
if not errorlevel 1 goto :wait_install
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "PATH=%%B;%PATH%"
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "PATH=%%B;%PATH%"
del /f /q "%PYINSTALLER%" 2>nul
python --version >nul 2>&1
if errorlevel 1 (
    echo  [X] Python installed but not in PATH. Try restarting terminal.
    goto :py_fail
)
echo  [V] Python installed
echo.
goto :python_ok

:py_fail
echo  [X] Python install failed. Manual: https://www.python.org/downloads/
pause
exit /b 1

:python_ok

:: ============================================================
:: DOWNLOAD ENGINE from kevtoolsource
:: ============================================================
if not exist "_engine\launcher.py" (
    echo  [*] Downloading engine from kevtoolsource...
    mkdir _engine 2>nul
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; " ^
        "$progressPreference='SilentlyContinue'; " ^
        "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/kevluvcode/kevtoolsource/main/_engine/launcher.py' " ^
        "-OutFile '_engine\launcher.py' -UseBasicParsing" 2>nul
    if not exist "_engine\launcher.py" (
        echo  [X] Failed to download engine. Check internet.
        pause
        exit /b 1
    )
    echo  [V] Engine downloaded
)

:: ============================================================
:: SYNC — download kevtool.py + modules from kevtoolsource
:: ============================================================
echo.
echo  ========================================
echo       KevTool Loader v2.0
echo  ========================================
echo.
python "_engine\launcher.py" sync
if errorlevel 1 (
    if not exist "_cache\kevtool.py" (
        echo  [X] No cached version. Check internet.
        pause
        exit /b 1
    )
)

:: ============================================================
:: LAUNCH
:: ============================================================
echo.
echo  ========================================
echo       Launching KevTool...
echo  ========================================
echo.
cd /d "%~dp0_cache"
python kevtool.py %*
set KEV_EXIT=%errorlevel%
cd /d "%~dp0"

:: ============================================================
:: SECURE WIPE — 3-pass overwrite + crypto random + delete
:: ============================================================
echo.
echo  [*] Secure wiping cached files...
python "_engine\launcher.py" cleanup
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ErrorActionPreference='SilentlyContinue'; " ^
    "Get-ChildItem -Path '_cache' -Recurse -File | ForEach-Object { " ^
    "  $s = $_.Length; " ^
    "  if ($s -gt 0) { " ^
    "    $fs = [IO.FileStream]::new($_.FullName, 'Open', 'Write'); " ^
    "    $bw = [IO.BinaryWriter]::new($fs); " ^
    "    $rng = [Security.Cryptography.RandomNumberGenerator]::Create(); " ^
    "    $buf = New-Object byte[] $s; " ^
    "    $rng.GetBytes($buf); " ^
    "    $bw.Write($buf); " ^
    "    $bw.Flush(); $fs.Flush(); " ^
    "    $fs.Close(); " ^
    "  } " ^
    "  Remove-Item $_.FullName -Force; " ^
    "}; " ^
    "Remove-Item '_cache' -Recurse -Force; " ^
    "Remove-Item '_engine' -Recurse -Force; " ^
    "if (Test-Path '_cache') { Remove-Item '_cache' -Recurse -Force -Confirm:$false }"
python -c "import gc, sys; [sys.modules.pop(k,None) for k in list(sys.modules) if 'kevtool' in k or k.startswith('modules')]; gc.collect(); gc.collect(); gc.collect()"
echo  [V] Secure wipe complete.
echo.
exit /b %KEV_EXIT%

:cleanup
echo.
echo  [*] Manual cleanup...
python "_engine\launcher.py" cleanup 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ErrorActionPreference='SilentlyContinue'; " ^
    "Remove-Item '_cache' -Recurse -Force; " ^
    "Remove-Item '_engine' -Recurse -Force"
echo  [V] Done.

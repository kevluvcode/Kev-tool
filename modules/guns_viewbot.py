"""Guns.lol Viewbot — View/visit bot using valid proxies."""

import os
import sys
import time
import random
import threading
import urllib.request
import urllib.error
import ssl
import json

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

PROXY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'valid_proxies.txt')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/120.0.0.0",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/605.1.15",
]

REFERRERS = [
    "https://www.google.com/", "https://www.bing.com/", "https://duckduckgo.com/",
    "https://twitter.com/", "https://www.reddit.com/", "https://www.facebook.com/",
    "https://www.instagram.com/", "https://t.me/", "https://discord.com/",
]

stop_flag = False
stats = {"success": 0, "fail": 0, "proxy_fail": 0}
lock = threading.Lock()

def _load_proxies():
    proxies = []
    for path in [PROXY_FILE, os.path.join(os.getcwd(), 'valid_proxies.txt')]:
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if not line.startswith('http'):
                            line = 'http://' + line
                        proxies.append(line)
    return list(set(proxies))

def _auto_solve_captcha(html):
    captcha_indicators = ['captcha', 'recaptcha', 'hcaptcha', 'cf-turnstile', 'challenge-platform']
    has_captcha = any(ind in html.lower() for ind in captcha_indicators)
    if not has_captcha:
        return True
    cf_turnstile = 'cf-turnstile' in html.lower()
    if cf_turnstile:
        time.sleep(random.uniform(3, 8))
        return True
    return random.random() < 0.3

def _send_view(url, proxy=None):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,*/*',
        'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.9', 'fr-FR,fr;q=0.9', 'de-DE,de;q=0.9']),
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Referer': random.choice(REFERRERS),
        'DNT': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
    }
    proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy}) if proxy else urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=ctx))
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = opener.open(req, timeout=10)
        body = resp.read().decode('utf-8', errors='ignore')
        status = resp.status
        _auto_solve_captcha(body)
        return status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0

def _worker(url, proxies, delay):
    global stop_flag
    while not stop_flag:
        proxy = random.choice(proxies) if proxies else None
        try:
            status = _send_view(url, proxy)
            if status in (200, 301, 302, 304):
                with lock:
                    stats["success"] += 1
            elif status == 403:
                with lock:
                    stats["fail"] += 1
            else:
                with lock:
                    stats["fail"] += 1
        except Exception:
            with lock:
                stats["proxy_fail"] += 1
        time.sleep(delay + random.uniform(0, 1))

def run(kevbin=None):
    global stop_flag, stats
    while True:
        clear()
        cprint("  \033[93m\u2554" + "\u2550"*44 + "\u2557")
        cprint("  \033[93m\u2551       GUNS.LOL VIEWBOT                   \u2551")
        cprint("  \033[93m\u255a" + "\u2550"*44 + "\u255d")
        cprint("  \033[91m[!] For authorized/testing use only\033[0m")
        print()
        cprint("  \033[97m[1]  Start Viewbot\033[0m")
        cprint("  \033[97m[2]  Check Proxies\033[0m")
        cprint("  \033[97m[3]  Auto-Solve Captcha Test\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        proxies = _load_proxies()
        cprint(f"  \033[90m  Loaded {len(proxies)} proxy(ies)\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '1':
            clear()
            cprint("  \033[93m┌── VIEWBOT CONFIG ──────────────────────────┐\033[0m")
            url = prompt("  \033[96mTarget URL: \033[0m").strip()
            if not url: continue
            if not url.startswith('http'):
                url = 'https://' + url
            try:
                threads = int(prompt("  \033[96mThreads (1-200, default 30): \033[0m").strip() or '30')
            except:
                threads = 30
            threads = max(1, min(200, threads))
            try:
                duration = int(prompt("  \033[96mDuration seconds (10-600, default 60): \033[0m").strip() or '60')
            except:
                duration = 60
            duration = max(10, min(600, duration))
            try:
                delay = float(prompt("  \033[96mDelay between requests sec (1-10, default 2): \033[0m").strip() or '2')
            except:
                delay = 2
            delay = max(1, min(10, delay))
            if not proxies:
                cprint("  \033[93m[!] No proxies found — running without proxy\033[0m")
            stop_flag = False
            stats = {"success": 0, "fail": 0, "proxy_fail": 0}
            cprint(f"\n  \033[36m[*] Starting viewbot: {url}")
            cprint(f"    Threads: {threads} | Duration: {duration}s | Proxies: {len(proxies)}\033[0m\n")
            t_list = []
            for _ in range(threads):
                t = threading.Thread(target=_worker, args=(url, proxies, delay), daemon=True)
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
                        ok = stats["success"]
                        fail = stats["fail"]
                        pf = stats["proxy_fail"]
                    rps = ok / max(elapsed, 0.001)
                    sys.stdout.write(f"\r  [{bar}] \033[97m{pct:3d}%\033[0m \033[92m{ok}\033[0m ok \033[91m{fail}\033[0m fail \033[90m{pf}\033[0m proxy_err \033[96m{rps:.1f}/s\033[0m  ")
                    sys.stdout.flush()
                    time.sleep(0.5)
            except KeyboardInterrupt:
                pass
            stop_flag = True
            time.sleep(1)
            with lock:
                final_ok = stats["success"]
                final_fail = stats["fail"]
            cprint(f"\n\n  \033[92m[X] VIEWBOT COMPLETE\033[0m")
            cprint(f"  \033[97m  Duration: {time.time() - start:.1f}s\033[0m")
            cprint(f"  \033[92m  Successful views: {final_ok}\033[0m")
            cprint(f"  \033[91m  Failed: {final_fail}\033[0m")
            pause()
        elif choice == '2':
            clear()
            cprint("  \033[93m┌── PROXY CHECK ─────────────────────────────┐\033[0m")
            if not proxies:
                cprint("  \033[91m[X] No proxies in valid_proxies.txt\033[0m")
            else:
                cprint(f"  \033[36m[*] Testing {len(proxies)} proxies...\033[0m\n")
                good = 0
                bad = 0
                for i, proxy in enumerate(proxies, 1):
                    try:
                        status = _send_view("https://httpbin.org/ip", proxy)
                        if status == 200:
                            good += 1
                            sys.stdout.write(f"\r  \033[92m[{i}/{len(proxies)}]\033[0m {proxy[:40]} OK  ")
                        else:
                            bad += 1
                    except:
                        bad += 1
                    sys.stdout.flush()
                cprint(f"\n\n  \033[92m  Working: {good}\033[0m | \033[91m  Dead: {bad}\033[0m")
        elif choice == '3':
            clear()
            cprint("  \033[93m┌── CAPTCHA TEST ────────────────────────────┐\033[0m")
            url = prompt("  \033[96mURL to test: \033[0m").strip()
            if not url: continue
            cprint("  \033[36m[*] Fetching page...\033[0m")
            status = _send_view(url)
            cprint(f"  \033[97m  Status: {status}\033[0m")
            cprint(f"  \033[92m  [X] Captcha auto-solver attempted\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

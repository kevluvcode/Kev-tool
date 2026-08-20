"""Proxy Scraper — pull proxies from public GitHub proxy lists."""

import os
import re
import threading
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'proxies')

SOURCES = [
    ('HTTP', 'TheSpeedX/PROXY-List', 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt'),
    ('HTTPS', 'TheSpeedX/PROXY-List', 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt'),
    ('SOCKS4', 'TheSpeedX/PROXY-List', 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt'),
    ('SOCKS5', 'TheSpeedX/PROXY-List', 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt'),
    ('HTTP', 'monogramm/proxy_list', 'https://raw.githubusercontent.com/monogramm/proxy_list/main/http.txt'),
    ('HTTPS', 'monogramm/proxy_list', 'https://raw.githubusercontent.com/monogramm/proxy_list/main/https.txt'),
    ('SOCKS4', 'monogramm/proxy_list', 'https://raw.githubusercontent.com/monogramm/proxy_list/main/socks4.txt'),
    ('SOCKS5', 'monogramm/proxy_list', 'https://raw.githubusercontent.com/monogramm/proxy_list/main/socks5.txt'),
    ('HTTPS', 'roosterkid/openproxylist', 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt'),
    ('SOCKS4', 'roosterkid/openproxylist', 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt'),
    ('SOCKS5', 'roosterkid/openproxylist', 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt'),
    ('SOCKS5', 'hookzof/socks5_list', 'https://raw.githubusercontent.com/hookzof/socks5_list/master/socks5.txt'),
    ('HTTP', 'clarketm/proxy-list', 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt'),
    ('HTTP', 'ShiftyTR/Proxy-List', 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt'),
    ('HTTPS', 'ShiftyTR/Proxy-List', 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt'),
    ('SOCKS4', 'ShiftyTR/Proxy-List', 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt'),
    ('SOCKS5', 'ShiftyTR/Proxy-List', 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt'),
    ('SOCKS5', 'jetkai/proxy-list', 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/socks5.txt'),
    ('SOCKS4', 'jetkai/proxy-list', 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/socks4.txt'),
    ('HTTP', 'jetkai/proxy-list', 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/http.txt'),
    ('HTTP', 'proxifly/free-proxy-list', 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http/data.txt'),
    ('HTTPS', 'proxifly/free-proxy-list', 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/https/data.txt'),
    ('SOCKS4', 'proxifly/free-proxy-list', 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks4/data.txt'),
    ('SOCKS5', 'proxifly/free-proxy-list', 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks5/data.txt'),
    ('ALL', 'proxifly/free-proxy-list', 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt'),
    ('HTTP', 'mmpx12/proxy-list', 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt'),
    ('HTTPS', 'mmpx12/proxy-list', 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt'),
    ('SOCKS4', 'mmpx12/proxy-list', 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt'),
    ('SOCKS5', 'mmpx12/proxy-list', 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt'),
    ('HTTP', 'Uptox/Proxy-List', 'https://raw.githubusercontent.com/Uptox/Proxy-List/main/http.txt'),
    ('HTTPS', 'Uptox/Proxy-List', 'https://raw.githubusercontent.com/Uptox/Proxy-List/main/https.txt'),
    ('SOCKS4', 'Uptox/Proxy-List', 'https://raw.githubusercontent.com/Uptox/Proxy-List/main/socks4.txt'),
    ('SOCKS5', 'Uptox/Proxy-List', 'https://raw.githubusercontent.com/Uptox/Proxy-List/main/socks5.txt'),
    ('HTTP', 'monosans/proxy-list', 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt'),
    ('HTTPS', 'monosans/proxy-list', 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt'),
    ('SOCKS4', 'monosans/proxy-list', 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt'),
    ('SOCKS5', 'monosans/proxy-list', 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt'),
    ('HTTP', 'ALIILOPROXY/proxy', 'https://raw.githubusercontent.com/ALIILOPROXY/proxy/main/http.txt'),
    ('HTTPS', 'ALIILOPROXY/proxy', 'https://raw.githubusercontent.com/ALIILOPROXY/proxy/main/https.txt'),
    ('SOCKS4', 'ALIILOPROXY/proxy', 'https://raw.githubusercontent.com/ALIILOPROXY/proxy/main/socks4.txt'),
    ('SOCKS5', 'ALIILOPROXY/proxy', 'https://raw.githubusercontent.com/ALIILOPROXY/proxy/main/socks5.txt'),
    ('HTTP', 'zimuq/proxy', 'https://raw.githubusercontent.com/zimuq/proxy/master/http.txt'),
    ('HTTPS', 'zimuq/proxy', 'https://raw.githubusercontent.com/zimuq/proxy/master/https.txt'),
    ('SOCKS4', 'zimuq/proxy', 'https://raw.githubusercontent.com/zimuq/proxy/master/socks4.txt'),
    ('SOCKS5', 'zimuq/proxy', 'https://raw.githubusercontent.com/zimuq/proxy/master/socks5.txt'),
    ('HTTP', 'yuceltoluyan/proxy-list', 'https://raw.githubusercontent.com/yuceltoluyan/proxy-list/main/http.txt'),
    ('HTTPS', 'yuceltoluyan/proxy-list', 'https://raw.githubusercontent.com/yuceltoluyan/proxy-list/main/https.txt'),
    ('SOCKS5', 'yuceltoluyan/proxy-list', 'https://raw.githubusercontent.com/yuceltoluyan/proxy-list/main/socks5.txt'),
    ('HTTP', 'B4RC0DE-TM/proxy-list', 'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/http.txt'),
    ('HTTPS', 'B4RC0DE-TM/proxy-list', 'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/https.txt'),
    ('SOCKS4', 'B4RC0DE-TM/proxy-list', 'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/socks4.txt'),
    ('SOCKS5', 'B4RC0DE-TM/proxy-list', 'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/socks5.txt'),
    ('HTTP', 'pproxy/proxy', 'https://raw.githubusercontent.com/pproxy/proxy/master/http.txt'),
    ('SOCKS5', 'pproxy/proxy', 'https://raw.githubusercontent.com/pproxy/proxy/master/socks5.txt'),
    ('HTTP', 'H4ck4ss3/PROXY-List', 'https://raw.githubusercontent.com/H4ck4ss3/PROXY-List/master/http.txt'),
    ('HTTPS', 'H4ck4ss3/PROXY-List', 'https://raw.githubusercontent.com/H4ck4ss3/PROXY-List/master/https.txt'),
    ('SOCKS4', 'H4ck4ss3/PROXY-List', 'https://raw.githubusercontent.com/H4ck4ss3/PROXY-List/master/socks4.txt'),
    ('SOCKS5', 'H4ck4ss3/PROXY-List', 'https://raw.githubusercontent.com/H4ck4ss3/PROXY-List/master/socks5.txt'),
]

_IP_RE = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3}):(\d{1,5})$')
_SCHEME_RE = re.compile(r'^(https?|socks4|socks5)://([^/:]+):(\d{1,5})$', re.I)


def _valid(proxy):
    m = _IP_RE.match(proxy.strip())
    if not m:
        return False
    return all(0 <= int(m.group(i)) <= 255 for i in range(1, 5)) and 1 <= int(m.group(5)) <= 65535


def _parse_line(line):
    """Return (ip:port or None, protocol or None) from a raw list line."""
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


def _fetch(url, timeout=12):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (KevTool)'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', errors='ignore')


def _scrape(protocols):
    os.makedirs(OUT_DIR, exist_ok=True)
    wanted = [s for s in SOURCES if s[0].lower() in protocols or s[0].lower() == 'all']
    results = {}
    ok = [0]
    lock = threading.Lock()

    def work(src):
        proto, _name, url = src
        try:
            text = _fetch(url)
            local = {}
            for line in text.splitlines():
                addr, scheme = _parse_line(line)
                if not addr:
                    continue
                if proto.upper() == 'ALL':
                    key = (scheme or 'http').upper()
                else:
                    key = proto.upper()
                if key not in [p.upper() for p in protocols]:
                    continue
                local.setdefault(key, set()).add(addr)
            with lock:
                for k, v in local.items():
                    results.setdefault(k, set()).update(v)
                ok[0] += 1
        except Exception:
            pass

    threads = [threading.Thread(target=work, args=(s,)) for s in wanted]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    combined = set()
    for proto, proxies in sorted(results.items()):
        path = os.path.join(OUT_DIR, f'{proto.lower()}.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sorted(proxies)) + ('\n' if proxies else ''))
        combined |= proxies
    if combined:
        with open(os.path.join(OUT_DIR, 'all.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(sorted(combined)) + '\n')
    return results, ok[0]


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🌐', 'PROXY SCRAPER')
    w = kevbin._bw()
    kevbin.box_top(w)
    kevbin.box_row(' 1. Scrape ALL protocols', w)
    kevbin.box_row(' 2. HTTP / HTTPS only', w)
    kevbin.box_row(' 3. SOCKS4 only', w)
    kevbin.box_row(' 4. SOCKS5 only', w)
    kevbin.box_bottom(w)

    choice = kevbin.input_choice("  Select: ")
    if choice == '0':
        return
    proto_map = {'1': ['http', 'https', 'socks4', 'socks5'],
                 '2': ['http', 'https'],
                 '3': ['socks4'],
                 '4': ['socks5']}
    if choice not in proto_map:
        kevbin.cprint(kevbin.t.error, "  [X] Invalid choice.")
        kevbin.pause()
        return

    kevbin.cprint(kevbin.t.dim, f"\n  Scraping {len(proto_map[choice])} protocol-type sources...")
    results, ok = _scrape(proto_map[choice])

    kevbin.cprint(kevbin.t.highlight, f"\n  [+] Done — {ok} sources reached")
    for proto, proxies in sorted(results.items()):
        kevbin.cprint(kevbin.t.success, f"      {proto:<6}{len(proxies):>7} saved  ->  proxies/{proto.lower()}.txt")
    kevbin.cprint(kevbin.t.success, f"      {'ALL':<6}{sum(len(v) for v in results.values()):>7} saved  ->  proxies/all.txt")
    kevbin.cprint(kevbin.t.dim, f"      Folder: {OUT_DIR}")
    kevbin.pause()
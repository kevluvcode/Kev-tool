"""IP Grabber — Create tracking links to capture IP addresses."""

import json
import os
import sys
import time
import hashlib
import re
import socket
import http.server
import threading
import urllib.request

try:
    import requests
except ImportError:
    requests = None

try:
    from kevbin import clear, cprint, pause
except ImportError:
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    def cprint(*a, **kw):
        msg = ' '.join(str(x) for x in a)
        sys.stdout.write(msg + '\n')
        sys.stdout.flush()
    def prompt(msg=''):
        sys.stdout.write(msg)
        sys.stdout.flush()
        return input()
    def pause():
        prompt('\n  \033[90mPress Enter to continue...\033[0m')

RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[90m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'

LOG_FILE = 'grabber_log.json'
_HTTP_SERVER = getattr(http.server, 'ThreadingHTTPServer', http.server.HTTPServer)
_ANSI_RE = re.compile(r'\033\[[0-9;]*m')
_LOG_LOCK = threading.Lock()

SETTINGS = {'redirect': '', 'alias': '', 'port': 8080}


def prompt(msg=''):
    sys.stdout.write(msg)
    sys.stdout.flush()
    return input()


def _out(msg=''):
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def _visible(s):
    return len(_ANSI_RE.sub('', str(s)))


def _ljust(s, w):
    s = str(s)
    return s + ' ' * max(0, w - _visible(s))


def _center(s, w):
    s = str(s)
    vis = _visible(s)
    left = max(0, (w - vis) // 2)
    right = max(0, w - vis - left)
    return ' ' * left + s + ' ' * right


def _ellipsize(s, n):
    s = str(s or '').replace('\n', ' ').replace('\r', ' ').strip()
    return s if len(s) <= n else s[:n - 1] + '…'


def _now():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def _short_id(seed=''):
    raw = seed + str(time.time()) + str(os.getpid())
    return hashlib.md5(raw.encode('utf-8', 'ignore')).hexdigest()[:8]


def _lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except OSError:
        return '127.0.0.1'
    finally:
        s.close()


def _load_log():
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def _append_log(entry):
    with _LOG_LOCK:
        rows = _load_log()
        rows.append(entry)
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)


def _http_json(url, payload=None, timeout=10):
    if requests is not None:
        if payload is None:
            r = requests.get(url, timeout=timeout,
                             headers={'User-Agent': 'kev-tool'})
        else:
            r = requests.post(url, json=payload, timeout=timeout,
                              headers={'User-Agent': 'kev-tool'})
        r.raise_for_status()
        return r.json()
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    method = 'GET' if payload is None else 'POST'
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={'User-Agent': 'kev-tool',
                                          'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _panel(title, lines, color=CYAN):
    width = max([_visible(x) for x in lines] + [_visible(title), 20]) + 4
    _out('  ' + color + '┌' + '─' * width + '┐' + RESET)
    _out('  ' + color + '│' + RESET + ' ' + BOLD + WHITE
         + _ljust(title, width - 2) + RESET + color + ' │' + RESET)
    if lines:
        _out('  ' + color + '├' + '─' * width + '┤' + RESET)
        for line in lines:
            _out('  ' + color + '│' + RESET + ' ' + _ljust(line, width - 2)
                 + color + ' │' + RESET)
    _out('  ' + color + '└' + '─' * width + '┘' + RESET)


def _banner(title):
    inner = 48
    _out()
    _out(BOLD + MAGENTA + '  ╔' + '═' * inner + '╗' + RESET)
    _out(MAGENTA + '  ║' + RESET + BOLD + WHITE + _center(title, inner)
         + RESET + MAGENTA + '║' + RESET)
    _out(BOLD + MAGENTA + '  ╠' + '═' * inner + '╣' + RESET)


def _menu_item(key, label):
    _out(MAGENTA + '  ║' + RESET + '   ' + YELLOW + '[' + key + ']'
         + RESET + ' ' + _ljust(label, 41) + MAGENTA + '║' + RESET)


def _menu_bottom():
    _out(BOLD + MAGENTA + '  ╚' + '═' * 48 + '╝' + RESET)


class CaptureHandler(http.server.BaseHTTPRequestHandler):
    server_version = 'KevTool'

    def do_GET(self):
        self._handle()

    def do_HEAD(self):
        self._handle(head=True)

    def _handle(self, head=False):
        ip = self.client_address[0]
        forwarded = self.headers.get('X-Forwarded-For')
        if forwarded:
            ip = forwarded.split(',')[0].strip()
        entry = {
            'type': 'hit',
            'time': _now(),
            'epoch': int(time.time()),
            'ip': ip,
            'method': self.command,
            'path': self.path,
            'user_agent': self.headers.get('User-Agent', ''),
            'referrer': self.headers.get('Referer',
                                         self.headers.get('Referrer', '')),
            'alias': SETTINGS.get('alias', ''),
        }
        _append_log(entry)
        stamp = time.strftime('%H:%M:%S')
        _out(GREEN + '  [' + stamp + '] ' + BOLD + 'CAPTURED ' + ip + RESET
             + DIM + '  ' + entry['method'] + ' ' + entry['path'] + RESET)
        _out(DIM + '      UA: ' + _ellipsize(entry['user_agent'], 72) + RESET)
        if entry['referrer']:
            _out(DIM + '      Ref: '
                 + _ellipsize(entry['referrer'], 70) + RESET)
        redirect = SETTINGS.get('redirect', '')
        if redirect and not head:
            self.send_response(302)
            self.send_header('Location', redirect)
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        body = (b'<!doctype html><html><head><title>Home</title></head>'
                b'<body style="background:#101014;color:#e6e6e6;'
                b'font-family:sans-serif;text-align:center;padding-top:40vh">'
                b'<p>Nothing to see here.</p></body></html>')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def _wrap_link(url, width=56):
    chunks = []
    rest = url
    while rest:
        chunks.append(rest[:width])
        rest = rest[width:]
    return chunks


def _generate_link():
    clear()
    _banner('GENERATE GRABBER LINK')
    _out(DIM + '  Build a link that records the visitor IP when opened.'
         + RESET)
    _out(DIM + '  Use only on systems you have permission to test.' + RESET)
    _out()
    redirect = prompt('  [?] Redirect URL after capture (blank = none): ')
    redirect = redirect.strip()
    alias = prompt('  [?] Custom alias (optional, blank = auto): ').strip()
    if not alias:
        alias = _short_id(redirect)
    SETTINGS['redirect'] = redirect
    SETTINGS['alias'] = alias
    _out()
    _out(BOLD + '  Link source:' + RESET)
    _out('   ' + YELLOW + '[1]' + RESET
         + ' Public endpoint (webhook.site, works instantly)')
    _out('   ' + YELLOW + '[2]' + RESET
         + ' Local server link (use menu option 2 to activate)')
    src = prompt('  [>] Select: ').strip()
    _out()
    dash = ''
    if src == '1':
        _out(CYAN + '  [*] Requesting endpoint from webhook.site...' + RESET)
        try:
            data = _http_json('https://webhook.site/token', payload={})
            uid = data.get('uuid')
            if not uid:
                raise ValueError('no uuid in response')
            link = 'https://webhook.site/' + uid
            dash = ('https://webhook.site/#!/token/' + uid + '/requests')
            _out(GREEN + '  [+] Endpoint created.' + RESET)
        except Exception as exc:
            _out(RED + '  [!] Could not reach webhook.site: ' + str(exc)
                 + RESET)
            _out(YELLOW + '  [i] Falling back to local server link.' + RESET)
            link = 'http://' + _lan_ip() + ':' + str(SETTINGS['port']) \
                + '/' + alias
            dash = 'activate via menu option 2'
    else:
        link = 'http://' + _lan_ip() + ':' + str(SETTINGS['port']) \
            + '/' + alias
        dash = 'activate via menu option 2'
    lines = []
    wrapped = _wrap_link(link)
    lines.append(YELLOW + BOLD + wrapped[0] + RESET)
    for extra in wrapped[1:]:
        lines.append(YELLOW + extra + RESET)
    lines.append('')
    lines.append(WHITE + 'Alias:    ' + RESET + alias)
    lines.append(WHITE + 'Redirect: ' + RESET + (redirect or '(decoy page)'))
    lines.append(WHITE + 'Results:  ' + RESET + (dash or 'local server log'))
    _panel('TRACKING LINK READY', lines)
    _out()
    if dash.startswith('http'):
        _out(DIM + '  View captures at:' + RESET)
        _out(CYAN + '  ' + dash + RESET)
    else:
        _out(DIM + '  Start "Local Capture Server" (option 2) with the same'
             + RESET)
        _out(DIM + '  port, then share the link above.' + RESET)
    pause()


def _start_server_flow():
    clear()
    _banner('LOCAL CAPTURE SERVER')
    _out(DIM + '  Any visit to this server is logged to ' + LOG_FILE
         + RESET)
    _out()
    raw = prompt('  [?] Port [' + str(SETTINGS['port']) + ']: ').strip()
    if raw.isdigit() and 0 < int(raw) < 65536:
        SETTINGS['port'] = int(raw)
    port = SETTINGS['port']
    alias = SETTINGS.get('alias') or _short_id()
    SETTINGS['alias'] = alias
    lan = _lan_ip()
    try:
        server = _HTTP_SERVER(('0.0.0.0', port), CaptureHandler)
    except OSError as exc:
        _out(RED + '  [!] Could not bind port ' + str(port) + ': '
             + str(exc) + RESET)
        pause()
        return
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever,
                              kwargs={'poll_interval': 0.25}, daemon=True)
    thread.start()
    _panel('SERVER RUNNING', [
        WHITE + 'Local:    ' + RESET + 'http://127.0.0.1:' + str(port)
        + '/' + alias,
        WHITE + 'Network:  ' + RESET + 'http://' + lan + ':' + str(port)
        + '/' + alias,
        WHITE + 'Redirect: ' + RESET
        + (SETTINGS.get('redirect') or '(decoy page)'),
        WHITE + 'Log:      ' + RESET + os.path.abspath(LOG_FILE),
        DIM + 'Press Ctrl+C to stop.' + RESET,
    ], color=GREEN)
    _out()
    _out(DIM + '  Waiting for requests...' + RESET)
    try:
        while thread.is_alive():
            time.sleep(0.25)
    except KeyboardInterrupt:
        _out()
        _out(YELLOW + '  [!] Ctrl+C received — shutting down...' + RESET)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        _out(GREEN + '  [+] Server stopped. Captures saved to '
             + os.path.abspath(LOG_FILE) + RESET)
    pause()


def _geo_lookup(ip):
    url = ('http://ip-api.com/json/' + ip
           + '?fields=status,message,country,regionName,city,isp,query')
    try:
        data = _http_json(url, timeout=8)
        if data.get('status') == 'success':
            parts = [data.get('city', ''), data.get('regionName', ''),
                     data.get('country', '')]
            loc = ', '.join(p for p in parts if p)
            isp = _ellipsize(data.get('isp', ''), 24)
            return loc or '?', isp
        return 'private?', data.get('message', 'fail')
    except Exception:
        return '?', '?'


def _view_logs():
    clear()
    _banner('CAPTURED IPS')
    rows = [r for r in _load_log() if isinstance(r, dict) and r.get('ip')]
    if not rows:
        _out(YELLOW + '  [i] No captures yet. Log file: '
             + os.path.abspath(LOG_FILE) + RESET)
        pause()
        return
    rows = rows[-40:]
    shown = len(rows)
    total = len([r for r in _load_log() if isinstance(r, dict)
                 and r.get('ip')])
    unique = []
    for row in reversed(rows):
        if row.get('ip') not in unique:
            unique.append(row.get('ip'))
    unique = unique[:12]
    geo = {}
    _out(DIM + '  [*] Resolving locations via ip-api.com (Ctrl+C to skip)...'
         + RESET)
    try:
        for ip in unique:
            sys.stdout.write('\r  [*] ' + ip + '          ')
            sys.stdout.flush()
            geo[ip] = _geo_lookup(ip)
            time.sleep(0.35)
    except KeyboardInterrupt:
        _out()
        _out(YELLOW + '  [!] Lookup skipped.' + RESET)
    sys.stdout.write('\r' + ' ' * 60 + '\r')
    sys.stdout.flush()
    cols = [19, 16, 26, 34]
    headers = ['TIME', 'IP', 'LOCATION / ISP', 'USER-AGENT']

    def sep(left, mid, right):
        return '  ' + left + mid.join('─' * (c + 2) for c in cols) + right

    def trow(cells, color=RESET):
        body = (' ' + BLUE + '│' + RESET + ' ').join(
            _ljust(cell, c) for cell, c in zip(cells, cols))
        return '  ' + BLUE + '│' + RESET + ' ' + body + ' ' + BLUE + '│' \
            + RESET

    _out()
    _out(sep('┌', '┬', '┐'))
    _out(trow([BOLD + WHITE + h + RESET for h in headers]))
    _out(sep('├', '┼', '┤'))
    for row in rows:
        ip = row.get('ip', '?')
        loc, isp = geo.get(ip, ('…', '…'))
        loc_cell = _ellipsize(loc, cols[2])
        if isp and isp not in ('?', '…'):
            loc_cell = _ellipsize(loc + ' · ' + isp, cols[2])
        cells = [
            row.get('time', '?'),
            CYAN + ip + RESET,
            loc_cell,
            DIM + _ellipsize(row.get('user_agent', ''), cols[3]) + RESET,
        ]
        _out(trow(cells))
    _out(sep('└', '┴', '┘'))
    _out()
    _out(DIM + '  Showing last ' + str(shown) + ' of ' + str(total)
         + ' captures · ' + os.path.abspath(LOG_FILE) + RESET)
    pause()


def _ip_lookup():
    clear()
    _banner('IP LOOKUP')
    _out(DIM + '  Geolocation via http://ip-api.com' + RESET)
    _out()
    target = prompt('  [?] IP address or host (blank = cancel): ').strip()
    if not target:
        return
    _out(CYAN + '  [*] Querying...' + RESET)
    url = ('http://ip-api.com/json/' + target
           + '?fields=status,message,country,regionName,city,zip,isp,org,'
             'as,timezone,lat,lon,reverse,mobile,proxy,hosting,query')
    try:
        data = _http_json(url, timeout=10)
    except Exception as exc:
        _out(RED + '  [!] Lookup failed: ' + str(exc) + RESET)
        pause()
        return
    if data.get('status') != 'success':
        _out(RED + '  [!] API error: '
             + str(data.get('message', 'unknown')) + RESET)
        pause()
        return

    def flag(v):
        return GREEN + 'yes' + RESET if v else DIM + 'no' + RESET

    lines = [
        WHITE + 'IP:       ' + RESET + CYAN + str(data.get('query', '?'))
        + RESET,
        WHITE + 'Country:  ' + RESET + str(data.get('country', '?')),
        WHITE + 'Region:   ' + RESET + str(data.get('regionName', '?')),
        WHITE + 'City:     ' + RESET + str(data.get('city', '?'))
        + '  ' + DIM + str(data.get('zip', '')) + RESET,
        WHITE + 'ISP:      ' + RESET + str(data.get('isp', '?')),
        WHITE + 'Org:      ' + RESET + str(data.get('org', '?')),
        WHITE + 'AS:       ' + RESET + str(data.get('as', '?')),
        WHITE + 'Timezone: ' + RESET + str(data.get('timezone', '?')),
        WHITE + 'Lat/Lon:  ' + RESET + str(data.get('lat', '?')) + ', '
        + str(data.get('lon', '?')),
        WHITE + 'Reverse:  ' + RESET + str(data.get('reverse', '-') or '-'),
        WHITE + 'Flags:    ' + RESET + 'mobile=' + flag(data.get('mobile'))
        + '  proxy=' + flag(data.get('proxy'))
        + '  hosting=' + flag(data.get('hosting')),
    ]
    _out()
    _panel('LOOKUP RESULT', lines)
    pause()


def _clear_log():
    clear()
    _banner('CLEAR LOG')
    path = os.path.abspath(LOG_FILE)
    if not os.path.exists(path):
        _out(YELLOW + '  [i] No log file found at ' + path + RESET)
        pause()
        return
    try:
        count = len(_load_log())
    except Exception:
        count = 0
    _out('  Log file: ' + WHITE + path + RESET)
    _out('  Entries:  ' + str(count))
    _out()
    confirm = prompt('  [?] Delete grabber_log.json? (y/N): ').strip().lower()
    if confirm == 'y':
        try:
            os.remove(path)
            _out(GREEN + '  [+] Log deleted.' + RESET)
        except OSError as exc:
            _out(RED + '  [!] Could not delete: ' + str(exc) + RESET)
    else:
        _out(DIM + '  Cancelled.' + RESET)
    pause()


def run(kevbin=None):
    global clear, cprint, pause
    if kevbin is not None:
        clear = getattr(kevbin, 'clear', clear)
        cprint = getattr(kevbin, 'cprint', cprint)
        pause = getattr(kevbin, 'pause', pause)
    os.system('')
    while True:
        clear()
        _banner('I P   G R A B B E R')
        _menu_item('1', 'Generate Grabber Link')
        _menu_item('2', 'Start Local Capture Server')
        _menu_item('3', 'View Captured IPs')
        _menu_item('4', 'IP Lookup')
        _menu_item('5', 'Clear Log')
        _menu_item('0', 'Back')
        _menu_bottom()
        try:
            choice = prompt('  [>] Select: ').strip()
        except (EOFError, KeyboardInterrupt):
            _out()
            return
        try:
            if choice == '0':
                return
            elif choice == '1':
                _generate_link()
            elif choice == '2':
                _start_server_flow()
            elif choice == '3':
                _view_logs()
            elif choice == '4':
                _ip_lookup()
            elif choice == '5':
                _clear_log()
            else:
                _out(RED + '  [!] Unknown option.' + RESET)
                time.sleep(0.6)
        except KeyboardInterrupt:
            _out()
            _out(YELLOW + '  [!] Cancelled.' + RESET)
            time.sleep(0.5)

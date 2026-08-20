"""Honeypot Detector - web trap scanner + network honeypot fingerprinting.

Scans a website for honeypot traps (hidden form fields, CSS-hidden
clickable traps, JS timing/mouse gates, tracking pixels, anti-bot
platforms, tracking cookies, missing security headers) and produces a
scored verdict. Also detects and solves the InfinityFree "adda" AES
challenge (testcookie-nginx-module) so the real page behind it can be
scanned. Also has a network mode that port-scans a host and
fingerprints known honeypot service banners (Cowrie, Dionaea, etc).
"""

try:
    import requests
except ImportError:
    requests = None

import re
import socket
import threading
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

HONEYPOT_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS', 80: 'HTTP',
    110: 'POP3', 143: 'IMAP', 139: 'NetBIOS', 443: 'HTTPS', 445: 'SMB',
    993: 'IMAPS', 995: 'POP3S', 1433: 'MSSQL', 3306: 'MySQL', 3389: 'RDP',
    5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis', 8080: 'HTTP Proxy',
    8443: 'HTTPS Alt', 9200: 'Elasticsearch', 11211: 'Memcached',
    27017: 'MongoDB',
}

# Field names/ids/classes that are classic honeypot bait.
TRAP_NAME_HINTS = (
    'honeypot', 'hp_', '_hp', 'trap', 'gotcha', 'second_email', 'confirm_email',
    'email_confirmation', 'email_confirm', 'your_email', 'alt_email', 'email2',
    'email_address2', 'website', 'web_address', 'homepage', 'url2', 'url_2',
    'website2', 'company', 'company_name', 'fax', 'fax_number', 'phone2',
    'home_phone', 'work_phone', 'cell_phone', 'mobile2', 'other_phone',
    'address2', 'addr2', 'middle_name', 'last_name2', 'name2', 'your_name',
    'real_name', 'user2', 'username2', 'login2', 'password2', 'pass2',
    'confirm2', 'verify', 'verify_human', 'human_check', 'are_you_human',
    'is_human', 'bot_check', 'botcheck', 'captcha_optional', 'comments2',
    'message2', 'subject2', 'city2', 'state2', 'zip2', 'postal2', 'bio',
    'about_you', 'aboutme', 'mywebsite', 'social_handle', 'linkedin_url',
)

CSS_HIDDEN = re.compile(
    r'display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?:\.\d+)?\b|'
    r'position\s*:\s*absolute[^;}]*?(?:left|top)\s*:\s*-{0,1}\d{3,}px|'
    r'(?:left|top)\s*:\s*-{0,1}\d{3,}px|'
    r'width\s*:\s*0(?:\.\d+)?\s*px|height\s*:\s*0(?:\.\d+)?\s*px|'
    r'text-indent\s*:\s*-9999|z-index\s*:\s*-\d|font-size\s*:\s*0\s*(?:px|em)|'
    r'max-height\s*:\s*0|clip\s*:\s*rect\s*\([^)]*\)|clip-path\s*:\s*inset\s*\(0\s+0\s+0\s+0\)',
    re.I,
)

TRACK_PIXEL = re.compile(
    r'pixel|beacon|1x1|__utm\.gif|analytics.*\.gif|track\.gif|pix\.gif|'
    r'\.webp|\.png" [^>]*?(width|height)=["\']?1|sendBeacon|new\s+Image\s*\(',
    re.I,
)

JS_TRAP = re.compile(
    r"addEventListener\s*\(\s*['\"](?:mousemove|mousedown|mouseover|keydown|touch)['\"]|"
    r"onmousemove|onmousedown|onmouseover|activeElement|"
    r"\.type\s*===?\s*['\"]hidden['\"]|requestAnimationFrame|"
    r"Date\.now\s*\(\s*\)\s*[-+]|performance\.now\s*\(\s*\)|"
    r"setTimeout\s*\(\s*['\"](?:[^'\"]*)?submitted|navigator\.webdriver|"
    r"navigator\.userAgent|canvas\s*\.|toDataURL|getBoundingClientRect|"
    r"document\.referrer|document\.hidden",
    re.I,
)

ANTI_BOT = {
    'Cloudflare': [r'cf-ray', r'__cf_bm', r'cf_chl', r'challenge-platform', r'server["\']?:\s*cloudflare', r'cf_chl_opt'],
    'hCaptcha': [r'hcaptcha\.com', r'grecaptcha', r'hc_captcha', r'h-captcha'],
    'reCAPTCHA': [r'recaptcha', r'g-recaptcha', r'grecaptcha', r'recaptcha/api'],
    'Turnstile': [r'turnstile', r'cf-turnstile', r'challenges\.cloudflare\.com'],
    'Akamai': [r'akamai', r'bm-verify', r'_abck', r'ak_bmsc', r'bm_sz'],
    'DataDome': [r'datadome', r'x-datadome'],
    'PerimeterX': [r'perimeterx', r'_px\d*', r'px-captcha'],
    'Incapsula': [r'incap_ses', r'visid_incap', r'incapsula'],
    'Arkose': [r'arkose', r'enforcement\.fun'],
    'Kasada': [r'kasada', r'kpsdk'],
    'ShieldSquare': [r'shieldsquare', r'px\.js', r'captcha-delivery'],
    'FriendlyCaptcha': [r'friendlycaptcha', r'frc-captcha'],
    'Altcha': [r'altcha'],
    'Auth0': [r'auth0', r'lock\.min\.js'],
    'InfinityFree adda': [r'aes\.js', r'slowAES', r'__test\s*=.*slowAES'],
}

SECURITY_HEADERS = [
    ('Strict-Transport-Security', 'HSTS missing'),
    ('Content-Security-Policy', 'CSP missing'),
    ('X-Frame-Options', 'clickjacking guard missing'),
    ('X-Content-Type-Options', 'MIME sniffing guard missing'),
    ('Referrer-Policy', 'Referrer-Policy missing'),
    ('Permissions-Policy', 'Permissions-Policy missing'),
]

COOKIE_TRACKERS = ('__cf_bm', '_ga', '_gid', '__utm', '_sp_', '_pk_', 'ajs_', '_fbp', '_gcl', 'amp_', '_hjid', '__atuv')

ROBOTS_META = re.compile(r'noindex|nofollow|noarchive|nosnippet', re.I)

# Banner fingerprints for known honeypot services (network mode).
HONEYPOT_BANNERS = (
    re.compile(r'cowrie', re.I),
    re.compile(r'dionaea', re.I),
    re.compile(r'glastopf|snare|nepenthes|amun', re.I),
    re.compile(r'conpot|gaspot|thug|honeyd|kfsensor', re.I),
    re.compile(r'SSH-2\.0-OpenSSH_6\.0p1 Debian-4\+deb7u2', re.I),
    re.compile(r'SSH-1\.99-OpenSSH_5\.1p1 Debian-6', re.I),
    re.compile(r'SSH-2\.0-OpenSSH_6\.6\.1 Debian-1', re.I),
    re.compile(r'SSH-2\.0-OpenSSH_5\.1p1 FreeBSD', re.I),
    re.compile(r'SSH-2\.0-libssh-0\.\d+$', re.I),
    re.compile(r'SSH-2\.0-OpenSSH_7\.9p1 Ubuntu', re.I),
    re.compile(r'220\s+.*honeypot', re.I),
    re.compile(r'220.*EscapeTelnet', re.I),
    re.compile(r'CandyPot|moodlepot|hellpot|apachehoney', re.I),
)

# ---------------------------------------------------------------------------
# InfinityFree "adda" AES-128 challenge solver (testcookie-nginx-module).
# The challenge page serves: slowAES.decrypt(c, 2, a, b) where a=key,
# b=iv, c=encrypted cookie value. It's AES-128 in CBC mode; the expected
# cookie value is the hex plaintext of a single 16-byte block.
# ---------------------------------------------------------------------------

ADDA_CHALLENGE = re.compile(
    r'toNumbers\s*\(\s*["\']([0-9a-fA-F]{32})["\']\s*\)\s*,'
    r'\s*\w+\s*=\s*toNumbers\s*\(\s*["\']([0-9a-fA-F]{32})["\']\s*\)\s*,'
    r'\s*\w+\s*=\s*toNumbers\s*\(\s*["\']([0-9a-fA-F]{32})["\']\s*\)',
    re.S,
)

_SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
]
_INV_SBOX = [0] * 256
for _i, _v in enumerate(_SBOX):
    _INV_SBOX[_v] = _i

_RCON = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36)


def _gm(a, b):
    r = 0
    for _ in range(8):
        if b & 1:
            r ^= a
        hi = a & 0x80
        a = (a << 1) & 0xff
        if hi:
            a ^= 0x1b
        b >>= 1
    return r


def _key_expansion(key):
    w = list(key)
    for i in range(4, 44):
        t = w[4 * (i - 1):4 * i]
        if i % 4 == 0:
            t = t[1:] + t[:1]
            t = [_SBOX[b] for b in t]
            t[0] ^= _RCON[i // 4 - 1]
        p = w[4 * (i - 4):4 * (i - 3)]
        w.extend((t[j] ^ p[j]) for j in range(4))
    return w


def _add_round_key(state, w):
    for i in range(16):
        state[i] ^= w[i]


def _inv_shift_rows(state):
    for r in (1, 2, 3):
        row = [state[r + 4 * c] for c in range(4)]
        row = row[-r:] + row[:-r]
        for c in range(4):
            state[r + 4 * c] = row[c]


def _inv_mix_columns(state):
    for c in range(4):
        a0, a1, a2, a3 = (state[r + 4 * c] for r in range(4))
        state[0 + 4 * c] = _gm(a0, 14) ^ _gm(a1, 11) ^ _gm(a2, 13) ^ _gm(a3, 9)
        state[1 + 4 * c] = _gm(a0, 9) ^ _gm(a1, 14) ^ _gm(a2, 11) ^ _gm(a3, 13)
        state[2 + 4 * c] = _gm(a0, 13) ^ _gm(a1, 9) ^ _gm(a2, 14) ^ _gm(a3, 11)
        state[3 + 4 * c] = _gm(a0, 11) ^ _gm(a1, 13) ^ _gm(a2, 9) ^ _gm(a3, 14)


def _aes128_decrypt_block(ct, key):
    state = list(ct)
    w = _key_expansion(key)
    _add_round_key(state, w[160:176])
    for r in range(9, 0, -1):
        _inv_shift_rows(state)
        state = [_INV_SBOX[b] for b in state]
        _add_round_key(state, w[16 * r:16 * (r + 1)])
        _inv_mix_columns(state)
    _inv_shift_rows(state)
    state = [_INV_SBOX[b] for b in state]
    _add_round_key(state, w[0:16])
    return bytes(state)


def _aes128_cbc_decrypt(ct, key, iv):
    blk = _aes128_decrypt_block(ct, key)
    return bytes(blk[i] ^ iv[i] for i in range(16))


def _extract_adda(html):
    """Return (key_hex, iv_hex, ct_hex) if this is an InfinityFree adda challenge."""
    if not ADDA_CHALLENGE.search(html):
        return None
    if not re.search(r'slowAES|__test\s*=', html, re.I):
        return None
    m = ADDA_CHALLENGE.search(html)
    return m.group(1), m.group(2), m.group(3)


def solve_adda(html):
    """Solve the InfinityFree adda AES challenge, returning the __test cookie value."""
    found = _extract_adda(html)
    if not found:
        return None
    key = bytes.fromhex(found[0])
    iv = bytes.fromhex(found[1])
    ct = bytes.fromhex(found[2])
    if not (len(key) == len(iv) == len(ct) == 16):
        return None
    pt = _aes128_cbc_decrypt(ct, key, iv)
    return pt.hex()


def _attr(attrs, key):
    for k, v in attrs:
        if k.lower() == key:
            return (v or '').strip()
    return ''


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.inputs = []
        self.forms = []
        self.images = []
        self.links = []
        self.scripts = []
        self.metas = []
        self.buttons = []
        self.textareas = []
        self.selects = []
        self.in_script = False
        self.script_buf = []
        self.script_srcs = []
        self.inline_style = []

    def handle_starttag(self, tag, attrs):
        d = {k.lower(): (v or '') for k, v in attrs}
        tag = tag.lower()
        if tag == 'input':
            self.inputs.append(d)
        elif tag == 'form':
            self.forms.append(d)
        elif tag == 'img':
            self.images.append(d)
        elif tag == 'a':
            self.links.append(d)
        elif tag == 'script':
            src = d.get('src', '')
            if src:
                self.script_srcs.append(src)
            self.in_script = True
            self.script_buf = []
        elif tag == 'meta':
            self.metas.append(d)
        elif tag == 'button':
            self.buttons.append(d)
        elif tag == 'textarea':
            self.textareas.append(d)
        elif tag == 'select':
            self.selects.append(d)
        elif tag == 'style':
            self.inline_style.append('')

    def handle_endtag(self, tag):
        if tag.lower() == 'script':
            self.scripts.append(''.join(self.script_buf))
            self.in_script = False

    def handle_data(self, data):
        if self.in_script:
            self.script_buf.append(data)


def _style_attrs(d):
    return (d.get('style', '') + ' ' + d.get('class', '')).lower()


def _is_css_hidden(d):
    return bool(CSS_HIDDEN.search(_style_attrs(d)))


def _is_trap_name(*values):
    joined = ' '.join(v for v in values if v).lower()
    if not joined:
        return False
    for hint in TRAP_NAME_HINTS:
        if hint in joined:
            return True
    return bool(re.search(r'(?:^|_)(?:hp|bot|trap)\d*$', joined))


def _is_pixel(img):
    w = re.sub(r'[^0-9]', '', img.get('width', ''))
    h = re.sub(r'[^0-9]', '', img.get('height', ''))
    src = img.get('src', '')
    try:
        if (w and int(w) <= 2) or (h and int(h) <= 2):
            return True
    except ValueError:
        pass
    return bool(TRACK_PIXEL.search(src))


def _fetch(kevbin, url, cookies=None):
    if requests is None:
        kevbin.box.error("  requests not installed - pip install requests")
        return None
    try:
        return requests.get(url, headers={
            'User-Agent': UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
        }, cookies=cookies, timeout=15, allow_redirects=True, verify=True)
    except Exception as e:
        kevbin.box.error(f"  Failed to fetch: {e}")
        return None


def analyze_html(html, url, headers, cookies):
    findings = []
    collector = Collector()
    try:
        collector.feed(html)
    except Exception:
        pass

    def add(sev, msg):
        findings.append((sev, msg))

    hidden_fields = 0
    for d in collector.inputs:
        ftype = (d.get('type', 'text') or '').lower()
        name = d.get('name', '')
        ident = d.get('id', '')
        hidden_attr = ftype == 'hidden'
        css_hidden = _is_css_hidden(d)
        trap = _is_trap_name(name, ident, d.get('class', ''))
        autofocus = d.get('autofocus') is not None
        if hidden_attr or css_hidden:
            hidden_fields += 1
            why = 'type=hidden' if hidden_attr else 'CSS-hidden'
            if trap:
                add('high', f"Hidden bait field '{name or ident}' ({why}) - classic honeypot")
            elif ftype in ('text', 'email', 'tel', 'password', 'url') and (name or ident):
                add('med', f"Hidden form field '{name or ident}' ({why})")
            elif autofocus and hidden_attr:
                add('high', f"Autofocus on hidden field '{name or ident}' - focus trap")
        else:
            if trap:
                add('med', f"Visible field named like trap bait: '{name or ident}'")
            if autofocus and css_hidden:
                add('high', f"Autofocus on invisible field '{name or ident}'")

    for d in collector.textareas + collector.selects:
        if _is_css_hidden(d) and _is_trap_name(d.get('name', ''), d.get('id', ''), d.get('class', '')):
            add('high', f"Hidden {d.get('name', 'field')} trap")

    hidden_links = 0
    for d in collector.links:
        if _is_css_hidden(d) and d.get('href', ''):
            hidden_links += 1
            add('high', f"Hidden clickable link -> {d.get('href', '')[:60]}")
    for d in collector.buttons:
        if _is_css_hidden(d):
            add('med', "Hidden button (possible trap)")

    pixels = 0
    for d in collector.images:
        if _is_pixel(d):
            pixels += 1
            add('low', f"Tracking pixel: {d.get('src', '')[:60] or '(no src)'}")

    all_js = ' '.join(collector.scripts)
    js_found = []
    for hit in JS_TRAP.findall(all_js):
        if hit and hit not in js_found:
            js_found.append(hit)
    if js_found:
        add('med', f"JS interaction/timing checks: {', '.join(js_found[:5])}")
    if re.search(r'getElementById\s*\(\s*[\'\"](?:hp|honeypot|trap|website|email2|url2)', all_js, re.I):
        add('high', "JS references honeypot field ids directly")
    if 'sendBeacon' in all_js:
        add('low', "sendBeacon() used (telemetry/exfil)")

    hay = ' '.join(collector.scripts) + ' ' + ' '.join(collector.script_srcs) + ' ' + cookies.lower() + ' ' + str(headers)
    platforms = []
    for name, pats in ANTI_BOT.items():
        if name == 'InfinityFree adda':
            continue
        if any(re.search(p, hay, re.I) for p in pats):
            platforms.append(name)
    if platforms:
        add('med', f"Anti-bot platform: {', '.join(platforms)}")

    robots = []
    for m in collector.metas:
        if m.get('name', '').lower() == 'robots' and ROBOTS_META.search(m.get('content', '')):
            robots.append(m['content'])
    if robots:
        add('low', f"robots meta: {', '.join(robots)}")

    track_cookies = [c for c in cookies.split(';') if any(t in c.lower() for t in COOKIE_TRACKERS)]
    if track_cookies:
        add('low', f"Tracking cookies: {', '.join(c.strip().split('=')[0] for c in track_cookies[:6])}")

    for hdr, why in SECURITY_HEADERS:
        if hdr.lower() not in headers:
            add('low', why)

    return {
        'html_len': len(html),
        'hidden_fields': hidden_fields,
        'hidden_links': hidden_links,
        'pixels': pixels,
        'platforms': platforms,
        'findings': findings,
    }


def scan_website(kevbin, url):
    resp = _fetch(kevbin, url)
    if resp is None:
        return None

    html = resp.text
    final_url = resp.url
    headers = {k.lower(): v for k, v in resp.headers.items()}
    cookies = '; '.join(f"{c.name}={c.value}" for c in resp.cookies)

    adda = None
    if 'slowAES' in html or '__test' in html or re.search(r'aes\.js', html, re.I):
        adda = _extract_adda(html)
        if adda:
            kevbin.box.warn("  [!] InfinityFree 'adda' AES challenge detected")
            kevbin.box.info(f"  key={adda[0]}  iv={adda[1]}  cipher={adda[2]}")
            cookie = solve_adda(html)
            if cookie:
                kevbin.box.success(f"  [+] Solved! __test cookie = {cookie}")
                kevbin.box.info("  Re-fetching with cookie to reveal the real page...")
                resp2 = _fetch(kevbin, final_url, cookies={'__test': cookie})
                if resp2 is not None and 'slowAES' not in resp2.text and '__test' not in resp2.text:
                    html = resp2.text
                    headers = {k.lower(): v for k, v in resp2.headers.items()}
                    cookies = '; '.join(f"{c.name}={c.value}" for c in resp2.cookies)
                    kevbin.box.success("  [+] Real page retrieved behind the challenge")
                else:
                    kevbin.box.warn("  [~] Cookie not accepted on first pass - using challenge page analysis")

    result = analyze_html(html, url, headers, cookies)
    result.update({
        'url': url, 'final': final_url, 'status': resp.status_code,
        'server': headers.get('server', 'unknown'),
        'redirects': len(resp.history),
        'adda': bool(adda),
        'adda_cookie': solve_adda(html) if adda else None,
    })
    return result


def score_findings(findings):
    w = {'high': 10, 'med': 6, 'low': 2}
    total = sum(w.get(s, 2) for s, _ in findings)
    return min(100, total)


def verdict(score):
    if score == 0:
        return 'CLEAN', kevbin_success
    if score <= 19:
        return 'LOW RISK', kevbin_success
    if score <= 39:
        return 'SUSPICIOUS', kevbin_warn
    if score <= 64:
        return 'LIKELY HONEYPOT', kevbin_warn
    return 'CONFIRMED HONEYPOT', kevbin_error


def scan_ports(kevbin, ip):
    results = []
    lock = threading.Lock()

    def probe(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            if s.connect_ex((ip, port)) == 0:
                banner = ''
                if port in (21, 22, 23, 25, 110, 143, 445, 1433, 3306, 5432, 5900, 6379):
                    try:
                        s.settimeout(3.0)
                        if port in (22, 23, 25, 110, 143, 445):
                            banner = s.recv(256).decode('utf-8', 'ignore').strip()
                        else:
                            s.sendall(b'\r\n')
                            banner = s.recv(256).decode('utf-8', 'ignore').strip()
                    except Exception:
                        pass
                with lock:
                    results.append((port, banner))
            s.close()
        except Exception:
            pass

    threads = []
    for port in HONEYPOT_PORTS:
        t = threading.Thread(target=probe, args=(port,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    rows = []
    hp_hits = 0
    for port, banner in sorted(results):
        svc = HONEYPOT_PORTS.get(port, '?')
        flagged = any(p.search(banner) for p in HONEYPOT_BANNERS) if banner else False
        if flagged:
            hp_hits += 1
        rows.append([port, svc, banner[:50] if banner else 'OPEN (no banner)', 'HONEYPOT!' if flagged else '-'])
    return rows, hp_hits


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🍯', 'HONEYPOT DETECTOR')
    kevbin.cprint(kevbin.t.secondary, "  Scans websites for honeypot traps or fingerprints a host's honeypot ports.")
    kevbin.line()

    if requests is None:
        kevbin.box.warn("  [i] requests not installed - web mode disabled (pip install requests)")

    kevbin.cprint(kevbin.t.num, "    [1] Scan a website (URL) - auto-solves InfinityFree adda AES")
    kevbin.cprint(kevbin.t.num, "    [2] Scan an IP / host (ports + banners)")
    mode = kevbin.box.input("  Mode", '1').strip()

    if mode == '2':
        ip = kevbin.box.input("  Target IP/host", '').strip()
        if not ip:
            kevbin.box.warn("  No target.")
            kevbin.pause()
            return
        kevbin.cprint(kevbin.t.txt, f"\n  Scanning {ip} ({len(HONEYPOT_PORTS)} ports)...\n")
        rows, hp_hits = scan_ports(kevbin, ip)
        if rows:
            kevbin.box.table(['Port', 'Service', 'Banner', 'Note'], rows, title='PORT RESULTS')
        else:
            kevbin.box.warn("  No common honeypot ports open.")
        if hp_hits:
            kevbin.box.error(f"  [!] {hp_hits} banner(s) match known honeypot fingerprints!")
        kevbin.box.info("  Note: open ports alone don't mean honeypot. Check banner + behavior.")
        kevbin.pause()
        return

    url = kevbin.box.input("  Target URL", '').strip()
    if not url:
        kevbin.box.warn("  No URL.")
        kevbin.pause()
        return
    if '://' not in url:
        url = 'https://' + url

    result = scan_website(kevbin, url)
    if not result:
        kevbin.pause()
        return

    kevbin.line()
    kevbin.box.title('SCAN PROFILE')
    kevbin.box.table(['Key', 'Value'], [
        ['Target', result['url']],
        ['Final URL', result['final']],
        ['Status', result['status']],
        ['Redirects', result['redirects']],
        ['Server', result['server']],
        ['HTML size', f"{result['html_len']} bytes"],
        ['Hidden fields', result['hidden_fields']],
        ['Hidden links', result['hidden_links']],
        ['Tracking pixels', result['pixels']],
        ['Anti-bot', ', '.join(result['platforms']) or 'none detected'],
        ['Adda solved', f"yes ({result['adda_cookie']})" if result['adda_cookie'] else ('detected, unsolved' if result['adda'] else 'no challenge')],
    ])

    score = score_findings(result['findings'])
    label, color_fn = verdict(score)

    kevbin.line()
    kevbin.box.title('FINDINGS')
    if not result['findings']:
        kevbin.box.success("  No honeypot indicators detected.")
    else:
        for sev, msg in result['findings']:
            if sev == 'high':
                kevbin.box.error(f"  [!!] {msg}")
            elif sev == 'med':
                kevbin.box.warn(f"  [!]  {msg}")
            else:
                kevbin.box.info(f"  [~]  {msg}")

    kevbin.line()
    kevbin.box.title('HONEYPOT SCORE')
    bar = 20
    filled = round(score / 100 * bar)
    color_fn(kevbin, f"  [{'█' * filled}{'░' * (bar - filled)}]  {score}/100  ->  {label}")
    if score >= 40:
        kevbin.box.error("  This page is very likely serving bots a honeypot. Avoid automated use.")
    elif score >= 15:
        kevbin.box.warn("  Some anti-bot/trap patterns present.")
    else:
        kevbin.box.success("  Looks clean.")
    kevbin.box.info("  Tips: hidden fields with bait names, mouse-move gated submits and")
    kevbin.box.info("  off-screen links are the strongest honeypot signals.")
    kevbin.pause()


def kevbin_success(kevbin, text):
    kevbin.box.success(text)


def kevbin_warn(kevbin, text):
    kevbin.box.warn(text)


def kevbin_error(kevbin, text):
    kevbin.box.error(text)

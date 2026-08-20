"""misc_tools — a grab-bag of fast, stdlib-only tools that never touch the network."""

import os
import re
import sys
import json
import glob
import random
import string
import hashlib
import datetime
import urllib.parse

_digits = string.digits
_letters = string.ascii_letters + string.digits
HEX_BASE = "0123456789abcdef"
BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
}
MORSE_REV = {v: k for k, v in MORSE.items()}
UPSIDE_DOWN = str.maketrans({
    'a': 'ɐ', 'b': 'q', 'c': 'ɔ', 'd': 'p', 'e': 'ǝ', 'f': 'ɟ', 'g': 'ƃ', 'h': 'ɥ', 'i': 'ı',
    'j': 'ɾ', 'k': 'ʞ', 'l': 'l', 'm': 'ɯ', 'n': 'u', 'o': 'o', 'p': 'd', 'q': 'b', 'r': 'ɹ',
    's': 's', 't': 'ʇ', 'u': 'n', 'v': 'ʌ', 'w': 'ʍ', 'x': 'x', 'y': 'ʎ', 'z': 'z',
    'A': '∀', 'B': '𐐒', 'C': 'Ɔ', 'D': 'ᗡ', 'E': 'Ǝ', 'F': 'Ⅎ', 'G': '⅁', 'H': 'H', 'I': 'I',
    'J': 'ſ', 'K': 'ʞ', 'L': '˥', 'M': 'W', 'N': 'N', 'O': 'O', 'P': 'Ԁ', 'Q': 'Q', 'R': 'ᴚ',
    'S': 'S', 'T': '⊥', 'U': '∩', 'V': 'Λ', 'W': 'M', 'X': 'X', 'Y': 'ʎ', 'Z': 'Z',
    '0': '0', '1': 'Ɩ', '2': 'ᄅ', '3': 'Ɛ', '4': 'ㄣ', '5': 'ϛ', '6': '9', '7': 'ㄥ', '8': '8', '9': '6',
    '?': '¿', '!': '¡', '.': '˙', ',': "'", "'": ',',
})
ANSI_BG_TMPL = "\033[48;2;{r};{g};{b}m  \033[0m"
ANSI_COLORS = [
    ("Black", "000000"), ("Maroon", "800000"), ("Green", "008000"), ("Olive", "808000"),
    ("Navy", "000080"), ("Purple", "800080"), ("Teal", "008080"), ("Silver", "c0c0c0"),
    ("Gray", "808080"), ("Red", "ff0000"), ("Lime", "00ff00"), ("Yellow", "ffff00"),
    ("Blue", "0000ff"), ("Fuchsia", "ff00ff"), ("Aqua", "00ffff"), ("White", "ffffff"),
    ("Orange", "ffa500"), ("Gold", "ffd700"), ("Cyan", "00bfff"), ("Coral", "ff7f50"),
    ("Crimson", "dc143c"), ("HotPink", "ff69b4"), ("Indigo", "4b0082"), ("Ivory", "fffff0"),
    ("Lavender", "e6e6fa"), ("Magenta", "ff00ff"), ("Maroon2", "800000"), ("Olive2", "808000"),
    ("Orchid", "da70d6"), ("Peru", "cd853f"), ("Plum", "dda0dd"), ("Salmon", "fa8072"),
]
PORTS = [("20", "FTP data"), ("21", "FTP control"), ("22", "SSH"), ("23", "Telnet"),
         ("25", "SMTP"), ("53", "DNS"), ("67/68", "DHCP"), ("80", "HTTP"), ("110", "POP3"),
         ("123", "NTP"), ("143", "IMAP"), ("194", "IRC"), ("443", "HTTPS"), ("465", "SMTPS"),
         ("587", "SMTP (submission)"), ("993", "IMAPS"), ("995", "POP3S"), ("1080", "SOCKS proxy"),
         ("1433", "MSSQL"), ("1521", "Oracle DB"), ("1723", "PPTP VPN"), ("1883", "MQTT"),
         ("2049", "NFS"), ("2375", "Docker API"), ("3306", "MySQL"), ("3389", "RDP"),
         ("5432", "PostgreSQL"), ("5900", "VNC"), ("6379", "Redis"), ("8080", "HTTP alt"),
         ("8443", "HTTPS alt"), ("8888", "HTTP alt"), ("9000", "App server"), ("9200", "Elasticsearch"),
         ("27017", "MongoDB")]


def _input_lines(kevbin, prompt="Paste text (empty line to finish):"):
    kevbin.box.info(prompt)
    out = []
    while True:
        line = kevbin.box.input("> ")
        if not line:
            break
        out.append(line)
    return out


def _rand_word(kevbin):
    w = kevbin.box.input("Generate X entries [10]: ") or "10"
    try:
        return max(1, min(500, int(w)))
    except ValueError:
        return 10


def _rgb(hexstr):
    h = hexstr.lstrip('#')
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _hex_to_rgb(hexstr):
    try:
        return _rgb(hexstr)
    except Exception:
        return None


def _fmt_bytes(n):
    n = float(n or 0)
    for unit in ('B', 'KB', 'MB', 'GB', 'TB', 'PB'):
        if n < 1024 or unit == 'PB':
            return f"{n:,.0f} {unit}"
        n /= 1024
    return '?'


def snowflake_decode(kevbin):
    """Decode a Discord ID into its creation timestamp."""
    kevbin.clear()
    kevbin.box.title("SNOWFLAKE DECODE")
    raw = kevbin.box.input("Discord ID: ").strip()
    try:
        sid = int(raw)
    except ValueError:
        kevbin.box.error(f"'{raw}' is not a number.")
        kevbin.pause()
        return
    if sid < (1 << 22):
        kevbin.box.error("ID too small to be a snowflake.")
        kevbin.pause()
        return
    ms = (sid >> 22) + 1420070400000
    try:
        when = datetime.datetime.utcfromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        when = f"{ms} ms epoch"
    rows = [
        ("Snowflake", str(sid)),
        ("Created (epoch ms)", str(ms)),
        ("Created", when),
        ("Worker", str((sid >> 17) & 0x1F)),
        ("Process", str((sid >> 12) & 0x1F)),
        ("Increment", str(sid & 0xFFF)),
        ("Age", str(datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(ms / 1000))),
    ]
    kevbin.box.table(rows, title="Parsed ID")
    kevbin.pause()


def embed_builder(kevbin):
    """Build a Discord embed JSON payload."""
    kevbin.clear()
    kevbin.box.title("EMBED JSON BUILDER")
    embed = {}
    title = kevbin.box.input("Title (empty skip): ")
    if title:
        embed["title"] = title
    desc = kevbin.box.input("Description (empty skip): ")
    if desc:
        embed["description"] = desc
    col = kevbin.box.input("Color (#hex / empty skip): ")
    if col:
        rgb = _hex_to_rgb(col)
        if rgb:
            embed["color"] = (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
    author = kevbin.box.input("Author (empty skip): ")
    if author:
        embed["author"] = {"name": author}
    footer = kevbin.box.input("Footer (empty skip): ")
    if footer:
        embed["footer"] = {"text": footer}
    fields = []
    kevbin.box.info("Fields (name:value each, empty line to stop):")
    while True:
        f = kevbin.box.input("field> ")
        if not f:
            break
        if ':' in f:
            n, v = f.split(':', 1)
            fields.append({"name": n.strip(), "value": v.strip(), "inline": False})
    if fields:
        embed["fields"] = fields
    payload = {"content": None, "embeds": [embed]}
    kevbin.box.code(json.dumps(payload, indent=2))
    kevbin.pause()


def email_format_gen(kevbin):
    """Generate probable business email formats."""
    kevbin.clear()
    kevbin.box.title("EMAIL FORMAT GENERATOR")
    first = kevbin.box.input("First name: ").strip()
    last = kevbin.box.input("Last name: ").strip()
    domain = kevbin.box.input("Domain (e.g. company.com): ").strip().lower()
    if not (first and last and domain):
        kevbin.box.error("First, last and domain are required.")
        kevbin.pause()
        return
    f, l = first.lower(), last.lower()
    fi, li = f[0], l[0]
    formats = [
        f"{fi}{l}", f"{f}{li}", f"{fi}{li}", f"{f}.{l}", f"{f}_{l}",
        f"{f}-{l}", f"{f}{l}", f"{l}{fi}", f"{f}.{li}", f"{fi}",
        f"{l}.{f}", f"{f}{l}{random.randint(10, 99)}",
    ]
    rows = [("Email", "Format")] + [ (f"{x}@{domain}", f"{f} {l}") for x in formats]
    kevbin.box.table(rows)
    kevbin.pause()


def url_extractor(kevbin):
    """Extract every URL from pasted text."""
    kevbin.clear()
    kevbin.box.title("URL EXTRACTOR")
    lines = _input_lines(kevbin)
    if not lines:
        return
    found = []
    pat = re.compile(r'(?:https?://|www\.)[^\s\'"<>\)\}\]]+')
    for ln in lines:
        found.extend(m.group(0).rstrip('.,;!?') for m in pat.finditer(ln))
    seen, uniq = set(), []
    for u in found:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    if not uniq:
        kevbin.box.error("No URLs found.")
        kevbin.pause()
        return
    rows = [("N", "URL")] + [(str(i + 1), u) for i, u in enumerate(uniq)]
    kevbin.box.table(rows)
    kevbin.box.info(f"{len(uniq)} unique URL(s).")
    kevbin.pause()


def osint_report(kevbin):
    """Assemble an OSINT report card from whatever the user has."""
    kevbin.clear()
    kevbin.box.title("OSINT REPORT BUILDER")
    parts = []
    fields = [("Username", "username"), ("Email", "email"), ("IP", "ip address"),
              ("Domain", "domain"), ("Phone", "phone"), ("Full name", "full name")]
    for label, prompt in fields:
        v = kevbin.box.input(f"{label} (empty skip): ").strip()
        if v:
            parts.append((label, v))
    lines = [l for _, l in _input_lines(kevbin, "Notes (empty to finish): ")]
    if not parts and not lines:
        kevbin.box.error("Nothing entered.")
        kevbin.pause()
        return
    rows = parts + [("Notes", ' | '.join(lines))] if lines else parts
    kevbin.box.title("OSINT REPORT CARD")
    for k, v in rows:
        kevbin.cprint(kevbin.t.txt, f"  {k:<12}{v}")
    kevbin.box.info(f"Generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}.")
    kevbin.pause()


def otp_gen(kevbin):
    """Generate authenticator-style codes."""
    kevbin.clear()
    kevbin.box.title("OTP CODE GENERATOR")
    n = _rand_word(kevbin)
    size = kevbin.box.input("Digits 6/8 [6]: ").strip() or "6"
    size = 8 if size == "8" else 6
    rows = [("index", "code")]
    codes = []
    for _ in range(n):
        codes.append(''.join(random.choice(_digits) for _ in range(size)))
    out = [f"{i:>3}] {c}" for i, c in enumerate(codes, 1)]
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def hexdump_text(kevbin):
    """Pretty hex dump of pasted text."""
    kevbin.clear()
    kevbin.box.title("HEX DUMP (TEXT)")
    data = " ".join(_input_lines(kevbin)).encode('utf-8')
    if not data:
        return
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hx = ' '.join(f"{b:02x}" for b in chunk)
        asc = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"{i:08x}  {hx:<47}  {asc}")
    kevbin.box.code("\n".join(lines))
    kevbin.box.info(f"{len(data)} bytes")
    kevbin.pause()


def password_strength(kevbin):
    """Local entropy check for a password."""
    kevbin.clear()
    kevbin.box.title("PASSWORD STRENGTH")
    pw = kevbin.box.input("Password: ")
    if not pw:
        return
    sets = [bool(re.search(r'[a-z]', pw)), bool(re.search(r'[A-Z]', pw)),
            bool(re.search(r'\d', pw)), bool(re.search(r'[^a-zA-Z0-9]', pw))]
    pool = 0
    if sets[0]:
        pool += 26
    if sets[1]:
        pool += 26
    if sets[2]:
        pool += 10
    if sets[3]:
        pool += 33
    entropy = len(pw) * (pool and _log2(pool) or 0)
    score = min(100, int(entropy / 1.4) if entropy else 0)
    bar = int(score / 5)
    verdict = ("Very weak", "Weak", "Fair", "Good", "Strong", "Excellent")[min(5, score // 20)]
    label = ''.join('█' * b + '░' * (20 - b) for b in [bar]) if bar else '░' * 20
    rows = [
        ("Length", f"{len(pw)} chars"),
        ("Lower/Upper/Digit/Symbol", '/'.join('Y' if s else 'N' for s in sets)),
        ("Char pool", str(pool)),
        ("Entropy", f"{entropy:.1f} bits"),
        ("Score", f"{score}/100  {label}"),
        ("Verdict", verdict),
        ("Hint", "Never reuse passwords; use a passphrase."),
    ]
    kevbin.box.table(rows)
    kevbin.pause()


def _log2(n):
    import math
    return math.log(max(n, 2), 2)


def curl_builder(kevbin):
    """Generate a curl command from parts."""
    kevbin.clear()
    kevbin.box.title("CURL BUILDER")
    method = (kevbin.box.input("Method GET/POST/PUT/DELETE [GET]: ") or "GET").upper()
    url = kevbin.box.input("URL: ").strip()
    if not url:
        return
    cmd = f"curl -X {method} '{url}'"
    kevbin.box.info("Headers as key: value (empty to stop):")
    while True:
        h = kevbin.box.input("h> ")
        if not h:
            break
        if ':' in h:
            k, v = h.split(':', 1)
            cmd += f" -H '{k.strip()}: {v.strip()}'"
    body = kevbin.box.input("Body (JSON/text, empty skip): ").strip()
    if body:
        cmd += f" -d '{body}'"
    cookie = kevbin.box.input("Cookie header (empty skip): ").strip()
    if cookie:
        cmd += f" -b '{cookie}'"
    follow = (kevbin.box.input("Follow redirects? y/N: ") or "n").lower()
    if follow.startswith('y'):
        cmd += " -L"
    kevbin.box.title("RESULT")
    kevbin.box.code(cmd)
    kevbin.pause()


def url_parser(kevbin):
    """Break a URL into its parts."""
    kevbin.clear()
    kevbin.box.title("URL PARSER")
    url = kevbin.box.input("URL: ").strip()
    if not url:
        return
    p = urllib.parse.urlparse(url if '://' in url else '//' + url)
    rows = [
        ("Scheme", p.scheme or "-"),
        ("Netloc", p.netloc or "-"),
        ("Host", p.hostname or "-"),
        ("Port", str(p.port) if p.port else "-"),
        ("Path", p.path or "/"),
        ("Query", p.query or "-"),
        ("Fragment", p.fragment or "-"),
    ]
    kevbin.box.table(rows, title="URL breakdown")
    if p.query:
        ks = []
        for k, v in urllib.parse.parse_qsl(p.query):
            ks.append((k, v))
        kevbin.box.table(ks + [], title="Query params")
    kevbin.pause()


def useragent_gen(kevbin):
    """Random realistic user agents."""
    import random as r
    kevbin.clear()
    kevbin.box.title("USER-AGENT GENERATOR")
    n = _rand_word(kevbin)
    uas = []
    for _ in range(n):
        uas.append(_random_ua(r))
    kevbin.box.code("\n".join(uas))
    kevbin.pause()


def _random_ua(r=None):
    r = r or random
    ver = lambda: '.'.join(str(r.randint(0, 99)) for _ in range(4))
    uas = [
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{ver()} (KHTML, like Gecko) Chrome/{ver()} Safari/537.36",
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{100 + r.randint(0, 30)}.0) Gecko/20100101 Firefox/{100 + r.randint(0, 30)}.0",
        f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_{r.randint(0, 7)}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{r.randint(14, 18)}.0 Safari/605.1.15",
        f"Mozilla/5.0 (iPhone; CPU iPhone OS {r.randint(14, 18)}_{r.randint(0, 6)} like Mac OS X) AppleWebKit/{ver()} (KHTML, like Gecko) Version/{r.randint(14, 18)}.0 Mobile Safari/604.1",
        f"Mozilla/5.0 (Linux; Android {r.randint(10, 14)}; Pixel {r.randint(4, 8)}) AppleWebKit/{ver()} (KHTML, like Gecko) Chrome/{ver()} Mobile Safari/537.36",
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{ver()} (KHTML, like Gecko) Chrome/{ver()} Safari/537.36 Edg/{ver()}",
    ]
    return r.choice(uas)


def text_binary(kevbin):
    """Text to/from binary."""
    kevbin.clear()
    kevbin.box.title("TEXT <-> BINARY")
    mode = (kevbin.box.input("Encode (text->binary) or Decode? E/D: ") or "e").lower()
    data = kevbin.box.input("Data: ")
    if not data:
        return
    if mode.startswith('e'):
        out = ' '.join(f"{ord(c):08b}" for c in data)
    else:
        try:
            out = ''.join(chr(int(b, 2)) for b in data.split())
        except ValueError:
            kevbin.box.error("Invalid binary string.")
            kevbin.pause()
            return
    kevbin.box.code(out)
    kevbin.pause()


def morse_code(kevbin):
    """Encode/decode Morse."""
    kevbin.clear()
    kevbin.box.title("MORSE CODE")
    mode = (kevbin.box.input("Encode or Decode? E/D: ") or "e").lower()
    data = kevbin.box.input("Data: ").strip()
    if not data:
        return
    if mode.startswith('e'):
        out = ' / '.join(' '.join(MORSE.get(ch.upper(), ch) for ch in word) for word in data.split())
    else:
        out = ''.join(MORSE_REV.get(tok, tok) for tok in data.split())
    kevbin.box.code(out)
    kevbin.pause()


def leet_speak(kevbin):
    """Make leetspeak variants."""
    kevbin.clear()
    kevbin.box.title("LEET SPEAK")
    data = kevbin.box.input("Text: ").strip()
    if not data:
        return
    maps = [
        str.maketrans({"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"}),
        str.maketrans({"a": "@", "e": "3", "l": "1", "o": "0", "s": "$", "t": "7"}),
        str.maketrans({"a": "4", "e": "€", "i": "!", "o": "0", "s": "z", "v": "\\/"}),
    ]
    out = [data.translate(m) for m in maps]
    out.append(''.join(r.choice([c, c.upper()]) for c in data))
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def reverse_upsidedown(kevbin):
    """Normal reverse + upside-down text."""
    kevbin.clear()
    kevbin.box.title("REVERSE / UPSIDE-DOWN")
    data = kevbin.box.input("Text: ")
    if not data:
        return
    kevbin.box.code("REVERSED:\n" + data[::-1] + "\n\nUPSIDE-DOWN:\n" + data.translate(UPSIDE_DOWN))
    kevbin.pause()


def scramble_words(kevbin):
    """Scramble words keeping first/last letters."""
    kevbin.clear()
    kevbin.box.title("WORD SCRAMBLER")
    data = kevbin.box.input("Text: ").strip()
    if not data:
        return
    variants = []
    for _ in range(5):
        out = []
        for w in re.findall(r"\S+", data):
            if len(w) > 3:
                mid = list(w[1:-1])
                random.shuffle(mid)
                w = w[0] + ''.join(mid) + w[-1]
            out.append(w)
        variants.append(' '.join(out))
    kevbin.box.code("\n".join(variants))
    kevbin.pause()


def palindrome_check(kevbin):
    """Find palindromic words / check a string."""
    kevbin.clear()
    kevbin.box.title("PALINDROME CHECK")
    data = kevbin.box.input("Text: ").strip()
    if not data:
        return
    clean = re.sub(r'[^a-z0-9]', '', data.lower())
    rows = [("Result", "Palindromic" if clean == clean[::-1] and clean else "Not a palindrome")]
    words = re.findall(r"[a-z]{3,}", data.lower())
    pals = sorted(set(w for w in words if w == w[::-1]), key=len, reverse=True)
    if pals:
        rows.append(("Longest palindrome", pals[0]))
        rows.append(("Palindromic words", ', '.join(pals[:10]) + ('...' if len(pals) > 10 else '')))
    kevbin.box.table(rows)
    kevbin.pause()


def random_poem(kevbin):
    """Generate a random haiku."""
    kevbin.clear()
    kevbin.box.title("RANDOM HAIKU")
    syl1 = ["rain", "moon", "wind", "sea", "snow", "leaf", "star", "sun", "dawn", "mist", "frost", "bird"]
    syl2 = ["silence", "the ocean", "an old door", "cold morning", "dark water", "the first light", "a red fox"]
    syl3 = ["snow falls by the gate", "the river runs quietly", "between two great stones", "a single cloud passes"]
    tb = ["morning light", "autumn wind", "quiet rain", "winter fog", "summer heat", "empty room", "night noises", "distant bell"]
    ha = [
        f"{random.choice(syl1)} {random.choice(tb)} —",
        f"{random.choice(syl3)}, {random.choice(tb)}.",
        f"{random.choice(syl1)}s in the {random.choice(['hills', 'yard', 'valley', 'town'])}.",
    ]
    kevbin.box.code("\n".join(ha))
    kevbin.pause()


def random_color(kevbin):
    """Random color + swatch."""
    kevbin.clear()
    kevbin.box.title("RANDOM COLOR")
    hexc = ''.join(random.choice("0123456789abcdef") for _ in range(6))
    r_, g_, b_ = _rgb(hexc)
    hsl = _rgb_to_hsl(r_, g_, b_)
    sw = ANSI_BG_TMPL.format(r=r_, g=g_, b=b_)
    rows = [
        ("Hex", f"#{hexc.upper()}"),
        ("RGB", f"rgb({r_}, {g_}, {b_})"),
        ("HSL", f"hsl({hsl[0]:.0f}, {hsl[1]:.0f}%, {hsl[2]:.0f}%)"),
        ("Swatch", sw + "  " + f"#{hexc.upper()}"),
    ]
    kevbin.box.table(rows)
    kevbin.pause()


def _rgb_to_hsl(r, g, b):
    import colorsys
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return h * 360, s * 100, l * 100


def ansi_tester(kevbin):
    """Display the xterm-256 color grid."""
    kevbin.clear()
    kevbin.box.title("ANSI 256-COLOR TESTER")
    out = []
    for base in range(0, 256, 32):
        row = ''.join(f"\033[48;5;{i}m  \033[0m" for i in range(base, min(base + 32, 256)))
        out.append(row)
        out.append(' '.join(f"\033[38;5;{i}m{i}\033[0m" for i in range(base, min(base + 32, 256))))
    kevbin.box.code("\n".join(out))
    kevbin.box.info("Foreground codes shown under each row of background swatches.")
    kevbin.pause()


def palette_tints(kevbin):
    """Generate tints/shades from a hex color."""
    kevbin.clear()
    kevbin.box.title("PALETTE TINTS / SHADES")
    hexc = kevbin.box.input("Base hex (#rrggbb): ").strip().lstrip('#')
    if not re.match(r'^[0-9a-fA-F]{6}$', hexc):
        kevbin.box.error("Need a 6-digit hex color.")
        kevbin.pause()
        return
    r_, g_, b_ = _rgb(hexc)
    out = ["-- TINTS (mix with white) --"]
    for i in range(0, 11):
        f = i / 10
        rr = int(r_ + (255 - r_) * f)
        gg = int(g_ + (255 - g_) * f)
        bb = int(b_ + (255 - b_) * f)
        h = f"{rr:02x}{gg:02x}{bb:02x}"
        out.append(f"{ANSI_BG_TMPL.format(r=rr, g=gg, b=bb)}  #{h}")
    out.append("-- SHADES (mix with black) --")
    for i in range(0, 11):
        f = i / 10
        rr = int(r_ * (1 - f))
        gg = int(g_ * (1 - f))
        bb = int(b_ * (1 - f))
        h = f"{rr:02x}{gg:02x}{bb:02x}"
        out.append(f"{ANSI_BG_TMPL.format(r=rr, g=gg, b=bb)}  #{h}")
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def named_colors(kevbin):
    """Common named colors with swatches."""
    kevbin.clear()
    kevbin.box.title("NAMED COLORS")
    lines = []
    for name, hexc in ANSI_COLORS:
        r_, g_, b_ = _rgb(hexc)
        lines.append(f"{ANSI_BG_TMPL.format(r=r_, g=g_, b=b_)}  {name:<12}#{hexc.upper()}")
    kevbin.box.code("\n".join(lines))
    kevbin.pause()


def unit_converter(kevbin):
    """Length / weight / temperature / data converter."""
    length = {"m": 1, "km": 1000, "cm": 0.01, "mm": 0.001, "mi": 1609.344,
              "yd": 0.9144, "ft": 0.3048, "in": 0.0254, "nm": 1852}
    weight = {"kg": 1, "g": 0.001, "mg": 1e-6, "lb": 0.45359237, "oz": 0.0283495231, "st": 6.35029318, "t": 1000}
    data = {"b": 1, "kb": 1024, "mb": 1024 ** 2, "gb": 1024 ** 3, "tb": 1024 ** 4, "kib": 1024, "mib": 1024 ** 2}
    kevbin.clear()
    kevbin.box.title("UNIT CONVERTER")
    kind = (kevbin.box.input("Category (length/weight/temp/data): ") or "length").lower()
    if kind.startswith("temp") or kind.startswith("t"):
        c = kevbin.box.input("Value (°C): ")
        try:
            c = float(c)
        except ValueError:
            kevbin.box.error("Need a number.")
            kevbin.pause()
            return
        rows = [("Fahrenheit", f"{c * 9 / 5 + 32:.2f}°F"), ("Kelvin", f"{c + 273.15:.2f} K"),
                ("Rankine", f"{(c + 273.15) * 9 / 5:.2f} °R")]
        kevbin.box.table(rows)
        kevbin.pause()
        return
    table = {"length": ("meters", length, "m"), "weight": ("kilograms", weight, "kg"),
             "data": ("bytes", data, "b")}
    if kind not in table:
        kevbin.box.error("Unknown category.")
        kevbin.pause()
        return
    label, units, base_u = table[kind]
    v = kevbin.box.input(f"Value (in {base_u}): ")
    from_u = (kevbin.box.input(f"From unit [{base_u}]: ") or base_u).strip().lower()
    to_u = kevbin.box.input("To unit (empty = all): ").strip().lower()
    try:
        val = float(v)
    except (TypeError, ValueError):
        kevbin.box.error("Need a number.")
        kevbin.pause()
        return
    if from_u not in units or (to_u and to_u not in units):
        kevbin.box.error(f"Unknown unit. Available: {', '.join(sorted(units))}")
        kevbin.pause()
        return
    base = val * units[from_u]
    if to_u:
        rows = [(to_u, f"{base / units[to_u]:,.6g}")]
    else:
        rows = [(u, f"{base / f:,.6g}") for u, f in sorted(units.items(), key=lambda x: x[0])]
    kevbin.box.table(rows, title=f"{label}")
    kevbin.pause()


def byte_converter(kevbin):
    """Convert a byte amount to every unit."""
    kevbin.clear()
    kevbin.box.title("BYTE CONVERTER")
    raw = kevbin.box.input("Bytes, or like '5.5 GB': ").strip()
    m = re.match(r"^([\d.]+)\s*([a-z]+)?$", raw.lower())
    if not m:
        kevbin.box.error("Invalid input.")
        kevbin.pause()
        return
    num = float(m.group(1))
    unit = m.group(2) or "b"
    mult = {"b": 1, "kb": 1024, "mb": 1024 ** 2, "gb": 1024 ** 3, "tb": 1024 ** 4,
            "pb": 1024 ** 5, "kib": 1024, "mib": 1024 ** 2, "gib": 1024 ** 3, "tib": 1024 ** 4}
    if unit not in mult:
        kevbin.box.error("Unknown unit.")
        kevbin.pause()
        return
    total = num * mult[unit]
    rows = [(u, f"{total / c:,.2f}") for u, c in mult.items()]
    rows.insert(0, ("Human (IEC)", _fmt_bytes(total)))
    kevbin.box.table(rows, title=f"{raw} = {int(total)} bytes")
    kevbin.pause()


def interest_calc(kevbin):
    """Simple / compound interest calculator."""
    kevbin.clear()
    kevbin.box.title("INTEREST CALCULATOR")
    try:
        p = float(kevbin.box.input("Principal: "))
        r = float(kevbin.box.input("Rate %/yr: "))
        t = float(kevbin.box.input("Years: "))
    except (TypeError, ValueError):
        kevbin.box.error("All values must be numbers.")
        kevbin.pause()
        return
    simple = p * (1 + (r / 100) * t)
    compound = p * (1 + r / 100) ** t
    rows = [("Simple interest", f"{simple:,.2f}"),
            ("Compound (yearly)", f"{compound:,.2f}"),
            ("Simple earned", f"{simple - p:,.2f}"),
            ("Compound earned", f"{compound - p:,.2f}")]
    kevbin.box.table(rows)
    kevbin.pause()


def bmi_calc(kevbin):
    """BMI + body fat category."""
    kevbin.clear()
    kevbin.box.title("BMI CALCULATOR")
    try:
        kg = float(kevbin.box.input("Weight (kg): "))
        cm = float(kevbin.box.input("Height (cm): "))
    except (TypeError, ValueError):
        kevbin.box.error("Need numbers.")
        kevbin.pause()
        return
    m = cm / 100
    bmi = kg / (m * m)
    if bmi < 18.5:
        cat = "Underweight"
    elif bmi < 25:
        cat = "Normal"
    elif bmi < 30:
        cat = "Overweight"
    else:
        cat = "Obese"
    rows = [("BMI", f"{bmi:.1f}"), ("Category", cat),
            ("Healthy range", f"{(18.5 * m * m):.1f} – {(24.9 * m * m):.1f} kg")]
    kevbin.box.table(rows)
    kevbin.pause()


def prime_tools(kevbin):
    """Prime checker, factorizer."""
    kevbin.clear()
    kevbin.box.title("PRIME & FACTORS")
    raw = kevbin.box.input("Number: ").strip()
    if not raw.isdigit():
        kevbin.box.error("Need a whole number.")
        kevbin.pause()
        return
    n = int(raw)
    isp = _is_prime(n)
    factors = _factorize(n)
    nxt = n + 1
    while not _is_prime(nxt) and nxt < n + 100000:
        nxt += 1
    rows = [("Is prime", "Yes" if isp else "No"),
            ("Prime factors", ' × '.join(factors) if factors else "-"),
            ("Next prime", str(nxt) if nxt < n + 100000 else "?"),
            ("Digit sum", str(sum(int(d) for d in raw))),
            ("Binary", bin(n)[2:]), ("Hex", hex(n)[2:].upper())]
    kevbin.box.table(rows)
    kevbin.pause()


def _is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def _factorize(n):
    n = abs(n)
    out, d = [], 2
    while d * d <= n:
        while n % d == 0:
            out.append(str(d))
            n //= d
        d += 1
    if n > 1:
        out.append(str(n))
    return out


def date_diff(kevbin):
    """Days between two dates."""
    kevbin.clear()
    kevbin.box.title("DATE DIFF")
    try:
        d1 = datetime.date.fromisoformat(kevbin.box.input("First date (YYYY-MM-DD): ").strip())
        d2 = datetime.date.fromisoformat(kevbin.box.input("Second date (YYYY-MM-DD): ").strip())
    except ValueError:
        kevbin.box.error("Use YYYY-MM-DD format.")
        kevbin.pause()
        return
    days = abs((d2 - d1).days)
    rows = [("Days", f"{days:,}"), ("Weeks", f"{days / 7:,.1f}"),
            ("Hours", f"{days * 24:,}"), ("Minutes", f"{days * 1440:,}"),
            ("Including end date", f"{days + 1:,}")]
    kevbin.box.table(rows)
    kevbin.pause()


def roblox_link_builder(kevbin):
    """Build Roblox profile / asset / place links."""
    kevbin.clear()
    kevbin.box.title("ROBLOX LINK BUILDER")
    kind = (kevbin.box.input("Type (user/asset/place/group): ") or "user").lower()
    ident = kevbin.box.input("ID (or username for user): ").strip()
    if not ident:
        return
    base = "https://www.roblox.com"
    links = {"user": f"{base}/users/{ident}",
             "asset": f"{base}/catalog/{ident}",
             "place": f"{base}/games/{ident}",
             "group": f"{base}/groups/{ident}"}.get(kind)
    rows = [("Type", kind.title()), ("ID", ident), ("Link", links or "unknown type")]
    kevbin.box.table(rows)
    if kind in ("asset",):
        rows2 = [("Marketplace", f"{base}/catalog/{ident}"),
                 ("Thumbnail", f"https://thumbnails.roblox.com/v1/assets?assetIds={ident}&size=420x420&format=Png")]
        kevbin.box.table(rows2 + [], title="More")
    kevbin.pause()


def username_style_gen(kevbin):
    """Stylized username variants."""
    kevbin.clear()
    kevbin.box.title("USERNAME STYLE GENERATOR")
    name = kevbin.box.input("Base name: ").strip()
    if not name:
        return
    low = name.lower()
    num = random.randint(10, 99)
    nums = {
        "raw": low,
        "capitalized": name.title(),
        "xX_wrapper": f"xX_{name}Xx",
        "leetspeak": low.translate(str.maketrans({"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"})),
        "underscored": low.replace(' ', '_'),
        "dotted": ('_'.join(name.split())),
        "with_number": f"{low}{num}",
        "all_caps": name.upper(),
        "reversed": low[::-1],
        "lord_of": f"Lord{name.title()}",
        "sub_underscore": f"_{low}_",
    }
    kevbin.box.code("\n".join(f"{k:<14}{v}" for k, v in nums.items()))
    kevbin.pause()


def gamertag_gen(kevbin):
    """Random gamertags."""
    kevbin.clear()
    kevbin.box.title("GAMERTAG GENERATOR")
    adj = ["savage", "ninja", "epic", "toxic", "fast", "shadow", "cursed", "golden", "silent", "rabid",
           "legendary", "noob", "pro", "frost", "blaze", "dark", "stormy", "witty", "lucky", "feral"]
    noun = ["wolf", "fox", "raven", "phoenix", "knight", "titan", "ghost", "reaper", "viper", "jaguar",
            "panda", "shark", "eagle", "dragon", "hunter", "wizard", "sniper", "bandit", "rogue", "ninja"]
    n = _rand_word(kevbin)
    tags = []
    for _ in range(n):
        style = random.randint(0, 4)
        a, no = random.choice(adj), random.choice(noun)
        if style == 0:
            tags.append(f"{a}_{no}{random.randint(0, 99)}")
        elif style == 1:
            tags.append(f"{a} {no}")
        elif style == 2:
            tags.append(f"x{no}{a}x")
        elif style == 3:
            tags.append(f"{a}{no}{random.randint(1, 9)}")
        else:
            tags.append(f"Mr{no}{random.randint(0, 99)}")
    kevbin.box.code("\n".join(tags))
    kevbin.pause()


def fake_ip(kevbin):
    """Generate random IP addresses."""
    kevbin.clear()
    kevbin.box.title("FAKE IP GENERATOR")
    n = _rand_word(kevbin)
    out = []
    for _ in range(n):
        out.append(f"{random.randint(1, 223)}.{random.randint(0, 255)}"
                   f".{random.randint(0, 255)}.{random.randint(1, 254)}")
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def fake_mac(kevbin):
    """Generate random MAC addresses."""
    kevbin.clear()
    kevbin.box.title("FAKE MAC GENERATOR")
    n = _rand_word(kevbin)
    sep = (kevbin.box.input("Separator ':' '-' 'none' [':']: ") or ":").strip()
    sep = '' if sep == 'none' else sep
    out = []
    for _ in range(n):
        m = sep.join(random.choice("0123456789abcdef") for _ in ['00', '11', '22', '33', '44', '55'])
        out.append(m)
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def fake_phone(kevbin):
    """Generate random phone numbers."""
    kevbin.clear()
    kevbin.box.title("FAKE PHONE GENERATOR")
    n = _rand_word(kevbin)
    out = []
    for _ in range(n):
        head = random.choice(['+1-202', '+44-20', '+49-30', '+33-1', '+61-2', '+1-310'])
        out.append(f"{head}-{random.randint(100, 999)}-{random.randint(1000, 9999)}")
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def fake_address(kevbin):
    """Generate a fake address."""
    kevbin.clear()
    kevbin.box.title("FAKE ADDRESS GENERATOR")
    streets = ["Maple", "Oak", "Cedar", "Elm", "Birch", "Pine", "Main", "Church", "Hill", "Park"]
    cities = ["Springfield", "Riverside", "Franklin", "Clinton", "Georgetown", "Salem", "Bristol", "Fairview"]
    out = []
    for _ in range(_rand_word(kevbin)):
        out.append(f"{random.randint(4, 9999)} {random.choice(streets)} {random.choice(['St', 'Rd', 'Ave', 'Ln', 'Dr'])}")
        out.append(f"{random.choice(cities)}, {' '.join(random.choices(string.ascii_uppercase, k=2))} {random.randint(10000, 99999)}")
        out.append('')
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def fake_company(kevbin):
    """Generate fake company names."""
    kevbin.clear()
    kevbin.box.title("FAKE COMPANY GENERATOR")
    p1 = ["Cyber", "Global", "Quantum", "Nova", "Vertex", "Apex", "Delta", "Omega", "Blue", "Iron",
          "Star", "Cloud", "Hyper", "Neo", "Vault", "Prime", "Orbit", "Logic", "Matrix", "Solar"]
    p2 = ["Works", "Systems", "Labs", "Dynamics", "Industries", "Technologies", "Solutions", "Networks",
          "Ventures", "Analytics", "Robotics", "Security", "Data", "Cloud", "Digital", "Wave"]
    n = _rand_word(kevbin)
    out = []
    for _ in range(n):
        kind = random.randint(0, 2)
        if kind == 0:
            out.append(f"{random.choice(p1)}{random.choice(p2)}")
        elif kind == 1:
            out.append(f"{random.choice(p1)} & {random.choice(p1)}{random.choice(p2)}")
        else:
            out.append(f"{random.choice(p1)} {random.choice(p2)} LLC")
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def hacker_alias(kevbin):
    """Generate hacker handles."""
    kevbin.clear()
    kevbin.box.title("HACKER ALIAS GENERATOR")
    pre = ["0x", "404", "root", "null", "ghost", "w1re", "daemon", "phantom", "binary", "void", "k1ng"]
    suf = ["hack", "byte", "bit", "sk1llz", "ops", "mvp", "1337", "agent", "pro", "x", "devil"]
    n = _rand_word(kevbin)
    out = []
    for _ in range(n):
        out.append(f"{random.choice(pre)}{random.choice(suf)}{random.randint(0, 99)}")
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def buzzword_gen(kevbin):
    """Generate corporate buzzword sentences."""
    kevbin.clear()
    kevbin.box.title("BUZZWORD GENERATOR")
    a = ["synergistic", "holistic", "disruptive", "scalable", "agile", "paradigm-shifting", "next-gen",
         "mission-critical", "value-added", "best-of-breed", "thought-leadership", "bleeding-edge"]
    b = ["solutions", "synergies", "paradigms", "platforms", "ecosystems", "workflows", "frameworks",
         "leverage points", "core competencies", "deliverables", "use cases", "vertical markets"]
    c = ["drive innovation", "unlock value", "streamline ops", "maximize ROI", "accelerate growth",
         "future-proof", "empower teams", "scale globally", "optimize chaos", "own the roadmap"]
    n = _rand_word(kevbin)
    out = []
    for _ in range(n):
        out.append(f"We leverage {random.choice(a)} {random.choice(b)} to {random.choice(c)}.")
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def emoji_flood(kevbin):
    """Generate emoji spam strings."""
    kevbin.clear()
    kevbin.box.title("EMOJI FLOOD")
    emos = ["😀", "🔥", "💀", "👑", "🥶", "🤖", "💀", "⚡", "🎉", "😈", "😂", "🤔", "✅", "❌", "💯", "👀"]
    n = _rand_word(kevbin)
    out = [''.join(random.choice(emos) for _ in range(n)) for _ in range(5)]
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def port_lookup(kevbin):
    """Common TCP/UDP port reference."""
    kevbin.clear()
    kevbin.box.title("PORT LOOKUP")
    q = (kevbin.box.input("Lookup a port (empty = show all): ").strip())
    if q:
        rows = [("Port", "Service")] + [p for p in PORTS if p[0] == q]
        if len(rows) == 1:
            rows.append((q, "unknown service"))
    else:
        rows = [("Port", "Service")] + list(PORTS)
    kevbin.box.table(rows, title="Common ports")
    kevbin.pause()


def random_domain(kevbin):
    """Generate random domain names."""
    kevbin.clear()
    kevbin.box.title("RANDOM DOMAIN GENERATOR")
    p1 = ["web", "net", "my", "best", "quick", "mega", "ultra", "bright", "tiny", "fast", "big", "fresh"]
    p2 = ["pixel", "loud", "link", "view", "code", "byte", "grid", "nest", "leaf", "forge", "wave", "hive"]
    tld = [".com", ".net", ".io", ".org", ".xyz", ".shop", ".dev", ".app"]
    n = _rand_word(kevbin)
    out = []
    for _ in range(n):
        out.append(f"{random.choice(p1)}{random.choice(p2)}{random.choice(tld)}")
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def subnet_list_gen(kevbin):
    """Enumerate a /24-style CIDR range."""
    import ipaddress
    kevbin.clear()
    kevbin.box.title("SUBNET LIST GENERATOR")
    cidr = kevbin.box.input("CIDR (e.g. 192.168.1.0/24): ").strip()
    try:
        net = ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        kevbin.box.error("Invalid CIDR.")
        kevbin.pause()
        return
    total = net.num_addresses
    if total > 512:
        rows = [("Network", str(net.network_address)), ("Broadcast", str(net.broadcast_address)),
                ("Hosts", str(net.num_addresses - 2) if net.version == 4 else str(total)),
                ("First", str(next(net.hosts(), net.network_address))),
                ("Last", str(next(reversed(list(net.hosts())), net.broadcast_address))),
                ("Prefix", str(net.prefixlen))]
        kevbin.box.table(rows)
        kevbin.box.info("Range too large to list every address.")
    else:
        hosts = list(net.hosts()) if net.version == 4 else list(net)
        kevbin.box.code("\n".join(str(h) for h in hosts[:256]))
    kevbin.pause()


def code_minify(kevbin):
    """Strip comments + blank lines from pasted code."""
    kevbin.clear()
    kevbin.box.title("CODE MINIFIER")
    lines = _input_lines(kevbin, "Paste code (empty to finish):")
    if not lines:
        return
    out = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith('#') or s.startswith('//') or s.startswith('/*') or s.startswith('--'):
            continue
        if s.startswith('"') and s.endswith('"'):
            pass
        out.append(ln.rstrip())
    kevbin.box.info(f"{len(lines)} lines -> {len(out)} lines")
    kevbin.box.code("\n".join(out))
    kevbin.pause()


def camel_tools(kevbin):
    """Convert phrases between naming conventions."""
    kevbin.clear()
    kevbin.box.title("CASE CONVERTER")
    s = kevbin.box.input("Phrase (e.g. 'hello world foo'): ").strip()
    if not s:
        return
    words = re.split(r"[^a-zA-Z0-9]+", s)
    words = [w for w in words if w]
    low = [w.lower() for w in words]
    if not low:
        return
    vals = {
        "lowerCamelCase": low[0] + ''.join(w.capitalize() for w in low[1:]),
        "UpperCamel/Pascal": ''.join(w.capitalize() for w in low),
        "snake_case": '_'.join(low),
        "kebab-case": '-'.join(low),
        "dot.case": '.'.join(low),
        "SCREAMING_SNAKE": '_'.join(low).upper(),
        "Title Case": ' '.join(w.capitalize() for w in low),
        "lowpercase": ''.join(low),
    }
    kevbin.box.code("\n".join(f"{k:<20}{v}" for k, v in vals.items()))
    kevbin.pause()


def semver_compare(kevbin):
    """Compare two semantic versions."""
    kevbin.clear()
    kevbin.box.title("SEMVER COMPARE")
    a = kevbin.box.input("Version A (e.g. 1.2.3): ").strip()
    b = kevbin.box.input("Version B: ").strip()
    if not a or not b:
        return
    cmp = _compare_ver(a, b)
    rel = "equal to" if cmp == 0 else ("newer/greater than" if cmp > 0 else "older/less than")
    rows = [("A", a), ("B", b), ("Result", f"{a} is {rel} {b}")]
    kevbin.box.table(rows)
    kevbin.pause()


def _ver_key(v):
    out = []
    for part in re.split(r"[-+.]", v):
        if part.isdigit():
            out.append(int(part))
        else:
            out.append(part)
    return out


def _compare_ver(a, b):
    ka, kb = _ver_key(a), _ver_key(b)
    for x, y in zip(ka, kb):
        if x != y:
            return -1 if x < y else 1
    return 0 if len(ka) == len(kb) else (-1 if len(ka) < len(kb) else 1)


def uuid_v5(kevbin):
    """Deterministic UUIDv5 / name-based hashes."""
    kevbin.clear()
    kevbin.box.title("UUID / NAME HASH")
    name = kevbin.box.input("Name string: ").strip()
    if not name:
        return
    ns = uuid_namespaces()
    rows = [("MD5", hashlib.md5(name.encode()).hexdigest()),
            ("SHA1", hashlib.sha1(name.encode()).hexdigest()),
            ("SHA256", hashlib.sha256(name.encode()).hexdigest()),
            ("SHA512 (short)", hashlib.sha512(name.encode()).hexdigest()[:64]),
            ("UUID5(DNS)", str(hashlib_uuid5(ns["DNS"], name))),
            ("UUID5(URL)", str(hashlib_uuid5(ns["URL"], name))),
            ("Base64", _b64(name))]
    kevbin.box.table(rows, title="Hashes for one input")
    kevbin.pause()


def uuid_namespaces():
    return {"DNS": hashlib_uuid_ns("dns"), "URL": hashlib_uuid_ns("url")}


def hashlib_uuid_ns(kind):
    from uuid import NAMESPACE_DNS, NAMESPACE_URL
    return NAMESPACE_DNS if kind == "dns" else NAMESPACE_URL


def hashlib_uuid5(ns, name):
    import uuid
    return uuid.uuid5(ns, name)


def _b64(s):
    import base64
    try:
        return base64.b64encode(s.encode()).decode()
    except Exception:
        return '?'


def bracket_matcher(kevbin):
    """Check balanced brackets in pasted code."""
    kevbin.clear()
    kevbin.box.title("BRACKET MATCHER")
    lines = _input_lines(kevbin, "Paste code (empty to finish):")
    text = '\n'.join(lines)
    if not text.strip():
        return
    pairs = {')': '(', ']': '[', '}': '{'}
    stack, err = [], None
    for i, ch in enumerate(text):
        if ch in '([{':
            stack.append((ch, i))
        elif ch in pairs:
            if not stack or stack[-1][0] != pairs[ch]:
                err = f"Unmatched '{ch}' at offset {i}"
                break
            stack.pop()
    if err is None and stack:
        ch, i = stack[-1]
        err = f"'{ch}' opened at offset {i} never closed"
    rows = [("Result", err or "All brackets balanced ✓"),
            ("Depth", str(len(stack))) if err is None else ("Open depth", str(len(stack))),
            ("Bytes", str(len(text)))]
    kevbin.box.table(rows)
    kevbin.pause()


def dir_tree(kevbin):
    """Print a directory tree."""
    kevbin.clear()
    kevbin.box.title("DIRECTORY TREE")
    start = kevbin.box.input("Path (empty = current): ").strip() or "."
    if not os.path.isdir(start):
        kevbin.box.error("Not a directory.")
        kevbin.pause()
        return
    limit = 200
    lines, count = [], 0
    for root, dirs, files in os.walk(start):
        if count >= limit:
            break
        level = root.replace(start, '').count(os.sep)
        indent = '  ' * level
        lines.append(f"{indent}{os.path.basename(root) or root}/")
        count += 1
        items = files[:10]
        for f in items:
            if count >= limit:
                break
            lines.append(f"{indent}  {f}")
            count += 1
        if len(files) > 10:
            lines.append(f"{indent}  ... +{len(files) - 10} files")
    kevbin.box.code("\n".join(lines))
    kevbin.box.info(f"{count} entries shown (truncated at {limit}).")
    kevbin.pause()


def file_search(kevbin):
    """Glob search for files."""
    kevbin.clear()
    kevbin.box.title("FILE SEARCH")
    pattern = kevbin.box.input("Pattern (e.g. **/*.py): ").strip() or "**/*"
    root = kevbin.box.input("Root (empty = current): ").strip() or "."
    hits = glob.glob(os.path.join(root, pattern), recursive=len(pattern) > 1 or True)[:200]
    if not hits:
        kevbin.box.error(f"No matches for {pattern}")
        kevbin.pause()
        return
    kevbin.box.code("\n".join(hits))
    kevbin.box.info(f"{len(hits)} match(es).")
    kevbin.pause()


def file_sizes(kevbin):
    """Biggest files in a directory."""
    kevbin.clear()
    kevbin.box.title("BIGGEST FILES")
    start = kevbin.box.input("Path (empty = current): ").strip() or "."
    if not os.path.isdir(start):
        kevbin.box.error("Not a directory.")
        kevbin.pause()
        return
    found = []
    for root, _, files in os.walk(start):
        for f in files:
            try:
                p = os.path.join(root, f)
                found.append((os.path.getsize(p), p))
                if len(found) > 4000:
                    break
            except OSError:
                pass
    found.sort(reverse=True)
    rows = [("Size", "Path")] + [(_fmt_bytes(s), p[:58]) for s, p in found[:20]]
    kevbin.box.table(rows, title=f"Top 20 in {start}")
    kevbin.pause()


def path_info(kevbin):
    """Details about a path."""
    kevbin.clear()
    kevbin.box.title("PATH INFO")
    p = kevbin.box.input("Path: ").strip()
    if not p:
        return
    p = os.path.abspath(p)
    if not os.path.exists(p):
        kevbin.box.error("Path does not exist.")
        kevbin.pause()
        return
    st = os.stat(p)
    import stat as stmod
    rows = [("Path", p),
            ("Exists", "Yes"),
            ("Type", "Directory" if os.path.isdir(p) else "File"),
            ("Size", _fmt_bytes(st.st_size)),
            ("Modified", datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")),
            ("Perms", stmod.filemode(st.st_mode)),
            ("Readable", "Yes" if os.access(p, os.R_OK) else "No"),
            ("Writable", "Yes" if os.access(p, os.W_OK) else "No")]
    kevbin.box.table(rows)
    kevbin.pause()


def random_qr_style(kevbin):
    """Skip — placeholder kept for menu safety."""
    kevbin.box.info("not implemented")
    kevbin.pause()
"""Site Viewer — View source + headers, auto-bypass AES cookie challenges."""

import re

try:
    import requests
except ImportError:
    requests = None


def _aes_bypass(session, url, html):
    """Detect and bypass InfinityFree-style AES cookie challenge. Returns (new_html, bypassed)."""
    m = re.search(
        r'var\s+a\s*=\s*toNumbers\("([0-9a-f]{32})"\)'
        r'.*?var\s+b\s*=\s*toNumbers\("([0-9a-f]{32})"\)'
        r'.*?var\s+c\s*=\s*toNumbers\("([0-9a-f]{32})"\)'
        r'.*?document\.cookie\s*=\s*"__test=".*?location\.href\s*=\s*"([^"]+)"',
        html, re.S
    )
    if not m:
        return html, False

    a_hex, b_hex, c_hex, redirect_url = m.group(1), m.group(2), m.group(3), m.group(4)
    kevbin_ref = [None]

    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad
    except ImportError:
        try:
            from Cryptodome.Cipher import AES
            from Cryptodome.Util.Padding import unpad
        except ImportError:
            return html, False

    try:
        key = bytes.fromhex(a_hex) + bytes.fromhex(b_hex)
        iv = bytes(16)
        ciphertext = bytes.fromhex(c_hex)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), 16)
        cookie_val = plaintext.hex()
    except Exception:
        return html, False

    session.cookies.set('__test', cookie_val, domain='/', path='/')
    try:
        r2 = session.get(redirect_url, timeout=10, verify=False)
        return r2.text, True
    except Exception:
        return html, False


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🔍', 'SITE VIEWER')
    kevbin.cprint(kevbin.t.secondary, "  Enter a URL to view source and headers.\n")

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    url = kevbin.input_choice("  URL: ").strip()
    if not url:
        return

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        r = session.get(url, timeout=10, verify=False)

        html = r.text
        bypassed = False
        if 'slowAES.decrypt' in html or 'toNumbers' in html:
            kevbin.cprint(kevbin.t.warning, "  [~] AES cookie challenge detected — bypassing...")
            html, bypassed = _aes_bypass(session, url, html)
            if bypassed:
                kevbin.cprint(kevbin.t.success, "  [+] Bypass successful!")
            else:
                kevbin.cprint(kevbin.t.error, "  [!] Bypass failed (install pycryptodome: pip install pycryptodome)")

        kevbin.cprint(kevbin.t.highlight, f"\n  +------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Field            | Value                            |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.secondary, f"  | Status           | {r.status_code:<34} |")
        kevbin.cprint(kevbin.t.secondary, f"  | Final URL        | {r.url[:34]:<34} |")
        kevbin.cprint(kevbin.t.secondary, f"  | Encoding         | {r.encoding:<34} |")
        kevbin.cprint(kevbin.t.secondary, f"  | Size             | {len(html):<34} |")
        if bypassed:
            kevbin.cprint(kevbin.t.success, f"  | AES Bypass       | {'Yes':<34} |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")

        kevbin.cprint(kevbin.t.accent, "\n  Response Headers:")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Header           | Value                            |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")
        for k, v in sorted(r.headers.items()):
            kevbin.cprint(kevbin.t.secondary, f"  | {k:<16} | {v[:34]:<34} |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")

        kevbin.cprint(kevbin.t.accent, "\n  HTML Source (first 2000 chars):")
        kevbin.cprint(kevbin.t.txt, f"  {html[:2000]}")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

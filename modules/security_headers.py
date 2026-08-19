"""Security Headers - Analyze HTTP security headers."""

try:
    import requests
except ImportError:
    requests = None


HEADERS_TO_CHECK = [
    ('Strict-Transport-Security', 'HSTS', 'Enforces HTTPS', True),
    ('X-Frame-Options', 'X-Frame-Options', 'Clickjacking protection', True),
    ('X-Content-Type-Options', 'X-Content-Type-Options', 'MIME sniffing protection', True),
    ('Content-Security-Policy', 'CSP', 'Content injection protection', True),
    ('X-XSS-Protection', 'X-XSS-Protection', 'XSS filter (legacy)', False),
    ('Referrer-Policy', 'Referrer-Policy', 'Referrer control', True),
    ('Permissions-Policy', 'Permissions-Policy', 'Feature permissions', True),
    ('Cross-Origin-Embedder-Policy', 'COEP', 'Cross-origin isolation', False),
    ('Cross-Origin-Opener-Policy', 'COOP', 'Cross-origin isolation', False),
    ('Cross-Origin-Resource-Policy', 'CORP', 'Cross-origin resource control', False),
]


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🛡️', 'SECURITY HEADERS')
    kevbin.cprint(kevbin.t.secondary, "  Enter a URL to analyze security headers.")
    kevbin.line()

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
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True)
        headers = {k.lower(): v for k, v in r.headers.items()}

        kevbin.cprint(kevbin.t.highlight, f"\n  +--------------------------+--------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Header                   | Status | Description                      |")
        kevbin.cprint(kevbin.t.highlight, f"  +--------------------------+--------+----------------------------------+")
        for header, short, desc, recommended in HEADERS_TO_CHECK:
            val = headers.get(header.lower())
            if val:
                kevbin.cprint(kevbin.t.success, f"  | {header:<24} | [OK]   | {val[:34]:<34} |")
            else:
                status = '[MISSING]' if recommended else '[OPTIONAL]'
                color = kevbin.t.error if recommended else kevbin.t.warning
                kevbin.cprint(color, f"  | {header:<24} | {status:<6} | {desc:<34} |")
        kevbin.cprint(kevbin.t.highlight, f"  +--------------------------+--------+----------------------------------+")

        if 'content-security-policy' in headers:
            kevbin.cprint(kevbin.t.accent, f"\n  CSP: {headers['content-security-policy'][:80]}")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

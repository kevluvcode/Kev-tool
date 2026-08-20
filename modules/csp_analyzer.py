"""CSP Analyzer - Parse and analyze Content Security Policy."""

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('📋', 'CSP ANALYZER')
    kevbin.cprint(kevbin.t.secondary, "  Enter a URL to fetch and analyze CSP header.")
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
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        csp = r.headers.get('Content-Security-Policy') or r.headers.get('Content-Security-Policy-Report-Only')

        if not csp:
            kevbin.cprint(kevbin.t.warning, "\n  [!] No CSP header found.")
            kevbin.pause()
            return

        kevbin.cprint(kevbin.t.highlight, f"\n  +------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Directive        | Value                            |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")

        for part in csp.split(';'):
            part = part.strip()
            if not part:
                continue
            if ' ' in part:
                directive, value = part.split(' ', 1)
            else:
                directive, value = part, ''
            kevbin.cprint(kevbin.t.secondary, f"  | {directive:<16} | {value[:34]:<34} |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")

        kevbin.cprint(kevbin.t.txt, f"\n  Raw: {csp[:80]}")
        if 'unsafe-inline' in csp:
            kevbin.cprint(kevbin.t.warning, "  [!] Contains 'unsafe-inline'")
        if 'unsafe-eval' in csp:
            kevbin.cprint(kevbin.t.warning, "  [!] Contains 'unsafe-eval'")
        if '*' in csp and 'self' not in csp:
            kevbin.cprint(kevbin.t.warning, "  [!] Wildcard without 'self'")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

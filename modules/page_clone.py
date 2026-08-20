"""Page Clone - Clone website HTML locally."""

try:
    import requests
except ImportError:
    requests = None

import os
import re


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('📄', 'PAGE CLONE')
    kevbin.cprint(kevbin.t.secondary, "  Enter a URL to download and save HTML.")
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
        r = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        r.raise_for_status()

        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace(':', '_')
        path = parsed.path.replace('/', '_').strip('_') or 'index'
        if not path.endswith('.html'):
            path += '.html'

        out_dir = f'cloned_{domain}'
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, path)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(r.text)

        kevbin.cprint(kevbin.t.success, f"\n  [+] Saved to: {out_path}")
        kevbin.cprint(kevbin.t.txt, f"  Size: {len(r.text)} bytes")
        kevbin.cprint(kevbin.t.txt, f"  Status: {r.status_code}")

        assets = re.findall(r'(?:src|href)=["\']([^"\']+)["\']', r.text)
        css_js = [a for a in assets if a.endswith(('.css', '.js'))]
        kevbin.cprint(kevbin.t.accent, f"  Found {len(css_js)} CSS/JS references (not downloaded)")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

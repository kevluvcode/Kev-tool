"""Web Cloner — Clone any website locally with assets."""

import os
import re

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🛡️', 'WEB CLONER')
    kevbin.cprint(kevbin.t.dim, "  Clone a website's HTML + assets locally.\n")

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    url = kevbin.input_choice("  Target URL: ").strip()
    if not url:
        return
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    domain = re.sub(r'[^a-zA-Z0-9]', '_', url.split('//')[1].split('/')[0])
    out_dir = os.path.join(os.getcwd(), f'cloned_{domain}')
    os.makedirs(out_dir, exist_ok=True)

    kevbin.cprint(kevbin.t.dim, f"  Cloning to {out_dir}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] Failed: {e}")
        kevbin.pause()
        return

    with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    kevbin.cprint(kevbin.t.success, f"  [✓] HTML saved ({len(html)} bytes)")

    assets = re.findall(r'(?:src|href)=["\']([^"\']+\.(css|js|png|jpg|gif|svg|ico|woff2?))["\']', html, re.I)
    if assets:
        adir = os.path.join(out_dir, 'assets')
        os.makedirs(adir, exist_ok=True)
        count = 0
        for aurl, ext in assets[:50]:
            if aurl.startswith('//'):
                aurl = 'https:' + aurl
            elif aurl.startswith('/'):
                from urllib.parse import urlparse
                p = urlparse(url)
                aurl = f"{p.scheme}://{p.netloc}{aurl}"
            elif not aurl.startswith(('http://', 'https://')):
                aurl = url.rstrip('/') + '/' + aurl.lstrip('/')
            fname = re.sub(r'[^a-zA-Z0-9._-]', '_', os.path.basename(aurl.split('?')[0]))
            if not fname:
                continue
            try:
                ar = requests.get(aurl, headers=headers, timeout=10, verify=False)
                if ar.status_code == 200:
                    with open(os.path.join(adir, fname), 'wb') as f:
                        f.write(ar.content)
                    count += 1
            except Exception:
                pass
        kevbin.cprint(kevbin.t.success, f"  [✓] {count} assets downloaded")

    kevbin.cprint(kevbin.t.success, f"\n  [✓] Cloned to {out_dir}")
    kevbin.pause()

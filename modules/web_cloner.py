"""Web Cloner — Clone any website locally with assets."""

import os
import re

try:
    import requests
except ImportError:
    requests = None


def run(navi):
    navi.clear()
    navi.section_header('🛡️', 'WEB CLONER')
    navi.cprint(navi.t.dim, "  Clone a website's HTML + assets locally.\n")

    if requests is None:
        navi.cprint(navi.t.error, "  [X] pip install requests")
        navi.pause()
        return

    url = navi.input_choice("  Target URL: ").strip()
    if not url:
        return
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    domain = re.sub(r'[^a-zA-Z0-9]', '_', url.split('//')[1].split('/')[0])
    out_dir = os.path.join(os.getcwd(), f'cloned_{domain}')
    os.makedirs(out_dir, exist_ok=True)

    navi.cprint(navi.t.dim, f"  Cloning to {out_dir}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] Failed: {e}")
        navi.pause()
        return

    with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    navi.cprint(navi.t.success, f"  [✓] HTML saved ({len(html)} bytes)")

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
        navi.cprint(navi.t.success, f"  [✓] {count} assets downloaded")

    navi.cprint(navi.t.success, f"\n  [✓] Cloned to {out_dir}")
    navi.pause()

"""Page Clone — Download a website with CSS, JS, and image assets."""

import os
import re
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    requests = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve(base, href):
    if not href or href.startswith(('data:', 'javascript:', 'mailto:', '#')):
        return None
    if href.startswith('//'):
        return 'https:' + href
    if href.startswith(('http://', 'https://')):
        return href
    return urljoin(base, href)


def _fname(url):
    path = urlparse(url).path.rstrip('/')
    name = os.path.basename(path) or 'asset'
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    if not name or name.startswith('.'):
        ext = os.path.splitext(urlparse(url).path)[1].lower()
        name = f"asset{ext}" if ext else "asset"
    return name


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('📄', 'PAGE CLONE')
    kevbin.cprint(kevbin.t.secondary, "  Download a website with HTML + CSS + JS + images.\n")

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    url = kevbin.input_choice("  URL: ").strip()
    if not url:
        return
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    parsed = urlparse(url)
    domain = re.sub(r'[^a-zA-Z0-9]', '_', parsed.netloc)
    out_dir = os.path.join(ROOT, f'cloned_{domain}')
    os.makedirs(out_dir, exist_ok=True)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    session = requests.Session()
    session.headers.update(headers)
    seen = set()
    downloaded = 0

    kevbin.cprint(kevbin.t.txt, f"  Fetching {url}...")

    try:
        resp = session.get(url, timeout=15, verify=False)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] Failed: {e}")
        kevbin.pause()
        return

    asset_urls = set()

    for m in re.finditer(r'<link\b[^>]+href=["\']([^"\']+)["\']', html, re.I):
        asset_urls.add(m.group(1))
    for m in re.finditer(r'<script\b[^>]+src=["\']([^"\']+)["\']', html, re.I):
        asset_urls.add(m.group(1))
    for m in re.finditer(r'<img\b[^>]+src=["\']([^"\']+)["\']', html, re.I):
        asset_urls.add(m.group(1))

    kevbin.cprint(kevbin.t.dim, f"  Found {len(asset_urls)} asset references")

    local_map = {}
    for href in asset_urls:
        resolved = _resolve(url, href)
        if not resolved or resolved in seen:
            continue
        seen.add(resolved)
        fname = _fname(resolved)
        dest = os.path.join(out_dir, fname)
        try:
            r = session.get(resolved, timeout=10, verify=False)
            if r.status_code == 200 and len(r.content) > 0:
                with open(dest, 'wb') as f:
                    f.write(r.content)
                local_map[resolved] = fname
                downloaded += 1
        except Exception:
            pass

    for orig, local in local_map.items():
        html = html.replace(orig, local)

    page_name = (parsed.path.rstrip('/') or '/').replace('/', '_').strip('_') or 'index'
    if not page_name.endswith('.html'):
        page_name += '.html'
    out_path = os.path.join(out_dir, page_name)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    files_saved = [f for f in os.listdir(out_dir) if os.path.isfile(os.path.join(out_dir, f))]

    kevbin.cprint(kevbin.t.success, f"\n  [+] Saved to: {out_path}")
    kevbin.cprint(kevbin.t.success, f"  [+] {len(files_saved)} files ({downloaded} assets downloaded)")
    kevbin.cprint(kevbin.t.txt, f"  Open: {out_path}")
    if files_saved:
        rows = [("File", "Size")] + [(n, f"{os.path.getsize(os.path.join(out_dir, n)):,} bytes") for n in sorted(files_saved)[:15]]
        kevbin.box_table(rows, title="Saved Files")
    kevbin.pause()

"""Web Cloner — Clone any website locally with ALL assets (CSS, JS, images, fonts, etc.)."""

import os
import re
import time
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    requests = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _aes_bypass(session, url, html):
    """Bypass InfinityFree-style AES cookie challenge."""
    m = re.search(
        r'var\s+a\s*=\s*toNumbers\("([0-9a-f]{32})"\)'
        r'.*?var\s+b\s*=\s*toNumbers\("([0-9a-f]{32})"\)'
        r'.*?var\s+c\s*=\s*toNumbers\("([0-9a-f]{32})"\)'
        r'.*?location\.href\s*=\s*"([^"]+)"',
        html, re.S
    )
    if not m:
        return html, False
    a_hex, b_hex, c_hex, redirect_url = m.group(1), m.group(2), m.group(3), m.group(4)
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
        session.cookies.set('__test', plaintext.hex(), domain='/', path='/')
        r2 = session.get(redirect_url, timeout=10, verify=False)
        return r2.text, True
    except Exception:
        return html, False


def _resolve(base, href):
    """Resolve a potentially-relative URL against a base."""
    if not href or href.startswith(('data:', 'javascript:', 'mailto:', '#')):
        return None
    if href.startswith('//'):
        return 'https:' + href
    if href.startswith(('http://', 'https://')):
        return href
    return urljoin(base, href)


def _fname(url, idx=0):
    """Turn a URL into a safe local filename."""
    path = urlparse(url).path.rstrip('/')
    name = os.path.basename(path) or 'index'
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    if not name or name.startswith('.'):
        ext_map = {'.css': 'style', '.js': 'script', '.png': 'img', '.jpg': 'img',
                   '.jpeg': 'img', '.gif': 'img', '.svg': 'svg', '.ico': 'icon',
                   '.woff': 'font', '.woff2': 'font', '.ttf': 'font', '.eot': 'font'}
        for ext, fallback in ext_map.items():
            if ext in (urlparse(url).path.lower()):
                name = f"{fallback}_{idx}{ext}"
                break
        else:
            name = f"asset_{idx}"
    return name


def _download(url, dest, headers, session, seen):
    """Download a URL to a file path. Returns (bytes, filename) or None."""
    if url in seen or not url:
        return None
    seen.add(url)
    try:
        r = session.get(url, headers=headers, timeout=10, verify=False, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 0:
            with open(dest, 'wb') as f:
                f.write(r.content)
            return (r.content, dest)
    except Exception:
        pass
    return None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🛡️', 'WEB CLONER')
    kevbin.cprint(kevbin.t.dim, "  Clone a website + ALL assets (CSS, JS, images, fonts, stylesheets).\n")

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    url = kevbin.input_choice("  Target URL: ").strip()
    if not url:
        return
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    domain = re.sub(r'[^a-zA-Z0-9]', '_', parsed.netloc)
    out_dir = os.path.join(ROOT, f'cloned_{domain}')
    os.makedirs(out_dir, exist_ok=True)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    session = requests.Session()
    session.headers.update(headers)
    seen = set()
    downloaded = 0

    kevbin.cprint(kevbin.t.txt, f"  Fetching {url}...")

    # ——— 1. Fetch main HTML ———
    try:
        resp = session.get(url, timeout=15, verify=False)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] Failed to fetch: {e}")
        kevbin.pause()
        return

    if 'slowAES.decrypt' in html or 'toNumbers' in html:
        kevbin.cprint(kevbin.t.warning, "  [~] AES cookie challenge detected — bypassing...")
        html, bypassed = _aes_bypass(session, url, html)
        if bypassed:
            kevbin.cprint(kevbin.t.success, "  [+] Bypass successful!")
        else:
            kevbin.cprint(kevbin.t.error, "  [!] Bypass failed (pip install pycryptodome)")

    # ——— 2. Extract ALL asset URLs from HTML ———
    asset_urls = set()

    # <link rel="stylesheet" href="...">, <link rel="icon" href="...">, <link rel="preload" href="...">
    for m in re.finditer(r'<link\b[^>]+>', html, re.I):
        tag = m.group(0)
        href_m = re.search(r'\bhref=["\']([^"\']+)["\']', tag, re.I)
        if href_m:
            asset_urls.add(('css', href_m.group(1)))
        # also catch <link rel="preload" as="font"
        if re.search(r'rel=["\'](?:preload|prefetch|preconnect)["\']', tag, re.I) and href_m:
            asset_urls.add(('preload', href_m.group(1)))

    # <script src="...">
    for m in re.finditer(r'<script\b[^>]+src=["\']([^"\']+)["\']', html, re.I):
        asset_urls.add(('js', m.group(1)))

    # <img src="...">  + srcset + data-src + data-lazy
    for m in re.finditer(r'<img\b[^>]+>', html, re.I):
        tag = m.group(0)
        for attr in ('src', 'data-src', 'data-lazy-src', 'data-original'):
            am = re.search(rf'\b{attr}=["\']([^"\']+)["\']', tag, re.I)
            if am:
                asset_urls.add(('img', am.group(1)))
        srcset_m = re.search(r'\bsrcset=["\']([^"\']+)["\']', tag, re.I)
        if srcset_m:
            for part in srcset_m.group(1).split(','):
                u = part.strip().split()[0]
                if u:
                    asset_urls.add(('img', u))

    # <picture> / <source srcset="...">
    for m in re.finditer(r'<source\b[^>]+srcset=["\']([^"\']+)["\']', html, re.I):
        for part in m.group(1).split(','):
            u = part.strip().split()[0]
            if u:
                asset_urls.add(('img', u))

    # <video src="...">, <audio src="...">, <video poster="...">
    for m in re.finditer(r'<(?:video|audio)\b[^>]+(?:src|poster)=["\']([^"\']+)["\']', html, re.I):
        asset_urls.add(('media', m.group(1)))

    # <meta property="og:image" content="...">
    for m in re.finditer(r'<meta\b[^>]+content=["\']([^"\']+)["\']', html, re.I):
        val = m.group(1)
        if any(ext in val.lower() for ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico')):
            asset_urls.add(('img', val))

    # inline style="background-image: url(...)"  /  background: url(...)
    for m in re.finditer(r'url\(["\']?([^"\')\s]+)["\']?\)', html, re.I):
        u = m.group(1)
        if not u.startswith(('data:', '#')):
            asset_urls.add(('style', u))

    # <image href="..."> (SVG)
    for m in re.finditer(r'<image\b[^>]+(?:href|src)=["\']([^"\']+)["\']', html, re.I):
        asset_urls.add(('img', m.group(1)))

    # ——— 3. Download CSS files and scrape them for url() / @import ———
    css_files = []
    to_scrape = list(asset_urls)
    extra_css_urls = set()

    kevbin.cprint(kevbin.t.dim, f"  Found {len(asset_urls)} raw references in HTML")

    for kind, href in to_scrape:
        resolved = _resolve(url, href)
        if not resolved:
            continue
        ext = os.path.splitext(urlparse(resolved).path)[1].lower()
        if ext == '.css' or kind == 'css':
            css_files.append(resolved)

    # Download CSS and parse for nested url() / @import
    scraped_css = set()
    while css_files:
        curl = css_files.pop(0)
        if curl in scraped_css:
            continue
        scraped_css.add(curl)
        dest = os.path.join(out_dir, _fname(curl))
        result = _download(curl, dest, headers, session, seen)
        if result:
            downloaded += 1
            content = result[0].decode('utf-8', errors='replace')
            # @import "..." or @import url("...")
            for im in re.finditer(r'@import\s+(?:url\(["\']?([^"\')\s]+)["\']?\)|["\']([^"\']+)["\'])', content, re.I):
                imp_url = im.group(1) or im.group(2)
                resolved = _resolve(curl, imp_url)
                if resolved:
                    asset_urls.add(('css', imp_url))
                    css_files.append(resolved)
            # url(...) in CSS
            for um in re.finditer(r'url\(["\']?([^"\')\s]+)["\']?\)', content, re.I):
                u = um.group(1)
                if not u.startswith(('data:', '#')):
                    resolved = _resolve(curl, u)
                    if resolved:
                        extra_css_urls.add(resolved)

    # Download assets referenced from CSS (fonts, background images)
    for u in extra_css_urls:
        if u in seen:
            continue
        ext = os.path.splitext(urlparse(u).path)[1].lower()
        dest = os.path.join(out_dir, _fname(u))
        result = _download(u, dest, headers, session, seen)
        if result:
            downloaded += 1

    # ——— 4. Download remaining HTML-referenced assets ———
    for kind, href in asset_urls:
        resolved = _resolve(url, href)
        if not resolved or resolved in seen:
            continue
        dest = os.path.join(out_dir, _fname(resolved))
        result = _download(resolved, dest, headers, session, seen)
        if result:
            downloaded += 1
            # If it's CSS, parse it too
            ext = os.path.splitext(urlparse(resolved).path)[1].lower()
            if ext == '.css':
                content = result[0].decode('utf-8', errors='replace')
                for im in re.finditer(r'@import\s+(?:url\(["\']?([^"\')\s]+)["\']?\)|["\']([^"\']+)["\'])', content, re.I):
                    imp_url = im.group(1) or im.group(2)
                    r2 = _resolve(resolved, imp_url)
                    if r2 and r2 not in seen:
                        css_files.append(r2)

    # ——— 5. Fix HTML to point to local files ———
    local_map = {}
    for seen_url in seen:
        fname = _fname(seen_url)
        if os.path.exists(os.path.join(out_dir, fname)):
            local_map[seen_url] = fname

    modified_html = html
    for orig, local in local_map.items():
        modified_html = modified_html.replace(orig, local)

    with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(modified_html)

    # ——— 6. Summary ———
    files_saved = []
    for f in os.listdir(out_dir):
        fp = os.path.join(out_dir, f)
        if os.path.isfile(fp):
            size = os.path.getsize(fp)
            files_saved.append((f, size))

    kevbin.cprint(kevbin.t.success, f"\n  [✓] Cloned to: {out_dir}")
    kevbin.cprint(kevbin.t.success, f"  [✓] {len(files_saved)} files saved ({downloaded} downloads)")
    kevbin.cprint(kevbin.t.txt, f"  Open: {os.path.join(out_dir, 'index.html')}")
    if files_saved:
        rows = [("File", "Size")] + [(n, f"{s:,} bytes") for n, s in sorted(files_saved, key=lambda x: -x[1])[:20]]
        kevbin.box_table(rows, title="Saved Files")
    kevbin.pause()

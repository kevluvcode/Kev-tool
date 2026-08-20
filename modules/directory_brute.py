"""Directory Brute — Web directory & file brute forcer."""

import socket
import ssl
import threading
import time
import urllib.parse


COMMON_DIRS = [
    'admin', 'login', 'wp-admin', 'wp-login.php', 'administrator',
    'phpmyadmin', 'phpMyAdmin', 'cpanel', 'webmail', 'mail',
    'backup', 'backups', 'old', 'new', 'temp', 'tmp', 'test',
    'dev', 'development', 'staging', 'stage', 'beta', 'demo',
    'api', 'v1', 'v2', 'v3', 'rest', 'graphql', 'swagger',
    'docs', 'documentation', 'help', 'support', 'faq',
    'uploads', 'upload', 'files', 'media', 'images', 'img', 'assets',
    'static', 'css', 'js', 'javascript', 'scripts', 'fonts',
    'config', 'configuration', 'settings', 'setup', 'install',
    '.env', '.git', '.svn', '.htaccess', '.htpasswd',
    'robots.txt', 'sitemap.xml', 'crossdomain.xml', 'favicon.ico',
    'server-status', 'server-info', 'info.php', 'phpinfo.php',
    'shell', 'cmd', 'console', 'terminal', 'ssh',
    'database', 'db', 'sql', 'mysql', 'postgres', 'mongo',
    'config.php', 'config.json', 'config.yml', 'config.xml',
    'wp-config.php', 'wp-config.php.bak', 'wp-config.php.old',
    '.DS_Store', 'Thumbs.db', 'web.config', 'elmah.axd',
    'trace.axd', 'status', 'health', 'ping', 'metrics',
    'cgi-bin', 'scripts', 'ssi', '.well-known',
    'swagger-ui', 'redoc', 'openapi.json',
    'wp-content', 'wp-includes', 'xmlrpc.php',
    'editor', 'filemanager', 'ftp', 'sftp',
    'register', 'signup', 'create', 'forgot', 'reset',
    'profile', 'account', 'dashboard', 'panel', 'portal',
    'search', 'sitemap', 'archive', 'archives', 'blog',
    'feed', 'rss', 'atom', 'json', 'xml', 'csv',
    'debug', 'log', 'logs', 'error', 'errors', '404', '500',
    '.env.bak', '.env.old', '.env.example', '.env.local',
    'Makefile', 'Dockerfile', 'docker-compose.yml', 'Vagrantfile',
    'README.md', 'LICENSE', 'CHANGELOG.md',
]

COMMON_EXTENSIONS = ['', '.php', '.html', '.txt', '.asp', '.aspx', '.jsp', '.py', '.bak', '.old', '.swp']

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Connection': 'close',
}


def _build_url(base, path, params=None):
    base = base.rstrip('/')
    return f"{base}/{path}"


def _check_url(url, timeout=3):
    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        path = parsed.path or '/'
        if parsed.query:
            path += '?' + parsed.query

        sock = socket.create_connection((host, port), timeout=timeout)
        if parsed.scheme == 'https':
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            sock = ctx.wrap_socket(sock, server_hostname=host)

        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n"
        for k, v in HEADERS.items():
            request += f"{k}: {v}\r\n"
        request += "\r\n"
        sock.sendall(request.encode())

        response = b''
        sock.settimeout(timeout)
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                if len(response) > 8192:
                    break
            except Exception:
                break
        sock.close()

        header_end = response.find(b'\r\n\r\n')
        if header_end == -1:
            return None, 0, ''
        status_line = response[:header_end].decode('utf-8', errors='ignore').split('\r\n')[0]
        parts = status_line.split(' ', 2)
        code = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        size = len(response) - header_end - 4
        return url, code, str(size)
    except Exception:
        return None, 0, ''


def _worker(queue, results, lock, done, total, kevbin):
    while True:
        try:
            item = queue.pop()
        except IndexError:
            return
        url, code = item
        status, size = _check_url(url)[:2], _check_url(url)[2]
        with lock:
            done[0] += 1
            if code and code not in (404, 0, 301, 302):
                results.append((url, code, size))
    pass


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('📁', 'DIRECTORY BRUTE FORCER')

    target = kevbin.input_choice("  Target URL (e.g. https://example.com): ").strip()
    if not target:
        return
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target

    kevbin.cprint(kevbin.t.dim, "  [1] Common dirs [2] Extended [3] Custom wordlist")
    mode = kevbin.input_choice("  Mode [1]: ").strip() or '1'
    custom_path = None
    if mode == '3':
        custom_path = kevbin.input_choice("  Wordlist path: ").strip().strip('"')
        if not custom_path:
            return

    threads_n = kevbin.input_choice("  Threads [20]: ").strip() or '20'
    try:
        threads_n = max(5, min(80, int(threads_n)))
    except ValueError:
        threads_n = 20

    wordlist = []
    if custom_path:
        try:
            with open(custom_path, 'r', encoding='utf-8', errors='ignore') as f:
                wordlist = [l.strip() for l in f if l.strip()]
        except Exception as e:
            kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()
            return
    elif mode == '2':
        wordlist = COMMON_DIRS
    else:
        wordlist = COMMON_DIRS[:50]

    queue = []
    for word in wordlist:
        for ext in COMMON_EXTENSIONS:
            path = word.lstrip('/') + ext
            url = _build_url(target, path)
            queue.append((url, path))

    kevbin.cprint(kevbin.t.dim, f"  [~] Testing {len(queue)} paths ({threads_n} threads)...")

    results = []
    lock = threading.Lock()
    done = [0]
    total = len(queue)
    workers = [threading.Thread(target=_worker, args=(queue, results, lock, done, total, kevbin), daemon=True)
               for _ in range(min(threads_n, total))]
    for w in workers:
        w.start()

    try:
        while done[0] < total:
            time.sleep(0.3)
            pct = int(done[0] / total * 100) if total else 0
            sys.stdout = __import__('sys').stdout
            sys.stdout.write(f"\r  [~] {done[0]}/{total} ({pct}%) found: {len(results)}  ")
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass

    for w in workers:
        w.join(timeout=3)

    import sys
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()

    if results:
        results.sort(key=lambda x: x[1])
        kevbin.cprint(kevbin.t.success, f"\n  [✓] {len(results)} paths found:\n")
        for url, code, size in results[:50]:
            color = kevbin.t.success if code < 300 else kevbin.t.warning
            kevbin.cprint(color, f"    {code}  {size:>6}B  {url}")

        save = kevbin.input_choice("\n  Save to file? (y/n): ").strip().lower()
        if save == 'y':
            out_path = kevbin.input_choice("  Path [results.txt]: ").strip() or 'results.txt'
            try:
                with open(out_path, 'w', encoding='utf-8') as f:
                    for url, code, size in results:
                        f.write(f"{code}\t{size}\t{url}\n")
                kevbin.cprint(kevbin.t.success, f"  [✓] Saved to {out_path}")
            except Exception as e:
                kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    else:
        kevbin.cprint(kevbin.t.warning, "\n  [!] No accessible paths found.")

    kevbin.pause()

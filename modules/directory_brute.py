"""Directory Brute — Web directory & file brute forcer."""

import socket
import ssl
import threading
import time
import urllib.parse


COMMON_DIRS = [
    # Authentication / administration
    'admin', 'admins', 'administrator', 'administrators', 'adminpanel',
    'admin-panel', 'admin_panel', 'adminarea', 'admin-area', 'admincp',
    'admin-cp', 'adminconsole', 'admin-console', 'adminlogin', 'admin-login',
    'admin1', 'admin2', 'admin3', 'adm', 'manage', 'management',
    'manager', 'control', 'controlpanel', 'control-panel', 'cp',
    'cpanel', 'whm', 'panel', 'dashboard', 'portal', 'backend',
    'backoffice', 'office', 'staff', 'staffonly', 'internal',

    # Login / account
    'login', 'log-in', 'signin', 'sign-in', 'signon', 'auth',
    'authentication', 'authorize', 'authorization', 'oauth', 'oauth2',
    'sso', 'logout', 'signout', 'sign-out', 'register', 'registration',
    'signup', 'sign-up', 'create-account', 'join', 'forgot',
    'forgot-password', 'forgotpassword', 'reset', 'reset-password',
    'password-reset', 'recover', 'recovery', 'verify', 'verification',
    'activate', 'activation', 'account', 'accounts', 'profile',
    'profiles', 'user', 'users', 'member', 'members', 'me',

    # WordPress
    'wp-admin', 'wp-login.php', 'wp-content', 'wp-includes',
    'wp-config.php', 'wp-config.php.bak', 'wp-config.php.old',
    'wp-config.php~', 'wp-json', 'wp-cron.php', 'wp-load.php',
    'wp-settings.php', 'xmlrpc.php', 'wp-comments-post.php',
    'wp-trackback.php', 'wp-signup.php', 'wp-activate.php',
    'wp-content/uploads', 'wp-content/plugins', 'wp-content/themes',
    'wp-content/cache', 'wp-content/debug.log',

    # CMS / common platforms
    'administrator', 'joomla', 'drupal', 'sites', 'modules',
    'themes', 'core', 'typo3', 'contao', 'magento', 'shop',
    'store', 'prestashop', 'opencart', 'ghost', 'cms',
    'cmsadmin', 'cms-admin', 'umbraco', 'sitecore',

    # Database / database tools
    'phpmyadmin', 'phpMyAdmin', 'pma', 'myadmin', 'adminer',
    'dbadmin', 'db-admin', 'database', 'databases', 'db',
    'sql', 'mysql', 'mysqli', 'postgres', 'postgresql',
    'mongo', 'mongodb', 'redis', 'elasticsearch',

    # APIs
    'api', 'api-docs', 'api-doc', 'api-docs/', 'apis',
    'v1', 'v2', 'v3', 'v4', 'api/v1', 'api/v2', 'api/v3',
    'rest', 'rest-api', 'graphql', 'graphql-playground',
    'graphiql', 'swagger', 'swagger-ui', 'swagger.json',
    'swagger.yaml', 'openapi', 'openapi.json', 'openapi.yaml',
    'redoc', 'redocly', 'docs/api',

    # Documentation / help
    'docs', 'doc', 'documentation', 'developer', 'developers',
    'devdocs', 'api-docs', 'guide', 'guides', 'manual',
    'help', 'support', 'support-center', 'supportcenter',
    'faq', 'kb', 'knowledgebase', 'wiki', 'readme',
    'README', 'README.md', 'CHANGELOG', 'CHANGELOG.md',
    'LICENSE', 'LICENSE.md',

    # Development / testing / staging
    'dev', 'development', 'develop', 'developer', 'stage',
    'staging', 'staging1', 'staging2', 'test', 'testing',
    'tests', 'qa', 'uat', 'sandbox', 'beta', 'alpha',
    'demo', 'preview', 'preprod', 'pre-production',
    'production', 'prod', 'local', 'localhost',

    # Files / uploads / media
    'uploads', 'upload', 'uploaded', 'files', 'file',
    'downloads', 'download', 'dl', 'media', 'images',
    'image', 'img', 'imgs', 'pictures', 'photos',
    'photo', 'video', 'videos', 'audio', 'assets',
    'asset', 'static', 'public', 'resources', 'resource',
    'storage', 'content', 'contents', 'attachments',
    'documents', 'document', 'data', 'dataset',

    # Frontend assets
    'css', 'js', 'javascript', 'scripts', 'script',
    'fonts', 'font', 'icons', 'icon', 'svg', 'favicon.ico',
    'dist', 'build', 'bundle', 'bundles', 'vendor',
    'vendors', 'node_modules', 'packages', 'components',

    # Configuration
    'config', 'configs', 'configuration', 'settings',
    'setting', 'setup', 'install', 'installer', 'install.php',
    'config.php', 'config.json', 'config.yml', 'config.yaml',
    'config.xml', 'settings.json', 'settings.php',
    'application.yml', 'application.yaml', 'application.properties',
    'appsettings.json', 'web.config', 'web.xml',
    'database.yml', 'database.yaml',

    # Environment / repository artifacts
    '.env', '.env.local', '.env.dev', '.env.development',
    '.env.test', '.env.testing', '.env.stage', '.env.staging',
    '.env.prod', '.env.production', '.env.example',
    '.env.sample', '.env.bak', '.env.backup', '.env.old',
    '.env.save', '.git', '.git/config', '.gitignore',
    '.gitattributes', '.github', '.gitlab', '.svn',
    '.svn/entries', '.hg', '.bzr',

    # Backups / temporary files
    'backup', 'backups', 'backup.zip', 'backup.tar',
    'backup.tar.gz', 'site-backup', 'db-backup',
    'database-backup', 'old', 'oldsite', 'old-site',
    'archive', 'archives', 'archived', 'copy', 'copies',
    'previous', 'temp', 'tmp', 'cache', 'cached',
    'logs', 'log', 'debug', 'debug.log', 'error',
    'errors', 'error.log', 'access.log',

    # Server / diagnostics
    'server-status', 'server-info', 'status', 'health',
    'healthz', 'ready', 'readiness', 'liveness', 'ping',
    'metrics', 'stats', 'statistics', 'monitoring',
    'diagnostics', 'debug', 'trace', 'trace.axd',
    'elmah.axd', 'info.php', 'phpinfo.php', 'phpinfo',
    'test.php', 'status.php',

    # Web server files
    '.htaccess', '.htpasswd', '.user.ini', 'web.config',
    'robots.txt', 'sitemap.xml', 'sitemap.txt', 'sitemap',
    'crossdomain.xml', 'clientaccesspolicy.xml',
    '.well-known', '.well-known/security.txt',
    'security.txt', 'humans.txt',

    # CGI / server paths
    'cgi-bin', 'cgi', 'fcgi-bin', 'scripts', 'script',
    'ssi', 'bin', 'server', 'servers', 'console',
    'terminal', 'cmd', 'shell', 'ssh', 'ftp', 'sftp',
    'webmail', 'mail', 'mailbox', 'email',

    # Common application routes
    'home', 'index', 'index.php', 'index.html',
    'app', 'application', 'apps', 'service', 'services',
    'search', 'browse', 'list', 'directory', 'catalog',
    'explore', 'discover', 'feed', 'rss', 'atom',
    'news', 'blog', 'blogs', 'article', 'articles',
    'post', 'posts', 'category', 'categories', 'tag', 'tags',

    # E-commerce
    'shop', 'store', 'cart', 'checkout', 'payment',
    'payments', 'billing', 'invoice', 'invoices',
    'orders', 'order', 'products', 'product', 'catalog',
    'wishlist', 'coupons', 'coupon',

    # User-facing application pages
    'dashboard', 'home', 'settings', 'preferences',
    'notifications', 'messages', 'message', 'inbox',
    'chat', 'chats', 'contact', 'contacts', 'about',
    'privacy', 'terms', 'legal', 'tos', 'policy',
    'security', 'report', 'reports', 'abuse',

    # Monitoring / infrastructure
    'grafana', 'prometheus', 'kibana', 'jenkins',
    'ci', 'cd', 'ci-cd', 'build', 'deploy', 'deployment',
    'monitor', 'monitoring', 'metrics', 'healthcheck',
    'actuator', 'actuator/health', 'actuator/env',
    'actuator/info', 'management',

    # Framework-related paths
    'laravel', 'symfony', 'yii', 'cake', 'codeigniter',
    'rails', 'django', 'flask', 'fastapi', 'express',
    'spring', 'actuator', 'aspnet', '.net',

    # Node / JavaScript ecosystem
    'package.json', 'package-lock.json', 'yarn.lock',
    'pnpm-lock.yaml', 'node_modules', '.npmrc',
    'next', '_next', 'nuxt', '_nuxt', 'vite',
    'webpack', 'manifest.json',

    # Python ecosystem
    'requirements.txt', 'requirements-dev.txt',
    'pyproject.toml', 'setup.py', 'setup.cfg',
    'Pipfile', 'Pipfile.lock', 'venv', '.venv',
    '__pycache__', 'manage.py', 'wsgi.py', 'asgi.py',

    # Containers / deployment
    'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    'compose.yml', 'compose.yaml', '.dockerignore',
    'kubernetes', 'k8s', 'helm', 'charts',
    'Vagrantfile', 'terraform', '.terraform',
    'ansible', 'playbook.yml', 'deploy.yml',

    # Cloud / CI configuration
    '.github/workflows', '.gitlab-ci.yml', '.travis.yml',
    'azure-pipelines.yml', 'bitbucket-pipelines.yml',
    'vercel.json', 'netlify.toml', 'wrangler.toml',
    'firebase.json', 'amplify.yml',

    # Common file formats
    'json', 'xml', 'csv', 'yaml', 'yml', 'txt',
    'pdf', 'zip', 'tar', 'gz', 'bak', 'old',

    # Miscellaneous common paths
    'private', 'protected', 'secure', 'restricted',
    'hidden', 'secret', 'secrets', 'keys', 'key',
    'cert', 'certs', 'certificate', 'certificates',
    'ssl', 'tls', 'public_html', 'htdocs', 'www',
    'site', 'website', 'web', 'root', 'main',
    '404', '403', '401', '500', '502', '503',
    'error', 'maintenance', 'maintenance.html',
    'offline', 'coming-soon',
]

COMMON_EXTENSIONS = [
    '',

    # Web / server-side
    '.php', '.php3', '.php4', '.php5', '.php7', '.phtml',
    '.html', '.htm', '.xhtml', '.shtml',
    '.asp', '.aspx', '.ashx', '.asmx',
    '.jsp', '.jspx', '.jsf',
    '.cgi', '.pl', '.fcgi',

    # Programming / application
    '.py', '.pyc',
    '.rb', '.java', '.class',
    '.cs', '.vb',
    '.go', '.rs',
    '.lua',

    # JavaScript / frontend
    '.js', '.mjs', '.cjs',
    '.json', '.map',

    # Text / config
    '.txt', '.text',
    '.xml', '.yaml', '.yml',
    '.ini', '.conf', '.config',
    '.cfg', '.cnf',
    '.properties', '.toml',
    '.env',

    # Backup / old versions
    '.bak', '.backup', '.back',
    '.old', '.orig', '.original',
    '.copy', '.save', '.saved',
    '.tmp', '.temp',
    '.swp', '.swo', '.swn',
    '~',

    # Archives
    '.zip', '.rar', '.7z',
    '.tar', '.gz', '.bz2', '.xz',
    '.tgz', '.tar.gz',
    '.tar.bz2', '.tar.xz',

    # Database
    '.sql', '.sqlite', '.sqlite3',
    '.db', '.mdb', '.accdb',

    # Logs
    '.log', '.logs',
    '.debug', '.trace',

    # Documents / exports
    '.csv', '.tsv',
    '.pdf',
    '.doc', '.docx',
    '.xls', '.xlsx',

    # Common sensitive config formats
    '.pem', '.key', '.crt', '.cer',
    '.p12', '.pfx',

    # Source / repository artifacts
    '.md', '.rst',
    '.lock',
    '.gitignore',
    '.dockerignore',

    # Miscellaneous
    '.dat', '.cache',
    '.dump', '.dmp',
    '.bin',
]

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

"""Subdomain Enum - Find subdomains via DNS brute force."""

try:
    import requests
except ImportError:
    requests = None

import socket

COMMON_SUBDOMAINS = [
    'www', 'mail', 'ftp', 'admin', 'api', 'dev', 'staging', 'test',
    'blog', 'shop', 'store', 'app', 'mobile', 'm', 'beta', 'demo',
    'docs', 'help', 'support', 'status', 'cdn', 'static', 'assets',
    'img', 'images', 'media', 'video', 'stream', 'live', 'tv',
    'vpn', 'remote', 'portal', 'intranet', 'extranet', 'git', 'svn',
    'jenkins', 'ci', 'build', 'deploy', 'registry', 'docker',
    'k8s', 'kubernetes', 'monitor', 'grafana', 'prometheus', 'alert',
    'log', 'logs', 'logging', 'elastic', 'kibana', 'splunk',
    'db', 'database', 'sql', 'mysql', 'postgres', 'redis', 'mongo',
    'backup', 'bak', 'old', 'new', 'tmp', 'temp', 'staging2', 'prod',
    'production', 'prod2', 'eu', 'us', 'asia', 'global', 'internal',
    'external', 'public', 'private', 'secure', 'ssl', 'tls',
    'ws', 'wss', 'socket', 'realtime', 'push', 'notify', 'webhook',
    'oauth', 'auth', 'login', 'sso', 'ldap', 'ad', 'saml',
    'jira', 'confluence', 'wiki', 'gitlab', 'github', 'bitbucket',
    'npm', 'pypi', 'maven', 'nuget', 'docker-registry', 'harbor',
]


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🔍', 'SUBDOMAIN ENUMERATION')
    kevbin.cprint(kevbin.t.secondary, "  Enter a domain to enumerate subdomains.")
    kevbin.line()

    domain = kevbin.input_choice("  Domain: ").strip().lower()
    if not domain:
        return

    if domain.startswith(('http://', 'https://')):
        from urllib.parse import urlparse
        domain = urlparse(domain).netloc

    use_crt = kevbin.input_choice("  Use crt.sh? (y/n) [y]: ").strip().lower() != 'n'

    found = set()

    if use_crt:
        try:
            r = requests.get(f'https://crt.sh/?q=%.{domain}&output=json', timeout=15)
            for entry in r.json():
                name = entry.get('name_value', '').lower()
                for n in name.split('\n'):
                    if n.endswith('.' + domain) and not n.startswith('*.'):
                        found.add(n)
        except Exception:
            pass

    for sub in COMMON_SUBDOMAINS:
        fqdn = f'{sub}.{domain}'
        try:
            socket.gethostbyname(fqdn)
            found.add(fqdn)
        except Exception:
            pass

    kevbin.cprint(kevbin.t.highlight, f"\n  +----------------------------------+")
    kevbin.cprint(kevbin.t.highlight, f"  | Subdomain                        |")
    kevbin.cprint(kevbin.t.highlight, f"  +----------------------------------+")
    if found:
        for sub in sorted(found):
            kevbin.cprint(kevbin.t.secondary, f"  | {sub:<34} |")
    else:
        kevbin.cprint(kevbin.t.dim, f"  | (none found)                     |")
    kevbin.cprint(kevbin.t.highlight, f"  +----------------------------------+")
    kevbin.cprint(kevbin.t.accent, f"\n  Total found: {len(found)}")
    kevbin.pause()

"""CORS Tester — Test CORS headers on any URL."""

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🛡️', 'CORS TESTER')

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    url = kevbin.input_choice("  URL to test: ").strip()
    if not url:
        return
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    kevbin.cprint(kevbin.t.dim, "  Testing CORS headers...\n")
    origins = ['https://evil.com', 'https://null', 'https://' + url.split('//')[1].split('/')[0], '*']

    for origin in origins:
        try:
            r = requests.options(url, headers={
                'Origin': origin,
                'Access-Control-Request-Method': 'GET',
            }, timeout=10)
            acao = r.headers.get('Access-Control-Allow-Origin', '')
            acac = r.headers.get('Access-Control-Allow-Credentials', '')
            acam = r.headers.get('Access-Control-Allow-Methods', '')

            kevbin.cprint(kevbin.t.secondary, f"  Origin: {origin}")
            if acao:
                kevbin.cprint(kevbin.t.warning, f"    ACAO: {acao}")
                if acac.lower() == 'true':
                    kevbin.cprint(kevbin.t.error, f"    ⚠ CREDENTIALS ALLOWED — potential vulnerability!")
            else:
                kevbin.cprint(kevbin.t.success, f"    No ACAO header")
            if acam:
                kevbin.cprint(kevbin.t.txt, f"    Methods: {acam}")
            kevbin.cprint(kevbin.t.txt, "")
        except Exception as e:
            kevbin.cprint(kevbin.t.warning, f"  {origin}: {e}")
    kevbin.pause()

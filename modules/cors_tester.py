"""CORS Tester — Test CORS headers on any URL."""

try:
    import requests
except ImportError:
    requests = None


def run(navi):
    navi.clear()
    navi.section_header('🛡️', 'CORS TESTER')

    if requests is None:
        navi.cprint(navi.t.error, "  [X] pip install requests")
        navi.pause()
        return

    url = navi.input_choice("  URL to test: ").strip()
    if not url:
        return
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    navi.cprint(navi.t.dim, "  Testing CORS headers...\n")
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

            navi.cprint(navi.t.secondary, f"  Origin: {origin}")
            if acao:
                navi.cprint(navi.t.warning, f"    ACAO: {acao}")
                if acac.lower() == 'true':
                    navi.cprint(navi.t.error, f"    ⚠ CREDENTIALS ALLOWED — potential vulnerability!")
            else:
                navi.cprint(navi.t.success, f"    No ACAO header")
            if acam:
                navi.cprint(navi.t.dim, f"    Methods: {acam}")
            navi.cprint(navi.t.dim, "")
        except Exception as e:
            navi.cprint(navi.t.dim, f"  {origin}: {e}")
    navi.pause()

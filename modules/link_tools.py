"""Link Tools — Link bypass, expander, and tracker checker."""

try:
    import requests
except ImportError:
    requests = None


def run(navi):
    while True:
        navi.clear()
        navi.section_header('🔍', 'LINK TOOLS')
        navi.cprint(navi.t.secondary, "  [1]  Link Expander — Resolve shortened URLs")
        navi.cprint(navi.t.secondary, "  [2]  Link Tracker Check — Check if URL is tracked")
        navi.cprint(navi.t.secondary, "  [3]  Link Info — Headers + status + redirects")
        navi.cprint(navi.t.secondary, "  [0]  Back")
        navi.line()
        choice = navi.input_choice()
        if choice == '0': return

        if requests is None:
            navi.cprint(navi.t.error, "  [X] pip install requests")
            navi.pause()
            continue

        if choice in ('1', '2', '3'):
            url = navi.input_choice("  URL: ").strip()
            if not url:
                continue
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            try:
                r = requests.get(url, timeout=10, allow_redirects=False, verify=False,
                               headers={'User-Agent': 'Mozilla/5.0'})
                navi.cprint(navi.t.highlight + navi.t.B, f"\n  ┌─ LINK INFO {'─' * 41}")
                navi.cprint(navi.t.secondary, f"  │ Final URL:   {r.url[:70]}")
                navi.cprint(navi.t.secondary, f"  │ Status:      {r.status_code}")
                navi.cprint(navi.t.secondary, f"  │ Server:      {r.headers.get('Server', '?')}")
                navi.cprint(navi.t.secondary, f"  │ Content-Type:{r.headers.get('Content-Type', '?')}")

                if r.history:
                    navi.cprint(navi.t.accent, f"  │ Redirects:")
                    for h in r.history:
                        navi.cprint(navi.t.dim, f"  │   {h.status_code} -> {h.url[:60]}")
                else:
                    navi.cprint(navi.t.dim, f"  │ No redirects")

                tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'fbclid', 'gclid',
                                  'ref', 'source', 'mc_cid', 'mc_eid']
                found = [p for p in tracking_params if p in r.url.lower()]
                if found:
                    navi.cprint(navi.t.warning, f"  │ Tracking params: {', '.join(found)}")

                navi.cprint(navi.t.highlight, f"  └{'─' * 53}")
            except Exception as e:
                navi.cprint(navi.t.error, f"  [X] {e}")
            navi.pause()

"""Link Tools — Link bypass, expander, and tracker checker."""

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🔍', 'LINK TOOLS')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Link Expander — Resolve shortened URLs")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Link Tracker Check — Check if URL is tracked")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Link Info — Headers + status + redirects")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0': return

        if requests is None:
            kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
            kevbin.pause()
            continue

        if choice in ('1', '2', '3'):
            url = kevbin.input_choice("  URL: ").strip()
            if not url:
                continue
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            try:
                r = requests.get(url, timeout=10, allow_redirects=False, verify=False,
                               headers={'User-Agent': 'Mozilla/5.0'})
                kevbin.cprint(kevbin.t.highlight + kevbin.t.B, f"\n  ┌─ LINK INFO {'─' * 41}")
                kevbin.cprint(kevbin.t.secondary, f"  │ Final URL:   {r.url[:70]}")
                kevbin.cprint(kevbin.t.secondary, f"  │ Status:      {r.status_code}")
                kevbin.cprint(kevbin.t.secondary, f"  │ Server:      {r.headers.get('Server', '?')}")
                kevbin.cprint(kevbin.t.secondary, f"  │ Content-Type:{r.headers.get('Content-Type', '?')}")

                if r.history:
                    kevbin.cprint(kevbin.t.accent, f"  │ Redirects:")
                    for h in r.history:
                        kevbin.cprint(kevbin.t.dim, f"  │   {h.status_code} -> {h.url[:60]}")
                else:
                    kevbin.cprint(kevbin.t.dim, f"  │ No redirects")

                tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'fbclid', 'gclid',
                                  'ref', 'source', 'mc_cid', 'mc_eid']
                found = [p for p in tracking_params if p in r.url.lower()]
                if found:
                    kevbin.cprint(kevbin.t.warning, f"  │ Tracking params: {', '.join(found)}")

                kevbin.cprint(kevbin.t.highlight, f"  └{'─' * 53}")
            except Exception as e:
                kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()


def bypass(kevbin):
    run(navi)


def spoof(kevbin):
    run(navi)


def tracker(kevbin):
    run(navi)

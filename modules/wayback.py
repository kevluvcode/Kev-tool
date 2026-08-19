"""Wayback Machine - Check historical snapshots of a URL."""

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('📜', 'WAYBACK MACHINE')
    kevbin.cprint(kevbin.t.secondary, "  Enter a URL or domain to find archived snapshots.")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    url = kevbin.input_choice("  URL/Domain: ").strip()
    if not url:
        return

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        api_url = 'https://web.archive.org/cdx/search/cdx'
        params = {
            'url': url,
            'output': 'json',
            'limit': 20,
            'collapse': 'digest',
            'fl': 'timestamp,original,statuscode,mimetype'
        }
        r = requests.get(api_url, params=params, timeout=15)
        data = r.json()

        if len(data) <= 1:
            kevbin.cprint(kevbin.t.warning, "\n  [!] No snapshots found.")
            kevbin.pause()
            return

        kevbin.cprint(kevbin.t.highlight, f"\n  +---------------------+------+----------------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Timestamp           | Code | MIME           | Original URL                     |")
        kevbin.cprint(kevbin.t.highlight, f"  +---------------------+------+----------------+----------------------------------+")
        for row in data[1:]:
            ts, orig, code, mime = row[0], row[1], row[2], row[3]
            if len(ts) == 14:
                ts_fmt = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}:{ts[12:14]}"
            else:
                ts_fmt = ts
            kevbin.cprint(kevbin.t.secondary, f"  | {ts_fmt:<19} | {code:<4} | {mime:<14} | {orig[:34]:<34} |")
        kevbin.cprint(kevbin.t.highlight, f"  +---------------------+------+----------------+----------------------------------+")

        kevbin.cprint(kevbin.t.accent, "\n  View: https://web.archive.org/web/*/" + url)
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

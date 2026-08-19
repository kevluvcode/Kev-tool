"""Tor Check — Check if an IP is a Tor exit node."""

try:
    import requests
except ImportError:
    requests = None


def run(navi):
    navi.clear()
    navi.section_header('🔍', 'TOR CHECK')

    if requests is None:
        navi.cprint(navi.t.error, "  [X] pip install requests")
        navi.pause()
        return

    ip = navi.input_choice("  IP to check (or Enter for your IP): ").strip()
    if not ip:
        try:
            r = requests.get('https://ipinfo.io/json', timeout=5)
            ip = r.json().get('ip', '')
            navi.cprint(navi.t.dim, f"  Your IP: {ip}")
        except Exception:
            navi.cprint(navi.t.error, "  [X] Could not detect your IP.")
            navi.pause()
            return

    try:
        r = requests.get(f'https://check.torproject.org/api/ip', timeout=10)
        data = r.json()
        is_tor = data.get('IsTor', False)
        exit_ip = data.get('IP', '?')
        if is_tor:
            navi.cprint(navi.t.warning, f"\n  [!] {exit_ip} IS a Tor exit node")
        else:
            navi.cprint(navi.t.success, f"\n  [✓] {exit_ip} is NOT a Tor exit node")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] {e}")
    navi.pause()

"""Tor Check — Check if an IP is a Tor exit node."""

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🔍', 'TOR CHECK')

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    ip = kevbin.input_choice("  IP to check (or Enter for your IP): ").strip()
    if not ip:
        try:
            r = requests.get('https://ipinfo.io/json', timeout=5)
            ip = r.json().get('ip', '')
            kevbin.cprint(kevbin.t.txt, f"  Your IP: {ip}")
        except Exception:
            kevbin.cprint(kevbin.t.error, "  [X] Could not detect your IP.")
            kevbin.pause()
            return

    try:
        r = requests.get(f'https://check.torproject.org/api/ip?ip={ip}', timeout=10)
        data = r.json()
        is_tor = data.get('IsTor', False)
        checked = data.get('IP', ip)
        if is_tor:
            kevbin.cprint(kevbin.t.warning, f"\n  [!] {checked} IS a Tor exit node")
        else:
            kevbin.cprint(kevbin.t.success, f"\n  [+] {checked} is NOT a Tor exit node")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

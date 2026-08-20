"""ASN Intel - Autonomous System Number lookup."""

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🔢', 'ASN INTEL')
    kevbin.cprint(kevbin.t.secondary, "  Enter an ASN (e.g. 15169) or IP address.")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    query = kevbin.input_choice("  ASN or IP: ").strip()
    if not query:
        return

    if query.isdigit():
        url = f'https://api.bgpview.io/asn/{query}'
    else:
        url = f'https://api.bgpview.io/ip/{query}'

    try:
        r = requests.get(url, timeout=10)
        data = r.json().get('data', {})

        if query.isdigit():
            kevbin.cprint(kevbin.t.highlight, f"\n  +------------------+----------------------------------+")
            kevbin.cprint(kevbin.t.highlight, f"  | Field            | Value                            |")
            kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")
            fields = [
                ('ASN', data.get('asn', '?')),
                ('Name', data.get('name', '?')),
                ('Description', data.get('description', '?')[:34]),
                ('Country', data.get('country_code', '?')),
                ('Type', data.get('type', '?')),
                ('IPv4 Prefixes', len(data.get('ipv4_prefixes', []))),
                ('IPv6 Prefixes', len(data.get('ipv6_prefixes', []))),
                ('Peers', len(data.get('peers', []))),
            ]
            for k, v in fields:
                val = str(v)[:34]
                kevbin.cprint(kevbin.t.secondary, f"  | {k:<16} | {val:<34} |")
            kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")

            if data.get('ipv4_prefixes'):
                kevbin.cprint(kevbin.t.accent, "\n  IPv4 Prefixes:")
                for p in data['ipv4_prefixes'][:10]:
                    kevbin.cprint(kevbin.t.txt, f"    {p.get('prefix','')}  {p.get('description','')}")
        else:
            kevbin.cprint(kevbin.t.highlight, f"\n  +------------------+----------------------------------+")
            kevbin.cprint(kevbin.t.highlight, f"  | Field            | Value                            |")
            kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")
            fields = [
                ('IP', data.get('ip', '?')),
                ('ASN', data.get('asn', {}).get('asn', '?')),
                ('ASN Name', data.get('asn', {}).get('name', '?')[:34]),
                ('Country', data.get('asn', {}).get('country_code', '?')),
                ('Prefixes', len(data.get('prefixes', []))),
            ]
            for k, v in fields:
                val = str(v)[:34]
                kevbin.cprint(kevbin.t.secondary, f"  | {k:<16} | {val:<34} |")
            kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

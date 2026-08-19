"""DNS over HTTPS - Encrypted DNS queries."""

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🔒', 'DNS OVER HTTPS')
    kevbin.cprint(kevbin.t.secondary, "  Query DNS via Cloudflare DoH (encrypted).")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    domain = kevbin.input_choice("  Domain: ").strip()
    if not domain:
        return

    record_type = kevbin.input_choice("  Type (A, AAAA, MX, TXT, NS, CNAME) [A]: ").strip().upper() or 'A'

    try:
        r = requests.get(
            'https://cloudflare-dns.com/dns-query',
            params={'name': domain, 'type': record_type},
            headers={'Accept': 'application/dns-json'},
            timeout=10
        )
        data = r.json()

        kevbin.cprint(kevbin.t.highlight, f"\n  +------+-----+-----+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Type | TTL | Num | Answer                           |")
        kevbin.cprint(kevbin.t.highlight, f"  +------+-----+-----+----------------------------------+")
        for ans in data.get('Answer', []):
            ans_type = ans.get('type', 0)
            type_names = {1: 'A', 28: 'AAAA', 15: 'MX', 16: 'TXT', 2: 'NS', 5: 'CNAME'}
            tname = type_names.get(ans_type, str(ans_type))
            ttl = ans.get('TTL', 0)
            kevbin.cprint(kevbin.t.secondary, f"  | {tname:<4} | {ttl:<3} | {ans.get('data','')[:32]:<32} |")
        kevbin.cprint(kevbin.t.highlight, f"  +------+-----+-----+----------------------------------+")

        if data.get('Status') != 0:
            kevbin.cprint(kevbin.t.warning, f"\n  [!] DNS Status: {data.get('Status')} (NOERROR=0)")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

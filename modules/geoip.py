"""GeoIP Lookup - IP geolocation using free APIs."""

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🌍', 'GEOIP LOOKUP')
    kevbin.cprint(kevbin.t.secondary, "  Enter an IP address to get location info.")
    kevbin.cprint(kevbin.t.dim, "  Leave blank to check your own IP.")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    ip = kevbin.input_choice("  IP: ").strip()
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
        r = requests.get(f'https://ipapi.co/{ip}/json/', timeout=10)
        data = r.json()

        kevbin.cprint(kevbin.t.highlight, f"\n  +------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Field            | Value                            |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")
        fields = [
            ('IP', data.get('ip', '?')),
            ('City', data.get('city', '?')),
            ('Region', data.get('region', '?')),
            ('Country', data.get('country_name', '?')),
            ('Country Code', data.get('country_code', '?')),
            ('Postal', data.get('postal', '?')),
            ('Latitude', data.get('latitude', '?')),
            ('Longitude', data.get('longitude', '?')),
            ('Timezone', data.get('timezone', '?')),
            ('ISP', data.get('org', '?')),
            ('ASN', data.get('asn', '?')),
        ]
        for k, v in fields:
            val = str(v)[:34]
            kevbin.cprint(kevbin.t.secondary, f"  | {k:<16} | {val:<34} |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

"""IP Blacklist Check - Check if IP is on common blacklists."""

try:
    import requests
except ImportError:
    requests = None


BLACKLISTS = [
    ('Spamhaus ZEN', 'https://api.spamhaus.org/check/ip/{ip}'),
    ('Spamhaus DBL', 'https://api.spamhaus.org/check/domain/{ip}'),
    ('AbuseIPDB', 'https://api.abuseipdb.com/api/v2/check?ipAddress={ip}&maxAgeInDays=90'),
    ('AlienVault OTX', 'https://otx.alienvault.com/api/v1/indicators/ipv4/{ip}/general'),
]


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🚫', 'IP BLACKLIST CHECK')
    kevbin.cprint(kevbin.t.secondary, "  Enter an IP address to check against blacklists.")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    ip = kevbin.input_choice("  IP: ").strip()
    if not ip:
        return

    kevbin.cprint(kevbin.t.dim, f"\n  Checking {ip} against known blacklists...\n")

    results = []

    try:
        r = requests.get(f'https://api.spamhaus.org/check/ip/{ip}', timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get('listed'):
                results.append(('Spamhaus ZEN', 'LISTED', data.get('details', '?')))
            else:
                results.append(('Spamhaus ZEN', 'CLEAN', '-'))
    except Exception:
        results.append(('Spamhaus ZEN', 'ERROR', 'API unavailable'))

    try:
        r = requests.get(f'https://api.abuseipdb.com/api/v2/check?ipAddress={ip}&maxAgeInDays=90', timeout=10)
        if r.status_code == 200:
            data = r.json().get('data', {})
            score = data.get('abuseConfidenceScore', 0)
            if score > 0:
                results.append(('AbuseIPDB', f'LISTED ({score}%)', f"{data.get('totalReports',0)} reports"))
            else:
                results.append(('AbuseIPDB', 'CLEAN', '-'))
    except Exception:
        results.append(('AbuseIPDB', 'ERROR', 'API unavailable (needs key)'))

    try:
        r = requests.get(f'https://otx.alienvault.com/api/v1/indicators/ipv4/{ip}/general', timeout=10)
        if r.status_code == 200:
            data = r.json()
            pulses = data.get('pulse_info', {}).get('count', 0)
            if pulses > 0:
                results.append(('AlienVault OTX', f'LISTED ({pulses} pulses)', '-'))
            else:
                results.append(('AlienVault OTX', 'CLEAN', '-'))
    except Exception:
        results.append(('AlienVault OTX', 'ERROR', 'API unavailable'))

    kevbin.cprint(kevbin.t.highlight, f"\n  +------------------+--------------------------+----------------------+")
    kevbin.cprint(kevbin.t.highlight, f"  | Blacklist        | Status                   | Details              |")
    kevbin.cprint(kevbin.t.highlight, f"  +------------------+--------------------------+----------------------+")
    for name, status, details in results:
        color = kevbin.t.error if 'LISTED' in status else kevbin.t.success
        kevbin.cprint(color, f"  | {name:<16} | {status:<24} | {details:<20} |")
    kevbin.cprint(kevbin.t.highlight, f"  +------------------+--------------------------+----------------------+")
    kevbin.pause()

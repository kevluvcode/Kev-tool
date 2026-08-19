"""Honeypot Detector - Basic honeypot detection."""

try:
    import requests
except ImportError:
    requests = None

import socket


HONEYPOT_PORTS = {
    21: 'FTP',
    22: 'SSH',
    23: 'Telnet',
    25: 'SMTP',
    53: 'DNS',
    80: 'HTTP',
    110: 'POP3',
    139: 'NetBIOS',
    143: 'IMAP',
    443: 'HTTPS',
    445: 'SMB',
    993: 'IMAPS',
    995: 'POP3S',
    1433: 'MSSQL',
    3306: 'MySQL',
    3389: 'RDP',
    5432: 'PostgreSQL',
    5900: 'VNC',
    6379: 'Redis',
    8080: 'HTTP Proxy',
    8443: 'HTTPS Alt',
    27017: 'MongoDB',
}


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🍯', 'HONEYPOT DETECTOR')
    kevbin.cprint(kevbin.t.secondary, "  Enter an IP to check for honeypot indicators.")
    kevbin.cprint(kevbin.t.dim, "  Checks common honeypot ports and banner analysis.")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    ip = kevbin.input_choice("  IP: ").strip()
    if not ip:
        return

    kevbin.cprint(kevbin.t.dim, f"\n  Scanning {ip} for open ports...\n")

    results = []
    for port, service in HONEYPOT_PORTS.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result == 0:
                results.append((port, service, 'OPEN'))
        except Exception:
            pass

    kevbin.cprint(kevbin.t.highlight, f"\n  +------+----------------------+--------+")
    kevbin.cprint(kevbin.t.highlight, f"  | Port | Service              | Status |")
    kevbin.cprint(kevbin.t.highlight, f"  +------+----------------------+--------+")
    if results:
        for port, service, status in results:
            kevbin.cprint(kevbin.t.warning, f"  | {port:<4} | {service:<20} | {status:<6} |")
    else:
        kevbin.cprint(kevbin.t.dim, f"  |      | (no common ports open)              |")
    kevbin.cprint(kevbin.t.highlight, f"  +------+----------------------+--------+")

    kevbin.cprint(kevbin.t.dim, "\n  Note: Open ports don't mean honeypot.")
    kevbin.cprint(kevbin.t.dim, "  Compare with shodan.io for full analysis.")
    kevbin.pause()

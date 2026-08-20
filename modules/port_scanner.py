"""Port Scanner — Multi-threaded TCP scanner with service banners + presets."""

import socket
import concurrent.futures
import time

SERVICE_DB = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 111: 'RPCBind', 135: 'MSRPC',
    139: 'NetBIOS', 143: 'IMAP', 443: 'HTTPS', 445: 'SMB',
    465: 'SMTPS', 514: 'Syslog', 554: 'RTSP', 587: 'SMTP-sub',
    631: 'IPP', 993: 'IMAPS', 995: 'POP3S', 1080: 'SOCKS',
    1433: 'MSSQL', 1521: 'Oracle', 1723: 'PPTP', 1883: 'MQTT',
    2049: 'NFS', 2375: 'Docker', 3306: 'MySQL', 3389: 'RDP',
    5432: 'PostgreSQL', 5601: 'Kibana', 5900: 'VNC', 6379: 'Redis',
    6443: 'K8s-API', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt',
    8888: 'HTTP-Alt', 9000: 'PHP-FPM', 9200: 'Elastic', 9418: 'Git',
    11211: 'Memcached', 27017: 'MongoDB', 50000: 'SAP',
}

PRESETS = {
    '1': ('top 20', [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 3306, 3389, 5432, 8080, 8443, 3389]),
    '2': ('web', [80, 443, 8080, 8443, 8888, 9000, 9200, 3000, 4000, 5000, 8000, 8081, 9090]),
    '3': ('database', [3306, 5432, 1433, 1521, 27017, 6379, 9200, 5984, 7474, 8529]),
    '4': ('mail', [25, 110, 143, 465, 587, 993, 995]),
    '5': ('full common', list(range(1, 1025))),
    '6': ('windows', [53, 88, 135, 139, 389, 445, 636, 1433, 3268, 3389, 5985, 5986]),
}


def _scan_port(host, port, timeout=1):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            if result == 0:
                svc = SERVICE_DB.get(port, 'unknown')
                banner = ''
                try:
                    s.settimeout(2)
                    s.send(b'HEAD / HTTP/1.0\r\nHost: ' + host.encode() + b'\r\n\r\n')
                    banner = s.recv(256).decode('utf-8', errors='ignore').strip()[:80]
                except Exception:
                    try:
                        s.send(b'\r\n')
                        banner = s.recv(256).decode('utf-8', errors='ignore').strip()[:80]
                    except Exception:
                        pass
                return port, True, svc, banner
            return port, False, '', ''
    except Exception:
        return port, False, '', ''


def _grab_banner(host, port, timeout=2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.send(b'\r\n')
        data = s.recv(1024).decode('utf-8', errors='ignore').strip()
        s.close()
        return data[:200]
    except Exception:
        return ''


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🔍', 'PORT SCANNER')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Preset scan")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Custom range scan")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Single port check")
        kevbin.cprint(kevbin.t.secondary, "  [4]  Banner grab")
        kevbin.cprint(kevbin.t.secondary, "  [5]  Port service lookup")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0':
            return

        if choice == '5':
            q = kevbin.input_choice("  Port number: ").strip()
            if q.isdigit():
                port = int(q)
                svc = SERVICE_DB.get(port, 'unknown')
                kevbin.cprint(kevbin.t.accent, f"\n  Port {port}: {svc}")
            kevbin.pause()
            continue

        if choice in ('1', '2', '3', '4'):
            host = kevbin.input_choice("  Target: ").strip()
            if not host:
                continue
            try:
                socket.gethostbyname(host)
            except socket.gaierror:
                kevbin.cprint(kevbin.t.error, f"  [X] Cannot resolve: {host}")
                kevbin.pause()
                continue

        if choice == '1':
            kevbin.cprint(kevbin.t.dim, "  Presets:")
            for k, (name, ports) in PRESETS.items():
                kevbin.cprint(kevbin.t.txt, f"    [{k}] {name} ({len(ports)} ports)")
            p = kevbin.input_choice("  Preset [1]: ").strip() or '1'
            preset = PRESETS.get(p, PRESETS['1'])
            ports = preset[1]
            timeout_s = kevbin.input_choice("  Timeout (s) [1]: ").strip() or '1'
            try:
                timeout_s = float(timeout_s)
            except ValueError:
                timeout_s = 1
            _do_scan(kevbin, host, ports, timeout_s)

        elif choice == '2':
            port_range = kevbin.input_choice("  Port range (e.g. 1-1024): ").strip() or '1-1024'
            try:
                if '-' in port_range:
                    s, e = port_range.split('-', 1)
                    ports = range(int(s), int(e) + 1)
                else:
                    ports = [int(port_range)]
            except ValueError:
                kevbin.cprint(kevbin.t.error, "  [X] Invalid range.")
                kevbin.pause()
                continue
            threads = kevbin.input_choice("  Threads [200]: ").strip() or '200'
            try:
                threads = max(10, min(500, int(threads)))
            except ValueError:
                threads = 200
            _do_scan(kevbin, host, ports, 1, threads)

        elif choice == '3':
            port = kevbin.input_choice("  Port: ").strip()
            if port.isdigit():
                port, is_open, svc, banner = _scan_port(host, int(port), 2)
                if is_open:
                    kevbin.cprint(kevbin.t.success, f"\n  Port {port}: OPEN ({svc})")
                    if banner:
                        kevbin.cprint(kevbin.t.txt, f"  Banner: {banner[:80]}")
                else:
                    kevbin.cprint(kevbin.t.warning, f"\n  Port {port}: CLOSED/FILTERED")
            kevbin.pause()

        elif choice == '4':
            port = kevbin.input_choice("  Port for banner: ").strip()
            if port.isdigit():
                kevbin.cprint(kevbin.t.dim, f"  Grabbing banner from {host}:{port}...")
                banner = _grab_banner(host, int(port))
                if banner:
                    kevbin.cprint(kevbin.t.accent, f"\n  Banner:\n{banner}")
                else:
                    kevbin.cprint(kevbin.t.warning, "  [!] No banner received.")
            kevbin.pause()


def _do_scan(kevbin, host, ports, timeout=1, threads=200):
    kevbin.cprint(kevbin.t.dim, f"  Scanning {host}...")
    start = time.time()
    open_ports = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        futures = {ex.submit(_scan_port, host, p, timeout): p for p in ports}
        for f in concurrent.futures.as_completed(futures):
            port, is_open, svc, banner = f.result()
            if is_open:
                open_ports.append((port, svc, banner))

    elapsed = time.time() - start
    open_ports.sort(key=lambda x: x[0])

    if open_ports:
        kevbin.cprint(kevbin.t.success, f"\n  [+] Open ports on {host}:\n")
        for port, svc, banner in open_ports:
            kevbin.cprint(kevbin.t.accent, f"    {port:<6} {svc:<16} {banner[:50]}")
    else:
        kevbin.cprint(kevbin.t.warning, f"\n  [!] No open ports found.")

    kevbin.cprint(kevbin.t.dim, f"\n  Scanned in {elapsed:.2f}s")
    kevbin.pause()

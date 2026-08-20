"""Network Scanner — ARP scan, port sweep, host discovery."""

import socket
import struct
import os
import sys
import time
import threading
import concurrent.futures


def _get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _get_network_range(ip):
    parts = ip.split('.')
    return f"{parts[0]}.{parts[1]}.{parts[2]}"


def _ping_host(ip, timeout=1):
    try:
        host = socket.gethostbyname(ip)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((host, 80))
        s.close()
        if result == 0:
            return ip, True
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.settimeout(timeout)
        result2 = s2.connect_ex((host, 443))
        s2.close()
        if result2 == 0:
            return ip, True
        s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s3.settimeout(timeout)
        result3 = s3.connect_ex((host, 22))
        s3.close()
        return ip, result3 == 0
    except Exception:
        return ip, False


def _get_hostname(ip, timeout=1):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ''


def _grab_mac_arp(ip):
    if os.name == 'nt':
        try:
            output = os.popen(f'arp -a {ip}').read()
            for line in output.splitlines():
                if ip in line:
                    parts = line.split()
                    for p in parts:
                        if '-' in p and len(p) == 17:
                            return p.replace('-', ':')
        except Exception:
            pass
    else:
        try:
            output = os.popen(f'arp -n {ip}').read()
            for line in output.splitlines():
                if ip in line:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if ':' in p and len(p) == 17:
                            return p
        except Exception:
            pass
    return ''


def scan_network(kevbin):
    local_ip = _get_local_ip()
    base = _get_network_range(local_ip)
    kevbin.cprint(kevbin.t.dim, f"  Local IP: {local_ip}")
    kevbin.cprint(kevbin.t.dim, f"  Scanning {base}.0/24...\n")

    prefix = kevbin.input_choice(f"  Network prefix [{base}.]: ").strip() or base

    start = time.time()
    alive = []
    lock = threading.Lock()

    def _sweep(ip):
        _, is_up = _ping_host(ip)
        if is_up:
            with lock:
                alive.append(ip)

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
        futures = []
        for i in range(1, 255):
            ip = f"{prefix}.{i}"
            futures.append(ex.submit(_sweep, ip))
        for f in concurrent.futures.as_completed(futures):
            pass

    elapsed = time.time() - start
    alive.sort(key=lambda x: int(x.split('.')[-1]))

    if alive:
        kevbin.cprint(kevbin.t.success, f"\n  [✓] {len(alive)} hosts alive ({elapsed:.1f}s):\n")
        rows = [["#", "IP Address", "Hostname", "MAC"]]
        for i, ip in enumerate(alive, 1):
            hostname = _get_hostname(ip)
            mac = _grab_mac_arp(ip)
            rows.append([str(i), ip, hostname[:30] or '-', mac or '-'])
        kevbin.box_table(headers=rows[0], rows=rows[1:], title="Live Hosts")
    else:
        kevbin.cprint(kevbin.t.warning, "\n  [!] No hosts found.")

    kevbin.pause()


def quick_scan(kevbin):
    local_ip = _get_local_ip()
    kevbin.cprint(kevbin.t.dim, f"  Quick scan from {local_ip}")

    target = kevbin.input_choice("  Target IP or hostname: ").strip()
    if not target:
        return

    try:
        target_ip = socket.gethostbyname(target)
    except Exception:
        kevbin.cprint(kevbin.t.error, "  [X] Cannot resolve host.")
        kevbin.pause()
        return

    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995,
                    1433, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 8888, 9200, 27017]

    kevbin.cprint(kevbin.t.dim, f"  Scanning {len(common_ports)} common ports on {target_ip}...")

    open_ports = []

    def _check(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            r = s.connect_ex((target_ip, port))
            if r == 0:
                service = _service_name(port)
                banner = ''
                try:
                    s.send(b'HEAD / HTTP/1.0\r\nHost: ' + target.encode() + b'\r\n\r\n')
                    banner = s.recv(256).decode('utf-8', errors='ignore').strip()[:60]
                except Exception:
                    pass
                open_ports.append((port, service, banner))
            s.close()
        except Exception:
            pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
        ex.map(_check, common_ports)

    open_ports.sort(key=lambda x: x[0])

    if open_ports:
        kevbin.cprint(kevbin.t.success, f"\n  [✓] Open ports on {target} ({target_ip}):\n")
        for port, service, banner in open_ports:
            kevbin.cprint(kevbin.t.accent, f"    Port {port:<6} {service:<20} {banner[:40]}")
    else:
        kevbin.cprint(kevbin.t.warning, "\n  [!] No common ports open.")

    kevbin.pause()


def port_sweep(kevbin):
    target = kevbin.input_choice("  Target IP/hostname: ").strip()
    if not target:
        return

    try:
        target_ip = socket.gethostbyname(target)
    except Exception:
        kevbin.cprint(kevbin.t.error, "  [X] Cannot resolve.")
        kevbin.pause()
        return

    port_range = kevbin.input_choice("  Port range [1-1000]: ").strip() or '1-1000'
    try:
        if '-' in port_range:
            s, e = port_range.split('-', 1)
            ports = list(range(int(s), int(e) + 1))
        else:
            ports = [int(port_range)]
    except ValueError:
        kevbin.cprint(kevbin.t.error, "  [X] Invalid range.")
        kevbin.pause()
        return

    threads_n = kevbin.input_choice("  Threads [200]: ").strip() or '200'
    try:
        threads_n = max(10, min(500, int(threads_n)))
    except ValueError:
        threads_n = 200

    kevbin.cprint(kevbin.t.dim, f"  Scanning {len(ports)} ports...")
    start = time.time()
    open_ports = []
    lock = threading.Lock()

    def _scan(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((target_ip, port)) == 0:
                with lock:
                    open_ports.append(port)
            s.close()
        except Exception:
            pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads_n) as ex:
        ex.map(_scan, ports)

    elapsed = time.time() - start
    open_ports.sort()

    if open_ports:
        kevbin.cprint(kevbin.t.success, f"\n  [✓] {len(open_ports)} open ports ({elapsed:.1f}s):\n")
        for p in open_ports:
            svc = _service_name(p)
            kevbin.cprint(kevbin.t.accent, f"    {p:<6} {svc}")
    else:
        kevbin.cprint(kevbin.t.warning, f"\n  [!] No open ports ({elapsed:.1f}s).")

    kevbin.pause()


def _service_name(port):
    services = {
        21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
        80: 'HTTP', 110: 'POP3', 135: 'MSRPC', 139: 'NetBIOS', 143: 'IMAP',
        443: 'HTTPS', 445: 'SMB', 993: 'IMAPS', 995: 'POP3S',
        1433: 'MSSQL', 1521: 'Oracle', 3306: 'MySQL', 3389: 'RDP',
        5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis',
        8080: 'HTTP-Alt', 8443: 'HTTPS-Alt', 9200: 'Elastic', 27017: 'Mongo',
    }
    return services.get(port, 'unknown')


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('📡', 'NETWORK SCANNER')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Network Sweep (find live hosts)")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Quick Scan (common ports)")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Full Port Sweep")
        kevbin.cprint(kevbin.t.secondary, "  [4]  My Local IP Info")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0':
            return
        if choice == '1':
            scan_network(kevbin)
        elif choice == '2':
            quick_scan(kevbin)
        elif choice == '3':
            port_sweep(kevbin)
        elif choice == '4':
            local_ip = _get_local_ip()
            hostname = socket.gethostname()
            try:
                ext_ip = socket.gethostbyname(socket.gethostname())
            except Exception:
                ext_ip = '?'
            kevbin.cprint(kevbin.t.accent, f"\n  Hostname:   {hostname}")
            kevbin.cprint(kevbin.t.accent, f"  Local IP:   {local_ip}")
            kevbin.cprint(kevbin.t.accent, f"  Network:    {_get_network_range(local_ip)}.0/24")
            kevbin.pause()

"""Port Scanner — TCP port scanner with banner grabbing."""

import socket
import concurrent.futures
import time


def _scan_port(host, port, timeout=1, grab_banner=False):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            if result == 0:
                banner = ''
                if grab_banner:
                    try:
                        s.send(b'HEAD / HTTP/1.0\r\nHost: ' + host.encode() + b'\r\n\r\n')
                        banner = s.recv(256).decode('utf-8', errors='ignore').strip()[:80]
                    except Exception:
                        pass
                return port, True, banner
            return port, False, ''
    except Exception:
        return port, False, ''


def run(navi):
    navi.clear()
    navi.section_header('🔍', 'PORT SCANNER')

    host = navi.input_choice("  Target: ").strip()
    if not host:
        return

    try:
        socket.gethostbyname(host)
    except socket.gaierror:
        navi.cprint(navi.t.error, f"  [X] Could not resolve: {host}")
        navi.pause()
        return

    port_range = navi.input_choice("  Port range (default 1-1024): ").strip() or '1-1024'
    try:
        if '-' in port_range:
            s, e = port_range.split('-', 1)
            ports = range(int(s), int(e) + 1)
        else:
            ports = [int(port_range)]
    except ValueError:
        navi.cprint(navi.t.error, "  [X] Invalid range.")
        navi.pause()
        return

    grab = navi.input_choice("  Grab banners? (y/n): ").lower() == 'y'

    navi.cprint(navi.t.dim, f"  Scanning {host}...")
    start = time.time()
    open_ports = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as ex:
        futures = {ex.submit(_scan_port, host, p, 1, grab): p for p in ports}
        for f in concurrent.futures.as_completed(futures):
            port, is_open, banner = f.result()
            if is_open:
                open_ports.append((port, banner))

    elapsed = time.time() - start
    open_ports.sort(key=lambda x: x[0])

    if open_ports:
        navi.cprint(navi.t.success, f"\n  [✓] Open ports on {host}:\n")
        for p, banner in open_ports:
            navi.cprint(navi.t.accent, f"    Port {p:5d}  OPEN")
            if banner:
                navi.cprint(navi.t.dim, f"           Banner: {banner[:60]}")
    else:
        navi.cprint(navi.t.warning, f"\n  [!] No open ports found.")

    navi.cprint(navi.t.dim, f"\n  Scanned {len(list(ports))} ports in {elapsed:.2f}s")
    navi.pause()

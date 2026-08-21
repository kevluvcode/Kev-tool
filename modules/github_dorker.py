"""GitHub Dorker — Search GitHub for exposed secrets and sensitive files."""

import os
import sys
import time
import json
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

DORKS = {
    "Passwords": '"password" filename:config',
    "API Keys": '"api_key" OR "apikey" OR "api-key" filename:.env',
    "AWS Keys": '"AKIA" filename:.env OR filename:config',
    "Private Keys": '"BEGIN RSA PRIVATE KEY" OR "BEGIN OPENSSH PRIVATE KEY"',
    "Database URLs": '"mongodb://" OR "mysql://" OR "postgres://" filename:.env',
    "GitHub Tokens": '"ghp_" OR "github_pat_"',
    "Discord Tokens": '"discord" "token" filename:.env',
    "Firebase": '"firebaseio.com" filename:.json',
    "Heroku": '"herokuapp.com" password',
    "SSH Keys": 'filename:id_rsa OR filename:id_dsa',
    "Env Files": 'filename:.env password',
    "Config Files": 'filename:config.php OR filename:config.json password',
    "SQL Dumps": 'filename:.sql extension:sql',
    "Logs": 'filename:debug.log OR filename:error.log',
    "Docker": 'filename:docker-compose.yml password',
    "Kubernetes": 'filename:kubeconfig',
    "Backup Files": 'filename:backup.sql OR filename:backup.zip',
    "JWT Secrets": '"jwt_secret" OR "JWT_SECRET" filename:.env',
    "Webhook URLs": '"discord.com/api/webhooks" filename:.env OR filename:config',
    "Payment Keys": '"sk_live" OR "pk_live" OR "sk_test"',
}

def search_github(query, token=None, page=1):
    url = f"https://api.github.com/search/code?q={urllib.request.quote(query)}&per_page=10&page={page}"
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "KevTool-OSINT"}
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return {"error": "Rate limited — add a GitHub token or wait"}
        return {"error": f"HTTP {e.code}"}
    except Exception as e:
        return {"error": str(e)}

def run(kevbin=None):
    while True:
        clear()
        cprint("  \033[93m\u2554" + "\u2550"*50 + "\u2557")
        cprint("  \033[93m\u2551       GITHUB DORKER                       \u2551")
        cprint("  \033[93m\u255a" + "\u2550"*50 + "\u255d")
        print()
        cprint("  \033[97m[1]  Run Predefined Dork\033[0m")
        cprint("  \033[97m[2]  Custom Dork Query\033[0m")
        cprint("  \033[97m[3]  Scan Target Repo\033[0m")
        cprint("  \033[97m[4]  List All Dorks\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0': return
        elif choice == '4':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  PREDEFINED DORKS\033[0m")
            cprint("  \033[93m\u2550"*54)
            for i, (name, query) in enumerate(DORKS.items(), 1):
                cprint(f"  \033[97m[{i:2}]  {name:20}\033[0m \033[90m{query[:45]}\033[0m")
        elif choice == '1':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  SELECT DORK\033[0m")
            cprint("  \033[93m\u2550"*54)
            items = list(DORKS.items())
            for i, (name, _) in enumerate(items, 1):
                cprint(f"  \033[97m[{i:2}]  {name}\033[0m")
            print()
            sel = prompt(f"  \033[96mSelect (1-{len(items)}): \033[0m").strip()
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(items):
                    name, query = items[idx]
                    cprint(f"  \033[36m[*] Running: {name}\033[0m")
                    cprint(f"  \033[90m  Query: {query}\033[0m\n")
                    result = search_github(query)
                    if "error" in result:
                        cprint(f"  \033[91m[X] {result['error']}\033[0m")
                    else:
                        items_r = result.get("items", [])
                        total = result.get("total_count", 0)
                        cprint(f"  \033[92m  Found: {total} results\033[0m\n")
                        for item in items_r[:10]:
                            repo = item.get("repository", {}).get("full_name", "?")
                            path = item.get("path", "?")
                            cprint(f"  \033[97m  {repo}\033[0m")
                            cprint(f"  \033[90m    {path}\033[0m")
                            cprint(f"  \033[90m    {item.get('html_url', '')}\033[0m")
                else:
                    cprint("  \033[91m[X] Invalid\033[0m")
            except: cprint("  \033[91m[X] Invalid input\033[0m")
        elif choice == '2':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  CUSTOM DORK\033[0m")
            cprint("  \033[93m\u2550"*54)
            query = prompt("  \033[96mGitHub search query: \033[0m").strip()
            if not query: continue
            cprint(f"  \033[36m[*] Searching: {query}\033[0m\n")
            result = search_github(query)
            if "error" in result:
                cprint(f"  \033[91m[X] {result['error']}\033[0m")
            else:
                items_r = result.get("items", [])
                total = result.get("total_count", 0)
                cprint(f"  \033[92m  Found: {total} results\033[0m\n")
                for item in items_r[:10]:
                    repo = item.get("repository", {}).get("full_name", "?")
                    path = item.get("path", "?")
                    cprint(f"  \033[97m  {repo}\033[0m")
                    cprint(f"  \033[90m    {path}\033[0m")
        elif choice == '3':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  SCAN TARGET REPO\033[0m")
            cprint("  \033[93m\u2550"*54)
            repo = prompt("  \033[96mRepo (owner/name): \033[0m").strip()
            if not repo: continue
            cprint(f"  \033[36m[*] Scanning {repo}...\033[0m\n")
            out_file = f"dork_{repo.replace('/','_')}_{int(time.time())}.txt"
            findings = 0
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(f"GitHub Dork Report: {repo}\n{'='*50}\n\n")
                for name, dork_query in DORKS.items():
                    query = f"repo:{repo} {dork_query}"
                    result = search_github(query)
                    if "error" in result:
                        continue
                    items_r = result.get("items", [])
                    total = result.get("total_count", 0)
                    if total > 0:
                        f.write(f"\n[{name}] — {total} results\n")
                        cprint(f"  \033[93m[{name}]\033[0m {total} results")
                        for item in items_r[:5]:
                            path = item.get("path", "?")
                            url = item.get("html_url", "")
                            f.write(f"  {path}\n  {url}\n")
                            findings += 1
                    time.sleep(0.5)
            cprint(f"\n  \033[92m[X] Report: {out_file} ({findings} findings)\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m"); time.sleep(0.5)
        pause()

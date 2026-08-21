"""Recovery Tool — Browser data extraction (cookies, passwords, tokens)."""

import os
import sys
import time
import json
import base64
import sqlite3
import shutil
import glob
from pathlib import Path

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

BROWSERS = {
    'Chrome': {
        'base': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data'),
        'profiles': ['Default', 'Profile 1', 'Profile 2', 'Profile 3'],
        'cookies': 'Cookies', 'passwords': 'Login Data', 'tokens': 'Local State',
    },
    'Edge': {
        'base': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data'),
        'profiles': ['Default', 'Profile 1', 'Profile 2'],
        'cookies': 'Cookies', 'passwords': 'Login Data', 'tokens': 'Local State',
    },
    'Brave': {
        'base': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data'),
        'profiles': ['Default', 'Profile 1'],
        'cookies': 'Cookies', 'passwords': 'Login Data', 'tokens': 'Local State',
    },
    'Opera': {
        'base': os.path.join(os.environ.get('APPDATA', ''), 'Opera Software', 'Opera Stable'),
        'profiles': ['.'],
        'cookies': 'Cookies', 'passwords': 'Login Data', 'tokens': 'Local State',
    },
    'Vivaldi': {
        'base': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Vivaldi', 'User Data'),
        'profiles': ['Default'],
        'cookies': 'Cookies', 'passwords': 'Login Data', 'tokens': 'Local State',
    },
}

def _dump_browser(name, config, out_dir):
    results = {"browser": name, "profiles": []}
    if not os.path.isdir(config['base']):
        return results, f"  \033[91m[X] {name} not found\033[0m"
    for profile in config['profiles']:
        prof_dir = os.path.join(config['base'], profile)
        if not os.path.isdir(prof_dir):
            continue
        prof_data = {"name": profile, "cookies": 0, "passwords": 0, "has_token_file": False}
        cookie_db = os.path.join(prof_dir, config['cookies'])
        if os.path.isfile(cookie_db):
            try:
                tmp = os.path.join(out_dir, f"{name}_{profile}_cookies.db")
                shutil.copy2(cookie_db, tmp)
                conn = sqlite3.connect(tmp)
                prof_data["cookies"] = conn.execute("SELECT COUNT(*) FROM cookies").fetchone()[0]
                conn.close()
            except Exception:
                pass
        pw_db = os.path.join(prof_dir, config['passwords'])
        if os.path.isfile(pw_db):
            try:
                tmp = os.path.join(out_dir, f"{name}_{profile}_passwords.db")
                shutil.copy2(pw_db, tmp)
                conn = sqlite3.connect(tmp)
                prof_data["passwords"] = conn.execute("SELECT COUNT(*) FROM logins").fetchone()[0]
                conn.close()
            except Exception:
                pass
        local_state = os.path.join(config['base'], config['tokens'])
        if os.path.isfile(local_state):
            prof_data["has_token_file"] = True
            try:
                shutil.copy2(local_state, os.path.join(out_dir, f"{name}_{profile}_localstate.json"))
            except Exception:
                pass
        results["profiles"].append(prof_data)
    return results, ""

def run(kevbin=None):
    while True:
        clear()
        cprint("  \033[93m\u2554" + "\u2550"*44 + "\u2557")
        cprint("  \033[93m\u2551       RECOVERY TOOL                       \u2551")
        cprint("  \033[93m\u255a" + "\u2550"*44 + "\u255d")
        cprint("  \033[91m[!] Own machine / authorized only\033[0m")
        print()
        cprint("  \033[97m[1]  Extract All Browser Data\033[0m")
        cprint("  \033[97m[2]  Extract Cookies Only\033[0m")
        cprint("  \033[97m[3]  Extract Passwords DB\033[0m")
        cprint("  \033[97m[4]  Extract Discord Tokens\033[0m")
        cprint("  \033[97m[5]  List Detected Browsers\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice in ('1', '2', '3', '4'):
            clear()
            out_dir = f"recovery_{int(time.time())}"
            os.makedirs(out_dir, exist_ok=True)
            cprint(f"\n  \033[36m[*] Extracting to {out_dir}/\033[0m\n")
            total_cookies = 0
            total_passwords = 0
            for bname, config in BROWSERS.items():
                cprint(f"  \033[97m[*] {bname}...\033[0m", end="")
                result, err = _dump_browser(bname, config, out_dir)
                if err:
                    cprint(f" {err}")
                    continue
                if result['profiles']:
                    for p in result['profiles']:
                        total_cookies += p['cookies']
                        total_passwords += p['passwords']
                        cprint(f" \033[92m{p['name']}\033[0m: {p['cookies']} cookies, {p['passwords']} passwords")
                else:
                    cprint(" \033[90mno profiles\033[0m")
            if choice == '4':
                cprint(f"\n  \033[36m[*] Searching for Discord tokens...\033[0m")
                discord_paths = [
                    os.path.join(os.environ.get('APPDATA', ''), 'discord', 'Local Storage', 'leveldb'),
                    os.path.join(os.environ.get('APPDATA', ''), 'discordcanary', 'Local Storage', 'leveldb'),
                    os.path.join(os.environ.get('APPDATA', ''), 'Lightcord', 'Local Storage', 'leveldb'),
                    os.path.join(os.environ.get('APPDATA', ''), 'discordptb', 'Local Storage', 'leveldb'),
                ]
                tokens_found = 0
                for dp in discord_paths:
                    if not os.path.isdir(dp):
                        continue
                    for fn in os.listdir(dp):
                        if not fn.endswith('.log') and not fn.endswith('.ldb'):
                            continue
                        fp = os.path.join(dp, fn)
                        try:
                            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            import re
                            matches = re.findall(r'[MN][A-Za-z\d]{23,}\.[\w-]{6,}\.[\w-]{27,}', content)
                            for token in set(matches):
                                tokens_found += 1
                                cprint(f"  \033[92m[TOKEN]\033[0m {token[:50]}...")
                                with open(os.path.join(out_dir, 'discord_tokens.txt'), 'a') as tf:
                                    tf.write(token + '\n')
                        except Exception:
                            pass
                if tokens_found == 0:
                    cprint("  \033[93m[X] No tokens found (Discord may be using encryption)\033[0m")
                else:
                    cprint(f"  \033[92m[X] Found {tokens_found} token(s) -> {out_dir}/discord_tokens.txt\033[0m")
            cprint(f"\n  \033[92m[X] Extraction complete: {out_dir}/\033[0m")
            cprint(f"  \033[97m  Cookies: {total_cookies:,} | Passwords: {total_passwords:,}\033[0m")
        elif choice == '5':
            clear()
            cprint("  \033[93m┌── DETECTED BROWSERS ───────────────────────┐\033[0m")
            for bname, config in BROWSERS.items():
                if os.path.isdir(config['base']):
                    cprint(f"  \033[92m[+]\033[0m \033[97m{bname}\033[0m \033[90m{config['base']}\033[0m")
                else:
                    cprint(f"  \033[91m[-]\033[0m \033[90m{bname} (not found)\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

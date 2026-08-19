#!/usr/bin/env python3
"""KevTool — KevBin Educational Security & Utilities Suite"""

import os
import sys
import json
import time
import importlib
import zipfile
import io

os.system('')

VERSION = "1.0.0"
AUTHOR = "KevBin"
GITHUB_REPO = "kevluvcode/Kev-tool"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"
GITHUB_ZIP = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/main.zip"

BANNER = r"""
 ##   ###  ########  ##:  :##  ######:    ######   ###   ##
 ##   ##   ########  ##    ##  #######    ######   ###   ##
 ## :##:   ##        :##  ##:  ##   :##     ##     ###:  ##
 ##.##:    ##        :##  ##:  ##    ##     ##     ####  ##
 #####     ##         ## .##   ##   :##     ##     ##:#: ##
 #####     #######    ##::##   #######.     ##     ## ## ##
 #####:    #######    ##::##   #######.     ##     ## ## ##
 ##::##    ##         :####:   ##   :##     ##     ## :#:##
 ##  ##    ##         .####.   ##    ##     ##     ##  ####
 ##  :##   ##          ####    ##   :##     ##     ##  :###
 ##   ##   ########    ####    ########   ######   ##   ###
 ##   :##  ########     ##     ######     ######   ##   ###
"""


def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception:
        pass


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
MODULES_DIR = os.path.join(BASE_DIR, 'modules')
SETTINGS_PATH = os.path.join(CONFIG_DIR, 'settings.json')
THEMES_PATH = os.path.join(CONFIG_DIR, 'themes.json')


class Theme:
    def __init__(self, data=None):
        d = data or {}
        self.primary = d.get('primary', '\033[38;2;88;101;242m')
        self.secondary = d.get('secondary', '\033[38;2;185;187;190m')
        self.accent = d.get('accent', '\033[38;2;87;242;134m')
        self.highlight = d.get('highlight', '\033[38;2;255;255;255m')
        self.dim = d.get('dim', '\033[38;2;120;123;130m')
        self.error = d.get('error', '\033[38;2;237;66;69m')
        self.success = d.get('success', '\033[38;2;87;242;134m')
        self.warning = d.get('warning', '\033[38;2;254;231;92m')
        self.banner = d.get('banner', '\033[38;2;88;101;242m')
        self.border = d.get('border', '\033[38;2;60;63;70m')
        self.R = d.get('reset', '\033[0m')
        self.B = d.get('bold', '\033[1m')


class KevTool:
    def __init__(self):
        self.settings = load_json(SETTINGS_PATH)
        self.themes = load_json(THEMES_PATH)
        theme_name = self.settings.get('current_theme', 'modern')
        theme_data = self.themes.get(theme_name, self.themes.get('modern', {}))
        self.t = Theme(theme_data)
        self.theme_name = theme_name

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def cprint(self, color, text, end='\n'):
        sys.stdout.write(f"{color}{text}{self.t.R}{end}")
        sys.stdout.flush()

    def line(self, char='─', width=60):
        self.cprint(self.t.border, '  ' + char * width)

    def section_header(self, icon, title):
        self.line()
        self.cprint(self.t.B + self.t.primary, f"  {icon}  {title}")
        self.line()

    def input_choice(self, prompt='  > '):
        try:
            return input(f"{self.t.primary}{prompt}{self.t.R}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return ''

    def pause(self):
        self.cprint(self.t.dim, '\n  Press Enter to continue...')
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            print()

    # ─── LOADING SCREEN ────────────────────────────────────────────

    def loading_screen(self):
        self.clear()
        lines = BANNER.split('\n')
        total_lines = len(lines)
        bar_width = 40

        for i, line in enumerate(lines):
            self.clear()
            for j in range(i + 1):
                self.cprint(self.t.banner, lines[j])
            progress = (i + 1) / total_lines
            filled = int(bar_width * progress)
            bar = '█' * filled + '░' * (bar_width - filled)
            pct = int(progress * 100)
            self.cprint(self.t.dim, '')
            self.cprint(self.t.primary, f"  [{bar}] {pct}%")
            self.cprint(self.t.dim, f"  Loading modules...")
            time.sleep(0.08)

        self.clear()
        for line in lines:
            self.cprint(self.t.banner, line)
        self.cprint(self.t.dim, '')
        self.cprint(self.t.primary, f"  [{'█' * bar_width}] 100%")
        self.cprint(self.t.accent, f"  {self.t.B}Welcome to KevTool v{VERSION} — {AUTHOR}")
        self.cprint(self.t.dim, f"  Educational Security & Utilities Suite")
        time.sleep(0.6)

    # ─── AUTO-UPDATE ────────────────────────────────────────────────

    def check_update(self):
        try:
            import requests
            resp = requests.get(f"{GITHUB_API}/commits?sha=main&per_page=1", timeout=10)
            if resp.status_code != 200:
                return
            commits = resp.json()
            if not commits:
                return
            remote_date = commits[0].get('commit', {}).get('committer', {}).get('date', '')
            local_version = self.settings.get('version', VERSION)

            self.cprint(self.t.dim, f"  Checking for updates...")
            self.cprint(self.t.dim, f"  Latest commit: {remote_date}")

            choice = self.input_choice("  Download latest from GitHub? (y/n): ").lower()
            if choice == 'y':
                self.cprint(self.t.dim, "  Downloading repo zip...")
                r = requests.get(GITHUB_ZIP, timeout=60, stream=True)
                if r.status_code == 200:
                    out_path = os.path.join(BASE_DIR, "KevTool_latest.zip")
                    total = 0
                    with open(out_path, 'wb') as f:
                        for chunk in r.iter_content(8192):
                            f.write(chunk)
                            total += len(chunk)
                    self.cprint(self.t.success, f"  [✓] Saved: {out_path} ({total:,} bytes)")
                    self.cprint(self.t.dim, "  Extract and replace files to update.")
                    self.cprint(self.t.dim, f"  Or run: python -c \"import zipfile; zipfile.ZipFile('{out_path}').extractall('.')\"")
                else:
                    self.cprint(self.t.error, f"  [X] Download failed (HTTP {r.status_code})")
                self.pause()
        except ImportError:
            self.cprint(self.t.error, "  [X] 'requests' not installed.")
            self.pause()
        except Exception as e:
            self.cprint(self.t.dim, f"  Update check skipped: {e}")

    # ─── MODULE RUNNER ──────────────────────────────────────────────

    def run_module(self, module_name, func_name='run'):
        try:
            spec = importlib.util.spec_from_file_location(
                module_name, os.path.join(MODULES_DIR, f'{module_name}.py')
            )
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            func = getattr(mod, func_name, None)
            if func:
                func(self)
            else:
                self.cprint(self.t.error, f"  [X] Module '{module_name}' has no '{func_name}' function.")
                self.pause()
        except Exception as e:
            self.cprint(self.t.error, f"  [X] Error: {e}")
            self.pause()

    # ─── MENUS ──────────────────────────────────────────────────────

    def main_menu(self):
        while True:
            self.clear()
            for line in BANNER.split('\n'):
                self.cprint(self.t.banner, line)
            self.cprint(self.t.dim, f"  v{VERSION} by {AUTHOR} — Educational Security Suite | Theme: {self.theme_name}")
            self.line()
            self.cprint(self.t.highlight + self.t.B, "  MAIN MENU")
            self.line()
            self.cprint(self.t.secondary, "  [1]  \033[38;2;237;66;69m\033[1m📡  Discord Operations")
            self.cprint(self.t.secondary, "  [2]  \033[38;2;254;130;92m\033[1m🔍  OSINT & Intelligence")
            self.cprint(self.t.secondary, "  [3]  \033[38;2;237;66;69m\033[1m🛡️  Security & Utilities")
            self.cprint(self.t.secondary, "  [4]  \033[38;2;254;130;92m\033[1m🎮  Game Suite (Roblox)")
            self.cprint(self.t.secondary, "  [5]  \033[38;2;158;92;230m\033[1m🎭  Simulation Modules")
            self.cprint(self.t.secondary, "  [6]  \033[38;2;52;152;219m\033[1m🎨  Themes & Settings")
            self.cprint(self.t.secondary, "  [0]  \033[38;2;237;66;69mExit")
            self.line()

            choice = self.input_choice()
            menus = {
                '1': self.menu_discord, '2': self.menu_osint,
                '3': self.menu_security, '4': self.menu_gaming,
                '5': self.menu_simulation, '6': self.menu_settings,
            }
            if choice == '0':
                self.clear()
                self.cprint(self.t.accent, f"\n  Goodbye! — {AUTHOR}\n")
                sys.exit(0)
            if choice in menus:
                menus[choice]()

    def menu_discord(self):
        while True:
            self.clear()
            self.section_header('📡', 'DISCORD OPERATIONS')
            self.cprint(self.t.secondary, "  [1]  Webhook Info        — View webhook details (read-only)")
            self.cprint(self.t.secondary, "  [2]  Token Decoder       — Decode & inspect Discord tokens")
            self.cprint(self.t.secondary, "  [3]  Account Info        — Fetch account info from token")
            self.cprint(self.t.secondary, "  [4]  Server Info         — Fetch server details via bot")
            self.cprint(self.t.secondary, "  [5]  Status Rotator      — Status rotation reference")
            self.cprint(self.t.secondary, "  [0]  Back")
            self.line()
            choice = self.input_choice()
            if choice == '0': return
            mods = {'1': ('discord_ops', 'webhook_info'), '2': ('discord_ops', 'token_decode'),
                    '3': ('discord_ops', 'account_info'), '4': ('discord_ops', 'server_info'),
                    '5': ('discord_ops', 'status_rotator')}
            if choice in mods:
                m, f = mods[choice]
                self.run_module(m, f)

    def menu_osint(self):
        while True:
            self.clear()
            self.section_header('🔍', 'OSINT & INTELLIGENCE')
            self.cprint(self.t.secondary, "  [1]  Whois Lookup        — Domain registration info")
            self.cprint(self.t.secondary, "  [2]  DNS Resolver         — A/MX/TXT/CNAME/NS records")
            self.cprint(self.t.secondary, "  [3]  Port Scanner         — TCP port scan + banner grab")
            self.cprint(self.t.secondary, "  [4]  IP Info              — Public IP information")
            self.cprint(self.t.secondary, "  [5]  Email Lookup         — Email reputation + MX check")
            self.cprint(self.t.secondary, "  [6]  Metadata Scanner     — File EXIF metadata extraction")
            self.cprint(self.t.secondary, "  [7]  Username Checker     — Multi-platform availability")
            self.cprint(self.t.secondary, "  [8]  Breach Check         — Email breach database lookup")
            self.cprint(self.t.secondary, "  [9]  Traceroute           — Network path tracing")
            self.cprint(self.t.secondary, "  [10] Tor Check            — Tor exit node detection")
            self.cprint(self.t.secondary, "  [11] Link Tools           — URL expand/track/info")
            self.cprint(self.t.secondary, "  [12] SSL Certificate      — Domain cert info")
            self.cprint(self.t.secondary, "  [0]  Back")
            self.line()
            choice = self.input_choice()
            if choice == '0': return
            mods = {'1': ('osint', 'whois_lookup'), '2': ('osint', 'dns_resolver'),
                    '3': ('port_scanner', 'run'), '4': ('osint', 'ip_info'),
                    '5': ('email_tools', 'run'), '6': ('osint', 'metadata_scan'),
                    '7': ('osint', 'username_check'), '8': ('breach_check', 'run'),
                    '9': ('traceroute', 'run'), '10': ('tor_check', 'run'),
                    '11': ('link_tools', 'run'), '12': ('ssl_cert', 'run')}
            if choice in mods:
                m, f = mods[choice]
                self.run_module(m, f)

    def menu_security(self):
        while True:
            self.clear()
            self.section_header('🛡️', 'SECURITY & UTILITIES')
            self.cprint(self.t.secondary, "  [1]  Obfuscator V2       — Python obfuscation (XOR + Anti-Print)")
            self.cprint(self.t.secondary, "  [2]  Web Cloner          — Clone any website locally")
            self.cprint(self.t.secondary, "  [3]  Cryptography        — Base64/Hex/ROT13 + Password gen")
            self.cprint(self.t.secondary, "  [4]  QR Generator        — Custom QR codes")
            self.cprint(self.t.secondary, "  [5]  Hash Tool            — Hash strings + online lookup")
            self.cprint(self.t.secondary, "  [6]  Base64 Image        — Encode/decode images")
            self.cprint(self.t.secondary, "  [7]  Ciphers             — Caesar/Vigenere/Atbash/XOR")
            self.cprint(self.t.secondary, "  [8]  JWT Tools           — Decode & generate JWT tokens")
            self.cprint(self.t.secondary, "  [9]  CORS Tester         — Test CORS headers")
            self.cprint(self.t.secondary, "  [10] Entropy             — Shannon entropy + password strength")
            self.cprint(self.t.secondary, "  [11] Hex Dump            — View hex data")
            self.cprint(self.t.secondary, "  [12] Regex Tester        — Test regular expressions")
            self.cprint(self.t.secondary, "  [13] Password Check      — Strength + breach check")
            self.cprint(self.t.secondary, "  [14] Timestamp Tool      — Unix timestamp converter")
            self.cprint(self.t.secondary, "  [0]  Back")
            self.line()
            choice = self.input_choice()
            if choice == '0': return
            mods = {'1': ('obfuscator', 'run'), '2': ('web_cloner', 'run'),
                    '3': ('crypto', 'run'), '4': ('qr_gen', 'run'),
                    '5': ('hash_tool', 'run'), '6': ('base64_image', 'run'),
                    '7': ('ciphers', 'run'), '8': ('jwt_tools', 'run'),
                    '9': ('cors_tester', 'run'), '10': ('entropy', 'run'),
                    '11': ('hex_dump', 'run'), '12': ('regex_tester', 'run'),
                    '13': ('passcheck', 'run'), '14': ('timestamp', 'run')}
            if choice in mods:
                m, f = mods[choice]
                self.run_module(m, f)

    def menu_gaming(self):
        while True:
            self.clear()
            self.section_header('🎮', 'GAME SUITE (ROBLOX)')
            self.cprint(self.t.secondary, "  [1]  User Intel          — Roblox user info lookup")
            self.cprint(self.t.secondary, "  [2]  Group Intel         — Roblox group info lookup")
            self.cprint(self.t.secondary, "  [3]  Cookie Login        — Validate .ROBLOSECURITY cookie")
            self.cprint(self.t.secondary, "  [4]  Asset Downloader    — Download Roblox assets")
            self.cprint(self.t.secondary, "  [5]  Inventory Viewer    — View user inventory")
            self.cprint(self.t.secondary, "  [6]  Game Info           — Roblox game/experience details")
            self.cprint(self.t.secondary, "  [0]  Back")
            self.line()
            choice = self.input_choice()
            if choice == '0': return
            mods = {'1': ('roblox_intel', 'run'), '2': ('roblox_intel', 'group_lookup'),
                    '3': ('roblox_control', 'run'), '4': ('roblox_control', 'asset_download'),
                    '5': ('roblox_intel', 'inventory_view'), '6': ('roblox_intel', 'game_info')}
            if choice in mods:
                m, f = mods[choice]
                self.run_module(m, f)

    def menu_simulation(self):
        while True:
            self.clear()
            self.section_header('🎭', 'SIMULATION MODULES')
            self.cprint(self.t.secondary, "  [1]  Identity Generator  — Realistic names, emails, addresses")
            self.cprint(self.t.secondary, "  [2]  Credit Card Gen     — Test card numbers (Luhn valid)")
            self.cprint(self.t.secondary, "  [3]  Wallet Generator    — Crypto wallet addresses")
            self.cprint(self.t.secondary, "  [4]  Username Generator  — Unique usernames")
            self.cprint(self.t.secondary, "  [5]  Password Generator  — Secure passwords")
            self.cprint(self.t.secondary, "  [6]  Lorem Ipsum         — Placeholder text")
            self.cprint(self.t.secondary, "  [7]  UUID Generator      — v4 UUIDs")
            self.cprint(self.t.secondary, "  [8]  Fake Nitro Code     — Random Nitro-style codes (test)")
            self.cprint(self.t.secondary, "  [9]  Server Template     — Discord server JSON template")
            self.cprint(self.t.secondary, "  [0]  Back")
            self.line()
            choice = self.input_choice()
            if choice == '0': return
            mods = {'1': ('faker_suite', 'identity_gen'), '2': ('faker_suite', 'credit_card_gen'),
                    '3': ('faker_suite', 'wallet_gen'), '4': ('faker_suite', 'username_gen'),
                    '5': ('faker_suite', 'password_gen'), '6': ('faker_suite', 'lorem_ipsum'),
                    '7': ('faker_suite', 'uuid_gen'), '8': ('faker_suite', 'fake_nitro'),
                    '9': ('faker_suite', 'server_template')}
            if choice in mods:
                m, f = mods[choice]
                self.run_module(m, f)

    def menu_settings(self):
        while True:
            self.clear()
            self.section_header('🎨', 'THEMES & SETTINGS')
            self.cprint(self.t.secondary, f"  Current theme: {self.t.B}{self.theme_name}{self.t.R}")
            self.cprint(self.t.secondary, f"  Version: {VERSION}")
            self.line()

            for idx, (name, data) in enumerate(self.themes.items(), 1):
                t = Theme(data)
                marker = ' ◀' if name == self.theme_name else ''
                self.cprint(t.primary, f"  [{idx:2d}]  {data.get('name', name)}{self.t.R}{self.t.accent}{marker}")

            self.line()
            self.cprint(self.t.secondary, "  [u]  Check for updates")
            self.cprint(self.t.secondary, "  [0]  Back")

            choice = self.input_choice()
            if choice == '0': return
            if choice.lower() == 'u':
                self.check_update()
                continue
            try:
                idx = int(choice)
                names = list(self.themes.keys())
                if 1 <= idx <= len(names):
                    self.theme_name = names[idx - 1]
                    self.settings['current_theme'] = self.theme_name
                    save_json(SETTINGS_PATH, self.settings)
                    self.t = Theme(self.themes[self.theme_name])
                    self.cprint(self.t.success, f"\n  Theme: {self.theme_name}")
                    self.pause()
            except (ValueError, IndexError):
                pass


def main():
    app = KevTool()
    app.loading_screen()
    app.check_update()
    app.main_menu()


if __name__ == '__main__':
    main()

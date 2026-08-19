#!/usr/bin/env python3
"""KevTool — KevBin Educational Security & Utilities Suite"""

import os
import sys
import json
import time
import importlib
import getpass

os.system('')
try:
    import colorama
    colorama.init()
except ImportError:
    pass

AUTHOR = "KevBin"
GITHUB_REPO = "kevluvcode/Kev-tool"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"
GITHUB_CLONE = f"https://github.com/{GITHUB_REPO}.git"
GITHUB_RAW_VERSION = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/version.txt"
PC_USER = getpass.getuser()

VERSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.txt')

def _read_version():
    try:
        with open(VERSION_PATH, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return "0.0.0"

VERSION = _read_version()

BANNER = r"""
     ██╗  ██╗██████╗  ██████╗ ███╗   ██╗    ████████╗███████╗██████╗ ███╗   ███╗
     ██║ ██╔╝██╔══██╗██╔═══██╗████╗  ██║    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
     █████╔╝ ██████╔╝██║   ██║██╔██╗ ██║       ██║   █████╗  ██████╔╝██╔████╔██║
     ██╔═██╗ ██╔══██╗██║   ██║██║╚██╗██║       ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
     ██║  ██╗██║  ██║╚██████╔╝██║ ╚████║       ██║   ███████╗██║  ██║██║ ╚═╝ ██║
     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝"""

TOOLS_PER_PAGE = 15


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
        self.t = Theme(self.themes.get(theme_name, self.themes.get('modern', {})))
        self.theme_name = theme_name
        self.prompt = f"{PC_USER}@kev> "

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def cprint(self, color, text, end='\n'):
        sys.stdout.write(f"{color}{text}{self.t.R}{end}")
        sys.stdout.flush()

    def line(self, char='─', width=62):
        self.cprint(self.t.border, '  ' + char * width)

    def section_header(self, icon, title):
        self.line()
        self.cprint(self.t.B + self.t.primary, f"  {icon}  {title}")
        self.line()

    def input_choice(self, prompt=None):
        p = prompt or self.prompt
        try:
            return input(f"{self.t.primary}{p}{self.t.R}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return ''

    def pause(self):
        self.cprint(self.t.dim, f'\n  {self.prompt}Press Enter...')
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            print()

    def loading_screen(self):
        lines = BANNER.split('\n')
        total = len(lines)
        bar_w = 40
        duration = 3.0
        step_time = duration / (total + 5)

        for i, line in enumerate(lines):
            self.clear()
            for j in range(i + 1):
                self.cprint(self.t.banner, lines[j])
            pct = int((i + 1) / total * 100)
            filled = int(bar_w * (i + 1) / total)
            bar = '█' * filled + '░' * (bar_w - filled)
            self.cprint(self.t.dim, '')
            self.cprint(self.t.primary, f"  [{bar}] {pct}%  Loading KevTool...")
            time.sleep(step_time)

        self.clear()
        for line in lines:
            self.cprint(self.t.banner, line)
        self.cprint(self.t.dim, '')
        self.cprint(self.t.primary, f"  [{'█' * bar_w}] 100%")
        self.cprint(self.t.accent, f"  {self.t.B}Welcome, {PC_USER}. KevTool v{VERSION} ready.")
        remaining = duration - (total + 5) * step_time
        if remaining > 0:
            time.sleep(remaining)
        else:
            time.sleep(0.3)

    def check_update(self):
        try:
            import requests
            self.cprint(self.t.dim, "  checking for updates...")
            resp = requests.get(GITHUB_RAW_VERSION, timeout=8)
            if resp.status_code == 200:
                remote_ver = resp.text.strip()
                if remote_ver and remote_ver != VERSION:
                    self.cprint(self.t.warning, f"  new version available: {remote_ver} (you have {VERSION})")
                    self.cprint(self.t.dim, f"  download: https://github.com/{GITHUB_REPO}")
                    choice = self.input_choice("  clone update now? (y/n): ")
                    if choice.lower() == 'y':
                        self.cprint(self.t.dim, "  cloning repo...")
                        import subprocess
                        install_dir = os.path.join(BASE_DIR, f"KevTool_{remote_ver}")
                        result = subprocess.run(
                            ['git', 'clone', GITHUB_CLONE, install_dir],
                            capture_output=True, text=True, timeout=60
                        )
                        if result.returncode == 0:
                            self.cprint(self.t.success, f"  [ok] cloned to: {install_dir}")
                            self.cprint(self.t.dim, "  run install.bat in the new folder to set it up")
                        else:
                            self.cprint(self.t.error, f"  [x] clone failed: {result.stderr.strip()}")
                    self.pause()
                else:
                    self.cprint(self.t.success, "  already up to date")
            else:
                self.cprint(self.t.dim, "  couldnt check for updates")
        except Exception:
            pass

    def run_module(self, module_name, func_name='run'):
        try:
            spec = importlib.util.spec_from_file_location(
                module_name, os.path.join(MODULES_DIR, f'{module_name}.py'))
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            func = getattr(mod, func_name, None)
            if func:
                func(self)
            else:
                self.cprint(self.t.error, f"  [X] No '{func_name}' in {module_name}")
                self.pause()
        except Exception as e:
            self.cprint(self.t.error, f"  [X] {e}")
            self.pause()

    def tool_menu(self, title, icon, tools, cols=2):
        page = 0
        while True:
            self.clear()
            self.section_header(icon, title)
            total = len(tools)
            pages = (total + TOOLS_PER_PAGE - 1) // TOOLS_PER_PAGE
            start = page * TOOLS_PER_PAGE
            end = min(start + TOOLS_PER_PAGE, total)
            for i in range(start, end):
                num = i + 1
                name, desc = tools[i]
                self.cprint(self.t.secondary, f"  [{num:3d}]  {name:24s} {self.t.dim}{desc}")
            self.line()
            if pages > 1:
                nav = f"  Page {page+1}/{pages}  [n]ext [p]rev"
                self.cprint(self.t.dim, nav)
            self.cprint(self.t.secondary, "  [0]  Back")
            choice = self.input_choice()
            if choice == '0': return
            if choice.lower() == 'n' and page < pages - 1:
                page += 1
                continue
            if choice.lower() == 'p' and page > 0:
                page -= 1
                continue
            try:
                idx = int(choice) - 1
                if 0 <= idx < total:
                    mod, func = tools[idx][2] if len(tools[idx]) > 2 else (tools[idx][0][0], 'run')
                    self.run_module(mod, func)
            except (ValueError, IndexError):
                pass

    def main_menu(self):
        while True:
            self.clear()
            for line in BANNER.split('\n'):
                self.cprint(self.t.banner, line)
            self.cprint(self.t.dim, f"  v{VERSION} | Theme: {self.theme_name} | {PC_USER}@kev")
            self.line()
            self.cprint(self.t.highlight + self.t.B, "  MAIN MENU")
            self.line()
            cats = [
                ('1', '📡', 'Discord Operations'),
                ('2', '🔍', 'OSINT & Intelligence'),
                ('3', '🛡️', 'Security & Utilities'),
                ('4', '🌐', 'Web & Network Tools'),
                ('5', '📝', 'Text & Encoding'),
                ('6', '🎨', 'Color & Design'),
                ('7', '💾', 'Data & Conversion'),
                ('8', '🎮', 'Game Suite (Roblox)'),
                ('9', '🎭', 'Simulation & Generators'),
                ('10', '📡', 'Network & DNS'),
                ('11', '🔧', 'Developer Tools'),
                ('12', '📁', 'File & Image Tools'),
                ('13', '⚙️', 'Themes & Settings'),
            ]
            for num, icon, name in cats:
                self.cprint(self.t.secondary, f"  [{num:>2s}]  {icon}  {name}")
            self.cprint(self.t.secondary, "  [ 0]  Exit")
            self.line()
            choice = self.input_choice()
            menus = {
                '1': self.menu_discord, '2': self.menu_osint, '3': self.menu_security,
                '4': self.menu_web, '5': self.menu_text, '6': self.menu_color,
                '7': self.menu_data, '8': self.menu_gaming, '9': self.menu_simulation,
                '10': self.menu_network, '11': self.menu_dev, '12': self.menu_file,
                '13': self.menu_settings,
            }
            if choice == '0':
                self.clear()
                self.cprint(self.t.accent, f"\n  Goodbye, {PC_USER}. — {AUTHOR}\n")
                sys.exit(0)
            if choice in menus:
                menus[choice]()

    # ─── CATEGORY MENUS ──────────────────────────────────────────

    def menu_discord(self):
        tools = [
            ('Webhook Info', 'View webhook details'),
            ('Token Decoder', 'Decode Discord tokens'),
            ('Account Info', 'Fetch account from token'),
            ('Server Info', 'Fetch server via bot'),
            ('Status Rotator', 'Status rotation reference'),
        ]
        mapped = [('discord_ops', 'webhook_info'), ('discord_ops', 'token_decode'),
                  ('discord_ops', 'account_info'), ('discord_ops', 'server_info'),
                  ('discord_ops', 'status_rotator')]
        self.tool_menu('DISCORD OPERATIONS', '📡',
                      [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)])

    def menu_osint(self):
        tools = [
            ('Whois Lookup', 'Domain registration info'),
            ('DNS Resolver', 'A/MX/TXT/CNAME/NS records'),
            ('IP Info', 'Public IP information'),
            ('Metadata Scanner', 'EXIF from images'),
            ('Username Checker', 'Multi-platform check'),
            ('Breach Check', 'Email breach lookup'),
            ('SSL Certificate', 'Domain cert info'),
            ('GeoIP Lookup', 'IP geolocation'),
            ('ASN Intel', 'ASN/IP range info'),
            ('Email Validate', 'Format + MX check'),
            ('Email Reputation', 'Email provider check'),
            ('Stealer Check', 'Credential leak check'),
            ('Wayback Machine', 'Historical snapshots'),
            ('Tech Stack', 'Website technology detection'),
            ('Blacklist Check', 'IP blacklist lookup'),
        ]
        mapped = [('osint', 'whois_lookup'), ('osint', 'dns_resolver'),
                  ('osint', 'ip_info'), ('osint', 'metadata_scan'),
                  ('osint', 'username_check'), ('breach_check', 'run'),
                  ('ssl_cert', 'run'), ('geoip', 'run'),
                  ('asn_intel', 'run'), ('email_tools', 'validate'),
                  ('email_tools', 'reputation'), ('stealer_check', 'run'),
                  ('wayback', 'run'), ('tech_stack', 'run'),
                  ('ip_blacklist', 'run')]
        self.tool_menu('OSINT & INTELLIGENCE', '🔍',
                      [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)])

    def menu_security(self):
        tools = [
            ('Obfuscator V2', 'Python XOR + Anti-Print'),
            ('Web Cloner', 'Clone websites locally'),
            ('Cryptography', 'Base64/Hex/ROT13'),
            ('QR Generator', 'Custom QR codes'),
            ('Hash Tool', 'Hash + online lookup'),
            ('Base64 Image', 'Encode/decode images'),
            ('Ciphers', 'Caesar/Vigenere/Atbash/XOR'),
            ('JWT Tools', 'Decode + generate JWT'),
            ('CORS Tester', 'Test CORS headers'),
            ('Entropy', 'Shannon entropy analysis'),
            ('Password Check', 'Strength + breach check'),
            ('Timestamp', 'Unix timestamp converter'),
            ('Security Headers', 'Analyze HTTP headers'),
            ('CSP Analyzer', 'Content Security Policy'),
            ('Honeypot Detector', 'Detect honeypots'),
            ('HTTP Status', 'HTTP status code lookup'),
            ('Port Scanner', 'TCP scan + banner grab'),
            ('Traceroute', 'Network path trace'),
            ('Tor Check', 'Tor exit node detection'),
            ('Link Tools', 'URL expand/track/info'),
            ('IP Pinger', 'ICMP ping utility'),
        ]
        mapped = [('obfuscator', 'run'), ('web_cloner', 'run'),
                  ('crypto', 'run'), ('qr_gen', 'run'),
                  ('hash_tool', 'run'), ('base64_image', 'run'),
                  ('ciphers', 'run'), ('jwt_tools', 'run'),
                  ('cors_tester', 'run'), ('entropy', 'run'),
                  ('passcheck', 'run'), ('timestamp', 'run'),
                  ('security_headers', 'run'), ('csp_analyzer', 'run'),
                  ('honeypot', 'run'), ('http_status', 'run'),
                  ('port_scanner', 'run'), ('traceroute', 'run'),
                  ('tor_check', 'run'), ('link_tools', 'run'),
                  ('ip_pinger', 'run')]
        self.tool_menu('SECURITY & UTILITIES', '🛡️',
                      [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)])

    def menu_web(self):
        tools = [
            ('Page Clone', 'Clone full websites'),
            ('Site Viewer', 'View source + headers'),
            ('Web Search', 'Search the web'),
            ('Webhook Tester', 'Test webhook endpoints'),
            ('Webhook Delete', 'Delete webhooks'),
            ('Link Bypass', 'Bypass link shorteners'),
            ('Link Spoof', 'View redirect chains'),
            ('Link Tracker', 'Track link clicks'),
            ('Browser FP', 'Browser fingerprint'),
            ('Webrtc Leak', 'WebRTC IP detection'),
            ('DNS over HTTPS', 'Encrypted DNS queries'),
            ('Subdomain Enum', 'Find subdomains'),
            ('Subnet Calculator', 'CIDR calculations'),
        ]
        mapped = [('page_clone', 'run'), ('site_viewer', 'run'),
                  ('web_search', 'run'), ('webhook_tools', 'tester'),
                  ('webhook_tools', 'delete'), ('link_tools', 'bypass'),
                  ('link_tools', 'spoof'), ('link_tools', 'tracker'),
                  ('browser_fp', 'run'), ('webrtc_leak', 'run'),
                  ('doh', 'run'), ('subenum', 'run'),
                  ('subnet_calc', 'run')]
        self.tool_menu('WEB & NETWORK TOOLS', '🌐',
                      [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)])

    def menu_text(self):
        tools = [
            ('Text Transform', 'Case/Reverse/Repeat'),
            ('Slug Generator', 'URL-safe slugs'),
            ('Sort Lines', 'Alphabetical/Numeric sort'),
            ('Markdown Preview', 'Render markdown'),
            ('Diff Tool', 'Compare two texts'),
            ('CSV Viewer', 'Parse + display CSV'),
            ('JSON Formatter', 'Pretty-print JSON'),
            ('SQL Formatter', 'Format SQL queries'),
            ('Regex Tester', 'Test regular expressions'),
            ('Word Counter', 'Word/char/line count'),
            ('Slugify', 'Convert to slug format'),
            ('HTML Entity', 'Encode/Decode entities'),
            ('URL Encode', 'URL encode/decode'),
            ('Unicode Tool', 'Unicode lookup/convert'),
            ('Emoji Lookup', 'Find emoji codes'),
            ('Text Stats', 'Readability analysis'),
        ]
        mapped = [('text_tools', 'transform'), ('text_tools', 'slugify'),
                  ('text_tools', 'sort'), ('markdown_tools', 'run'),
                  ('diff_tool', 'run'), ('csv_viewer', 'run'),
                  ('json_formatter', 'run'), ('sql_formatter', 'run'),
                  ('regex_tester', 'run'), ('text_tools', 'wordcount'),
                  ('text_tools', 'slugify2'), ('text_tools', 'html_entity'),
                  ('text_tools', 'url_encode'), ('unicode_tool', 'run'),
                  ('emoji_lookup', 'run'), ('text_tools', 'stats')]
        self.tool_menu('TEXT & ENCODING', '📝',
                      [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)])

    def menu_color(self):
        tools = [
            ('Color Converter', 'HEX/RGB/HSL conversion'),
            ('Gradient Generator', 'CSS gradient builder'),
            ('Contrast Checker', 'WCAG contrast ratio'),
            ('Color Palette', 'Generate color palettes'),
            ('Image Colors', 'Extract colors from image'),
        ]
        mapped = [('color_tools', 'converter'), ('color_tools', 'gradient'),
                  ('color_tools', 'contrast'), ('color_tools', 'palette'),
                  ('color_tools', 'image_colors')]
        self.tool_menu('COLOR & DESIGN', '🎨',
                      [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)])

    def menu_data(self):
        tools = [
            ('Base-N Encoder', 'Binary/Octal/Hex encode'),
            ('Base64 Decode', 'Decode Base64 strings'),
            ('Roman Numerals', 'Convert to/from Roman'),
            ('Number System', 'Dec/Hex/Bin/Oct convert'),
            ('Percentage Calc', 'Percentage calculations'),
            ('YAML <-> TOML', 'Convert between formats'),
            ('CSV Tools', 'Parse/merge CSV files'),
            ('JSON <-> XML', 'Convert between formats'),
            ('Receipt Generator', 'Fake receipt maker'),
            ('UUID Generator', 'Generate UUIDs v4'),
            ('Barcode Generator', 'Code128/Code39'),
            ('Password Generator', 'Secure passwords'),
            ('Random Data', 'Random numbers/strings'),
            ('Duration Calc', 'Time duration math'),
            ('Age Calculator', 'Calculate age from DOB'),
        ]
        mapped = [('base_n', 'run'), ('base64_decoder', 'run'),
                  ('numerals', 'roman'), ('numerals', 'convert'),
                  ('percentage', 'run'), ('yaml_toml', 'run'),
                  ('csv_tools', 'run'), ('json_formatter', 'xml'),
                  ('receipt', 'run'), ('uuid_gen', 'run'),
                  ('barcode', 'run'), ('password_gen', 'run'),
                  ('random_gen', 'run'), ('duration', 'run'),
                  ('age_calc', 'run')]
        self.tool_menu('DATA & CONVERSION', '💾',
                      [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)])

    def menu_gaming(self):
        tools = [
            ('User Intel', 'Roblox user lookup'),
            ('Group Intel', 'Roblox group lookup'),
            ('Cookie Login', 'Validate .ROBLOSECURITY'),
            ('Asset Downloader', 'Download Roblox assets'),
            ('Inventory Viewer', 'View user inventory'),
            ('Game Info', 'Roblox game details'),
        ]
        mapped = [('roblox_intel', 'run'), ('roblox_intel', 'group_lookup'),
                  ('roblox_control', 'run'), ('roblox_control', 'asset_download'),
                  ('roblox_intel', 'inventory_view'), ('roblox_intel', 'game_info')]
        self.tool_menu('GAME SUITE (ROBLOX)', '🎮',
                      [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)])

    def menu_simulation(self):
        tools = [
            ('Identity Generator', 'Realistic fake identities'),
            ('Credit Card Gen', 'Test card numbers (Luhn)'),
            ('Crypto Wallets', 'Generate wallet addresses'),
            ('Username Generator', 'Unique usernames'),
            ('Password Generator', 'Secure passwords'),
            ('Lorem Ipsum', 'Placeholder text'),
            ('Fake Nitro Code', 'Random Nitro-style codes'),
            ('Server Template', 'Discord server JSON'),
            ('ASCII Art', 'Text to ASCII art'),
            ('Stealth Art', 'Zalgo/glitch text'),
            ('Creeper Text', 'Creeper text effect'),
            ('Small Caps', 'Small caps text'),
            ('Bubble Text', 'Bubble unicode text'),
            ('Mirror Text', 'Flipped text'),
        ]
        mapped = [('faker_suite', 'identity_gen'), ('faker_suite', 'credit_card_gen'),
                  ('faker_suite', 'wallet_gen'), ('faker_suite', 'username_gen'),
                  ('faker_suite', 'password_gen'), ('faker_suite', 'lorem_ipsum'),
                  ('faker_suite', 'fake_nitro'), ('faker_suite', 'server_template'),
                  ('ascii_art', 'run'), ('text_effects', 'zalgo'),
                  ('text_effects', 'creeper'), ('text_effects', 'smallcaps'),
                  ('text_effects', 'bubble'), ('text_effects', 'mirror')]
        self.tool_menu('SIMULATION & GENERATORS', '🎭',
                      [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)])

    def menu_network(self):
        tools = [
            ('Port Scanner', 'TCP port scan + banners'),
            ('Traceroute', 'Network path trace'),
            ('DNS Resolver', 'Resolve DNS records'),
            ('DNS over HTTPS', 'Encrypted DNS'),
            ('Subdomain Enum', 'Find subdomains'),
            ('Subnet Calculator', 'CIDR math'),
            ('Whois', 'Domain registration'),
            ('IP Pinger', 'ICMP ping'),
            ('ASN Lookup', 'ASN information'),
            ('Blacklist Check', 'IP blacklist check'),
        ]
        mapped = [('port_scanner', 'run'), ('traceroute', 'run'),
                  ('osint', 'dns_resolver'), ('doh', 'run'),
                  ('subenum', 'run'), ('subnet_calc', 'run'),
                  ('osint', 'whois_lookup'), ('ip_pinger', 'run'),
                  ('asn_intel', 'run'), ('ip_blacklist', 'run')]
        self.tool_menu('NETWORK & DNS', '📡',
                      [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)])

    def menu_dev(self):
        tools = [
            ('Request Builder', 'Build HTTP requests'),
            ('Header Inspector', 'View/edit headers'),
            ('Cookie Inspector', 'View/edit cookies'),
            ('JS Obfuscator', 'JavaScript obfuscation'),
            ('Lua Obfuscator', 'Lua code obfuscation'),
            ('Lua Sandbox', 'Run Lua code safely'),
            ('Cron Builder', 'Build cron expressions'),
            ('Cron Parser', 'Parse cron schedules'),
            ('Code Formatter', 'Format source code'),
            ('YAML/TOML', 'Config file conversion'),
            ('JSON Formatter', 'Pretty-print JSON'),
            ('SQL Formatter', 'Format SQL queries'),
        ]
        mapped = [('reqbuild', 'run'), ('header_inspector', 'run'),
                  ('cookie_inspector', 'run'), ('js_obfuscator', 'run'),
                  ('lua_obfuscator', 'run'), ('lua_sandbox', 'run'),
                  ('cron_builder', 'run'), ('cron_parser', 'run'),
                  ('code_formatter', 'run'), ('yaml_toml', 'run'),
                  ('json_formatter', 'run'), ('sql_formatter', 'run')]
        self.tool_menu('DEVELOPER TOOLS', '🔧',
                      [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)])

    def menu_file(self):
        tools = [
            ('File Type Detector', 'Identify file types'),
            ('Image to Base64', 'Encode images'),
            ('Photo Metadata', 'EXIF extraction'),
            ('Metadata Stripper', 'Remove metadata'),
            ('Hex Dump', 'View hex data'),
            ('Steganography', 'Hide data in images'),
            ('File Checksum', 'MD5/SHA hash files'),
            ('Binary Viewer', 'View binary data'),
        ]
        mapped = [('file_type', 'run'), ('base64_image', 'run'),
                  ('photo_meta', 'run'), ('metadata_strip', 'run'),
                  ('hex_dump', 'run'), ('steganography', 'run'),
                  ('file_checksum', 'run'), ('hex_dump', 'binary')]
        self.tool_menu('FILE & IMAGE TOOLS', '📁',
                      [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)])

    def menu_settings(self):
        while True:
            self.clear()
            self.section_header('⚙️', 'THEMES & SETTINGS')
            self.cprint(self.t.secondary, f"  Theme: {self.t.B}{self.theme_name}{self.t.R}")
            self.cprint(self.t.secondary, f"  User:  {PC_USER}")
            self.cprint(self.t.secondary, f"  Ver:   {VERSION}")
            self.line()
            for idx, (name, data) in enumerate(self.themes.items(), 1):
                t = Theme(data)
                marker = ' ◀' if name == self.theme_name else ''
                self.cprint(t.primary, f"  [{idx:2d}]  {data.get('name', name)}{marker}")
            self.line()
            self.cprint(self.t.secondary, "  [u]  check for updates")
            self.cprint(self.t.secondary, "  [0]  back")
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

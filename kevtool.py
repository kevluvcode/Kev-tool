#!/usr/bin/env python3
"""
KevTool — KevBin Educational Security & Utilities Suite
Python 3.6+ | Windows + Linux + macOS | standalone modules
"""

import os
import sys
import io as _io
import json
import time
import importlib
import getpass
import subprocess
import shutil
import random
import re
from types import SimpleNamespace

PY_MAJ, PY_MIN = sys.version_info[:2]

if PY_MAJ < 3 or (PY_MAJ == 3 and PY_MIN < 6):
    print("  [X] KevTool requires Python 3.6 or newer.")
    print("      Download it from https://www.python.org/downloads/")
    sys.exit(1)

def _setup_utf8():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
        try:
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    else:
        try:
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except Exception:
            pass

def _enable_ansi():
    if os.name == 'nt':
        os.system('')
        try:
            import ctypes
            k = ctypes.windll.kernel32
            h = k.GetStdHandle(-11)
            m = ctypes.c_uint32()
            if k.GetConsoleMode(h, ctypes.byref(m)):
                k.SetConsoleMode(h, m.value | 0x0004 | 0x0008)
        except Exception:
            pass

_setup_utf8()
_enable_ansi()

try:
    from pystyle import Colors, Colorate, Center
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pystyle", "-q"])
    from pystyle import Colors, Colorate, Center

PC_USER = getpass.getuser()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, 'modules')
CONFIG_DIR = os.path.join(MODULES_DIR, 'config')
VERSION_PATH = os.path.join(MODULES_DIR, 'version.txt')
REQ_PATH = os.path.join(MODULES_DIR, 'requirements.txt')

def _read_version():
    try:
        with open(VERSION_PATH, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return "1.2.0"

VERSION = _read_version()

AUTHOR = "KevBin"
GITHUB_REPO = "kevluvcode/Kev-tool"
GITHUB_CLONE = f"https://github.com/{GITHUB_REPO}.git"
GITHUB_RAW_VERSION = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/modules/version.txt"

THEMES = {
    "modern": {"banner": Colors.white_to_blue, "head": Colors.white, "num": Colors.white_to_blue,
               "txt": Colors.white, "sub": Colors.white_to_blue, "inp": Colors.white_to_blue},
    "modern_red": {"banner": Colors.white_to_red, "head": Colors.white, "num": Colors.white_to_red,
                   "txt": Colors.white, "sub": Colors.white_to_red, "inp": Colors.white_to_red},
    "modern_purple": {"banner": Colors.blue_to_purple, "head": Colors.white, "num": Colors.blue_to_purple,
                      "txt": Colors.white, "sub": Colors.blue_to_purple, "inp": Colors.blue_to_purple},
    "blue": {"banner": Colors.white_to_blue, "head": Colors.blue_to_cyan, "num": Colors.cyan_to_blue,
             "txt": Colors.white_to_blue, "sub": Colors.blue_to_cyan, "inp": Colors.blue_to_cyan},
    "red": {"banner": Colors.red_to_white, "head": Colors.white_to_red, "num": Colors.white_to_red,
            "txt": Colors.white, "sub": Colors.red_to_white, "inp": Colors.white_to_red},
    "purple": {"banner": Colors.blue_to_purple, "head": Colors.purple_to_blue, "num": Colors.purple_to_blue,
               "txt": Colors.white, "sub": Colors.purple_to_blue, "inp": Colors.purple_to_blue},
    "green": {"banner": Colors.green_to_white, "head": Colors.white_to_green, "num": Colors.white_to_green,
              "txt": Colors.white, "sub": Colors.green_to_white, "inp": Colors.white_to_green},
    "yellow": {"banner": Colors.yellow_to_red, "head": Colors.red_to_yellow, "num": Colors.yellow_to_red,
               "txt": Colors.white, "sub": Colors.red_to_yellow, "inp": Colors.red_to_yellow},
    "rainbow": {"banner": Colors.rainbow, "head": Colors.rainbow, "num": Colors.rainbow,
                "txt": Colors.white, "sub": Colors.rainbow, "inp": Colors.rainbow},
}

BANNER_LINES = [
    r"  ____  __.                    ___________           .__",
    r"|    |/ _|_______  __  ______ \__    ___/___   ____ |  |",
    r"|      <_/ __ \  \/ / /_____/   |    | /  _ \ /  _ \|  |",
    r"|    |  \  ___/\   /  /_____/   |    |(  <_> |  <_> )  |__",
    r"|____|__ \___  >\_/             |____| \____/ \____/|____/",
    r"        \/   \/",
]

BANNER_SMALL = [
    r" _   _    _ __     _____ ",
    r"| \ | |  / \\ \   / /_ _|",
    r"|  \| | / _ \\ \ / / | | ",
    r"| |\  |/ ___ \\ V /  | | ",
    r"|_| \_/_/   \_\\_/  |___|",
]

DEFAULT_CONFIG = {
    "current_theme": "modern",
    "check_updates": True,
    "boot_screen": True,
    "animations": True,
    "typing_effect": True,
    "per_page": 14,
    "auto_update": True,
}

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

def ensure_config():
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
    except Exception:
        pass
    cfg = load_json(os.path.join(CONFIG_DIR, 'settings.json'))
    changed = False
    for k, v in DEFAULT_CONFIG.items():
        if k not in cfg:
            cfg[k] = v
            changed = True
    if changed:
        save_json(os.path.join(CONFIG_DIR, 'settings.json'), cfg)
    return cfg

CONFIG_PATH = os.path.join(CONFIG_DIR, 'settings.json')

def _strip_ansi(text):
    return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', str(text))

def _vis_len(text):
    """Visual width of a string (ANSI stripped, CJK/emoji counted as 2)."""
    s = _strip_ansi(text)
    w = 0
    for ch in s:
        o = ord(ch)
        if (0x1100 <= o <= 0x115F or 0x2E80 <= o <= 0xA4CF or 0xAC00 <= o <= 0xD7A3
                or 0xF900 <= o <= 0xFAFF or 0xFE30 <= o <= 0xFE4F
                or 0xFF00 <= o <= 0xFF60 or 0xFFE0 <= o <= 0xFFE6 or o >= 0x1F000):
            w += 2
        else:
            w += 1
    return w

def _pad_to(text, width, trunc_mark="…"):
    """Pad (or truncate) a string to an exact visual width."""
    s = str(text)
    pad = max(0, width - _vis_len(s))
    if pad == 0:
        return s
    return s + " " * pad

_TAG_COLORS = {
    'black': '\033[90m', 'red': '\033[91m', 'green': '\033[92m',
    'yellow': '\033[93m', 'blue': '\033[94m', 'magenta': '\033[95m',
    'purple': '\033[95m', 'cyan': '\033[96m', 'white': '\033[97m',
    'gray': '\033[90m', 'grey': '\033[90m', 'dim': '\033[2m',
    'bold': '\033[1m', 'reverse': '\033[7m', 'underline': '\033[4m',
}

def _markup(text):
    """Render [red]...[/red] style tags (and [on #hex] swatches) to ANSI."""
    s = str(text)
    def _color_solid(m):
        return _TAG_COLORS.get(m.group(2).lower(), '')
    def _color_reset(m):
        tag = m.group(2)
        if tag.lower() in ('bold', 'dim'):
            return '\033[22m' if tag.lower() == 'bold' else '\033[22m'
        return Colors.reset
    s = re.sub(r'\[on\s+#?([0-9a-fA-F]{3,8})\]', r'\033[48;2;\1m\x00on', s)
    s = s.replace('\x00on', '')  # placeholder replaced below
    try:
        def _hex_bg(m):
            h = m.group(1)
            if len(h) == 3:
                h = ''.join(c * 2 for c in h)
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f'\033[48;2;{r};{g};{b}m'
        s = re.sub(r'\[on\s+#([0-9a-fA-F]{3,8})\]', _hex_bg, s)
    except Exception:
        pass
    s = re.sub(r'\[/on\s+#?([0-9a-fA-F]{3,8})\]', Colors.reset, s)
    s = re.sub(r'\[/([a-zA-Z]+)\]', _color_reset, s)
    s = re.sub(r'\[([a-zA-Z]+)\]', _color_solid, s)
    return s

def get_config():
    return load_json(CONFIG_PATH)

def get_theme():
    cfg = get_config()
    name = cfg.get('current_theme', 'modern').lower()
    return THEMES.get(name, THEMES['modern'])

def clr():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def cprint_horizontal(color, text):
    cfg = get_config()
    if cfg.get('current_theme', 'modern').lower() == 'rainbow':
        return Colorate.Horizontal(Colors.rainbow, str(text))
    if isinstance(color, str):
        return f"{color}{text}{Colors.reset}"
    return Colorate.Horizontal(color, str(text))

def ensure_deps():
    missing = []
    for pkg in ('requests', 'qrcode', 'PIL', 'dns', 'whois', 'socks'):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print("  [*] Installing missing packages:", ", ".join(missing))
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                                   "-r", REQ_PATH, "pystyle", "PySocks"])
        except Exception as e:
            print(f"  [!] pip install failed: {e}")

def print_banner():
    cfg = get_config()
    theme_name = cfg.get('current_theme', 'modern').lower()
    cl = get_theme()

    lines = BANNER_LINES if theme_name.startswith('modern') else BANNER_SMALL
    for line in lines:
        print(cprint_horizontal(cl['banner'], Center.XCenter(line)))
    print()

def theme_wave(theme_name=None):
    cl = get_theme()
    tw = shutil.get_terminal_size().columns
    n = min(60, max(20, (tw // 2) - 4))
    try:
        for i in range(n):
            bar = "░" * i + "█" + "░" * (n - i - 1)
            sys.stdout.write("\r  " + cprint_horizontal(cl['inp'], bar))
            sys.stdout.flush()
            time.sleep(0.006)
        sys.stdout.write("\n")
    except Exception:
        pass

def draw_card_box(title, items):
    cl = get_theme()
    tw = shutil.get_terminal_size().columns
    per = 3 if tw >= 110 else 2 if tw >= 70 else 1
    box_w = max(20, min(38, (tw - 6) // per))
    inner = box_w - 2

    bd_len = max(0, (inner - len(title)) // 2)
    bd_ext = "─" if (inner - len(title)) > 0 and (inner - len(title)) % 2 != 0 else ""
    print(cprint_horizontal(cl['head'], " " * 2 + "┌" + "─" * bd_len + title + "─" * bd_len + bd_ext + "┐"))

    item_list = list(items.items())
    for i in range(0, len(item_list), per):
        row_items = item_list[i:i + per]
        line = "  "
        for k, v in row_items:
            tag = f"  [{k}] "
            w_ = max(1, inner - len(tag))
            shown = v if len(v) <= w_ else v[:w_ - 1] + "."
            line += cprint_horizontal(cl['num'], tag) + cprint_horizontal(cl['txt'], shown) + " " * max(0, w_ - len(shown)) + "  "
        print(line)

    print(cprint_horizontal(cl['head'], " " * 2 + "└" + "─" * inner + "┘"))

def draw_menu_grid(categories):
    cl = get_theme()
    tw = shutil.get_terminal_size().columns
    cw = 32
    per = max(1, (tw - 4) // (cw + 2))
    if tw < 68 or per < 2:
        per = 1
        cw = max(28, tw - 8)
    else:
        per = min(per, 4)

    rows = [categories[i:i + per] for i in range(0, len(categories), per)]
    for row in rows:
        top = ""
        mid = ""
        bot = ""
        for num, name in row:
            tag = f"[{num}] "
            room = max(1, cw - 2 - len(tag))
            shown = name if len(name) <= room else name[:room - 1] + "."
            pad = max(0, cw - 2 - len(tag) - len(shown))
            top += "┌" + "─" * (cw - 2) + "┐  "
            mid += "│" + cprint_horizontal(cl['num'], tag) + cprint_horizontal(cl['txt'], shown) + " " * pad + "│  "
            bot += "└" + "─" * (cw - 2) + "┘  "
        print(cprint_horizontal(cl['num'], top))
        print(mid)
        print(cprint_horizontal(cl['num'], bot))
    print()

def get_input(prompt=None):
    if prompt is None:
        prompt = f"{PC_USER}@kevbin:~#"
    else:
        prompt = prompt.replace("kevbin@root/", f"{PC_USER}@kevbin/")
        prompt = prompt.replace("kevbin@", f"{PC_USER}@kevbin/")
    cl = get_theme()
    return input(cprint_horizontal(cl['inp'], f"\n  {prompt} ")).strip()

def loading_screen():
    cl = get_theme()
    clr()
    for line in BANNER_LINES:
        print(cprint_horizontal(cl['banner'], Center.XCenter(line)))
        time.sleep(0.04)

    tw = shutil.get_terminal_size().columns
    bar_w = min(56, max(24, tw - 34))
    labels = ["Checksum verifying", "Unpacking modules", "Self-test complete"]
    frames = "|/-\\"
    for i, label in enumerate(labels):
        pct = int(((i + 1) / len(labels)) * 100)
        filled = int(bar_w * pct / 100)
        bar = "█" * filled + "░" * (bar_w - filled)
        for f in frames:
            line = (cprint_horizontal(cl['num'], f"  {f} ")
                    + cprint_horizontal(cl['txt'], label.ljust(22))
                    + cprint_horizontal(cl['inp'], f"[{bar}]")
                    + cprint_horizontal(cl['num'], f" {pct}%"))
            sys.stdout.write("\r" + line)
            sys.stdout.flush()
            time.sleep(0.02)
    sys.stdout.write("\n\n")
    print(cprint_horizontal(cl['head'], f"  [+] KevTool v{VERSION} ready — {PC_USER}. Enjoy.\n"))
    time.sleep(0.3)

def _ver_tuple(v):
    try:
        return tuple(int(x) for x in re.findall(r'\d+', str(v)))[:3]
    except Exception:
        return (0,)

def check_update():
    try:
        import requests
        cl = get_theme()
        print(cprint_horizontal(cl['sub'], "  Checking for updates..."))
        resp = requests.get(GITHUB_RAW_VERSION, timeout=8)
        if resp.status_code == 200:
            remote_ver = resp.text.strip()
            if remote_ver and _ver_tuple(remote_ver) > _ver_tuple(VERSION):
                print(cprint_horizontal(cl['head'], f"\n  [!] New Version Detected: {remote_ver} (you have {VERSION})"))
                print(cprint_horizontal(cl['txt'], f"  Download: https://github.com/{GITHUB_REPO}"))
                choice = get_input("  Clone update now? (y/n): ")
                if choice.lower() == 'y':
                    print(cprint_horizontal(cl['txt'], "  Cloning repo..."))
                    install_dir = os.path.join(BASE_DIR, f"KevTool_{remote_ver}")
                    result = subprocess.run(['git', 'clone', GITHUB_CLONE, install_dir],
                                            capture_output=True, text=True, timeout=60)
                    if result.returncode == 0:
                        print(cprint_horizontal(cl['head'], f"  [+] Cloned to: {install_dir}"))
                    else:
                        print(cprint_horizontal(cl['num'], f"  [!] Clone failed: {result.stderr.strip()}"))
                get_input("  Press Enter...")
            else:
                print(cprint_horizontal(cl['head'], "  Already up to date"))
                time.sleep(0.3)
        else:
            time.sleep(0.3)
    except Exception:
        pass

class KevTool:
    def __init__(self):
        self.settings = ensure_config()
        self.theme_name = self.settings.get('current_theme', 'modern')
        self.prompt = f"{PC_USER}@kevbin:~#"
        self._refresh_t()

    @staticmethod
    def _grad():
        cl = get_theme()
        return SimpleNamespace(
            head=cl['head'], num=cl['num'], txt=cl['txt'], sub=cl['sub'], inp=cl['inp'],
            banner=cl['banner'], primary=cl['banner'], secondary=cl['num'], accent=cl['num'],
            highlight=cl['head'], success=Colors.green_to_white, error=Colors.red_to_white,
            warning=Colors.yellow_to_red, dim="\033[2m", B="\033[1m",
            reset=Colors.reset, R=Colors.reset,
        )

    def _refresh_t(self):
        self.t = self._grad()

    @property
    def box(self):
        return _Box(self)

    def clear(self):
        clr()

    def _bw(self):
        tw = shutil.get_terminal_size().columns
        return max(30, min(58, tw - 10))

    def cprint(self, color=None, text='', end='\n'):
        if color is None:
            color = self.t.txt
        sys.stdout.write(cprint_horizontal(color, str(text)) + end)

    def line(self, char='─'):
        self.cprint(self.t.dim, "  " + char * max(20, self._bw() - 2))

    def section_header(self, icon, title):
        self.clear()
        w = self._bw()
        txt = f" {icon}  {title} "
        pad = max(0, w - _vis_len(txt))
        left, right = pad // 2, pad - (pad // 2)
        self.cprint(self.t.head, "  ┌" + "─" * left + txt + "─" * right + "┐")
        self.cprint(self.t.dim, "  │" + " " * w + "│")

    def box_top(self, width=None):
        w = width or self._bw()
        self.cprint(self.t.head, "  ┌" + "─" * w + "┐")

    def box_mid(self, width=None):
        w = width or self._bw()
        self.cprint(self.t.head, "  ├" + "─" * w + "┤")

    def box_bottom(self, width=None):
        w = width or self._bw()
        self.cprint(self.t.head, "  └" + "─" * w + "┘")

    def box_row(self, content, width=None):
        w = width if isinstance(width, int) else self._bw()
        inner = max(0, w - 2)
        shown = str(content)
        if _vis_len(shown) > inner:
            shown = shown[:inner - 1] + "…"
        self.cprint(self.t.txt, "  │" + _pad_to(shown, inner) + "│")

    def box_title(self, text):
        w = self._bw()
        t = f" {text} "
        pad = max(0, w - 2 - _vis_len(t))
        left, right = pad // 2, pad - (pad // 2)
        self.cprint(self.t.head, "  ┌" + "─" * left + t + "─" * right + "┐")

    def box_print(self, text, color=None):
        s = str(text)
        if '[' in s and ']' in s and re.search(r'\[/?[a-z]', s, re.I):
            sys.stdout.write(_markup(s) + "\n")
        else:
            self.cprint(color or self.t.txt, s)

    def box_input(self, prompt, default=None):
        r = self.input_choice(prompt)
        if r or default is None:
            return r
        return default

    def box_code(self, text, width=None):
        w = width if isinstance(width, int) else self._bw()
        inner = max(1, w - 2)
        for ln in (str(text).splitlines() or ['']):
            shown = _markup(ln)
            if _vis_len(shown) > inner:
                shown = shown[:inner - 1] + "…"
            sys.stdout.write("  │" + _pad_to(shown, inner) + "│\n")

    def box_table(self, headers=None, rows=None, title=None):
        """box_table(headers, rows) or box_table(rows, title=...) or box.table(headers, rows)."""
        if rows is None and isinstance(headers, (list, tuple)) and headers:
            if isinstance(headers[0], (list, tuple)):
                rows, headers = headers, None
            else:
                rows = []
        rows = [list(r) if isinstance(r, (list, tuple)) else [r] for r in (rows or [])]
        if title:
            self.box_title(str(title))
        if not headers and rows:
            headers = rows.pop(0)
        if not headers:
            headers = ["Value" for _ in range(len(rows[0]) if rows else 1)]
        w = self._bw()
        inner = max(8, w - 2)
        widths = [_vis_len(str(h)) for h in headers]
        for r in rows:
            for i in range(min(len(r), len(headers))):
                widths[i] = min(max(widths[i], _vis_len(str(r[i]))), max(10, inner // len(headers)))
        while sum(widths) + 3 * (len(widths) - 1) > inner and max(widths) > 10:
            widths[widths.index(max(widths))] -= 1
        sep = "─┼─".join("─" * x for x in widths)
        total = sum(widths) + 3 * (len(widths) - 1)
        self.cprint(self.t.head, "  ┌" + "─" * total + "┐")
        hdr = " │ ".join(_pad_to(str(h), widths[i]) for i, h in enumerate(headers))
        self.cprint(self.t.head, "  │ " + hdr + " │")
        self.cprint(self.t.head, "  ├─" + sep + "─┤")
        for r in rows:
            def _cut(v, i):
                s = str(v)
                if _vis_len(s) <= widths[i]:
                    return s
                return s[:max(1, widths[i] - 1)] + "…"
            cells = " │ ".join(_pad_to(_cut(r[i], i), widths[i]) for i in range(len(headers)))
            self.cprint(self.t.txt, "  │ " + cells + " │")
        self.cprint(self.t.head, "  └" + "─" * total + "┘")

    def input_choice(self, prompt=None):
        return get_input(prompt)

    def pause(self):
        self.cprint(self.t.inp, f"\n  {self.prompt} Press Enter...", end="")
        try:
            input()
        except EOFError:
            pass

    def run_module(self, module_name, func_name='run'):
        try:
            spec = importlib.util.spec_from_file_location(module_name, os.path.join(MODULES_DIR, f'{module_name}.py'))
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            func = getattr(mod, func_name, None)
            if func:
                func(self)
            else:
                self.cprint(self.t.num, f"  [!] No '{func_name}' in {module_name}")
                self.pause()
        except Exception as e:
            self.cprint(self.t.num, f"  [!] {e}")
            self.pause()

    def tool_menu(self, title, icon, tools, tab=None, tabs=13):
        page = 0
        per_page = int(self.settings.get('per_page', 14))
        while True:
            self.section_header(icon, title)
            w = self._bw()
            inner = max(1, w - 2)
            total = len(tools)
            pages = max(1, (total + per_page - 1) // per_page)
            start = page * per_page
            end = min(start + per_page, total)
            name_w = max(22, min(36, inner // 2 - 3))
            desc_w = max(8, inner - name_w - 3)

            self.box_top(w)
            if tab:
                l = f" TAB {tab}/{tabs} "
                r = " [0] = MAIN MENU "
                self.box_row(l + " " * max(0, inner - _vis_len(l) - _vis_len(r)) + r, w)
                self.box_mid(w)
            for i in range(start, end):
                num = i + 1
                name, desc = tools[i][0], tools[i][1]
                left = f" [{num:>2}]  {name}"
                if _vis_len(left) > name_w:
                    left = left[:name_w - 1] + "…"
                right = desc if _vis_len(desc) <= desc_w else desc[:desc_w - 1] + "…"
                self.box_row(_pad_to(left, name_w) + "  " + _pad_to(right, desc_w), w)
            self.box_mid(w)
            if pages > 1:
                l = f" PAGE {page + 1}/{pages} "
                r = " [N] NEXT   [P] PREV "
                self.box_row(l + " " * max(0, inner - _vis_len(l) - _vis_len(r)) + r, w)
            self.box_row(" [0]  Return to Main Menu", w)
            self.box_bottom(w)

            choice = self.input_choice()
            if choice == '0':
                return
            if choice.lower() == 'n' and page < pages - 1:
                page += 1
                continue
            if choice.lower() == 'p' and page > 0:
                page -= 1
                continue
            try:
                idx = int(choice) - 1
                if 0 <= idx < total:
                    mod, func = tools[idx][2]
                    self.run_module(mod, func)
            except (ValueError, IndexError):
                pass

    def main_menu(self):
        cats = [
            ('1', 'Discord Operations'), ('2', 'OSINT & Intelligence'),
            ('3', 'Security & Utilities'), ('4', 'Web & Network Tools'),
            ('5', 'Text & Encoding'), ('6', 'Color & Design'),
            ('7', 'Data & Conversion'), ('8', 'Game Suite (Roblox)'),
            ('9', 'Simulation & Generators'), ('10', 'Network & DNS'),
            ('11', 'Developer Tools'), ('12', 'File & Image Tools'),
            ('13', 'Themes & Settings'),
        ]
        menus = {
            '1': self.menu_discord, '2': self.menu_osint, '3': self.menu_security,
            '4': self.menu_web, '5': self.menu_text, '6': self.menu_color,
            '7': self.menu_data, '8': self.menu_gaming, '9': self.menu_simulation,
            '10': self.menu_network, '11': self.menu_dev, '12': self.menu_file,
            '13': self.menu_settings,
        }
        while True:
            cl = get_theme()
            clr()
            print_banner()
            print(cprint_horizontal(cl['sub'], Center.XCenter(f"v{VERSION} | Theme: {self.theme_name} | {PC_USER}@kevbin")))
            print()
            draw_menu_grid(cats)
            self.cprint(cl['num'], "  [ 0]  Exit")
            choice = self.input_choice()
            if choice == '0':
                clr()
                self.cprint(self.t.head, f"\n  Goodbye, {PC_USER}. — {AUTHOR}\n")
                sys.exit(0)
            if choice in menus:
                menus[choice]()

    def menu_discord(self):
        tools = [
            ('Webhook Info', 'View webhook details'),
            ('Token Decoder', 'Decode Discord tokens'),
            ('Account Info', 'Fetch account from token'),
            ('Server Info', 'Fetch server via bot'),
            ('Status Rotator', 'Status rotation reference'),
            ('Bot Invite', 'Generate bot invite URL'),
        ]
        mapped = [('discord_ops', 'webhook_info'), ('discord_ops', 'token_decode'),
                  ('discord_ops', 'account_info'), ('discord_ops', 'server_info'),
                  ('discord_ops', 'status_rotator'), ('discord_ops', 'bot_invite_gen')]
        self.tool_menu('DISCORD OPERATIONS', '📡', [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)], tab=1)

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
        self.tool_menu('OSINT & INTELLIGENCE', '🔍', [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)], tab=2)

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
            ('System Info', 'CPU/RAM/Disk/OS details'),
            ('Proxy Scraper', 'Grab proxies from GitHub lists'),
            ('Proxy Checker', 'Validate proxies multi-threaded'),
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
                  ('ip_pinger', 'run'), ('system_info', 'run'),
                  ('proxy_scraper', 'run'), ('proxy_checker', 'run')]
        self.tool_menu('SECURITY & UTILITIES', '🛡️', [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)], tab=3)

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
            ('WebRTC Leak', 'WebRTC IP detection'),
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
        self.tool_menu('WEB & NETWORK TOOLS', '🌐', [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)], tab=4)

    def menu_text(self):
        tools = [
            ('Text Transform', 'Case/Reverse/Repeat'),
            ('Slugify', 'URL-safe slugs'),
            ('Sort Lines', 'Alphabetical/Numeric sort'),
            ('Markdown Preview', 'Render markdown'),
            ('Diff Tool', 'Compare two texts'),
            ('CSV Viewer', 'Parse + display CSV'),
            ('JSON Formatter', 'Pretty-print JSON'),
            ('SQL Formatter', 'Format SQL queries'),
            ('Regex Tester', 'Test regular expressions'),
            ('Word Counter', 'Word/char/line count'),
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
                  ('text_tools', 'html_entity'), ('text_tools', 'url_encode'),
                  ('unicode_tool', 'run'), ('emoji_lookup', 'run'),
                  ('text_tools', 'stats')]
        self.tool_menu('TEXT & ENCODING', '📝', [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)], tab=5)

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
        self.tool_menu('COLOR & DESIGN', '🎨', [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)], tab=6)

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
        self.tool_menu('DATA & CONVERSION', '💾', [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)], tab=7)

    def menu_gaming(self):
        tools = [
            ('User Intel', 'Roblox user lookup'),
            ('Group Intel', 'Roblox group lookup'),
            ('Name History', 'Roblox previous usernames'),
            ('Username Check', 'Roblox username availability'),
            ('Cookie Login', 'Validate .ROBLOSECURITY'),
            ('Asset Downloader', 'Download Roblox assets'),
            ('Inventory Viewer', 'View user inventory'),
            ('Game Info', 'Roblox game details'),
        ]
        mapped = [('roblox_intel', 'run'), ('roblox_intel', 'group_lookup'),
                  ('roblox_intel', 'name_history'), ('roblox_intel', 'username_check'),
                  ('roblox_control', 'run'), ('roblox_control', 'asset_download'),
                  ('roblox_intel', 'inventory_view'), ('roblox_intel', 'game_info')]
        self.tool_menu('GAME SUITE (ROBLOX)', '🎮', [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)], tab=8)

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
            ('Fake Mail Gen', 'Fake email + password'),
            ('Fake DDoS', 'Simulated DDoS attack'),
            ('Fake Wallet Miner', 'Simulated mining rig'),
            ('Social Botter', 'Simulated view botter'),
            ('Fake PayPal OTP', 'Simulated OTP code'),
            ('Fake Account Gen', 'Fake account credentials'),
            ('Fake Fortnite Check', 'Simulated skin checker'),
            ('Fake Exodus', 'Fake crypto seed phrase'),
            ('Hacker Terminal', 'Fake hacker typer'),
            ('Ransomware Sim', 'Simulated ransomware warn'),
            ('Fake Bruteforcer', 'Simulated brute force'),
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
                  ('faker_suite', 'fake_mail'), ('faker_suite', 'fake_ddos'),
                  ('faker_suite', 'fake_wallet_miner'), ('faker_suite', 'social_botter'),
                  ('faker_suite', 'fake_paypal_otp'), ('faker_suite', 'fake_account_gen'),
                  ('faker_suite', 'fake_fortnite_checker'), ('faker_suite', 'fake_exodus'),
                  ('faker_suite', 'hacker_terminal'), ('faker_suite', 'ransomware_sim'),
                  ('faker_suite', 'fake_bruteforcer'),
                  ('ascii_art', 'run'), ('text_effects', 'zalgo'),
                  ('text_effects', 'creeper'), ('text_effects', 'smallcaps'),
                  ('text_effects', 'bubble'), ('text_effects', 'mirror')]
        self.tool_menu('SIMULATION & GENERATORS', '🎭', [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)], tab=9)

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
        self.tool_menu('NETWORK & DNS', '📡', [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)], tab=10)

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
        self.tool_menu('DEVELOPER TOOLS', '🔧', [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)], tab=11)

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
        self.tool_menu('FILE & IMAGE TOOLS', '📁', [(t[0], t[1], mapped[i]) for i, t in enumerate(tools)], tab=12)

    def menu_settings(self):
        while True:
            cl = get_theme()
            clr()
            print_banner()
            print(cprint_horizontal(cl['sub'], Center.XCenter(f"v{VERSION} | Theme: {self.theme_name} | {PC_USER}@kevbin")))
            print()

            draw_card_box("THEMES & SETTINGS", {
                "1": f"Modern (current)" if self.theme_name == "modern" else "Modern",
                "2": f"Modern Red (current)" if self.theme_name == "modern_red" else "Modern Red",
                "3": f"Modern Purple (current)" if self.theme_name == "modern_purple" else "Modern Purple",
                "4": f"Blue (current)" if self.theme_name == "blue" else "Blue",
                "5": f"Red (current)" if self.theme_name == "red" else "Red",
                "6": f"Purple (current)" if self.theme_name == "purple" else "Purple",
                "7": f"Green (current)" if self.theme_name == "green" else "Green",
                "8": f"Yellow (current)" if self.theme_name == "yellow" else "Yellow",
                "9": f"Rainbow (current)" if self.theme_name == "rainbow" else "Rainbow",
                "U": "Check for updates",
                "0": "Return to Main Menu",
            })

            choice = self.input_choice()
            if choice == '0':
                return
            if choice.lower() == 'u':
                check_update()
                continue

            theme_map = {
                '1': 'modern', '2': 'modern_red', '3': 'modern_purple',
                '4': 'blue', '5': 'red', '6': 'purple',
                '7': 'green', '8': 'yellow', '9': 'rainbow'
            }
            if choice in theme_map:
                new_theme = theme_map[choice]
                self.settings['current_theme'] = new_theme
                save_json(CONFIG_PATH, self.settings)
                self.theme_name = new_theme
                self._refresh_t()
                self.cprint(self.t.head, f"\n  [+] Theme -> {new_theme.upper()}")
                theme_wave(new_theme)
                time.sleep(0.3)

class _Box:
    """`kevbin.box.*` namespace API used by modules."""

    def __init__(self, kt):
        self.kt = kt

    def title(self, text):
        self.kt.box_title(str(text))

    def print(self, text, color=None):
        self.kt.box_print(text, color)

    def code(self, text, width=None):
        self.kt.box_code(text, width)

    def table(self, headers=None, rows=None, title=None):
        self.kt.box_table(headers, rows, title)

    def input(self, prompt, default=None):
        return self.kt.box_input(prompt, default)

    def info(self, text):
        self.kt.cprint(self.kt.t.secondary, str(text))

    def success(self, text):
        self.kt.cprint(self.kt.t.success, str(text))

    def error(self, text):
        self.kt.cprint(self.kt.t.error, str(text))

    def warn(self, text):
        self.kt.cprint(self.kt.t.warning, str(text))

    def confirm(self, prompt, default=True):
        hint = " [y]/n" if default else " y/[n]"
        r = self.kt.input_choice(prompt + hint).strip().lower()
        if not r:
            return default
        return r in ('y', 'yes', '1', 'true', 'on')

    def select(self, label, options):
        for i, o in enumerate(options, 1):
            self.kt.cprint(self.kt.t.txt, f"    [{i}] {o}")
        r = self.kt.input_choice(label + ": ").strip()
        if r.isdigit() and 1 <= int(r) <= len(options):
            return options[int(r) - 1]
        if r:
            return r
        return options[0] if options else ''

def _run_cli(args):
    if '--list' in args:
        print(f"\n  KevTool v{VERSION} — {len(files)} standalone modules:\n")
        for f in files:
            try:
                spec = importlib.util.spec_from_file_location('_l', os.path.join(MODULES_DIR, f + '.py'))
                m = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(m)
                fns = [n for n, v in vars(m).items() if callable(v) and not n.startswith('_')]
                print(f"    {f:<26}{', '.join(fns)[:60]}")
            except Exception as e:
                print(f"    {f:<26}[load failed: {e}]")
        print()
        return False
    if '--tool' in args:
        i = args.index('--tool')
        name = args[i + 1] if len(args) > i + 1 else None
        func = 'run'
        if '--func' in args:
            j = args.index('--func')
            func = args[j + 1] if len(args) > j + 1 else 'run'
        if not name:
            print("  usage: python kevtool.py --tool <module> [--func <fn>]\n"
                  "         python kevtool.py --list")
            return False
        KevTool().run_module(name, func)
        return False
    if '--theme' in args:
        i = args.index('--theme')
        name = args[i + 1] if len(args) > i + 1 else None
        if name and name.lower() in THEMES:
            cfg = get_config()
            cfg['current_theme'] = name.lower()
            save_json(CONFIG_PATH, cfg)
            print(f"  [+] Theme -> {name.upper()}")
    return None

def init_os():
    _enable_ansi()
    tw, th = 120, 38
    try:
        if os.name == 'nt':
            os.system(f'mode con cols={tw} lines={th}')
        sys.stdout.write(f'\x1b[8;{th};{tw}t')
        sys.stdout.flush()
    except Exception:
        pass
    cols, _ = shutil.get_terminal_size()
    if cols < 80:
        print(cprint_horizontal(get_theme()['num'], f"\n  [!] WARNING: Terminal width is {cols} (less than 80)."))
        time.sleep(2.0)

def start_title_scramble(interval=0.001):
    """Flicker the console window title with random strings (Windows)."""
    if os.name != 'nt':
        return None
    try:
        import ctypes
        import threading
    except Exception:
        return None
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*"
    stop = threading.Event()

    def _loop():
        while not stop.is_set():
            n = random.randint(10, 28)
            title = ''.join(random.choice(chars) for _ in range(n))
            try:
                ctypes.windll.kernel32.SetConsoleTitleW(title)
            except Exception:
                pass
            stop.wait(interval)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return t

def main():
    ensure_config()
    ensure_deps()
    args = sys.argv[1:]
    cli = _run_cli(args)
    if cli is not None:
        sys.exit(0 if cli else 1)
    init_os()
    start_title_scramble()
    no_boot = '--no-boot' in args
    no_update = '--no-update' in args
    if not no_boot:
        loading_screen()
    check_update()
    KevTool().main_menu()

if __name__ == '__main__':
    main()
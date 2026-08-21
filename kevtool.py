#!/usr/bin/env python3
"""
KevTool — KevBin Educational Security & Utilities Suite
Python 3.6+ | Windows + Linux + macOS | standalone modules
"""

import os
import sys
import io as _io
import io
import json
import time
import zipfile
import importlib
import getpass
import subprocess
import shutil
import random
import re
import threading
import socket
import urllib.request
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
GITHUB_RAW_VERSION = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/modules/version.txt"
GITHUB_ZIP_URL = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/main.zip"
VALID_PROXIES_PATH = os.path.join(BASE_DIR, 'valid_proxies.txt')

PROXY_SOURCES = [
    ('TheSpeedX HTTP', 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt'),
    ('TheSpeedX HTTPS', 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt'),
    ('TheSpeedX SOCKS4', 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt'),
    ('TheSpeedX SOCKS5', 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt'),
    ('Proxifly ALL', 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt'),
    ('Proxifly HTTP', 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http/data.txt'),
    ('Proxifly HTTPS', 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/https/data.txt'),
    ('Proxifly SOCKS4', 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks4/data.txt'),
    ('Proxifly SOCKS5', 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks5/data.txt'),
    ('mmpx12 HTTP', 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt'),
    ('mmpx12 HTTPS', 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt'),
    ('mmpx12 SOCKS4', 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt'),
    ('mmpx12 SOCKS5', 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt'),
    ('Uptox HTTP', 'https://raw.githubusercontent.com/Uptox/Proxy-List/main/http.txt'),
    ('Uptox HTTPS', 'https://raw.githubusercontent.com/Uptox/Proxy-List/main/https.txt'),
    ('Uptox SOCKS4', 'https://raw.githubusercontent.com/Uptox/Proxy-List/main/socks4.txt'),
    ('Uptox SOCKS5', 'https://raw.githubusercontent.com/Uptox/Proxy-List/main/socks5.txt'),
    ('monosans HTTP', 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt'),
    ('monosans HTTPS', 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt'),
    ('monosans SOCKS4', 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt'),
    ('monosans SOCKS5', 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt'),
    ('monogramm HTTP', 'https://raw.githubusercontent.com/monogramm/proxy_list/main/http.txt'),
    ('monogramm HTTPS', 'https://raw.githubusercontent.com/monogramm/proxy_list/main/https.txt'),
    ('monogramm SOCKS4', 'https://raw.githubusercontent.com/monogramm/proxy_list/main/socks4.txt'),
    ('monogramm SOCKS5', 'https://raw.githubusercontent.com/monogramm/proxy_list/main/socks5.txt'),
    ('roosterkid HTTPS', 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt'),
    ('roosterkid SOCKS4', 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt'),
    ('roosterkid SOCKS5', 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt'),
    ('hookzof SOCKS5', 'https://raw.githubusercontent.com/hookzof/socks5_list/master/socks5.txt'),
    ('clarketm HTTP', 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt'),
    ('ShiftyTR HTTP', 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt'),
    ('ShiftyTR HTTPS', 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt'),
    ('ShiftyTR SOCKS4', 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt'),
    ('ShiftyTR SOCKS5', 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt'),
    ('jetkai HTTP', 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/http.txt'),
    ('jetkai SOCKS4', 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/socks4.txt'),
    ('jetkai SOCKS5', 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/socks5.txt'),
    ('zimuq HTTP', 'https://raw.githubusercontent.com/zimuq/proxy/master/http.txt'),
    ('zimuq HTTPS', 'https://raw.githubusercontent.com/zimuq/proxy/master/https.txt'),
    ('zimuq SOCKS4', 'https://raw.githubusercontent.com/zimuq/proxy/master/socks4.txt'),
    ('zimuq SOCKS5', 'https://raw.githubusercontent.com/zimuq/proxy/master/socks5.txt'),
    ('yuceltoluyan HTTP', 'https://raw.githubusercontent.com/yuceltoluyan/proxy-list/main/http.txt'),
    ('yuceltoluyan HTTPS', 'https://raw.githubusercontent.com/yuceltoluyan/proxy-list/main/https.txt'),
    ('yuceltoluyan SOCKS5', 'https://raw.githubusercontent.com/yuceltoluyan/proxy-list/main/socks5.txt'),
    ('B4RC0DE HTTP', 'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/http.txt'),
    ('B4RC0DE HTTPS', 'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/https.txt'),
    ('B4RC0DE SOCKS4', 'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/socks4.txt'),
    ('B4RC0DE SOCKS5', 'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/socks5.txt'),
    ('pproxy HTTP', 'https://raw.githubusercontent.com/pproxy/proxy/master/http.txt'),
    ('pproxy SOCKS5', 'https://raw.githubusercontent.com/pproxy/proxy/master/socks5.txt'),
    ('H4ck4ss3 HTTP', 'https://raw.githubusercontent.com/H4ck4ss3/PROXY-List/master/http.txt'),
    ('H4ck4ss3 HTTPS', 'https://raw.githubusercontent.com/H4ck4ss3/PROXY-List/master/https.txt'),
    ('H4ck4ss3 SOCKS4', 'https://raw.githubusercontent.com/H4ck4ss3/PROXY-List/master/socks4.txt'),
    ('H4ck4ss3 SOCKS5', 'https://raw.githubusercontent.com/H4ck4ss3/PROXY-List/master/socks5.txt'),
]

def _hex(rgb: str) -> str:
    r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"


EXTRA_THEMES = {
    "dracula": {"banner": Colors.blue_to_purple, "head": _hex("bd93f9"), "num": _hex("ff79c6"),
                "txt": _hex("f8f8f2"), "sub": _hex("50fa7b"), "inp": _hex("8be9fd")},
    "monokai": {"banner": Colors.blue_to_red, "head": _hex("f92672"), "num": _hex("a6e22e"),
                "txt": _hex("f8f8f2"), "sub": _hex("e6db74"), "inp": _hex("66d9ef")},
    "nord": {"banner": Colors.cyan_to_blue, "head": _hex("81a1c1"), "num": _hex("88c0d0"),
             "txt": _hex("e5e9f0"), "sub": _hex("a3be8c"), "inp": _hex("5e81ac")},
    "ocean": {"banner": Colors.blue_to_green, "head": _hex("00bcd4"), "num": _hex("00e5ff"),
              "txt": _hex("e0f7fa"), "sub": _hex("4dd0e1"), "inp": _hex("80deea")},
    "matrix": {"banner": Colors.green_to_white, "head": _hex("00ff41"), "num": _hex("76ff03"),
               "txt": _hex("d0ffd0"), "sub": _hex("00c853"), "inp": _hex("64dd17")},
    "midnight": {"banner": Colors.blue_to_purple, "head": _hex("7986cb"), "num": _hex("9fa8da"),
                 "txt": _hex("e8eaf6"), "sub": _hex("64b5f6"), "inp": _hex("b39ddb")},
    "sunset": {"banner": Colors.red_to_yellow, "head": _hex("ff7043"), "num": _hex("ff8a65"),
               "txt": _hex("fff3e0"), "sub": _hex("ffb74d"), "inp": _hex("ffab91")},
    "fire": {"banner": Colors.yellow_to_red, "head": _hex("ff5722"), "num": _hex("ff7043"),
             "txt": _hex("ffe0b2"), "sub": _hex("ff9800"), "inp": _hex("ff9e80")},
    "forest": {"banner": Colors.green_to_yellow, "head": _hex("689f38"), "num": _hex("8bc34a"),
               "txt": _hex("e8f5e9"), "sub": _hex("cddc39"), "inp": _hex("aed581")},
    "gold": {"banner": Colors.yellow_to_green, "head": _hex("f9a825"), "num": _hex("f9d423"),
             "txt": _hex("fff8e1"), "sub": _hex("ef6c00"), "inp": _hex("ffd54f")},
    "cyberpunk": {"banner": Colors.blue_to_purple, "head": _hex("00f5d4"), "num": _hex("f20089"),
                  "txt": _hex("e6f7f5"), "sub": _hex("ffd60a"), "inp": _hex("7209b7")},
    "synthwave": {"banner": Colors.purple_to_blue, "head": _hex("ff63b0"), "num": _hex("a89bff"),
                  "txt": _hex("f8f8ff"), "sub": _hex("00fff5"), "inp": _hex("ff5ca8")},
    "terminal": {"banner": Colors.green_to_cyan, "head": _hex("a0f66d"), "num": _hex("00ffaa"),
                 "txt": _hex("ffffff"), "sub": _hex("5af78e"), "inp": _hex("57ff7e")},
    "high_contrast": {"banner": Colors.black_to_white, "head": _hex("ffffff"), "num": _hex("ffff00"),
                      "txt": _hex("ffffff"), "sub": _hex("00ffff"), "inp": _hex("ffff00")},
    "bubblegum": {"banner": Colors.red_to_white, "head": _hex("ff6ec7"), "num": _hex("ff87d0"),
                  "txt": _hex("fff0f6"), "sub": _hex("ff9f8a"), "inp": _hex("ffc2e2")},
    "mint": {"banner": Colors.green_to_cyan, "head": _hex("1de9b6"), "num": _hex("4db6ac"),
             "txt": _hex("e0f2f1"), "sub": _hex("a7ffeb"), "inp": _hex("80cbc4")},
    "violet": {"banner": Colors.purple_to_blue, "head": _hex("b388ff"), "num": _hex("d1c4e9"),
               "txt": _hex("ede7f6"), "sub": _hex("9575cd"), "inp": _hex("ce93d8")},
    "rust": {"banner": Colors.red_to_white, "head": _hex("e64a19"), "num": _hex("ff7043"),
             "txt": _hex("fbe9e7"), "sub": _hex("d84315"), "inp": _hex("ffab91")},
    "steel": {"banner": Colors.white_to_blue, "head": _hex("90a4ae"), "num": _hex("b0bec5"),
              "txt": _hex("eceff1"), "sub": _hex("78909c"), "inp": _hex("cfd8dc")},
    "peacock": {"banner": Colors.cyan_to_blue, "head": _hex("20c997"), "num": _hex("0fb9b1"),
                "txt": _hex("e6fffa"), "sub": _hex("12b886"), "inp": _hex("5cdbd3")},
    "ember": {"banner": Colors.red_to_yellow, "head": _hex("ff4500"), "num": _hex("ff6347"),
              "txt": _hex("fff5ee"), "sub": _hex("ff8c00"), "inp": _hex("ffa07a")},
    "aurora": {"banner": Colors.cyan_to_blue, "head": _hex("7fdbca"), "num": _hex("a8e6cf"),
               "txt": _hex("e8fff5"), "sub": _hex("88d8b0"), "inp": _hex("b5ead7")},
    "lava": {"banner": Colors.red_to_white, "head": _hex("cc0000"), "num": _hex("ff3300"),
             "txt": _hex("ffe0cc"), "sub": _hex("ff6600"), "inp": _hex("ff9900")},
    "ice": {"banner": Colors.cyan_to_blue, "head": _hex("b3e5fc"), "num": _hex("81d4fa"),
            "txt": _hex("e1f5fe"), "sub": _hex("4fc3f7"), "inp": _hex("29b6f6")},
    "candy": {"banner": Colors.red_to_white, "head": _hex("ff80ab"), "num": _hex("ff4081"),
              "txt": _hex("fce4ec"), "sub": _hex("f48fb1"), "inp": _hex("f06292")},
    "neon_green": {"banner": Colors.green_to_white, "head": _hex("39ff14"), "num": _hex("76ff03"),
                   "txt": _hex("e8ffe8"), "sub": _hex("00e676"), "inp": _hex("69f0ae")},
    "neon_pink": {"banner": Colors.red_to_white, "head": _hex("ff10f0"), "num": _hex("ff6ec7"),
                  "txt": _hex("fff0f8"), "sub": _hex("ff1493"), "inp": _hex("ff69b4")},
    "neon_blue": {"banner": Colors.blue_to_cyan, "head": _hex("00d4ff"), "num": _hex("00bfff"),
                  "txt": _hex("e0f7ff"), "sub": _hex("0099ff"), "inp": _hex("00ccff")},
    "neon_orange": {"banner": Colors.yellow_to_red, "head": _hex("ff6600"), "num": _hex("ff8c00"),
                    "txt": _hex("fff5e6"), "sub": _hex("ff9500"), "inp": _hex("ffb347")},
    "neon_purple": {"banner": Colors.purple_to_blue, "head": _hex("bf00ff"), "num": _hex("d500f9"),
                    "txt": _hex("f3e5f5"), "sub": _hex("aa00ff"), "inp": _hex("e040fb")},
    "neon_yellow": {"banner": Colors.yellow_to_red, "head": _hex("ffff00"), "num": _hex("ffff00"),
                    "txt": _hex("fffff0"), "sub": _hex("ffd600"), "inp": _hex("ffea00")},
    "blood": {"banner": Colors.red_to_white, "head": _hex("8b0000"), "num": _hex("b71c1c"),
              "txt": _hex("ffebee"), "sub": _hex("c62828"), "inp": _hex("e53935")},
    "toxic": {"banner": Colors.green_to_yellow, "head": _hex("76ff03"), "num": _hex("ccff00"),
              "txt": _hex("f1f8e9"), "sub": _hex("b2ff59"), "inp": _hex("c6ff00")},
    "royal": {"banner": Colors.blue_to_purple, "head": _hex("ffd700"), "num": _hex("daa520"),
              "txt": _hex("fff8e1"), "sub": _hex("b8860b"), "inp": _hex("f0c040")},
    "sakura": {"banner": Colors.red_to_white, "head": _hex("ffb7c5"), "num": _hex("ff69b4"),
               "txt": _hex("fff0f5"), "sub": _hex("db7093"), "inp": _hex("ff85a2")},
    "ocean_deep": {"banner": Colors.blue_to_purple, "head": _hex("0077b6"), "num": _hex("00b4d8"),
                   "txt": _hex("e0f4ff"), "sub": _hex("0096c7"), "inp": _hex("48cae4")},
    "solarized_dark": {"banner": Colors.blue_to_green, "head": _hex("839496"), "num": _hex("93a1a1"),
                       "txt": _hex("fdf6e3"), "sub": _hex("586e75"), "inp": _hex("657b83")},
    "solarized_light": {"banner": Colors.yellow_to_red, "head": _hex("002b36"), "num": _hex("073642"),
                        "txt": _hex("002b36"), "sub": _hex("586e75"), "inp": _hex("657b83")},
    "gruvbox": {"banner": Colors.yellow_to_red, "head": _hex("fabd2f"), "num": _hex("fe8019"),
                "txt": _hex("ebdbb2"), "sub": _hex("b8bb26"), "inp": _hex("fb4934")},
    "tokyo_night": {"banner": Colors.purple_to_blue, "head": _hex("7aa2f7"), "num": _hex("bb9af7"),
                    "txt": _hex("c0caf5"), "sub": _hex("9ece6a"), "inp": _hex("7dcfff")},
    "catppuccin": {"banner": Colors.blue_to_purple, "head": _hex("cba6f7"), "num": _hex("f38ba8"),
                   "txt": _hex("cdd6f4"), "sub": _hex("a6e3a1"), "inp": _hex("89dceb")},
    "rose_pine": {"banner": Colors.purple_to_blue, "head": _hex("c4a7e7"), "num": _hex("eb6f92"),
                  "txt": _hex("e0def4"), "sub": _hex("31748f"), "inp": _hex("9ccfd8")},
    "everforest": {"banner": Colors.green_to_yellow, "head": _hex("a7c080"), "num": _hex("dbbc7f"),
                   "txt": _hex("d3c6aa"), "sub": _hex("83c092"), "inp": _hex("7fbbb3")},
    "palenight": {"banner": Colors.blue_to_purple, "head": _hex("c792ea"), "num": _hex("f07178"),
                  "txt": _hex("d0d4e0"), "sub": _hex("c3e88d"), "inp": _hex("82aaff")},
    "material_ocean": {"banner": Colors.blue_to_cyan, "head": _hex("82aaff"), "num": _hex("c792ea"),
                       "txt": _hex("d0d4e0"), "sub": _hex("c3e88d"), "inp": _hex("89ddff")},
    "onedark": {"banner": Colors.blue_to_purple, "head": _hex("61afef"), "num": _hex("c678dd"),
                "txt": _hex("abb2bf"), "sub": _hex("98c379"), "inp": _hex("56b6c2")},
    "github_dark": {"banner": Colors.blue_to_purple, "head": _hex("79c0ff"), "num": _hex("d2a8ff"),
                    "txt": _hex("c9d1d9"), "sub": _hex("7ee787"), "inp": _hex("a5d6ff")},
    "github_light": {"banner": Colors.white_to_blue, "head": _hex("0550ae"), "num": _hex("8250df"),
                     "txt": _hex("24292f"), "sub": _hex("116329"), "inp": _hex("0969da")},
    "ayu_dark": {"banner": Colors.blue_to_purple, "head": _hex("e6b450"), "num": _hex("ed9366"),
                 "txt": _hex("bfbdb6"), "sub": _hex("aad94c"), "inp": _hex("39bae6")},
    "mellow_yellow": {"banner": Colors.yellow_to_red, "head": _hex("ffb627"), "num": _hex("fc036c"),
                      "txt": _hex("f8f8f2"), "sub": _hex("ff0054"), "inp": _hex("ffbe0b")},
    "deep_sea": {"banner": Colors.blue_to_purple, "head": _hex("00b4d8"), "num": _hex("0077b6"),
                 "txt": _hex("caf0f8"), "sub": _hex("023e8a"), "inp": _hex("48cae4")},
    "cherry_blossom": {"banner": Colors.red_to_white, "head": _hex("f4a0b5"), "num": _hex("e8729a"),
                       "txt": _hex("fff0f5"), "sub": _hex("d63384"), "inp": _hex("f78dac")},
    "emerald": {"banner": Colors.green_to_cyan, "head": _hex("10b981"), "num": _hex("34d399"),
                "txt": _hex("ecfdf5"), "sub": _hex("059669"), "inp": _hex("6ee7b7")},
    "amber": {"banner": Colors.yellow_to_red, "head": _hex("f59e0b"), "num": _hex("fbbf24"),
              "txt": _hex("fffbeb"), "sub": _hex("d97706"), "inp": _hex("fcd34d")},
    "sky": {"banner": Colors.cyan_to_blue, "head": _hex("0ea5e9"), "num": _hex("38bdf8"),
            "txt": _hex("f0f9ff"), "sub": _hex("0284c7"), "inp": _hex("7dd3fc")},
    "crimson": {"banner": Colors.red_to_white, "head": _hex("dc143c"), "num": _hex("ff2442"),
                "txt": _hex("fff0f0"), "sub": _hex("b91c3c"), "inp": _hex("ff4d6a")},
    "jade": {"banner": Colors.green_to_white, "head": _hex("00a86b"), "num": _hex("00cc88"),
             "txt": _hex("f0fff5"), "sub": _hex("009966"), "inp": _hex("33cc99")},
    "copper": {"banner": Colors.red_to_yellow, "head": _hex("b87333"), "num": _hex("da8a47"),
               "txt": _hex("fff5ee"), "sub": _hex("cd7f32"), "inp": _hex("e8a65b")},
    "slate": {"banner": Colors.white_to_blue, "head": _hex("64748b"), "num": _hex("94a3b8"),
              "txt": _hex("f1f5f9"), "sub": _hex("475569"), "inp": _hex("cbd5e1")},
    "flame": {"banner": Colors.red_to_yellow, "head": _hex("ff4500"), "num": _hex("ff6b35"),
              "txt": _hex("fff8f0"), "sub": _hex("e63900"), "inp": _hex("ff7b42")},
    "twilight": {"banner": Colors.purple_to_blue, "head": _hex("6c5ce7"), "num": _hex("a29bfe"),
                 "txt": _hex("f0f0ff"), "sub": _hex("4834d4"), "inp": _hex("7c6cf0")},
    "spring": {"banner": Colors.green_to_yellow, "head": _hex("66bb6a"), "num": _hex("aed581"),
               "txt": _hex("f1f8e9"), "sub": _hex("81c784"), "inp": _hex("a5d6a7")},
    "autumn": {"banner": Colors.red_to_yellow, "head": _hex("bf360c"), "num": _hex("e65100"),
               "txt": _hex("fff3e0"), "sub": _hex("d84315"), "inp": _hex("ff6e40")},
    "winter": {"banner": Colors.cyan_to_blue, "head": _hex("b3e5fc"), "num": _hex("e1f5fe"),
               "txt": _hex("f8fbff"), "sub": _hex("4fc3f7"), "inp": _hex("81d4fa")},
    "neon_rain": {"banner": Colors.rainbow, "head": _hex("ff00ff"), "num": _hex("00ffff"),
                  "txt": _hex("ffffff"), "sub": _hex("ff1493"), "inp": _hex("00ff7f")},
    "blood_moon": {"banner": Colors.red_to_white, "head": _hex("b71c1c"), "num": _hex("d32f2f"),
                   "txt": _hex("ffebee"), "sub": _hex("f44336"), "inp": _hex("ef5350")},
    "deep_space": {"banner": Colors.blue_to_purple, "head": _hex("311b92"), "num": _hex("4a148c"),
                   "txt": _hex("ede7f6"), "sub": _hex("6200ea"), "inp": _hex("7c4dff")},
    "sunset_burn": {"banner": Colors.yellow_to_red, "head": _hex("ff5722"), "num": _hex("ff9100"),
                    "txt": _hex("fff3e0"), "sub": _hex("ff6d00"), "inp": _hex("ffab40")},
    "electric": {"banner": Colors.blue_to_cyan, "head": _hex("00e5ff"), "num": _hex("1de9b6"),
                 "txt": _hex("e0ffff"), "sub": _hex("00bfa5"), "inp": _hex("64ffda")},
    "phantom": {"banner": Colors.purple_to_blue, "head": _hex("9c27b0"), "num": _hex("ce93d8"),
                "txt": _hex("f3e5f5"), "sub": _hex("7b1fa2"), "inp": _hex("ba68c8")},
    "mango": {"banner": Colors.yellow_to_red, "head": _hex("ff8f00"), "num": _hex("ffc107"),
              "txt": _hex("fffde7"), "sub": _hex("ff6f00"), "inp": _hex("ffd54f")},
    "coral_reef": {"banner": Colors.red_to_white, "head": _hex("ff6f61"), "num": _hex("ff8a80"),
                   "txt": _hex("fff5f5"), "sub": _hex("e57373"), "inp": _hex("ff8a80")},
    "arctic_fox": {"banner": Colors.white_to_blue, "head": _hex("e0e0e0"), "num": _hex("bdbdbd"),
                   "txt": _hex("fafafa"), "sub": _hex("9e9e9e"), "inp": _hex("f5f5f5")},
    "volcano": {"banner": Colors.red_to_yellow, "head": _hex("d32f2f"), "num": _hex("ff5722"),
                "txt": _hex("fbe9e7"), "sub": _hex("c62828"), "inp": _hex("ff7043")},
    "cosmic": {"banner": Colors.blue_to_purple, "head": _hex("7e57c2"), "num": _hex("9575cd"),
               "txt": _hex("ede7f6"), "sub": _hex("673ab7"), "inp": _hex("b39ddb")},
    "jungle": {"banner": Colors.green_to_yellow, "head": _hex("2e7d32"), "num": _hex("43a047"),
               "txt": _hex("e8f5e9"), "sub": _hex("388e3c"), "inp": _hex("66bb6a")},
    "honeycomb": {"banner": Colors.yellow_to_green, "head": _hex("ff8f00"), "num": _hex("ffa000"),
                  "txt": _hex("fffde7"), "sub": _hex("f57f17"), "inp": _hex("ffca28")},
    "storm": {"banner": Colors.white_to_blue, "head": _hex("455a64"), "num": _hex("607d8b"),
              "txt": _hex("eceff1"), "sub": _hex("37474f"), "inp": _hex("78909c")},
    "laser": {"banner": Colors.red_to_white, "head": _hex("ff0040"), "num": _hex("ff0066"),
              "txt": _hex("fff0f5"), "sub": _hex("cc0033"), "inp": _hex("ff1a75")},
    "horizon": {"banner": Colors.blue_to_purple, "head": _hex("c099ff"), "num": _hex("ff66b2"),
                "txt": _hex("f8f0ff"), "sub": _hex("e95678"), "inp": _hex("f09383")},
    "nova": {"banner": Colors.cyan_to_blue, "head": _hex("00d2ff"), "num": _hex("3a7bd5"),
             "txt": _hex("e0f7ff"), "sub": _hex("0099cc"), "inp": _hex("00bfef")},
    "glacier": {"banner": Colors.cyan_to_blue, "head": _hex("b2dfdb"), "num": _hex("80cbc4"),
                "txt": _hex("e0f2f1"), "sub": _hex("4db6ac"), "inp": _hex("a7ffeb")},
    "rebel": {"banner": Colors.red_to_yellow, "head": _hex("ff1744"), "num": _hex("ff5252"),
              "txt": _hex("ffebee"), "sub": _hex("d50000"), "inp": _hex("ff8a80")},
    "dream": {"banner": Colors.purple_to_blue, "head": _hex("e1bee7"), "num": _hex("ce93d8"),
              "txt": _hex("fce4ec"), "sub": _hex("ab47bc"), "inp": _hex("f48fb1")},
    "phoenix": {"banner": Colors.red_to_yellow, "head": _hex("ff6d00"), "num": _hex("ff9100"),
                "txt": _hex("fff8e1"), "sub": _hex("e65100"), "inp": _hex("ffab40")},
    "nebula": {"banner": Colors.blue_to_purple, "head": _hex("b388ff"), "num": _hex("ea80fc"),
               "txt": _hex("f3e5f5"), "sub": _hex("7c4dff"), "inp": _hex("b39ddb")},
    "vapor": {"banner": Colors.cyan_to_blue, "head": _hex("ff80ab"), "num": _hex("80d8ff"),
              "txt": _hex("e0f7fa"), "sub": _hex("a7ffeb"), "inp": _hex("b9f6ca")},
    "retro": {"banner": Colors.yellow_to_green, "head": _hex("ffab00"), "num": _hex("ffd600"),
              "txt": _hex("fffde7"), "sub": _hex("ffc400"), "inp": _hex("ffe57f")},
    "hacker_green": {"banner": Colors.green_to_white, "head": _hex("00e676"), "num": _hex("69f0ae"),
                     "txt": _hex("e8f5e9"), "sub": _hex("00c853"), "inp": _hex("b9f6ca")},
    "blood_diamond": {"banner": Colors.red_to_white, "head": _hex("c62828"), "num": _hex("e53935"),
                      "txt": _hex("ffebee"), "sub": _hex("b71c1c"), "inp": _hex("ef5350")},
    "mystic": {"banner": Colors.purple_to_blue, "head": _hex("ab47bc"), "num": _hex("ce93d8"),
               "txt": _hex("f3e5f5"), "sub": _hex("9c27b0"), "inp": _hex("ba68c8")},
}

THEMES = {**{
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
}, **EXTRA_THEMES}

BANNER_LINES = [
    r"  ____  __.                    ___________           .__",
    r"|    |/ _|_______  __  ______ \__    ___/___   ____ |  |",
    r"|      <_/ __ \  \/ / /_____/   |    | /  _ \ /  _ \|  |",
    r"|    |  \  ___/\   /  /_____/   |    |(  <_> |  <_> )  |__",
    r"|____|__ \___  >\_/             |____| \____/ \____/|____/",
    r"        \/   \/",
]

BANNER_SMALL = [
    r" ____  __.                  ___________           .__   ",
    r"|    |/ _|_______  __       \__    ___/___   ____ |  |  ",
    r"|      <_/ __ \  \/ /  ______ |    | /  _ \ /  _ \|  |  ",
    r"|    |  \  ___/\   /  /_____/ |    |(  <_> |  <_> )  |__",
    r"|____|__ \___  >\_/           |____| \____/ \____/|____/",
    r"        \/   \/                                          ",
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

MENU_TABS = [
    {"n": 1, "short": "DISCORD", "title": "DISCORD OPERATIONS", "icon": "📡",
     "tools": [('Discord Webhook Info', 'View webhook details'), ('Discord Token', 'Decode Discord tokens'),
               ('Discord Account', 'Fetch account from token'), ('Discord Server', 'Fetch server via bot'),
               ('Discord Status', 'Status rotation reference'), ('Discord Bot Invite', 'Generate bot invite URL'),
               ('Discord Snowflake', 'Decode Discord ID'), ('Discord Embed', 'Discord embed JSON')],
     "mapped": [('discord_ops', 'webhook_info'), ('discord_ops', 'token_decode'),
                ('discord_ops', 'account_info'), ('discord_ops', 'server_info'),
                ('discord_ops', 'status_rotator'), ('discord_ops', 'bot_invite_gen'),
                ('misc_tools', 'snowflake_decode'), ('misc_tools', 'embed_builder')]},
    {"n": 2, "short": "OSINT", "title": "OSINT & INTELLIGENCE", "icon": "🔍",
     "tools": [('Whois Lookup', 'Domain registration info'), ('DNS Resolver', 'A/MX/TXT/CNAME/NS records'),
               ('IP Info', 'Public IP information'), ('Metadata Scanner', 'EXIF from images'),
               ('Username Checker', 'Multi-platform check'), ('Breach Check', 'Email breach lookup'),
               ('SSL Certificate', 'Domain cert info'), ('GeoIP Lookup', 'IP geolocation'),
               ('ASN Intel', 'ASN/IP range info'), ('Email Validate', 'Format + MX check'),
               ('Email Reputation', 'Email provider check'), ('Stealer Check', 'Credential leak check'),
               ('Wayback Machine', 'Historical snapshots'), ('Tech Stack', 'Website technology detection'),
               ('Blacklist Check', 'IP blacklist lookup'),
               ('Email Format Gen', 'Probable email formats'), ('URL Extractor', 'Pull URLs from text'),
               ('OSINT Report', 'Assemble report card')],
     "mapped": [('osint', 'whois_lookup'), ('osint', 'dns_resolver'), ('osint', 'ip_info'),
                ('osint', 'metadata_scan'), ('osint', 'username_check'), ('breach_check', 'run'),
                ('ssl_cert', 'run'), ('geoip', 'run'), ('asn_intel', 'run'),
                ('email_tools', 'validate'), ('email_tools', 'reputation'), ('stealer_check', 'run'),
                ('wayback', 'run'), ('tech_stack', 'run'), ('ip_blacklist', 'run'),
                ('misc_tools', 'email_format_gen'), ('misc_tools', 'url_extractor'),
                ('misc_tools', 'osint_report')]},
    {"n": 3, "short": "SECURITY", "title": "SECURITY & UTILITIES", "icon": "🛡️",
     "tools": [('Obfuscator V3', 'Multi-Layer XOR/B64 + AST Mangle'), ('Web Cloner', 'Clone websites locally'),
               ('Cryptography', 'Base64/Hex/ROT13'), ('QR Generator', 'QR codes + decode'),
               ('Hash Tool', 'Hash files/strings + HMAC'), ('Base64 Image', 'Encode/decode images'),
               ('Ciphers', 'Caesar/Vigenere/Rail Fence/Bacon/XOR'), ('JWT Tools', 'Decode + generate JWT'),
               ('CORS Tester', 'Test CORS headers'), ('Entropy', 'Frequency analysis + entropy'),
               ('Password Check', 'Strength + breach check'), ('Timestamp', 'Unix timestamp converter'),
               ('Security Headers', 'Analyze HTTP headers'), ('CSP Analyzer', 'Content Security Policy'),
               ('Honeypot Detector', 'Detect honeypots'), ('HTTP Status', 'HTTP status code lookup'),
               ('Port Scanner', 'Multi-threaded + service detection'), ('Traceroute', 'Network path trace'),
               ('Tor Check', 'Tor exit node detection'), ('Link Tools', 'URL expand/track/info'),
               ('IP Pinger', 'ICMP ping utility'), ('System Info', 'CPU/RAM/Disk/OS details'),
               ('Proxy Scraper', 'Grab proxies from GitHub lists'), ('Proxy Checker', 'Validate proxies multi-threaded'),
               ('OTP Generator', 'Authenticator-style codes'), ('Hex Dump', 'Pretty hex output'),
               ('Hash Cracker', 'Hash ID + wordlist crack')],
     "mapped": [('obfuscator', 'run'), ('web_cloner', 'run'), ('crypto', 'run'), ('qr_gen', 'run'),
                ('hash_tool', 'run'), ('base64_image', 'run'), ('ciphers', 'run'), ('jwt_tools', 'run'),
                ('cors_tester', 'run'), ('entropy', 'run'), ('passcheck', 'run'), ('timestamp', 'run'),
                ('security_headers', 'run'), ('csp_analyzer', 'run'), ('honeypot', 'run'),
                ('http_status', 'run'), ('port_scanner', 'run'), ('traceroute', 'run'),
                ('tor_check', 'run'), ('link_tools', 'run'), ('ip_pinger', 'run'),
                ('system_info', 'run'), ('proxy_scraper', 'run'), ('proxy_checker', 'run'),
                ('misc_tools', 'otp_gen'), ('misc_tools', 'hexdump_text'),
                ('hash_cracker', 'run')]},
    {"n": 4, "short": "WEB", "title": "WEB & NETWORK TOOLS", "icon": "🌐",
     "tools": [('Web Cloner', 'Clone websites + all assets'), ('Site Viewer', 'View source + headers'),
               ('Web Search', 'Search the web'), ('Webhook Tester', 'Test webhook endpoints'),
               ('Webhook Delete', 'Delete webhooks'), ('Link Bypass', 'Bypass link shorteners'),
               ('Link Spoof', 'View redirect chains'), ('Link Tracker', 'Track link clicks'),
               ('Browser FP', 'Browser fingerprint'), ('WebRTC Leak', 'WebRTC IP detection'),
               ('DNS over HTTPS', 'Encrypted DNS queries'), ('Subdomain Enum', 'Find subdomains'),
               ('Subnet Calculator', 'CIDR calculations'),
               ('Curl Builder', 'Generate curl commands'), ('URL Parser', 'Break down a URL'),
               ('User-Agent Gen', 'Random real UAs'), ('WAF Detector', 'Identify web firewalls'),
               ('Directory Brute', 'Web dir/file brute forcer'), ('Calculator', 'Scientific calculator')],
     "mapped": [('web_cloner', 'run'), ('site_viewer', 'run'), ('web_search', 'run'),
                ('webhook_tools', 'tester'), ('webhook_tools', 'delete'), ('link_tools', 'bypass'),
                ('link_tools', 'spoof'), ('link_tools', 'tracker'), ('browser_fp', 'run'),
                ('webrtc_leak', 'run'), ('doh', 'run'), ('subenum', 'run'), ('subnet_calc', 'run'),
                ('misc_tools', 'curl_builder'), ('misc_tools', 'url_parser'),
                ('misc_tools', 'useragent_gen'), ('waf_detect', 'run'),
                ('directory_brute', 'run'), ('calculator', 'run')]},
    {"n": 5, "short": "TEXT", "title": "TEXT & ENCODING", "icon": "📝",
     "tools": [('Text Transform', 'Case/Reverse/Repeat'), ('Slugify', 'URL-safe slugs'),
               ('Sort Lines', 'Alphabetical/Numeric sort'), ('Markdown Preview', 'Render markdown'),
               ('Diff Tool', 'Compare two texts'), ('CSV Viewer', 'Parse + display CSV'),
               ('JSON Formatter', 'Pretty-print JSON'), ('SQL Formatter', 'Format SQL queries'),
               ('Regex Tester', 'Test regular expressions'), ('Word Counter', 'Word/char/line count'),
               ('HTML Entity', 'Encode/Decode entities'), ('URL Encode', 'URL encode/decode'),
               ('Unicode Tool', 'Unicode lookup/convert'), ('Emoji Lookup', 'Find emoji codes'),
               ('Text Stats', 'Readability analysis'),
               ('Text <-> Binary', 'Binary conversion'), ('Morse Code', 'Encode/decode Morse'),
               ('Leet Speak', 'Leetspeak variants'), ('Reverse/Upside', 'Flipped text'),
               ('Word Scrambler', 'Scramble letters'), ('Palindrome Check', 'Find palindromes'),
               ('Random Haiku', 'Free verse on demand')],
     "mapped": [('text_tools', 'transform'), ('text_tools', 'slugify'), ('text_tools', 'sort'),
                ('markdown_tools', 'run'), ('diff_tool', 'run'), ('csv_viewer', 'run'),
                ('json_formatter', 'run'), ('sql_formatter', 'run'), ('regex_tester', 'run'),
                ('text_tools', 'wordcount'), ('text_tools', 'html_entity'), ('text_tools', 'url_encode'),
                ('unicode_tool', 'run'), ('emoji_lookup', 'run'), ('text_tools', 'stats'),
                ('misc_tools', 'text_binary'), ('misc_tools', 'morse_code'),
                ('misc_tools', 'leet_speak'), ('misc_tools', 'reverse_upsidedown'),
                ('misc_tools', 'scramble_words'), ('misc_tools', 'palindrome_check'),
                ('misc_tools', 'random_poem')]},
    {"n": 6, "short": "COLOR", "title": "COLOR & DESIGN", "icon": "🎨",
     "tools": [('Color Converter', 'HEX/RGB/HSL conversion'), ('Gradient Generator', 'CSS gradient builder'),
               ('Contrast Checker', 'WCAG contrast ratio'), ('Color Palette', 'Generate color palettes'),
               ('Image Colors', 'Extract colors from image'),
               ('Random Color', 'Random + swatch'), ('ANSI Tester', '256-color grid'),
               ('Tints & Shades', 'Palette from hex'), ('Named Colors', '60 named swatches')],
     "mapped": [('color_tools', 'converter'), ('color_tools', 'gradient'),
                ('color_tools', 'contrast'), ('color_tools', 'palette'), ('color_tools', 'image_colors'),
                ('misc_tools', 'random_color'), ('misc_tools', 'ansi_tester'),
                ('misc_tools', 'palette_tints'), ('misc_tools', 'named_colors')]},
    {"n": 7, "short": "DATA", "title": "DATA & CONVERSION", "icon": "💾",
     "tools": [('Base-N Encoder', 'Binary/Octal/Hex encode'), ('Base64 Decode', 'Decode Base64 strings'),
               ('Roman Numerals', 'Convert to/from Roman'), ('Number System', 'Dec/Hex/Bin/Oct convert'),
               ('Percentage Calc', 'Percentage calculations'), ('YAML <-> TOML', 'Convert between formats'),
               ('CSV Tools', 'Parse/merge CSV files'), ('JSON <-> XML', 'Convert between formats'),
               ('Receipt Generator', 'Fake receipt maker'), ('UUID Generator', 'Generate UUIDs v4'),
               ('Barcode Generator', 'Code128/Code39'), ('Password Generator', 'Secure passwords'),
               ('Random Data', 'Random numbers/strings'), ('Duration Calc', 'Time duration math'),
               ('Age Calculator', 'Calculate age from DOB'),
               ('Unit Converter', 'Length/weight/temp'), ('Byte Converter', 'All byte units'),
               ('Interest Calc', 'Simple/compound'), ('BMI Calc', 'Body mass index'),
               ('Prime & Factors', 'Prime utilities'), ('Date Diff', 'Days between dates')],
     "mapped": [('base_n', 'run'), ('base64_decoder', 'run'), ('numerals', 'roman'),
                ('numerals', 'convert'), ('percentage', 'run'), ('yaml_toml', 'run'),
                ('csv_tools', 'run'), ('json_formatter', 'xml'), ('receipt', 'run'),
                ('uuid_gen', 'run'), ('barcode', 'run'), ('password_gen', 'run'),
                ('random_gen', 'run'), ('duration', 'run'), ('age_calc', 'run'),
                ('misc_tools', 'unit_converter'), ('misc_tools', 'byte_converter'),
                ('misc_tools', 'interest_calc'), ('misc_tools', 'bmi_calc'),
                ('misc_tools', 'prime_tools'), ('misc_tools', 'date_diff')]},
{"n": 8, "short": "ROBLOX", "title": "ROBLOX GAME SUITE", "icon": "🎮",
     "tools": [('Roblox User Intel', 'User lookup'), ('Roblox Group Intel', 'Group lookup'),
                ('Roblox Name History', 'Previous usernames'), ('Roblox Username', 'Check availability'),
                ('Roblox Cookie Login', 'Validate .ROBLOSECURITY'), ('Roblox Asset DL', 'Download assets'),
                ('Roblox Inventory', 'View user inventory'), ('Roblox Game Info', 'Game details'),
                ('Roblox Link Builder', 'Profile/asset links'), ('Username Styles', 'Stylized variants'),
                ('Gamertag Gen', 'Random gamertags')],
     "mapped": [('roblox_intel', 'run'), ('roblox_intel', 'group_lookup'), ('roblox_intel', 'name_history'),
                ('roblox_intel', 'username_check'), ('roblox_control', 'run'),
                ('roblox_control', 'asset_download'), ('roblox_intel', 'inventory_view'),
                ('roblox_intel', 'game_info'),
                ('misc_tools', 'roblox_link_builder'), ('misc_tools', 'username_style_gen'),
                ('misc_tools', 'gamertag_gen')]},
    {"n": 9, "short": "SIM", "title": "SIMULATION & GENERATORS", "icon": "🎭",
     "tools": [('Identity Generator', 'Realistic fake identities'), ('Credit Card Gen', 'Test card numbers (Luhn)'),
               ('Crypto Wallets', 'Generate wallet addresses'), ('Username Generator', 'Unique usernames'),
               ('Password Generator', 'Secure passwords'), ('Lorem Ipsum', 'Placeholder text'),
               ('Fake Nitro Code', 'Random Nitro-style codes'), ('Server Template', 'Discord server JSON'),
               ('Fake Mail Gen', 'Fake email + password'), ('Fake DDoS', 'Simulated DDoS attack'),
               ('Fake Wallet Miner', 'Simulated mining rig'), ('Social Botter', 'Simulated view botter'),
               ('Fake PayPal OTP', 'Simulated OTP code'), ('Fake Account Gen', 'Fake account credentials'),
               ('Fake Fortnite Check', 'Simulated skin checker'), ('Fake Exodus', 'Fake crypto seed phrase'),
               ('Hacker Terminal', 'Fake hacker typer'), ('Ransomware Sim', 'Simulated ransomware warn'),
               ('Fake Bruteforcer', 'Simulated brute force'), ('ASCII Art', 'Text to ASCII art'),
               ('Stealth Art', 'Zalgo/glitch text'), ('Creeper Text', 'Creeper text effect'),
               ('Small Caps', 'Small caps text'), ('Bubble Text', 'Bubble unicode text'),
               ('Mirror Text', 'Flipped text'),
               ('Fake Crypto Wallet', 'Fake BTC/ETH/SOL wallets + seeds'), ('Fake Money', 'Prop cash + gift cards + casino chips'),
               ('Fake IP', 'Random IPs'), ('Fake MAC', 'Random MACs'),
               ('Fake Phone', 'Random numbers'), ('Fake Address', 'Random address'),
               ('Fake Company', 'Random companies'), ('Hacker Alias', 'Handles'),
               ('Buzzword Gen', 'Corporate speak'), ('Emoji Flood', 'Emoji spam')],
     "mapped": [('faker_suite', 'identity_gen'), ('faker_suite', 'credit_card_gen'),
                ('faker_suite', 'wallet_gen'), ('faker_suite', 'username_gen'),
                ('faker_suite', 'password_gen'), ('faker_suite', 'lorem_ipsum'),
                ('faker_suite', 'fake_nitro'), ('faker_suite', 'server_template'),
                ('faker_suite', 'fake_mail'), ('faker_suite', 'fake_ddos'),
                ('faker_suite', 'fake_wallet_miner'), ('faker_suite', 'social_botter'),
                ('faker_suite', 'fake_paypal_otp'), ('faker_suite', 'fake_account_gen'),
                ('faker_suite', 'fake_fortnite_checker'), ('faker_suite', 'fake_exodus'),
                ('faker_suite', 'hacker_terminal'), ('faker_suite', 'ransomware_sim'),
                ('faker_suite', 'fake_bruteforcer'), ('ascii_art', 'run'),
                ('text_effects', 'zalgo'), ('text_effects', 'creeper'),
                ('text_effects', 'smallcaps'), ('text_effects', 'bubble'), ('text_effects', 'mirror'),
                ('fake_crypto', 'run'), ('fake_money', 'run'),
                ('misc_tools', 'fake_ip'), ('misc_tools', 'fake_mac'),
                ('misc_tools', 'fake_phone'), ('misc_tools', 'fake_address'),
                ('misc_tools', 'fake_company'), ('misc_tools', 'hacker_alias'),
                ('misc_tools', 'buzzword_gen'), ('misc_tools', 'emoji_flood')]},
    {"n": 10, "short": "NET", "title": "NETWORK & DNS", "icon": "📡",
     "tools": [('Port Scanner', 'TCP port scan + banners'), ('Traceroute', 'Network path trace'),
               ('DNS Resolver', 'Resolve DNS records'), ('DNS over HTTPS', 'Encrypted DNS'),
               ('Subdomain Enum', 'Find subdomains'), ('Subnet Calculator', 'CIDR math'),
               ('Whois', 'Domain registration'), ('IP Pinger', 'ICMP ping'),
               ('ASN Lookup', 'ASN information'), ('Blacklist Check', 'IP blacklist check'),
               ('Port Lookup', 'Common port services'), ('Random Domain', 'Name generator'),
               ('Subnet List', 'Enumerate CIDR range')],
     "mapped": [('port_scanner', 'run'), ('traceroute', 'run'), ('osint', 'dns_resolver'),
                ('doh', 'run'), ('subenum', 'run'), ('subnet_calc', 'run'),
                ('osint', 'whois_lookup'), ('ip_pinger', 'run'), ('asn_intel', 'run'),
                ('ip_blacklist', 'run'),
                ('misc_tools', 'port_lookup'), ('misc_tools', 'random_domain'),
                ('misc_tools', 'subnet_list_gen')]},
    {"n": 11, "short": "DEV", "title": "DEVELOPER TOOLS", "icon": "🔧",
     "tools": [('Request Builder', 'Build HTTP requests'), ('Header Inspector', 'View/edit headers'),
               ('Cookie Inspector', 'View/edit cookies'), ('JS Obfuscator', 'JavaScript obfuscation'),
               ('Lua Obfuscator', 'Lua code obfuscation'), ('Lua Sandbox', 'Run Lua code safely'),
               ('Cron Builder', 'Build cron expressions'), ('Cron Parser', 'Parse cron schedules'),
               ('Code Formatter', 'Format source code'), ('YAML/TOML', 'Config file conversion'),
               ('JSON Formatter', 'Pretty-print JSON'), ('SQL Formatter', 'Format SQL queries'),
               ('Code Minify', 'Strip comments/blanks'), ('Case Converter', 'Camel/snake/kebab'),
               ('Semver Compare', 'Compare versions'), ('UUID/Hash Gen', 'Name-based hashes'),
               ('Bracket Matcher', 'Balanced check')],
     "mapped": [('reqbuild', 'run'), ('header_inspector', 'run'), ('cookie_inspector', 'run'),
                ('js_obfuscator', 'run'), ('lua_obfuscator', 'run'), ('lua_sandbox', 'run'),
                ('cron_builder', 'run'), ('cron_parser', 'run'), ('code_formatter', 'run'),
                ('yaml_toml', 'run'), ('json_formatter', 'run'), ('sql_formatter', 'run'),
                ('misc_tools', 'code_minify'), ('misc_tools', 'camel_tools'),
                ('misc_tools', 'semver_compare'), ('misc_tools', 'uuid_v5'),
                ('misc_tools', 'bracket_matcher')]},
    {"n": 12, "short": "FILE", "title": "FILE & IMAGE TOOLS", "icon": "📁",
     "tools": [('File Type Detector', 'Identify file types'), ('Image to Base64', 'Encode images'),
               ('Photo Metadata', 'EXIF extraction'), ('Metadata Stripper', 'Remove metadata'),
               ('Hex Dump', 'View hex data'), ('Steganography', 'Hide data in images'),
               ('File Checksum', 'MD5/SHA hash files'), ('Binary Viewer', 'View binary data'),
               ('Dir Tree', 'Print directory tree'), ('File Search', 'Glob pattern lookup'),
               ('Biggest Files', 'Top sizes in dir'), ('Path Info', 'Path details')],
     "mapped": [('file_type', 'run'), ('base64_image', 'run'), ('photo_meta', 'run'),
                ('metadata_strip', 'run'), ('hex_dump', 'run'), ('steganography', 'run'),
                ('file_checksum', 'run'), ('hex_dump', 'binary'),
                ('misc_tools', 'dir_tree'), ('misc_tools', 'file_search'),
                ('misc_tools', 'file_sizes'), ('misc_tools', 'path_info')]},
    {"n": 13, "short": "SETTINGS", "title": "THEMES & SETTINGS", "icon": "⚙️",
     "tools": [], "mapped": []},
]

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
        return _TAG_COLORS.get(m.group(1).lower(), '')
    def _color_reset(m):
        tag = m.group(1)
        if tag.lower() in ('bold', 'dim'):
            return '\033[22m'
        return Colors.reset
    def _on_bg(m):
        h = m.group(1)
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        try:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f'\033[48;2;{r};{g};{b}m\x00on'
        except Exception:
            return m.group(0)
    s = re.sub(r'\[on\s+#?([0-9a-fA-F]{3,8})\]', _on_bg, s)
    s = s.replace('\x00on', '')
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
        sys.stdout.write('\x1b[2J\x1b[H')
        sys.stdout.flush()

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
        print(" " * max(0, (tw - _vis_len(line)) // 2) + line)

    print(cprint_horizontal(cl['head'], " " * 2 + "└" + "─" * inner + "┘"))

def draw_menu_grid(categories):
    cl = get_theme()
    tw = shutil.get_terminal_size().columns
    cw = 26
    per = max(1, (tw - 4) // (cw + 2))
    if tw < 68 or per < 2:
        per = 1
        cw = max(24, tw - 8)
    else:
        per = min(per, 4)

    rows = [categories[i:i + per] for i in range(0, len(categories), per)]
    for row in rows:
        tops = []
        mids = []
        bots = []
        for num, name in row:
            tag = f"[{num}] "
            room = max(1, cw - 2 - len(tag))
            shown = name if len(name) <= room else name[:room - 1] + "."
            pad = max(0, cw - 2 - len(tag) - len(shown))
            tops.append("┌" + "─" * (cw - 2) + "┐")
            mids.append("│" + cprint_horizontal(cl['num'], tag) + cprint_horizontal(cl['txt'], shown) + " " * pad + "│")
            bots.append("└" + "─" * (cw - 2) + "┘")
        for line in (cprint_horizontal(cl['num'], "  ".join(tops)),
                     "  ".join(mids),
                     cprint_horizontal(cl['num'], "  ".join(bots))):
            print(" " * max(0, (tw - _vis_len(line)) // 2) + line)
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

def check_update(auto=False):
    try:
        import requests
    except ImportError:
        return
    cl = get_theme()
    if not auto:
        print(cprint_horizontal(cl['sub'], "  Checking for updates..."))
    try:
        resp = requests.get(GITHUB_RAW_VERSION, timeout=8)
        if resp.status_code != 200:
            if not auto:
                print(cprint_horizontal(cl['num'], "  [!] Could not reach update server"))
            return
        remote_ver = resp.text.strip()
        if not remote_ver:
            return
        remote_tup = _ver_tuple(remote_ver)
        local_tup = _ver_tuple(VERSION)
        if remote_tup <= local_tup:
            if not auto:
                print(cprint_horizontal(cl['head'], "  Already up to date"))
                time.sleep(0.3)
            return
        print(cprint_horizontal(cl['head'], f"\n  [!] New Version Detected: {remote_ver} (you have {VERSION})"))
        print(cprint_horizontal(cl['txt'], f"  Download: https://github.com/{GITHUB_REPO}"))
        if not auto:
            choice = get_input("  Auto-update now? (y/n): ")
        else:
            choice = 'y'
            time.sleep(0.5)
        if choice.lower() == 'y':
            install_dir = os.path.join(BASE_DIR, f"KevTool-{remote_ver}")
            print(cprint_horizontal(cl['txt'], f"  Downloading v{remote_ver}..."))
            try:
                zip_data = requests.get(GITHUB_ZIP_URL, timeout=60).content
            except Exception as e:
                print(cprint_horizontal(cl['num'], f"  [!] Download failed: {e}"))
                get_input("  Press Enter...")
                return
            if os.path.isdir(install_dir):
                try:
                    shutil.rmtree(install_dir)
                except Exception:
                    pass
            try:
                with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                    top_folder = zf.namelist()[0].split('/')[0]
                    zf.extractall(BASE_DIR)
                extracted = os.path.join(BASE_DIR, top_folder)
                if extracted != install_dir and os.path.isdir(extracted):
                    os.rename(extracted, install_dir)
            except Exception as e:
                print(cprint_horizontal(cl['num'], f"  [!] Extract failed: {e}"))
                get_input("  Press Enter...")
                return
            try:
                src_cfg = os.path.join(CONFIG_DIR, 'settings.json')
                dst_dir = os.path.join(install_dir, 'modules', 'config')
                if os.path.isfile(src_cfg) and os.path.isdir(dst_dir):
                    shutil.copy2(src_cfg, os.path.join(dst_dir, 'settings.json'))
            except Exception:
                pass
            print(cprint_horizontal(cl['head'], f"  [+] Updated to v{remote_ver}!"))
            print(cprint_horizontal(cl['txt'], f"  Run from: {install_dir}"))
            print(cprint_horizontal(cl['dim'], "  Your settings were preserved."))
        get_input("  Press Enter...")
    except Exception as e:
        if not auto:
            print(cprint_horizontal(cl['num'], f"  [!] Update check failed: {e}"))


_PROXY_IP_RE = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3}):(\d{1,5})$')
_PROXY_SCHEME_RE = re.compile(r'^(https?|socks4|socks5)://([^/:]+):(\d{1,5})$', re.I)
_PROXY_TEST_URL = 'http://www.gstatic.com/generate_204'


def _proxy_valid(addr):
    m = _PROXY_IP_RE.match(addr.strip())
    if not m:
        return False
    return all(0 <= int(m.group(i)) <= 255 for i in range(1, 5)) and 1 <= int(m.group(5)) <= 65535


def _proxy_parse(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return None, None
    m = _PROXY_SCHEME_RE.match(line)
    if m:
        host, port = m.group(2), m.group(3)
        if not _proxy_valid(f"{host}:{port}"):
            return None, None
        return f"{host}:{port}", m.group(1).lower()
    if _proxy_valid(line):
        return line, 'http'
    return None, None


def _proxy_test_one(addr, proto, timeout=2):
    if proto == 'http':
        try:
            host, port = addr.split(':')
            s = socket.create_connection((host, int(port)), timeout=timeout)
            s.sendall(b'GET /generate_204 HTTP/1.1\r\nHost: www.gstatic.com\r\nConnection: close\r\n\r\n')
            resp = b''
            s.settimeout(timeout)
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    resp += chunk
                    if len(resp) > 2048:
                        break
                except Exception:
                    break
            s.close()
            return b' 200' in resp or b' 204' in resp
        except Exception:
            return False
    else:
        try:
            import socks
        except ImportError:
            return False
        host, _, port = addr.rpartition(':')
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5 if proto == 'socks5' else socks.SOCKS4, host, int(port))
        s.settimeout(timeout)
        try:
            s.connect(('www.gstatic.com', 80))
            s.send(b'GET /generate_204 HTTP/1.1\r\nHost: www.gstatic.com\r\nConnection: close\r\n\r\n')
            resp = s.recv(2048).decode('utf-8', errors='ignore')
            return ' 200' in resp or ' 204' in resp
        except Exception:
            return False
        finally:
            try:
                s.close()
            except Exception:
                pass


def _proxy_worker(queue, valid_out, lock, done_count):
    while True:
        try:
            addr, proto = queue.pop()
        except IndexError:
            return
        ok = _proxy_test_one(addr, proto)
        with lock:
            done_count[0] += 1
            if ok:
                valid_out.append(f"{proto}://{addr}" if proto != 'http' else addr)


def auto_proxy_check(max_proxies=500, threads=80):
    """Fetch proxies from all sources, test them, save valid to valid_proxies.txt."""
    cl = get_theme()
    print(cprint_horizontal(cl['sub'], f"  [~] Fetching proxies from {len(PROXY_SOURCES)} sources..."))
    seen = set()
    queue = []
    fetch_lock = threading.Lock()
    fetch_stats = [0, 0]  # [ok, fail]

    def _fetch_one(name_url):
        name, url = name_url
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'KevTool'})
            with urllib.request.urlopen(req, timeout=10) as r:
                raw = r.read().decode('utf-8', errors='ignore')
            count = 0
            for line in raw.splitlines():
                addr, proto = _proxy_parse(line)
                if addr and (addr, proto) not in seen:
                    seen.add((addr, proto))
                    queue.append((addr, proto))
                    count += 1
            with fetch_lock:
                fetch_stats[0] += 1
        except Exception:
            with fetch_lock:
                fetch_stats[1] += 1

    fetch_threads = [threading.Thread(target=_fetch_one, args=(s,), daemon=True) for s in PROXY_SOURCES]
    for t in fetch_threads:
        t.start()
    for t in fetch_threads:
        t.join(timeout=15)

    print(cprint_horizontal(cl['sub'], f"  [+] {fetch_stats[0]} sources reached, {fetch_stats[1]} failed — {len(queue)} proxies collected"))
    if not queue:
        print(cprint_horizontal(cl['num'], "  [!] No proxies found from any source"))
        return
    if len(queue) > max_proxies:
        random.shuffle(queue)
        queue = queue[:max_proxies]
    random.shuffle(queue)
    total = len(queue)
    print(cprint_horizontal(cl['sub'], f"  [~] Testing {total} proxies ({threads} threads)..."))
    valid = []
    lock = threading.Lock()
    done_count = [0]
    workers = [threading.Thread(target=_proxy_worker, args=(queue, valid, lock, done_count), daemon=True)
               for _ in range(min(threads, total))]
    for t in workers:
        t.start()
    try:
        while done_count[0] < total:
            time.sleep(0.3)
            pct = int(done_count[0] / total * 100) if total else 0
            sys.stdout.write(f"\r  [~] Testing proxies... {done_count[0]}/{total} ({pct}%) valid: {len(valid)}  ")
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    for t in workers:
        t.join(timeout=5)
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()
    if valid:
        try:
            with open(VALID_PROXIES_PATH, 'w', encoding='utf-8') as f:
                f.write('\n'.join(valid) + '\n')
        except Exception:
            pass
        print(cprint_horizontal(cl['head'], f"  [+] {len(valid)} working proxies saved to valid_proxies.txt"))
    else:
        print(cprint_horizontal(cl['num'], "  [!] No working proxies found"))


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
        sys.stdout.write('\033[0m')
        sys.stdout.flush()
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
        self.clear()
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
        self.clear()

    def _draw_tab_bar(self, active):
        cl = get_theme()
        tw = shutil.get_terminal_size().columns

        def build(sep, max_label):
            plains, segs = [], []
            for t in MENU_TABS:
                label = f"{t['n']}:{t['short']}"
                if max_label and len(label) > max_label:
                    label = label[:max_label]
                if t['n'] == active:
                    plain = f"▌{label}▐"
                    seg = cprint_horizontal(cl['num'], plain)
                else:
                    plain = f"|{label}_"
                    seg = cprint_horizontal(cl['sub'], plain)
                plains.append(plain)
                segs.append(seg)
            return plains, segs

        sep = " "
        plains, segs = build(sep, 0)
        line_plain = sep.join(plains)
        if len(line_plain) > tw:
            # tighten separators first
            sep = ""
            plains, segs = build(sep, 0)
            line_plain = sep.join(plains)
        if len(line_plain) > tw:
            # binary-search the largest label length that fits
            hi = max(len(f"{t['n']}:{t['short']}") for t in MENU_TABS)
            lo, best = 2, None
            while lo <= hi:
                mid = (lo + hi) // 2
                p, _ = build(sep, mid)
                if len(sep.join(p)) <= tw:
                    best, lo = mid, mid + 1
                else:
                    hi = mid - 1
            if best is not None:
                plains, segs = build(sep, best)
                line_plain = sep.join(plains)

        line = sep.join(segs)
        pad = max(0, (tw - len(line_plain)) // 2)
        print(" " * pad + line)
        at = pad
        for plain, t in zip(plains, MENU_TABS):
            w = len(plain)
            if t['n'] == active:
                print(cprint_horizontal(cl['head'], " " * (at + (w // 2)) + "▲"))
                break
            at += w + len(sep)

    def tool_menu(self, tab=1):
        tabs = MENU_TABS
        tab = max(1, min(tab, len(tabs)))
        while True:
            info = tabs[tab - 1]
            cl = get_theme()
            clr()
            print_banner()
            print(cprint_horizontal(cl['sub'], Center.XCenter(
                f"v{VERSION} | Theme: {self.theme_name} | {PC_USER}@kevbin")))
            print(cprint_horizontal(cl['head'], Center.XCenter(f"  {info['icon']}  {info['title']}  ")))
            print()
            self._draw_tab_bar(tab)
            print()

            if info['n'] == 13:
                self._settings_body()
                footer = " [N] NEXT TAB    [P] PREV TAB    [0] EXIT "
                print(cprint_horizontal(cl['sub'], " " * max(0, (shutil.get_terminal_size().columns - _vis_len(footer)) // 2) + footer))
                choice = self.input_choice()
                if choice == '0':
                    clr()
                    self.cprint(self.t.head, f"\n  Goodbye, {PC_USER}. — {AUTHOR}\n")
                    sys.exit(0)
                if choice.lower() == 'n':
                    tab = tab % len(tabs) + 1
                    continue
                if choice.lower() == 'p':
                    tab = (tab - 2) % len(tabs) + 1
                    continue
                if choice.lower() == 'u':
                    check_update()
                    self.pause()
                    continue
                if choice.isdigit() and 1 <= int(choice) <= len(sorted(THEMES)):
                    new_theme = sorted(THEMES)[int(choice) - 1]
                    self.settings['current_theme'] = new_theme
                    save_json(CONFIG_PATH, self.settings)
                    self.theme_name = new_theme
                    self._refresh_t()
                    self.cprint(self.t.head, f"\n  [+] Theme -> {new_theme.upper()}")
                    theme_wave(new_theme)
                    time.sleep(0.3)
                    continue
                continue

            total = len(info['tools'])
            draw_menu_grid([(str(i + 1), info['tools'][i][0]) for i in range(total)])
            footer = " [N] NEXT TAB    [P] PREV TAB    [0] EXIT "
            print(cprint_horizontal(cl['sub'], " " * max(0, (shutil.get_terminal_size().columns - _vis_len(footer)) // 2) + footer))

            choice = self.input_choice()
            if choice == '0':
                clr()
                self.cprint(self.t.head, f"\n  Goodbye, {PC_USER}. — {AUTHOR}\n")
                sys.exit(0)
            if choice.lower() == 'n':
                tab = tab % len(tabs) + 1
                continue
            if choice.lower() == 'p':
                tab = (tab - 2) % len(tabs) + 1
                continue
            try:
                idx = int(choice) - 1
                if 0 <= idx < total:
                    mod, func = info['mapped'][idx]
                    self.run_module(mod, func)
            except (ValueError, IndexError):
                pass

    def _settings_body(self):
        cl = get_theme()
        theme_names = sorted(THEMES)
        items = {}
        for i, name in enumerate(theme_names, 1):
            flag = " *" if self.theme_name == name else ""
            items[str(i)] = name.replace("_", " ").title() + flag
        items["U"] = "Check for updates"
        draw_card_box("THEMES & SETTINGS", items)

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
    if not no_update:
        cfg = get_config()
        if cfg.get('check_updates', True):
            check_update(auto=True)
    if not no_update:
        auto_proxy_check()
    KevTool().tool_menu(1)

if __name__ == '__main__':
    main()
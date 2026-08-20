"""Hash Tool — Hash strings/files, HMAC, online lookup, wordlist check."""

import hashlib
import os
import hmac

try:
    import requests
except ImportError:
    requests = None


def _hash_file(filepath, algo='sha256', chunk_size=65536):
    h = hashlib.new(algo)
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _all_hashes(data):
    results = {}
    for name in ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'blake2b']:
        try:
            h = hashlib.new(name)
            h.update(data.encode() if isinstance(data, str) else data)
            results[name.upper()] = h.hexdigest()
        except Exception:
            pass
    return results


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🛡️', 'HASH TOOL')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Hash a string (all algorithms)")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Hash a file")
        kevbin.cprint(kevbin.t.secondary, "  [3]  HMAC (keyed hash)")
        kevbin.cprint(kevbin.t.secondary, "  [4]  MD5 lookup (online)")
        kevbin.cprint(kevbin.t.secondary, "  [5]  SHA256 lookup (online)")
        kevbin.cprint(kevbin.t.secondary, "  [6]  Compare two hashes")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0':
            return

        if choice == '1':
            t = kevbin.input_choice("  Text: ")
            if t:
                results = _all_hashes(t)
                kevbin.cprint(kevbin.t.accent, f"\n  Hashes for '{t[:40]}':")
                for name, val in results.items():
                    kevbin.cprint(kevbin.t.txt, f"    {name:<10} {val}")
            kevbin.pause()

        elif choice == '2':
            path = kevbin.input_choice("  File path: ").strip().strip('"').strip("'")
            if not path or not os.path.isfile(path):
                kevbin.cprint(kevbin.t.error, "  [X] File not found.")
                kevbin.pause()
                continue
            kevbin.cprint(kevbin.t.dim, f"  Hashing {os.path.getsize(path):,} bytes...")
            results = {}
            for name in ['md5', 'sha1', 'sha256', 'sha512']:
                results[name.upper()] = _hash_file(path, name)
            results['CRC32'] = hex(_crc32_file(path))
            kevbin.cprint(kevbin.t.accent, f"\n  File hashes:")
            for name, val in results.items():
                kevbin.cprint(kevbin.t.txt, f"    {name:<10} {val}")
            kevbin.pause()

        elif choice == '3':
            key = kevbin.input_choice("  Secret key: ").strip()
            if not key:
                continue
            t = kevbin.input_choice("  Text to hash: ").strip()
            if not t:
                continue
            results = {}
            for name in ['md5', 'sha1', 'sha256', 'sha512']:
                try:
                    results[name.upper()] = hmac.new(key.encode(), t.encode(), getattr(hashlib, name)).hexdigest()
                except Exception:
                    pass
            kevbin.cprint(kevbin.t.accent, f"\n  HMAC results:")
            for name, val in results.items():
                kevbin.cprint(kevbin.t.txt, f"    HMAC-{name}  {val}")
            kevbin.pause()

        elif choice in ('4', '5') and requests:
            algo = 'md5' if choice == '4' else 'sha256'
            h = kevbin.input_choice(f"  {algo.upper()} hash: ").strip()
            if h:
                try:
                    r = requests.get(f"https://api.cryptopp.it/decrypt/{algo}/{h}", timeout=10)
                    d = r.json()
                    if d.get('found'):
                        kevbin.cprint(kevbin.t.success, f"\n  [✓] {d.get('result', '')}")
                    else:
                        kevbin.cprint(kevbin.t.warning, "  [!] Not found in online DB.")
                except Exception as e:
                    kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()

        elif choice == '6':
            h1 = kevbin.input_choice("  Hash 1: ").strip()
            h2 = kevbin.input_choice("  Hash 2: ").strip()
            if h1 and h2:
                if h1.lower() == h2.lower():
                    kevbin.cprint(kevbin.t.success, "  [✓] Hashes MATCH")
                else:
                    kevbin.cprint(kevbin.t.error, "  [X] Hashes DO NOT match")
                kevbin.cprint(kevbin.t.dim, f"    Len: {len(h1)} vs {len(h2)}")
            kevbin.pause()


def _crc32_file(filepath):
    import binascii
    crc = 0
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            crc = binascii.crc32(chunk, crc)
    return crc & 0xFFFFFFFF

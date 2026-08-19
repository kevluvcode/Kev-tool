"""Hash Tool — Hash strings and lookup MD5/SHA256."""

import hashlib

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🛡️', 'HASH TOOL')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Hash a string (MD5/SHA1/SHA256)")
        kevbin.cprint(kevbin.t.secondary, "  [2]  MD5 lookup (online)")
        kevbin.cprint(kevbin.t.secondary, "  [3]  SHA256 lookup (online)")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0': return
        if choice == '1':
            t = kevbin.input_choice("  Text: ")
            if t:
                kevbin.cprint(kevbin.t.accent, f"\n  MD5:    {hashlib.md5(t.encode()).hexdigest()}")
                kevbin.cprint(kevbin.t.accent, f"  SHA1:   {hashlib.sha1(t.encode()).hexdigest()}")
                kevbin.cprint(kevbin.t.accent, f"  SHA256: {hashlib.sha256(t.encode()).hexdigest()}")
            kevbin.pause()
        elif choice in ('2', '3') and requests:
            algo = 'md5' if choice == '2' else 'sha256'
            h = kevbin.input_choice(f"  {algo.upper()} hash: ").strip()
            if h:
                try:
                    r = requests.get(f"https://api.cryptopp.it/decrypt/{algo}/{h}", timeout=10)
                    d = r.json()
                    if d.get('found'):
                        kevbin.cprint(kevbin.t.success, f"\n  [✓] {d.get('result', '')}")
                    else:
                        kevbin.cprint(kevbin.t.warning, "  [!] Not found.")
                except Exception as e:
                    kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()

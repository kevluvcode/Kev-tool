"""Hash Tool — Hash strings and lookup MD5/SHA256."""

import hashlib

try:
    import requests
except ImportError:
    requests = None


def run(navi):
    while True:
        navi.clear()
        navi.section_header('🛡️', 'HASH TOOL')
        navi.cprint(navi.t.secondary, "  [1]  Hash a string (MD5/SHA1/SHA256)")
        navi.cprint(navi.t.secondary, "  [2]  MD5 lookup (online)")
        navi.cprint(navi.t.secondary, "  [3]  SHA256 lookup (online)")
        navi.cprint(navi.t.secondary, "  [0]  Back")
        navi.line()
        choice = navi.input_choice()
        if choice == '0': return
        if choice == '1':
            t = navi.input_choice("  Text: ")
            if t:
                navi.cprint(navi.t.accent, f"\n  MD5:    {hashlib.md5(t.encode()).hexdigest()}")
                navi.cprint(navi.t.accent, f"  SHA1:   {hashlib.sha1(t.encode()).hexdigest()}")
                navi.cprint(navi.t.accent, f"  SHA256: {hashlib.sha256(t.encode()).hexdigest()}")
            navi.pause()
        elif choice in ('2', '3') and requests:
            algo = 'md5' if choice == '2' else 'sha256'
            h = navi.input_choice(f"  {algo.upper()} hash: ").strip()
            if h:
                try:
                    r = requests.get(f"https://api.cryptopp.it/decrypt/{algo}/{h}", timeout=10)
                    d = r.json()
                    if d.get('found'):
                        navi.cprint(navi.t.success, f"\n  [✓] {d.get('result', '')}")
                    else:
                        navi.cprint(navi.t.warning, "  [!] Not found.")
                except Exception as e:
                    navi.cprint(navi.t.error, f"  [X] {e}")
            navi.pause()

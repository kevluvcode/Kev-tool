"""Passcheck — Password strength + breach check."""

import hashlib
import string

try:
    import requests
except ImportError:
    requests = None


def _strength(pwd):
    score = 0
    if len(pwd) >= 8: score += 1
    if len(pwd) >= 12: score += 1
    if len(pwd) >= 16: score += 1
    if any(c.isupper() for c in pwd): score += 1
    if any(c.islower() for c in pwd): score += 1
    if any(c.isdigit() for c in pwd): score += 1
    if any(c in string.punctuation for c in pwd): score += 1
    common = ['password', '123456', 'qwerty', 'admin', 'letmein', 'welcome', 'monkey', 'dragon']
    if pwd.lower() not in common:
        score += 1
    return score


def run(navi):
    navi.clear()
    navi.section_header('🛡️', 'PASSWORD CHECK')
    pwd = navi.input_choice("  Password: ")
    if not pwd:
        return

    score = _strength(pwd)
    labels = ['Very Weak', 'Weak', 'Fair', 'Fair', 'Good', 'Strong', 'Strong', 'Very Strong', 'Excellent']
    label = labels[min(score, len(labels) - 1)]

    navi.cprint(navi.t.accent, f"\n  Length:     {len(pwd)}")
    navi.cprint(navi.t.accent, f"  Strength:   {label} ({score}/8)")

    if requests and len(pwd) >= 4:
        sha1 = hashlib.sha1(pwd.encode()).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        try:
            r = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=5)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    h, count = line.split(':')
                    if h == suffix:
                        navi.cprint(navi.t.error, f"\n  [!] BREACHED {int(count):,} times!")
                        navi.pause()
                        return
                navi.cprint(navi.t.success, "\n  [✓] Not found in breach database.")
        except Exception:
            navi.cprint(navi.t.dim, "  (breach check skipped)")
    navi.pause()

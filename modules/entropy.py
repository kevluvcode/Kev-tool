"""Entropy — Calculate Shannon entropy + password strength analysis."""

import math
import string
from collections import Counter


def _shannon_entropy(data):
    if not data:
        return 0
    counter = Counter(data)
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in counter.values())


def _password_strength(password):
    score = 0
    checks = {
        'Length >= 8': len(password) >= 8,
        'Length >= 12': len(password) >= 12,
        'Length >= 16': len(password) >= 16,
        'Has uppercase': any(c.isupper() for c in password),
        'Has lowercase': any(c.islower() for c in password),
        'Has digits': any(c.isdigit() for c in password),
        'Has symbols': any(c in string.punctuation for c in password),
        'No common patterns': password.lower() not in ['password', '123456', 'qwerty', 'admin', 'letmein'],
    }
    score = sum(checks.values())
    return score, checks


def run(navi):
    while True:
        navi.clear()
        navi.section_header('🛡️', 'ENTROPY & PASSWORD STRENGTH')
        navi.cprint(navi.t.secondary, "  [1]  Calculate Shannon Entropy")
        navi.cprint(navi.t.secondary, "  [2]  Password Strength Analyzer")
        navi.cprint(navi.t.secondary, "  [0]  Back")
        navi.line()
        choice = navi.input_choice()
        if choice == '0': return

        if choice == '1':
            text = navi.input_choice("  Text: ")
            if text:
                entropy = _shannon_entropy(text)
                charset_size = len(set(text))
                theoretical = math.log2(charset_size) if charset_size > 1 else 0
                navi.cprint(navi.t.accent, f"\n  Shannon Entropy:     {entropy:.4f} bits/char")
                navi.cprint(navi.t.accent, f"  Total Entropy:       {entropy * len(text):.2f} bits")
                navi.cprint(navi.t.accent, f"  Unique Characters:   {charset_size}")
                navi.cprint(navi.t.accent, f"  Theoretical Max:     {theoretical:.4f} bits/char")
                if entropy > 4.0:
                    navi.cprint(navi.t.success, "  Rating: HIGH randomness")
                elif entropy > 3.0:
                    navi.cprint(navi.t.warning, "  Rating: MEDIUM randomness")
                else:
                    navi.cprint(navi.t.error, "  Rating: LOW randomness")
            navi.pause()

        elif choice == '2':
            pwd = navi.input_choice("  Password: ")
            if pwd:
                score, checks = _password_strength(pwd)
                entropy = _shannon_entropy(pwd)
                navi.cprint(navi.t.accent, f"\n  Password: {'*' * len(pwd)} ({len(pwd)} chars)")
                navi.cprint(navi.t.accent, f"  Shannon Entropy: {entropy:.2f} bits/char")
                navi.cprint(navi.t.accent, f"  Total Entropy:   {entropy * len(pwd):.1f} bits\n")
                for check, passed in checks.items():
                    icon = navi.t.success + '✓' if passed else navi.t.error + '✗'
                    navi.cprint(navi.t.secondary, f"    {icon} {check}{navi.t.R}")
                navi.cprint(navi.t.accent, f"\n  Score: {score}/8")
            navi.pause()

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


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🛡️', 'ENTROPY & PASSWORD STRENGTH')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Calculate Shannon Entropy")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Password Strength Analyzer")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0': return

        if choice == '1':
            text = kevbin.input_choice("  Text: ")
            if text:
                entropy = _shannon_entropy(text)
                charset_size = len(set(text))
                theoretical = math.log2(charset_size) if charset_size > 1 else 0
                kevbin.cprint(kevbin.t.accent, f"\n  Shannon Entropy:     {entropy:.4f} bits/char")
                kevbin.cprint(kevbin.t.accent, f"  Total Entropy:       {entropy * len(text):.2f} bits")
                kevbin.cprint(kevbin.t.accent, f"  Unique Characters:   {charset_size}")
                kevbin.cprint(kevbin.t.accent, f"  Theoretical Max:     {theoretical:.4f} bits/char")
                if entropy > 4.0:
                    kevbin.cprint(kevbin.t.success, "  Rating: HIGH randomness")
                elif entropy > 3.0:
                    kevbin.cprint(kevbin.t.warning, "  Rating: MEDIUM randomness")
                else:
                    kevbin.cprint(kevbin.t.error, "  Rating: LOW randomness")
            kevbin.pause()

        elif choice == '2':
            pwd = kevbin.input_choice("  Password: ")
            if pwd:
                score, checks = _password_strength(pwd)
                entropy = _shannon_entropy(pwd)
                kevbin.cprint(kevbin.t.accent, f"\n  Password: {'*' * len(pwd)} ({len(pwd)} chars)")
                kevbin.cprint(kevbin.t.accent, f"  Shannon Entropy: {entropy:.2f} bits/char")
                kevbin.cprint(kevbin.t.accent, f"  Total Entropy:   {entropy * len(pwd):.1f} bits\n")
                for check, passed in checks.items():
                    icon = '✓' if passed else '✗'
                    kevbin.cprint(kevbin.t.secondary, f"    {icon} {check}{kevbin.t.R}")
                kevbin.cprint(kevbin.t.accent, f"\n  Score: {score}/8")
            kevbin.pause()

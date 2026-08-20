"""Entropy — Shannon entropy + frequency analysis + visual chart + password strength."""

import math
import string
from collections import Counter


def _shannon_entropy(data):
    if not data:
        return 0
    counter = Counter(data)
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in counter.values())


def _freq_analysis(text):
    freq = Counter(c.lower() for c in text if c.isalpha())
    total = sum(freq.values()) or 1
    return freq, total


def _freq_chart(freq, total, width=30):
    if not freq:
        return ''
    max_count = max(freq.values()) if freq else 1
    lines = []
    for ch, count in sorted(freq.items(), key=lambda x: -x[1])[:15]:
        bar_len = int(count / max_count * width) if max_count else 0
        bar = '#' * bar_len
        pct = count / total * 100
        lines.append(f"    {ch}  {bar:<{width}} {count:>5} ({pct:5.1f}%)")
    return '\n'.join(lines)


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
    pool = 0
    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(c in string.punctuation for c in password):
        pool += 33
    entropy = len(password) * math.log2(max(pool, 2))
    return score, checks, entropy


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🛡️', 'ENTROPY & ANALYSIS')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Shannon Entropy")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Frequency Analysis + Chart")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Password Strength")
        kevbin.cprint(kevbin.t.secondary, "  [4]  Compare two strings")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0':
            return

        if choice == '1':
            text = kevbin.input_choice("  Text: ")
            if text:
                entropy = _shannon_entropy(text)
                charset_size = len(set(text))
                theoretical = math.log2(charset_size) if charset_size > 1 else 0
                kevbin.cprint(kevbin.t.accent, f"\n  Shannon Entropy:     {entropy:.4f} bits/char")
                kevbin.cprint(kevbin.t.accent, f"  Total Entropy:       {entropy * len(text):.2f} bits")
                kevbin.cprint(kevbin.t.accent, f"  String Length:       {len(text)}")
                kevbin.cprint(kevbin.t.accent, f"  Unique Characters:   {charset_size}")
                kevbin.cprint(kevbin.t.accent, f"  Theoretical Max:     {theoretical:.4f} bits/char")
                bar_len = int(entropy * 5)
                bar = '#' * min(bar_len, 40) + '.' * max(0, 40 - bar_len)
                kevbin.cprint(kevbin.t.accent, f"  [{bar}] {entropy:.2f}")
                if entropy > 4.0:
                    kevbin.cprint(kevbin.t.success, "  Rating: HIGH randomness")
                elif entropy > 3.0:
                    kevbin.cprint(kevbin.t.warning, "  Rating: MEDIUM randomness")
                else:
                    kevbin.cprint(kevbin.t.error, "  Rating: LOW randomness")
            kevbin.pause()

        elif choice == '2':
            text = kevbin.input_choice("  Text to analyze: ")
            if text:
                freq, total = _freq_analysis(text)
                chart = _freq_chart(freq, total)
                kevbin.cprint(kevbin.t.accent, f"\n  Character Frequency ({total} alpha chars):\n")
                kevbin.cprint(kevbin.t.txt, chart)
                kevbin.cprint(kevbin.t.accent, f"\n  Unique: {len(freq)} letters")
                dig = Counter(c for c in text if c.isdigit())
                if dig:
                    kevbin.cprint(kevbin.t.accent, f"  Digits: {dict(dig.most_common(10))}")
                sym = Counter(c for c in text if not c.isalnum())
                if sym:
                    kevbin.cprint(kevbin.t.accent, f"  Symbols: {len(sym)} total")
            kevbin.pause()

        elif choice == '3':
            pwd = kevbin.input_choice("  Password: ")
            if pwd:
                score, checks, entropy = _password_strength(pwd)
                ratings = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong",
                           "Excellent", "Maximum"]
                rating = ratings[min(score, len(ratings) - 1)]
                kevbin.cprint(kevbin.t.accent, f"\n  Password: {'*' * len(pwd)} ({len(pwd)} chars)")
                kevbin.cprint(kevbin.t.accent, f"  Shannon Entropy: {_shannon_entropy(pwd):.2f} bits/char")
                kevbin.cprint(kevbin.t.accent, f"  Total Entropy:   {entropy:.1f} bits")
                kevbin.cprint(kevbin.t.accent, f"  Strength:        {rating} ({score}/8)")
                bar = '#' * int(entropy / 5) + '.' * max(0, 40 - int(entropy / 5))
                kevbin.cprint(kevbin.t.accent, f"  [{bar}]")
                kevbin.cprint(kevbin.t.accent, "")
                for check, passed in checks.items():
                    icon = '+' if passed else '-'
                    color = kevbin.t.success if passed else kevbin.t.dim
                    kevbin.cprint(color, f"    [{icon}] {check}")
                crack_times = {
                    'Online (1k/s)': f"{2**entropy / 1000:.0f}s",
                    'Offline (1B/s)': f"{2**entropy / 1e9:.0f}s",
                    'Offline (10B/s)': f"{2**entropy / 1e10:.0f}s",
                }
                kevbin.cprint(kevbin.t.accent, "\n  Estimated crack time:")
                for label, val in crack_times.items():
                    kevbin.cprint(kevbin.t.txt, f"    {label}: {val}")
            kevbin.pause()

        elif choice == '4':
            t1 = kevbin.input_choice("  String 1: ")
            t2 = kevbin.input_choice("  String 2: ")
            if t1 and t2:
                e1 = _shannon_entropy(t1)
                e2 = _shannon_entropy(t2)
                kevbin.cprint(kevbin.t.accent, f"\n  String 1: len={len(t1)} entropy={e1:.4f}")
                kevbin.cprint(kevbin.t.accent, f"  String 2: len={len(t2)} entropy={e2:.4f}")
                diff = abs(e1 - e2)
                kevbin.cprint(kevbin.t.accent, f"  Diff:     {diff:.4f}")
                if e1 > e2:
                    kevbin.cprint(kevbin.t.success, "  String 1 is MORE random")
                elif e2 > e1:
                    kevbin.cprint(kevbin.t.success, "  String 2 is MORE random")
                else:
                    kevbin.cprint(kevbin.t.dim, "  Both have equal entropy")
            kevbin.pause()

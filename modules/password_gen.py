"""Password Generator — Secure passwords + passphrases + memorable words."""

import secrets
import string
import math


ADJECTIVES = [
    'brave', 'calm', 'dark', 'eager', 'fair', 'glad', 'happy', 'keen',
    'mild', 'nice', 'pale', 'rare', 'safe', 'tall', 'vast', 'warm',
    'bold', 'cool', 'deep', 'fast', 'gold', 'iron', 'just', 'kind',
    'lean', 'loud', 'mild', 'neat', 'open', 'pure', 'rich', 'soft',
    'swift', 'true', 'wise', 'young', 'amber', 'black', 'blue', 'green',
    'white', 'winter', 'summer', 'autumn', 'spring', 'silent', 'gentle',
    'fierce', 'cosmic', 'lunar', 'solar', 'arctic', 'royal', 'silent',
    'steady', 'quick', 'vivid', 'proud', 'sharp', 'bright', 'silent',
]

NOUNS = [
    'bear', 'bird', 'deer', 'fish', 'fox', 'hawk', 'lion', 'wolf',
    'star', 'moon', 'fire', 'wind', 'wave', 'storm', 'frost', 'stone',
    'blade', 'crown', 'flame', 'shield', 'tower', 'river', 'mountain',
    'eagle', 'tiger', 'dragon', 'phoenix', 'shadow', 'thunder', 'crystal',
    'forest', 'harbor', 'island', 'jungle', 'ocean', 'planet', 'rocket',
    'castle', 'garden', 'sunset', 'temple', 'legend', 'spark', 'blaze',
]

VERBS = [
    'runs', 'leaps', 'flies', 'swims', 'dives', 'rides', 'hunts',
    'guards', 'fights', 'shines', 'burns', 'grows', 'flows', 'roars',
]


def _generate_password(length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous):
    chars = ""
    if use_upper:
        chars += string.ascii_uppercase
    if use_lower:
        chars += string.ascii_lowercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if exclude_ambiguous:
        ambiguous = "il1Lo0O"
        chars = "".join(c for c in chars if c not in ambiguous)
    if not chars:
        raise ValueError("At least one character type must be selected")
    return "".join(secrets.choice(chars) for _ in range(length))


def _generate_passphrase(word_count=4, separator='-', use_numbers=True):
    words = []
    words.append(secrets.choice(ADJECTIVES))
    words.append(secrets.choice(NOUNS))
    for _ in range(max(0, word_count - 2)):
        words.append(secrets.choice(ADJECTIVES + NOUNS))
    if use_numbers:
        words.append(str(secrets.randbelow(900) + 100))
    return separator.join(words)


def _password_strength(password):
    score = 0
    checks = []
    checks.append(("Length >= 8", len(password) >= 8))
    checks.append(("Length >= 12", len(password) >= 12))
    checks.append(("Length >= 16", len(password) >= 16))
    checks.append(("Lowercase", any(c.islower() for c in password)))
    checks.append(("Uppercase", any(c.isupper() for c in password)))
    checks.append(("Digits", any(c.isdigit() for c in password)))
    checks.append(("Symbols", any(c in string.punctuation for c in password)))
    checks.append(("No common", password.lower() not in [
        'password', '123456', 'qwerty', 'admin', 'letmein', 'welcome']))
    score = sum(1 for _, p in checks if p)
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
    ratings = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong",
               "Excellent", "Maximum"]
    rating = ratings[min(score, len(ratings) - 1)]
    return rating, score, checks, entropy


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🔑', 'PASSWORD GENERATOR')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Random password")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Passphrase (word-based)")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Batch generate")
        kevbin.cprint(kevbin.t.secondary, "  [4]  Check password strength")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0':
            return

        if choice == '1':
            length = kevbin.input_choice("  Length [16]: ").strip() or '16'
            try:
                length = max(4, min(128, int(length)))
            except ValueError:
                length = 16
            use_upper = kevbin.input_choice("  Uppercase? (Y/n): ").strip().lower() != 'n'
            use_lower = kevbin.input_choice("  Lowercase? (Y/n): ").strip().lower() != 'n'
            use_digits = kevbin.input_choice("  Digits? (Y/n): ").strip().lower() != 'n'
            use_symbols = kevbin.input_choice("  Symbols? (Y/n): ").strip().lower() != 'n'
            excl = kevbin.input_choice("  Exclude ambiguous (il1Lo0O)? (y/N): ").strip().lower() == 'y'
            pwd = _generate_password(length, use_upper, use_lower, use_digits, use_symbols, excl)
            rating, score, checks, entropy = _password_strength(pwd)
            kevbin.cprint(kevbin.t.accent, f"\n  {pwd}")
            kevbin.cprint(kevbin.t.accent, f"  Strength: {rating} ({score}/8)  Entropy: {entropy:.1f} bits")
            for name, passed in checks:
                icon = '+' if passed else '-'
                kevbin.cprint(kevbin.t.secondary, f"    [{icon}] {name}")
            save = kevbin.input_choice("\n  Save to file? (y/n): ").strip().lower()
            if save == 'y':
                path = kevbin.input_choice("  Path [passwords.txt]: ").strip() or 'passwords.txt'
                try:
                    with open(path, 'w') as f:
                        f.write(pwd + '\n')
                    kevbin.cprint(kevbin.t.success, f"  [+] Saved to {path}")
                except Exception as e:
                    kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()

        elif choice == '2':
            wc = kevbin.input_choice("  Word count [4]: ").strip() or '4'
            try:
                wc = max(2, min(8, int(wc)))
            except ValueError:
                wc = 4
            sep = kevbin.input_choice("  Separator [-]: ").strip() or '-'
            use_nums = kevbin.input_choice("  Include number? (Y/n): ").strip().lower() != 'n'
            for _ in range(5):
                phrase = _generate_passphrase(wc, sep, use_nums)
                rating, score, checks, entropy = _password_strength(phrase)
                kevbin.cprint(kevbin.t.accent, f"  {phrase:<45} {rating} ({entropy:.0f} bits)")
            kevbin.pause()

        elif choice == '3':
            count = kevbin.input_choice("  How many [10]: ").strip() or '10'
            try:
                count = max(1, min(200, int(count)))
            except ValueError:
                count = 10
            length = kevbin.input_choice("  Length [16]: ").strip() or '16'
            try:
                length = max(4, min(128, int(length)))
            except ValueError:
                length = 16
            passwords = [_generate_password(length, True, True, True, True, False) for _ in range(count)]
            kevbin.cprint(kevbin.t.accent, f"\n  Generated {count} passwords:\n")
            for i, pwd in enumerate(passwords, 1):
                kevbin.cprint(kevbin.t.txt, f"  {i:>3}. {pwd}")
            save = kevbin.input_choice("\n  Save to file? (y/n): ").strip().lower()
            if save == 'y':
                path = kevbin.input_choice("  Path [passwords.txt]: ").strip() or 'passwords.txt'
                try:
                    with open(path, 'w') as f:
                        f.write('\n'.join(passwords) + '\n')
                    kevbin.cprint(kevbin.t.success, f"  [+] Saved {count} passwords to {path}")
                except Exception as e:
                    kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()

        elif choice == '4':
            pwd = kevbin.input_choice("  Password to check: ").strip()
            if pwd:
                rating, score, checks, entropy = _password_strength(pwd)
                kevbin.cprint(kevbin.t.accent, f"\n  Strength: {rating} ({score}/8)")
                kevbin.cprint(kevbin.t.accent, f"  Entropy:  {entropy:.1f} bits")
                kevbin.cprint(kevbin.t.accent, f"  Length:   {len(pwd)} chars")
                for name, passed in checks:
                    icon = '+' if passed else '-'
                    kevbin.cprint(kevbin.t.secondary, f"    [{icon}] {name}")
                bar_len = int(entropy / 5)
                bar = '#' * min(bar_len, 40) + '.' * max(0, 40 - bar_len)
                kevbin.cprint(kevbin.t.accent, f"  [{bar}] {entropy:.0f} bits")
            kevbin.pause()

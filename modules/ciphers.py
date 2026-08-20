"""Ciphers — Caesar, Vigenere, Atbash, XOR, ROT13, Rail Fence, Bacon, Autokey."""

import string
from collections import Counter


def _caesar(text, shift, decrypt=False):
    if decrypt:
        shift = -shift
    result = []
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result.append(chr((ord(c) - base + shift) % 26 + base))
        else:
            result.append(c)
    return ''.join(result)


def _vigenere(text, key, decrypt=False):
    result = []
    ki = 0
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            k = ord(key[ki % len(key)].upper()) - ord('A')
            if decrypt:
                k = -k
            result.append(chr((ord(c) - base + k) % 26 + base))
            ki += 1
        else:
            result.append(c)
    return ''.join(result)


def _autokey(text, key, decrypt=False):
    result = []
    key_idx = ord(key[0].upper()) - ord('A')
    keystream = [key_idx]
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            if decrypt:
                dec = (ord(c) - base - keystream[-1]) % 26
                result.append(chr(dec + base))
                keystream.append(dec)
            else:
                enc = (ord(c) - base + keystream[-1]) % 26
                result.append(chr(enc + base))
                keystream.append(ord(c.upper()) - ord('A'))
        else:
            result.append(c)
    return ''.join(result)


def _atbash(text):
    result = []
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result.append(chr(base + 25 - (ord(c) - base)))
        else:
            result.append(c)
    return ''.join(result)


def _xor(text, key):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))


def _rot13(text):
    return _caesar(text, 13)


def _rail_fence(text, rails=3):
    if rails <= 1 or rails >= len(text):
        return text
    fence = [[] for _ in range(rails)]
    row, direction = 0, 1
    for ch in text:
        fence[row].append(ch)
        if row == 0:
            direction = 1
        elif row == rails - 1:
            direction = -1
        row += direction
    return ''.join(''.join(r) for r in fence)


def _rail_fence_decrypt(text, rails=3):
    if rails <= 1 or rails >= len(text):
        return text
    pattern = []
    row, direction = 0, 1
    for _ in range(len(text)):
        pattern.append(row)
        if row == 0:
            direction = 1
        elif row == rails - 1:
            direction = -1
        row += direction
    result = [''] * len(text)
    idx = 0
    for r in range(rails):
        for i in range(len(text)):
            if pattern[i] == r:
                result[i] = text[idx]
                idx += 1
    return ''.join(result)


def _bacon_encode(text):
    result = []
    for c in text.lower():
        if c.isalpha():
            idx = ord(c) - ord('a')
            bits = format(idx, '05b').replace('0', 'A').replace('1', 'B')
            result.append(bits)
    return ' '.join(result)


def _bacon_decode(text):
    clean = text.upper().replace(' ', '')
    result = []
    for i in range(0, len(clean) - 4, 5):
        chunk = clean[i:i + 5]
        bits = chunk.replace('A', '0').replace('B', '1')
        try:
            idx = int(bits, 2)
            result.append(chr(ord('a') + idx))
        except ValueError:
            pass
    return ''.join(result)


def _frequency_analysis(text):
    freq = Counter(c.lower() for c in text if c.isalpha())
    total = sum(freq.values()) or 1
    english = {'e': 12.7, 't': 9.1, 'a': 8.2, 'o': 7.5, 'i': 7.0, 'n': 6.7,
               's': 6.3, 'h': 6.1, 'r': 6.0, 'd': 4.3, 'l': 4.0, 'c': 2.8}
    sorted_obs = sorted(freq.items(), key=lambda x: -x[1])
    sorted_eng = sorted(english.items(), key=lambda x: -x[1])
    mapping = {}
    for i, (obs, _) in enumerate(sorted_obs[:min(len(sorted_eng), len(sorted_obs))]):
        mapping[obs] = sorted_eng[i][0]
    lines = []
    lines.append(f"  {'Char':<6} {'Count':<8} {'Freq%':<8} {'Mapped'}")
    lines.append(f"  {'─'*40}")
    for ch, count in sorted_obs[:15]:
        pct = count / total * 100
        mapped = mapping.get(ch, '?')
        lines.append(f"  {ch:<6} {count:<8} {pct:<8.1f} -> {mapped}")
    return '\n'.join(lines)


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🛡️', 'CIPHERS')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Caesar Cipher")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Vigenere Cipher")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Atbash Cipher")
        kevbin.cprint(kevbin.t.secondary, "  [4]  XOR Cipher")
        kevbin.cprint(kevbin.t.secondary, "  [5]  ROT13")
        kevbin.cprint(kevbin.t.secondary, "  [6]  Rail Fence")
        kevbin.cprint(kevbin.t.secondary, "  [7]  Baconian Cipher")
        kevbin.cprint(kevbin.t.secondary, "  [8]  Autokey Cipher")
        kevbin.cprint(kevbin.t.secondary, "  [9]  Frequency Analysis")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0':
            return

        if choice in ('1', '2', '3', '4', '5', '6', '7', '8'):
            text = kevbin.input_choice("  Text: ").strip()
            if not text:
                continue

            if choice == '1':
                shift = kevbin.input_choice("  Shift (1-25): ").strip()
                shift = int(shift) if shift.isdigit() and 1 <= int(shift) <= 25 else 3
                enc = _caesar(text, shift)
                dec = _caesar(text, shift, decrypt=True)
            elif choice == '2':
                key = kevbin.input_choice("  Key (letters only): ").strip()
                if not key or not key.isalpha():
                    kevbin.cprint(kevbin.t.error, "  [X] Key must be letters.")
                    kevbin.pause()
                    continue
                enc = _vigenere(text, key)
                dec = _vigenere(text, key, decrypt=True)
            elif choice == '3':
                enc = _atbash(text)
                dec = _atbash(text)
            elif choice == '4':
                key = kevbin.input_choice("  Key: ").strip()
                if not key:
                    continue
                enc = _xor(text, key)
                dec = _xor(enc, key)
            elif choice == '5':
                enc = _rot13(text)
                dec = _rot13(text)
            elif choice == '6':
                rails = kevbin.input_choice("  Rails (2-10) [3]: ").strip() or '3'
                try:
                    rails = max(2, min(10, int(rails)))
                except ValueError:
                    rails = 3
                enc = _rail_fence(text, rails)
                dec = _rail_fence_decrypt(enc, rails)
            elif choice == '7':
                enc = _bacon_encode(text)
                dec = _bacon_decode(text)
            elif choice == '8':
                key = kevbin.input_choice("  Key letter: ").strip()
                if not key or not key[0].isalpha():
                    kevbin.cprint(kevbin.t.error, "  [X] Key must be a letter.")
                    kevbin.pause()
                    continue
                enc = _autokey(text, key)
                dec = _autokey(enc, key, decrypt=True)

            kevbin.cprint(kevbin.t.accent, f"\n  Encrypted: {enc}")
            kevbin.cprint(kevbin.t.accent, f"  Decrypted: {dec}")
            kevbin.pause()

        elif choice == '9':
            text = kevbin.input_choice("  Text to analyze: ").strip()
            if text:
                result = _frequency_analysis(text)
                kevbin.cprint(kevbin.t.accent, f"\n{result}")
            kevbin.pause()

"""Ciphers — Caesar, Vigenere, Atbash, XOR cipher."""

import string


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


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🛡️', 'CIPHERS')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Caesar Cipher (rotate letters)")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Vigenere Cipher (keyword)")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Atbash Cipher (A↔Z)")
        kevbin.cprint(kevbin.t.secondary, "  [4]  XOR Cipher (character key)")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0': return

        if choice in ('1', '2', '3', '4'):
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

            kevbin.cprint(kevbin.t.accent, f"\n  Encrypted: {enc}")
            kevbin.cprint(kevbin.t.accent, f"  Decrypted: {dec}")
            kevbin.pause()

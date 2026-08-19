"""Cryptography — Base64, Hex, ROT13, and password generator."""

import base64
import codecs
import secrets
import string
import random


def _gen_password(length=16):
    pool = string.ascii_letters + string.digits + '!@#$%^&*()-_=+[]{}|;:,.<>?'
    return ''.join(secrets.choice(pool) for _ in range(length))


def run(navi):
    while True:
        navi.clear()
        navi.section_header('🛡️', 'CRYPTOGRAPHY')
        navi.cprint(navi.t.secondary, "  [1]  Base64 Encode")
        navi.cprint(navi.t.secondary, "  [2]  Base64 Decode")
        navi.cprint(navi.t.secondary, "  [3]  Hex Encode")
        navi.cprint(navi.t.secondary, "  [4]  Hex Decode")
        navi.cprint(navi.t.secondary, "  [5]  ROT13")
        navi.cprint(navi.t.secondary, "  [6]  Password Generator")
        navi.cprint(navi.t.secondary, "  [0]  Back")
        navi.line()
        choice = navi.input_choice()
        if choice == '0': return
        if choice == '1':
            t = navi.input_choice("  Text: ")
            navi.cprint(navi.t.accent, f"\n  {base64.b64encode(t.encode()).decode()}")
            navi.pause()
        elif choice == '2':
            t = navi.input_choice("  Base64: ")
            try:
                navi.cprint(navi.t.accent, f"\n  {base64.b64decode(t).decode()}")
            except Exception as e:
                navi.cprint(navi.t.error, f"  [X] {e}")
            navi.pause()
        elif choice == '3':
            t = navi.input_choice("  Text: ")
            navi.cprint(navi.t.accent, f"\n  {t.encode().hex()}")
            navi.pause()
        elif choice == '4':
            t = navi.input_choice("  Hex: ")
            try:
                navi.cprint(navi.t.accent, f"\n  {bytes.fromhex(t).decode()}")
            except Exception as e:
                navi.cprint(navi.t.error, f"  [X] {e}")
            navi.pause()
        elif choice == '5':
            t = navi.input_choice("  Text: ")
            navi.cprint(navi.t.accent, f"\n  {codecs.encode(t, 'rot_13')}")
            navi.pause()
        elif choice == '6':
            l = navi.input_choice("  Length (default 16): ").strip()
            ln = int(l) if l.isdigit() and int(l) >= 4 else 16
            navi.cprint(navi.t.accent, f"\n  {_gen_password(ln)}")
            navi.pause()

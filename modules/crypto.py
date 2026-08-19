"""Cryptography — Base64, Hex, ROT13, and password generator."""

import base64
import codecs
import secrets
import string
import random


def _gen_password(length=16):
    pool = string.ascii_letters + string.digits + '!@#$%^&*()-_=+[]{}|;:,.<>?'
    return ''.join(secrets.choice(pool) for _ in range(length))


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🛡️', 'CRYPTOGRAPHY')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Base64 Encode")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Base64 Decode")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Hex Encode")
        kevbin.cprint(kevbin.t.secondary, "  [4]  Hex Decode")
        kevbin.cprint(kevbin.t.secondary, "  [5]  ROT13")
        kevbin.cprint(kevbin.t.secondary, "  [6]  Password Generator")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0': return
        if choice == '1':
            t = kevbin.input_choice("  Text: ")
            kevbin.cprint(kevbin.t.accent, f"\n  {base64.b64encode(t.encode()).decode()}")
            kevbin.pause()
        elif choice == '2':
            t = kevbin.input_choice("  Base64: ")
            try:
                kevbin.cprint(kevbin.t.accent, f"\n  {base64.b64decode(t).decode()}")
            except Exception as e:
                kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()
        elif choice == '3':
            t = kevbin.input_choice("  Text: ")
            kevbin.cprint(kevbin.t.accent, f"\n  {t.encode().hex()}")
            kevbin.pause()
        elif choice == '4':
            t = kevbin.input_choice("  Hex: ")
            try:
                kevbin.cprint(kevbin.t.accent, f"\n  {bytes.fromhex(t).decode()}")
            except Exception as e:
                kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()
        elif choice == '5':
            t = kevbin.input_choice("  Text: ")
            kevbin.cprint(kevbin.t.accent, f"\n  {codecs.encode(t, 'rot_13')}")
            kevbin.pause()
        elif choice == '6':
            l = kevbin.input_choice("  Length (default 16): ").strip()
            ln = int(l) if l.isdigit() and int(l) >= 4 else 16
            kevbin.cprint(kevbin.t.accent, f"\n  {_gen_password(ln)}")
            kevbin.pause()

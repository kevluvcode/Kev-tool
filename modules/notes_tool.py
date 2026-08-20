"""Notes Tool — Quick encrypted notes with password protection."""

import os
import hashlib
import base64
import json
import time


NOTES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'notes')


def _ensure_dir():
    os.makedirs(NOTES_DIR, exist_ok=True)


def _derive_key(password):
    return hashlib.sha256(password.encode()).digest()


def _xor_encrypt(data, key):
    key_len = len(key)
    return bytes(b ^ key[i % key_len] for i, b in enumerate(data))


def _encrypt(plaintext, password):
    key = _derive_key(password)
    data = plaintext.encode('utf-8')
    encrypted = _xor_encrypt(data, key)
    return base64.b64encode(encrypted).decode('ascii')


def _decrypt(cipher_b64, password):
    key = _derive_key(password)
    encrypted = base64.b64decode(cipher_b64)
    decrypted = _xor_encrypt(encrypted, key)
    return decrypted.decode('utf-8', errors='replace')


def _list_notes():
    _ensure_dir()
    notes = []
    for f in os.listdir(NOTES_DIR):
        if f.endswith('.enc'):
            name = f[:-4]
            path = os.path.join(NOTES_DIR, f)
            mtime = os.path.getmtime(path)
            notes.append((name, mtime))
    notes.sort(key=lambda x: x[1], reverse=True)
    return notes


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('📝', 'ENCRYPTED NOTES')
        notes = _list_notes()
        kevbin.cprint(kevbin.t.secondary, "  [1]  Create note")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Read note")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Edit note")
        kevbin.cprint(kevbin.t.secondary, "  [4]  Delete note")
        kevbin.cprint(kevbin.t.secondary, "  [5]  List notes")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")

        if notes:
            kevbin.cprint(kevbin.t.dim, f"\n  {len(notes)} note(s) stored:")
            for name, mtime in notes[:10]:
                ts = time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))
                kevbin.cprint(kevbin.t.txt, f"    {name}  ({ts})")
        kevbin.line()

        choice = kevbin.input_choice()
        if choice == '0':
            return

        if choice == '1':
            name = kevbin.input_choice("  Note name: ").strip()
            if not name:
                continue
            password = kevbin.input_choice("  Password: ").strip()
            if not password:
                kevbin.cprint(kevbin.t.error, "  [X] Password required.")
                kevbin.pause()
                continue
            kevbin.cprint(kevbin.t.dim, "  Type note content (empty line to finish):")
            content_lines = []
            while True:
                line = kevbin.input_choice("  ")
                if line == '':
                    break
                content_lines.append(line)
            content = '\n'.join(content_lines)
            if not content:
                continue
            encrypted = _encrypt(content, password)
            _ensure_dir()
            path = os.path.join(NOTES_DIR, f"{name}.enc")
            with open(path, 'w') as f:
                f.write(encrypted)
            kevbin.cprint(kevbin.t.success, f"  [✓] Note '{name}' saved (encrypted).")
            kevbin.pause()

        elif choice == '2':
            name = kevbin.input_choice("  Note name: ").strip()
            path = os.path.join(NOTES_DIR, f"{name}.enc")
            if not os.path.isfile(path):
                kevbin.cprint(kevbin.t.error, "  [X] Note not found.")
                kevbin.pause()
                continue
            password = kevbin.input_choice("  Password: ").strip()
            try:
                with open(path) as f:
                    cipher = f.read()
                content = _decrypt(cipher, password)
                kevbin.cprint(kevbin.t.accent, f"\n  --- {name} ---")
                for line in content.split('\n'):
                    kevbin.cprint(kevbin.t.txt, f"  {line}")
                kevbin.cprint(kevbin.t.accent, f"  --- end ---")
            except Exception:
                kevbin.cprint(kevbin.t.error, "  [X] Wrong password or corrupted note.")
            kevbin.pause()

        elif choice == '3':
            name = kevbin.input_choice("  Note name: ").strip()
            path = os.path.join(NOTES_DIR, f"{name}.enc")
            if not os.path.isfile(path):
                kevbin.cprint(kevbin.t.error, "  [X] Note not found.")
                kevbin.pause()
                continue
            password = kevbin.input_choice("  Password: ").strip()
            try:
                with open(path) as f:
                    cipher = f.read()
                content = _decrypt(cipher, password)
                kevbin.cprint(kevbin.t.dim, f"  Current content:\n  {content[:200]}...")
                kevbin.cprint(kevbin.t.dim, "  New content (empty line to finish):")
                new_lines = []
                while True:
                    line = kevbin.input_choice("  ")
                    if line == '':
                        break
                    new_lines.append(line)
                new_content = '\n'.join(new_lines)
                if new_content:
                    encrypted = _encrypt(new_content, password)
                    with open(path, 'w') as f:
                        f.write(encrypted)
                    kevbin.cprint(kevbin.t.success, "  [✓] Note updated.")
            except Exception:
                kevbin.cprint(kevbin.t.error, "  [X] Wrong password.")
            kevbin.pause()

        elif choice == '4':
            name = kevbin.input_choice("  Note name to delete: ").strip()
            path = os.path.join(NOTES_DIR, f"{name}.enc")
            if not os.path.isfile(path):
                kevbin.cprint(kevbin.t.error, "  [X] Note not found.")
                kevbin.pause()
                continue
            confirm = kevbin.input_choice(f"  Delete '{name}'? (y/n): ").strip().lower()
            if confirm == 'y':
                os.remove(path)
                kevbin.cprint(kevbin.t.success, f"  [✓] Deleted '{name}'.")
            kevbin.pause()

        elif choice == '5':
            notes = _list_notes()
            if notes:
                kevbin.cprint(kevbin.t.accent, f"\n  {len(notes)} note(s):\n")
                for name, mtime in notes:
                    ts = time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))
                    size = os.path.getsize(os.path.join(NOTES_DIR, f"{name}.enc"))
                    kevbin.cprint(kevbin.t.txt, f"    {name:<25} {ts}  ({size} bytes)")
            else:
                kevbin.cprint(kevbin.t.warning, "  [!] No notes stored.")
            kevbin.pause()

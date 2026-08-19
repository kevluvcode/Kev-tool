"""Obfuscator V2 — Python code obfuscation with XOR encryption and Anti-Print."""

import base64
import os
import random
import string


def _rand_name(length=12):
    return '_' + ''.join(random.choices(string.ascii_lowercase + '_', k=length))


def _xor_encrypt(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def run(navi):
    navi.clear()
    navi.section_header('🛡️', 'OBFUSCATOR V2')
    navi.cprint(navi.t.secondary, "  Python code obfuscation with XOR encryption + anti-print.\n")

    path = navi.input_choice("  Path to .py file: ").strip('"').strip("'")
    if not path or not os.path.isfile(path):
        navi.cprint(navi.t.error, "  [X] File not found.")
        navi.pause()
        return

    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()

    navi.cprint(navi.t.dim, f"  Loaded {len(source)} chars.\n")
    navi.cprint(navi.t.secondary, "  [1] XOR + Base64 (recommended)")
    navi.cprint(navi.t.secondary, "  [2] Base64 only (lighter)")
    navi.cprint(navi.t.secondary, "  [3] Full stealth (XOR + B64 + anti-print + mangling)")
    mode = navi.input_choice()

    key = os.urandom(32)
    encoded = base64.b64encode(_xor_encrypt(source.encode(), key)).decode()
    kv, dv = _rand_name(), _rand_name()

    if mode == '2':
        out = f"import base64 as {_rand_name()}\nexec(__import__('base64').b64decode('{encoded}').decode())\n"
    elif mode == '3':
        block = "import builtins as _b;_o=_b.print;def print(*a,**k):pass;_b.print=print;_b.input=lambda *a:'';"
        keys = ','.join(str(b) for b in key)
        out = f"import base64 as {_rand_name()},sys as {_rand_name()}\n__=[{keys}]\n{block}\nexec(''.join(chr(b^__[i%{len(key)}])for i,b in enumerate(__import__('base64').b64decode('{encoded}'))))\n"
    else:
        keys = ','.join(str(b) for b in key)
        out = f"import base64 as {_rand_name()}\n{kv}=[{keys}]\n{dv}='{encoded}'\nexec(''.join(chr(b^{kv}[i%{len(key)}])for i,b in enumerate(__import__('base64').b64decode({dv}))))\n"

    out_path = path.rsplit('.', 1)[0] + '_obf.py'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out)

    navi.cprint(navi.t.success, f"\n  [✓] Saved: {out_path} ({len(source)} -> {len(out)} chars)")
    navi.pause()

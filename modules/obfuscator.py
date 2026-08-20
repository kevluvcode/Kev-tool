"""Obfuscator V3 — Heavy-duty Python obfuscation suite."""

import os
import re
import sys
import ast
import math
import random
import string
import base64
import marshal
import textwrap
import hashlib
import struct


def _rand_name(length=None):
    length = length or random.randint(10, 18)
    first = random.choice(string.ascii_lowercase + string.ascii_uppercase)
    rest = ''.join(random.choices(string.ascii_letters + string.digits, k=length - 1))
    return first + rest


def _rand_hex():
    return ''.join(random.choices('0123456789abcdef', k=random.randint(6, 14)))


def _xor_bytes(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def _rot_bytes(data, n):
    return bytes((b + n) % 256 for b in data)


def _split_bytes(data, chunk_min=2, chunk_max=6):
    chunks = []
    i = 0
    while i < len(data):
        size = random.randint(chunk_min, chunk_max)
        chunks.append(data[i:i + size])
        i += size
    return chunks


def _gen_junk_imports(n=3):
    junk = []
    modules = ['base64', 'codecs', 'hashlib', 'json', 'struct', 'zlib',
               'dis', 'types', 'collections', 'functools', 'itertools',
               'operator', 'string', 'textwrap', 'unicodedata', 'binascii']
    for _ in range(n):
        mod = random.choice(modules)
        alias = _rand_name()
        junk.append(f"import {mod} as {alias}")
    return '\n'.join(junk)


def _gen_opaque_predicates(n=3):
    preds = []
    for _ in range(n):
        x = random.randint(1, 9999)
        always_true = random.choice([
            f"({x} * {x} + {x}) % 2 == 0",
            f"({x} ** 2) >= 0",
            f"len('{_rand_hex()}') > 0",
            f"isinstance({x}, int)",
            f"'{''.join(random.choices(string.ascii_letters, k=3))}' != ''",
            f"{x} + {x} == {2 * x}",
            f"bool({x}) is True",
        ])
        var = _rand_name()
        preds.append(f"{var} = {always_true}")
    return '\n'.join(preds)


def _layer_xor_b64(source, layers=3):
    data = source.encode('utf-8')
    keys = []
    for _ in range(layers):
        key = os.urandom(random.randint(16, 32))
        keys.append(key)
        data = _xor_bytes(data, key)
        data = base64.b64encode(data)
    return data.decode('ascii'), keys


def _layer_rot_xor_b64(source, layers=3):
    data = source.encode('utf-8')
    keys = []
    rots = []
    for _ in range(layers):
        rot = random.randint(1, 250)
        key = os.urandom(random.randint(12, 24))
        rots.append(rot)
        keys.append(key)
        data = _rot_bytes(data, rot)
        data = _xor_bytes(data, key)
        data = base64.b64encode(data)
    return data.decode('ascii'), keys, rots


def _build_decoder_v1(encoded, keys):
    layers = len(keys)
    key_lists = [','.join(str(b) for b in k) for k in reversed(keys)]
    ks = [_rand_name() for _ in range(layers)]
    ds = [_rand_name() for _ in range(layers)]
    lines = []
    lines.append(f"{ds[0]}='{encoded}'")
    for i in range(layers):
        lines.append(f"{ks[i]}=[{key_lists[i]}]")
        if i < layers - 1:
            lines.append(f"{ds[i + 1]}=''.join(chr(b^{ks[i]}[j%{len(keys[i])}])for j,b in enumerate(__import__('base64').b64decode({ds[i]})))")
    lines.append(f"exec({ds[-1]})")
    return ';'.join(lines)


def _build_decoder_v2(encoded, keys, rots):
    key_lists = [','.join(str(b) for b in k) for k in reversed(keys)]
    rot_list = list(reversed(rots))
    ks = [_rand_name() for _ in range(len(keys))]
    ds = [_rand_name() for _ in range(len(keys) + 1)]
    lines = []
    lines.append(f"{ds[0]}='{encoded}'")
    for i in range(len(keys)):
        lines.append(f"{ks[i]}=[{key_lists[i]}]")
        dec = f"''.join(chr(((b-{rot_list[i]})%256)^{ks[i]}[j%{len(keys[i])}])for j,b in enumerate(__import__('base64').b64decode({ds[i]})))"
        lines.append(f"{ds[i + 1]}={dec}")
    lines.append(f"exec({ds[-1]})")
    return ';'.join(lines)


def _wrap_in_try(code):
    return f"try:\n{textwrap.indent(code, '    ')}\nexcept SystemExit:\n    pass\nexcept:\n    pass\n"


def _anti_debug_code():
    checks = [
        f"import sys as {_rand_name()};{random.choice(['sys.settrace','sys.gettrace'])} and None",
        f"__import__('sys').settrace(None)",
    ]
    return random.choice(checks)


def _build_launcher(encoded_payload, keys, mode):
    fn = _rand_name()
    gb = _rand_name()
    loader = _rand_name()
    km = _rand_name()
    obf = _rand_name()

    if mode == '1':
        decoder = _build_decoder_v1(encoded_payload, keys)
    elif mode == '3':
        decoder = _build_decoder_v1(encoded_payload, keys)
    else:
        decoder = f"exec(__import__('base64').b64decode('{encoded_payload}').decode())"

    junk = _gen_junk_imports(random.randint(2, 4))
    predicates = _gen_opaque_predicates(random.randint(2, 4))
    anti_dbg = _anti_debug_code()

    chunk_size = random.randint(40, 80)
    wrapped = textwrap.fill(decoder, chunk_size)

    parts = []
    parts.append(f"# -*- coding: utf-8 -*-")
    parts.append(junk)
    parts.append(predicates)
    parts.append(anti_dbg)
    parts.append(f"{loader} = lambda: None")
    parts.append(f"{fn} = lambda {gb}: exec({gb})")
    parts.append(f"{obf} = '{_rand_hex()}'")
    parts.append(f"{km} = {obf}")
    parts.append(wrapped)

    return '\n'.join(parts)


def _stealth_mode(source):
    key = os.urandom(64)
    data = source.encode('utf-8')
    data = _xor_bytes(data, key)
    data = base64.b64encode(data)

    hex_chunks = _split_bytes(data, 3, 8)
    hex_strs = [c.hex() for c in hex_chunks]
    var = _rand_name()
    parts = ','.join(f"'{h}'" for h in hex_strs)
    decoder = (
        f"exec(bytes(int({var}[i:i+2],16)^{(key[0] ^ 0xFF)} "
        f"for i in range(0,len({var}),2)).decode())"
    )

    anti_debug = _anti_debug_code()
    junk = _gen_junk_imports(random.randint(3, 5))
    predicates = _gen_opaque_predicates(random.randint(3, 5))

    wrapper = f"""{junk}
{predicates}
{anti_debug}
{var}=''{parts}''
exec(''.join(chr(int({var}[i:i+2],16)^{key[0]^0xFF})for i in range(0,len({var}),2)).decode())"""
    return wrapper


def _ast_mangle(source):
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    renamed = {}

    def _mangle_name():
        return '_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(6, 12)))

    class Renamer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if not node.name.startswith('_') and random.random() < 0.6:
                new = _mangle_name()
                renamed[node.name] = new
                node.name = new
            self.generic_visit(node)
            return node

        def visit_Name(self, node):
            if node.id in renamed:
                node.id = renamed[node.id]
            return node

    try:
        tree = Renamer().visit(tree)
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)
    except Exception:
        return source


def _mangle_strings(source):
    def _enc_str(m):
        s = m.group(1)
        if len(s) < 2:
            return m.group(0)
        key = random.randint(1, 254)
        encoded = ''.join(chr((ord(c) ^ key) % 256) for c in s)
        v = _rand_name(8)
        return f"(lambda {v}:''.join(chr(c^{key})for c in {v}))('{encoded.encode('unicode_escape').decode()}')"

    source = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", _enc_str, source)
    source = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', _enc_str, source)
    return source


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('💀', 'OBFUSCATOR V3')
    kevbin.cprint(kevbin.t.secondary, "  Heavy-duty Python obfuscation suite.\n")

    path = kevbin.input_choice("  Path to .py file: ").strip('"').strip("'")
    if not path or not os.path.isfile(path):
        kevbin.cprint(kevbin.t.error, "  [X] File not found.")
        kevbin.pause()
        return

    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()

    kevbin.cprint(kevbin.t.dim, f"  Loaded {len(source)} chars.\n")
    w = kevbin._bw()
    kevbin.box_top(w)
    kevbin.box_row(' 1. XOR + Base64 (3 layers)', w)
    kevbin.box_row(' 2. Base64 only (light)', w)
    kevbin.box_row(' 3. ROT + XOR + B64 (4 layers)', w)
    kevbin.box_row(' 4. Full Stealth (hex chunks + XOR + junk + opaque)', w)
    kevbin.box_row(' 5. AST Rename + String Encrypt + Layered Encode', w)
    kevbin.box_bottom(w)
    mode = kevbin.input_choice("  Select: ")

    kevbin.cprint(kevbin.t.dim, "\n  [~] Obfuscating...")
    tries = 0

    if mode == '2':
        encoded = base64.b64encode(source.encode()).decode()
        out = f"import base64 as {_rand_name()}\nexec(__import__('base64').b64decode('{encoded}').decode())\n"

    elif mode == '3':
        encoded, keys, rots = _layer_rot_xor_b64(source, layers=4)
        decoder = _build_decoder_v2(encoded, keys, rots)
        out = _build_launcher(decoder, keys, mode)

    elif mode == '4':
        out = _stealth_mode(source)

    elif mode == '5':
        tries += 1
        mangled = _ast_mangle(source)
        mangled = _mangle_strings(mangled)
        encoded, keys = _layer_xor_b64(mangled, layers=3)
        decoder = _build_decoder_v1(encoded, keys)
        junk = _gen_junk_imports(random.randint(3, 5))
        predicates = _gen_opaque_predicates(random.randint(3, 5))
        anti_dbg = _anti_debug_code()
        out = f"{junk}\n{predicates}\n{anti_dbg}\n{decoder}\n"

    else:
        encoded, keys = _layer_xor_b64(source, layers=3)
        decoder = _build_decoder_v1(encoded, keys)
        junk = _gen_junk_imports(random.randint(2, 4))
        predicates = _gen_opaque_predicates(random.randint(2, 4))
        anti_dbg = _anti_debug_code()
        out = f"{junk}\n{predicates}\n{anti_dbg}\n{decoder}\n"

    out = f"# -*- coding: utf-8 -*-\n# Obfuscated with Obfuscator V3\n\n{out}"

    out_path = path.rsplit('.', 1)[0] + '_obf.py'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out)

    kevbin.cprint(kevbin.t.success, f"\n  [✓] Saved: {out_path}")
    kevbin.cprint(kevbin.t.dim, f"  Original: {len(source)} chars -> Obfuscated: {len(out)} chars")
    kevbin.cprint(kevbin.t.dim, f"  Layers: {mode} | Tries: {tries + 1}")
    kevbin.pause()

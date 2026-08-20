"""Lua Obfuscator — Heavy-duty Lua code obfuscation suite."""

import os
import re
import random
import string


LUA_KEYWORDS = {
    'and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for',
    'function', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat',
    'return', 'then', 'true', 'until', 'while', 'goto',
    'print', 'tostring', 'tonumber', 'type', 'pcall', 'xpcall',
    'error', 'assert', 'require', 'pairs', 'ipairs', 'next',
    'select', 'unpack', 'rawget', 'rawset', 'setmetatable', 'getmetatable',
    'table', 'string', 'math', 'io', 'os', 'coroutine', 'debug',
}

INITIALS = string.ascii_lowercase + '_'


def _rand_name(length=None):
    length = length or random.randint(6, 14)
    first = random.choice(INITIALS)
    rest = ''.join(random.choices(string.ascii_lowercase + string.digits + '_', k=length - 1))
    return first + rest


def _rand_hex(length=8):
    return ''.join(random.choices('0123456789abcdef', k=length))


def _encode_string_literal(s):
    result = []
    for ch in s:
        if random.random() < 0.5:
            result.append(f"\\{ord(ch):03d}")
        else:
            result.append(ch)
    return '"' + ''.join(result) + '"'


def _xor_encrypt_string(s, key=None):
    key = key or random.randint(1, 254)
    encoded = ''.join(chr((ord(c) ^ key) % 256) for c in s)
    return encoded, key


def _build_xor_decoder(var_name, encoded_str, key, chunk_var):
    lines = []
    lines.append(f"local {chunk_var} = {encoded_str}")
    lines.append(f"local {var_name} = \"\"")
    lines.append(f"for i = 1, #{chunk_var}, 2 do")
    lines.append(f"  local b = tonumber(string.sub({chunk_var}, i, i + 1), 16)")
    lines.append(f"  {var_name} = {var_name} .. string.char(bit.bxor(b, {key}))")
    lines.append(f"end")
    return lines


def _add_dead_code():
    patterns = [
        "if false then end",
        "local _ = nil",
        "pcall(function() end)",
        "do end",
        "for _ = 1, 0 do end",
        "local " + _rand_name() + " = function() return nil end",
        "if 1 == 2 then error('dead') end",
        "local _ = _ and _ or nil",
    ]
    return random.choice(patterns)


def _opaque_predicates(n=3):
    lines = []
    for _ in range(n):
        x = random.randint(1, 9999)
        pred = random.choice([
            f"({x} * {x} + {x}) % 2 == 0",
            f"{x} + {x} == {2 * x}",
            f"#{_rand_hex(4)} > 0",
            f"type({x}) == 'number'",
            f"tostring({x}) ~= nil",
            f"{x} ^ 2 >= 0",
        ])
        var = _rand_name()
        lines.append(f"local {var} = {pred}")
    return '\n'.join(lines)


def _control_flow_flatten(code):
    lines = code.split('\n')
    if len(lines) < 3:
        return code
    chunks = []
    chunk_size = random.randint(2, 4)
    for i in range(0, len(lines), chunk_size):
        chunks.append(lines[i:i + chunk_size])
    if not chunks:
        return code

    state_var = _rand_name()
    goto_var = _rand_name()
    max_state = len(chunks)

    output = []
    output.append(f"local {state_var} = 1")
    output.append(f"local {goto_var} = nil")

    flat_lines = []
    for i, chunk in enumerate(chunks):
        label = _rand_name(6)
        flat_lines.append(f"--[{label}]")
        flat_lines.extend(chunk)
        if i < len(chunks) - 1:
            next_state = i + 2
            flat_lines.append(f"{state_var} = {next_state}")
        else:
            flat_lines.append(f"{state_var} = 0")
        flat_lines.append("")

    output.append(f"while {state_var} > 0 do")
    for i, chunk in enumerate(chunks):
        label = _rand_name(6)
        output.append(f"  if {state_var} == {i + 1} then")
        for line in chunk:
            output.append(f"    {line}")
        if i < len(chunks) - 1:
            output.append(f"    {state_var} = {i + 2}")
        else:
            output.append(f"    {state_var} = 0")
        output.append(f"  end")
    output.append("end")

    return '\n'.join(output)


def _mangle_identifiers(code):
    var_map = {}

    def _is_mangleable(name):
        if name in LUA_KEYWORDS:
            return False
        if name.startswith('_') and len(name) > 1:
            return False
        if len(name) < 2:
            return False
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            return False
        return True

    def _replace_name(m):
        name = m.group(0)
        if _is_mangleable(name) and name not in var_map:
            var_map[name] = _rand_name()
        return var_map.get(name, name)

    code = re.sub(r'\blocal\s+([a-zA-Z_][a-zA-Z0-9_]*)', lambda m: f"local {var_map.setdefault(m.group(1), _rand_name())}" if _is_mangleable(m.group(1)) else m.group(0), code)
    code = re.sub(r'\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)', lambda m: f"function {var_map.setdefault(m.group(1), _rand_name())}" if _is_mangleable(m.group(1)) else m.group(0), code)
    code = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=', lambda m: f"{var_map.get(m.group(1), m.group(1))} =" if _is_mangleable(m.group(1)) else m.group(0), code)
    code = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', lambda m: var_map.get(m.group(0), m.group(0)) if _is_mangleable(m.group(0)) else m.group(0), code)
    return code


def _encrypt_strings_xor(code):
    def _enc(m):
        s = m.group(1)
        if len(s) < 2:
            return m.group(0)
        encoded, key = _xor_encrypt_string(s)
        hex_encoded = encoded.encode('utf-8').hex()
        decoder_var = _rand_name(8)
        chunk_var = _rand_name(8)
        lines = _build_xor_decoder(decoder_var, f'"{hex_encoded}"', key, chunk_var)
        return decoder_var
    code = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', _enc, code)
    code = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", _enc, code)
    return code


def _add_string_concat_chaos(code):
    def _chaos(m):
        s = m.group(1)
        if len(s) < 3:
            return m.group(0)
        parts = []
        for ch in s:
            if random.random() < 0.4:
                parts.append(f"string.char({ord(ch)})")
            else:
                parts.append(_encode_string_literal(ch))
        return ' .. '.join(parts)
    code = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', _chaos, code)
    return code


def _wrap_chunks(code):
    lines = code.split('\n')
    output = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('--') and random.random() < 0.12:
            var = _rand_name()
            output.append(f"local {var} = (function() {stripped} return nil end)()")
        else:
            output.append(line)
    return '\n'.join(output)


def _strip_comments(code):
    code = re.sub(r'--\[\[.*?\]\]', '', code, flags=re.DOTALL)
    code = re.sub(r'--.*', '', code)
    return code


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('💀', 'LUA OBFUSCATOR')
    kevbin.cprint(kevbin.t.secondary, "  Heavy-duty Lua code obfuscation.\n")

    code = kevbin.input_choice("  Enter Lua code (or 'file' to load): ")
    if not code:
        return

    if code.strip().lower() == 'file':
        path = kevbin.input_choice("  File path: ").strip('"').strip("'")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()
            return

    w = kevbin._bw()
    kevbin.box_top(w)
    kevbin.box_row(' 1. Identifier Mangle + Dead Code', w)
    kevbin.box_row(' 2. XOR String Encrypt + Opaque Predicates', w)
    kevbin.box_row(' 3. Control Flow Flatten + Mangle', w)
    kevbin.box_row(' 4. Full Stealth (all layers)', w)
    kevbin.box_bottom(w)
    mode = kevbin.input_choice("  Select: ")

    kevbin.cprint(kevbin.t.dim, "\n  [~] Obfuscating Lua...")

    code = _strip_comments(code)

    if mode == '1':
        code = _mangle_identifiers(code)
        code = _add_dead_code() + '\n' + code + '\n' + _add_dead_code()
        code = _wrap_chunks(code)

    elif mode == '2':
        code = _encrypt_strings_xor(code)
        predicates = _opaque_predicates(random.randint(3, 5))
        code = predicates + '\n' + code
        code = _mangle_identifiers(code)
        code = _wrap_chunks(code)

    elif mode == '3':
        code = _control_flow_flatten(code)
        code = _mangle_identifiers(code)
        code = _opaque_predicates(random.randint(2, 3)) + '\n' + code
        code = _add_string_concat_chaos(code)

    else:
        code = _mangle_identifiers(code)
        code = _encrypt_strings_xor(code)
        code = _control_flow_flatten(code)
        predicates = _opaque_predicates(random.randint(4, 6))
        dead = '\n'.join(_add_dead_code() for _ in range(random.randint(3, 6)))
        code = predicates + '\n' + dead + '\n' + code
        code = _add_string_concat_chaos(code)
        code = _wrap_chunks(code)

    kevbin.cprint(kevbin.t.success, f"\n  [✓] Obfuscated ({mode})")
    kevbin.box.code(code)

    save = kevbin.input_choice("\n  Save to file? (y/n): ").strip().lower()
    if save == 'y':
        out_path = kevbin.input_choice("  Output path [obfuscated.lua]: ").strip().strip('"').strip("'")
        if not out_path:
            out_path = "obfuscated.lua"
        try:
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(code)
            kevbin.cprint(kevbin.t.success, f"  [✓] Saved to {out_path}")
        except Exception as e:
            kevbin.cprint(kevbin.t.error, f"  [X] {e}")

    kevbin.pause()

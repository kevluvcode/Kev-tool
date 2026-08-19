import re
import random
import string

LUA_KEYWORDS = {'and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for', 'function', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat', 'return', 'then', 'true', 'until', 'while', 'goto'}

def _rand_name(prefix="v"):
    return prefix + "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(4, 8)))

def _encode_string(s):
    result = []
    for ch in s:
        if ch.isprintable() and ch not in '"\\':
            if random.random() < 0.3:
                result.append(f"\\{ord(ch):03d}")
            else:
                result.append(ch)
        else:
            result.append(f"\\{ord(ch):03d}")
    return '"' + "".join(result) + '"'

def _add_dead_code():
    patterns = [
        "if false then print('dead') end",
        "local {} = {}\n".format(_rand_name(), _rand_name()),
        "for i=1,0 do end",
        "pcall(function() end)",
        "type({})".format(_rand_name()),
    ]
    return random.choice(patterns)

def run(kevbin):
    kevbin.box.title("Lua Obfuscator")
    code = kevbin.box.input("Enter Lua code (or 'file' to load from file): ")
    if not code:
        return
    
    if code.strip() == "file":
        path = kevbin.box.input("File path: ")
        try:
            with open(path, 'r') as f:
                code = f.read()
        except Exception as e:
            kevbin.box.error(f"Failed to read file: {e}")
            return
    
    var_map = {}
    
    def is_valid_var(name):
        return name not in LUA_KEYWORDS and not name.startswith('_') and len(name) >= 2 and re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name)
    
    code = re.sub(r'\blocal\s+([a-zA-Z_][a-zA-Z0-9_]*)', lambda m: f"local {var_map.setdefault(m.group(1), _rand_name())}" if is_valid_var(m.group(1)) else m.group(0), code)
    code = re.sub(r'\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)', lambda m: f"function {var_map.setdefault(m.group(1), _rand_name())}" if is_valid_var(m.group(1)) else m.group(0), code)
    code = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=', lambda m: f"{var_map.get(m.group(1), m.group(1))} =" if is_valid_var(m.group(1)) else m.group(0), code)
    code = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', lambda m: var_map.get(m.group(0), m.group(0)) if is_valid_var(m.group(0)) else m.group(0), code)
    
    code = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', lambda m: _encode_string(m.group(1)), code)
    code = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", lambda m: _encode_string(m.group(1)), code)
    
    lines = code.split('\n')
    output = []
    for line in lines:
        output.append(line)
        if random.random() < 0.15 and line.strip() and not line.strip().startswith('--'):
            output.append(_add_dead_code())
    code = '\n'.join(output)
    
    code = re.sub(r'(--\[\[.*?\]\])', '', code, flags=re.DOTALL)
    code = re.sub(r'(--.*)', '', code)
    
    kevbin.box.code(code)
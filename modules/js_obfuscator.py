import re
import random
import string

JS_KEYWORDS = {'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 'default', 'delete', 'do', 'else', 'export', 'extends', 'finally', 'for', 'function', 'if', 'import', 'in', 'instanceof', 'new', 'return', 'super', 'switch', 'this', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield', 'let', 'await', 'async', 'of', 'static', 'enum', 'implements', 'interface', 'package', 'protected', 'private', 'public'}

def _rand_name(prefix="v"):
    return prefix + "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(4, 8)))

def _encode_string(s):
    result = []
    for ch in s:
        if ch.isprintable() and ch not in '"\\':
            if random.random() < 0.3:
                result.append(f"\\u{ord(ch):04x}")
            else:
                result.append(ch)
        else:
            result.append(f"\\u{ord(ch):04x}")
    return '"' + "".join(result) + '"'

def _add_dead_code():
    patterns = [
        "if(false){console.log('dead');}",
        "var {} = {};".format(_rand_name(), _rand_name()),
        "for(var i=0;i<0;i++){};",
        "try{}catch(e){};",
        "typeof {};".format(_rand_name()),
    ]
    return random.choice(patterns)

def run(kevbin):
    kevbin.box.title("JavaScript Obfuscator")
    code = kevbin.box.input("Enter JS code (or 'file' to load from file): ")
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
    
    def replace_var(match):
        name = match.group(1)
        if name in JS_KEYWORDS or name.startswith('_') or len(name) < 2:
            return match.group(0)
        if name not in var_map:
            var_map[name] = _rand_name()
        return match.group(0).replace(name, var_map[name])
    
    code = re.sub(r'\b(var|let|const)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)', lambda m: f"{m.group(1)} {var_map.setdefault(m.group(2), _rand_name())}", code)
    code = re.sub(r'\bfunction\s+([a-zA-Z_$][a-zA-Z0-9_$]*)', lambda m: f"function {var_map.setdefault(m.group(1), _rand_name())}", code)
    code = re.sub(r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*function', lambda m: f"{var_map.setdefault(m.group(1), _rand_name())}: function", code)
    code = re.sub(r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=', lambda m: f"{var_map.get(m.group(1), m.group(1))} =", code)
    code = re.sub(r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\b', lambda m: var_map.get(m.group(0), m.group(0)) if m.group(0) not in JS_KEYWORDS else m.group(0), code)
    
    code = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', lambda m: _encode_string(m.group(1)), code)
    code = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", lambda m: _encode_string(m.group(1)), code)
    
    lines = code.split('\n')
    output = []
    for line in lines:
        output.append(line)
        if random.random() < 0.15 and line.strip() and not line.strip().startswith('//'):
            output.append(_add_dead_code())
    code = '\n'.join(output)
    
    kevbin.box.code(code)
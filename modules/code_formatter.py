import re

def run(kevbin):
    kevbin.box.title("Code Formatter")
    code = kevbin.box.input("Enter code (or 'file' to load): ")
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
    
    lines = code.split('\n')
    
    indent_size = 4
    indent_level = 0
    output = []
    prev_blank = False
    
    for line in lines:
        stripped = line.rstrip()
        
        if not stripped:
            if not prev_blank and output:
                output.append("")
            prev_blank = True
            continue
        
        prev_blank = False
        
        if re.match(r'^\s*(else|elif|except|finally|catch|}\s*(else|elif|except|finally|catch)?)', stripped):
            indent_level = max(0, indent_level - 1)
        
        if re.match(r'^\s*[)}\]]', stripped):
            indent_level = max(0, indent_level - 1)
        
        indent = " " * (indent_level * indent_size)
        output.append(indent + stripped.lstrip())
        
        if re.search(r':\s*$', stripped) and not re.search(r':\s*#', stripped):
            if not re.match(r'^\s*(elif|else|except|finally)\s*:', stripped):
                indent_level += 1
        
        if re.search(r'{\s*$', stripped) or re.search(r'\(\s*$', stripped) or re.search(r'\[\s*$', stripped):
            pass
        
        if re.search(r'[)}\]]\s*$', stripped) and not re.search(r'[({\[]\s*[)}\]]\s*$', stripped):
            indent_level = max(0, indent_level - 1)
    
    result = "\n".join(output)
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    kevbin.box.code(result)
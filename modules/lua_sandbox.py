import sys
import subprocess

def run(kevbin):
    kevbin.box.title("Lua Sandbox")
    
    try:
        import lupa
        has_lupa = True
    except ImportError:
        has_lupa = False
        kevbin.box.warn("lupa not installed. Install with: pip install lupa")
        kevbin.box.info("Falling back to system lua interpreter...")
    
    while True:
        kevbin.box.title("Lua Sandbox - Enter code (empty to exit)")
        code = kevbin.box.input("lua> ")
        if not code:
            break
        
        if code.strip() == "exit":
            break
        
        if has_lupa:
            lua = lupa.LuaRuntime(unpack_returned_tuples=True)
            try:
                # Create safe environment
                safe_globals = {
                    'print': print,
                    'pairs': pairs,
                    'ipairs': ipairs,
                    'next': next,
                    'type': type,
                    'tostring': str,
                    'tonumber': float,
                    'math': __import__('math'),
                    'string': __import__('string'),
                    'table': {},
                    'os': {'clock': lambda: 0, 'time': lambda: 0, 'date': lambda: ""},
                }
                lua.globals().update(safe_globals)
                result = lua.execute(code)
                if result is not None:
                    kevbin.box.success(f"Result: {result}")
            except Exception as e:
                kevbin.box.error(f"Error: {e}")
        else:
            try:
                proc = subprocess.run(['lua', '-e', code], capture_output=True, text=True, timeout=5)
                if proc.stdout:
                    kevbin.box.code(proc.stdout)
                if proc.stderr:
                    kevbin.box.error(proc.stderr)
            except FileNotFoundError:
                kevbin.box.error("lua interpreter not found in PATH")
                break
            except subprocess.TimeoutExpired:
                kevbin.box.error("Execution timed out")
            except Exception as e:
                kevbin.box.error(f"Error: {e}")
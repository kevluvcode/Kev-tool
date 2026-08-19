import base64
import binascii


def _try_decode(data: bytes) -> dict:
    results = {}
    
    for name, decoder in [
        ("Standard", base64.b64decode),
        ("URL-Safe", base64.urlsafe_b64decode),
        ("Base32", base64.b32decode),
        ("Base16/Hex", base64.b16decode),
    ]:
        try:
            decoded = decoder(data)
            results[name] = decoded
        except Exception:
            pass
    
    try:
        results["ASCII"] = data.decode('ascii')
    except UnicodeDecodeError:
        pass
    
    try:
        results["UTF-8"] = data.decode('utf-8')
    except UnicodeDecodeError:
        pass
    
    try:
        results["UTF-16"] = data.decode('utf-16')
    except UnicodeDecodeError:
        pass
    
    return results


def _format_bytes(data: bytes, max_len: int = 100) -> str:
    if len(data) > max_len:
        return data[:max_len].hex() + f" ... ({len(data)} bytes total)"
    return data.hex()


def run(kevbin):
    kevbin.box_title("Base64 Decoder")
    kevbin.box_print("Decode Base64, Base32, Base16 strings. Auto-detects encoding.")
    
    while True:
        kevbin.box_print("")
        inp = kevbin.box_input("Enter encoded string (or 'q' to quit): ").strip()
        if inp.lower() in ('q', 'quit', 'exit'):
            break
        if not inp:
            continue
        
        inp_bytes = inp.encode('ascii')
        
        results = _try_decode(inp_bytes)
        
        if not results:
            kevbin.box_print("[red]Could not decode with any standard encoding[/red]")
            continue
        
        rows = [["Encoding", "Decoded Output"]]
        for name, output in results.items():
            if isinstance(output, bytes):
                display = _format_bytes(output)
                rows.append([name, f"[dim]{display}[/dim]"])
            else:
                rows.append([name, output])
        
        kevbin.box_table(rows, title="Decoded Results")
        
        raw_bytes = None
        for name in ["Standard", "URL-Safe", "Base32", "Base16/Hex"]:
            if name in results and isinstance(results[name], bytes):
                raw_bytes = results[name]
                break
        
        if raw_bytes:
            kevbin.box_print(f"\n[dim]Raw bytes ({len(raw_bytes)} bytes): {raw_bytes.hex()}[/dim]")
            
            if len(raw_bytes) <= 32:
                hex_dump = " ".join(f"{b:02x}" for b in raw_bytes)
                kevbin.box_print(f"[dim]Hex: {hex_dump}[/dim]")
                
                ascii_dump = "".join(chr(b) if 32 <= b < 127 else "." for b in raw_bytes)
                kevbin.box_print(f"[dim]ASCII: {ascii_dump}[/dim]")


if __name__ == "__main__":
    class MockKevbin:
        def box_title(self, t): print(f"\n=== {t} ===")
        def box_print(self, t): print(t)
        def box_input(self, t): return input(t + " ")
        def box_table(self, rows, title=""):
            if title: print(f"\n{title}")
            for row in rows:
                print(" | ".join(str(c) for c in row))
        def box_code(self, code, language=""): print(code)
    
    run(MockKevbin())
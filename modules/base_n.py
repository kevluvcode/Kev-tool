import string

BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
BASE32_ALPHABET_HEX = "0123456789ABCDEFGHIJKLMNOPQRSTUV"
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE85_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~"

BASES = {
    "2": ("Binary", "01"),
    "8": ("Octal", "01234567"),
    "10": ("Decimal", "0123456789"),
    "16": ("Hexadecimal", "0123456789ABCDEF"),
    "32": ("Base32 (RFC 4648)", BASE32_ALPHABET),
    "32h": ("Base32 (Hex)", BASE32_ALPHABET_HEX),
    "58": ("Base58 (Bitcoin)", BASE58_ALPHABET),
    "62": ("Base62", BASE62_ALPHABET),
    "85": ("Base85 (Z85)", BASE85_ALPHABET),
}


def _decode_to_int(value: str, base: int, alphabet: str) -> int:
    value = value.strip().upper()
    if base == 16 and value.startswith("0X"):
        value = value[2:]
    elif base == 2 and value.startswith("0B"):
        value = value[2:]
    elif base == 8 and value.startswith("0O"):
        value = value[2:]
    
    if base in (32, 58, 62, 85):
        char_to_val = {c: i for i, c in enumerate(alphabet)}
        result = 0
        for char in value:
            if char not in char_to_val:
                raise ValueError(f"Invalid character '{char}' for base {base}")
            result = result * base + char_to_val[char]
        return result
    
    return int(value, base)


def _encode_from_int(value: int, base: int, alphabet: str) -> str:
    if value == 0:
        return alphabet[0]
    
    if base in (32, 58, 62, 85):
        result = ""
        while value > 0:
            value, rem = divmod(value, base)
            result = alphabet[rem] + result
        return result
    
    if base == 2:
        return bin(value)[2:]
    elif base == 8:
        return oct(value)[2:]
    elif base == 10:
        return str(value)
    elif base == 16:
        return hex(value)[2:].upper()
    
    result = ""
    while value > 0:
        value, rem = divmod(value, base)
        result = alphabet[rem] + result
    return result


def _convert_base(value: str, from_base: str, to_base: str) -> str:
    from_name, from_alphabet = BASES[from_base]
    to_name, to_alphabet = BASES[to_base]
    
    from_base_num = int(from_base) if from_base not in ("32h",) else 32
    to_base_num = int(to_base) if to_base not in ("32h",) else 32
    
    decoded = _decode_to_int(value, from_base_num, from_alphabet)
    return _encode_from_int(decoded, to_base_num, to_alphabet)


def run(kevbin):
    kevbin.box_title("Base-N Encoder/Decoder")
    kevbin.box_print("Convert between binary, octal, decimal, hex, base32, base58, base62, base85")
    
    kevbin.box_print("\nSupported bases:")
    for key, (name, alphabet) in BASES.items():
        kevbin.box_print(f"  {key:>3} - {name} ({alphabet[:16]}{'...' if len(alphabet) > 16 else ''})")
    
    while True:
        kevbin.box_print("")
        from_base = kevbin.box_input("From base (2,8,10,16,32,32h,58,62,85) or 'q' to quit: ").strip().lower()
        if from_base in ('q', 'quit', 'exit'):
            break
        if from_base not in BASES:
            kevbin.box_print("[red]Invalid base[/red]")
            continue
        
        value = kevbin.box_input(f"Value in base {from_base}: ").strip()
        if not value:
            continue
        
        to_base = kevbin.box_input("To base (2,8,10,16,32,32h,58,62,85) [10]: ").strip().lower() or "10"
        if to_base not in BASES:
            kevbin.box_print("[red]Invalid target base[/red]")
            continue
        
        try:
            result = _convert_base(value, from_base, to_base)
            
            from_name, _ = BASES[from_base]
            to_name, _ = BASES[to_base]
            
            rows = [
                ["Property", "Value"],
                [f"Input ({from_name})", value],
                [f"Output ({to_name})", result],
            ]
            kevbin.box_table(rows, title="Conversion Result")
            
            if to_base == "10":
                decoded = _decode_to_int(value, int(from_base) if from_base != "32h" else 32, BASES[from_base][1])
                kevbin.box_print(f"[dim]Decimal value: {decoded}[/dim]")
                
        except ValueError as e:
            kevbin.box_print(f"[red]Error: {e}[/red]")
        except Exception as e:
            kevbin.box_print(f"[red]Unexpected error: {e}[/red]")


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
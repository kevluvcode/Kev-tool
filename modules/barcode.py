import re

CODE128_PATTERNS = {
    ' ': "11011001100", '!': "1100101100", '"': "1100100110", '#': "1001001100",
    '$': "1001000110", '%': "1000100110", '&': "1101001100", "'": "1100101000",
    '(': "1100100010", ')': "1100010100", '*': "1100010010", '+': "1011001100",
    ',': "1001101100", '-': "1001100110", '.': "1011000110", '/': "1001101110",
    '0': "1101000110", '1': "1100101110", '2': "1101110110", '3': "1101110100",
    '4': "1101110010", '5': "1101110001", '6': "1101101110", '7': "1101101101",
    '8': "1101101010", '9': "1101011010", ':': "1101011100", ';': "1101101110",
    '<': "1110101100", '=': "1110100110", '>': "1110010110", '?': "1110111010",
    '@': "1110110100", 'A': "1110110010", 'B': "1110110001", 'C': "1110101110",
    'D': "1110010111", 'E': "1110111010", 'F': "1110111010", 'G': "1110110110",
    'H': "1110110100", 'I': "1110011010", 'J': "1110011010", 'K': "1101110111",
    'L': "1101111010", 'M': "1101111010", 'N': "1101111010", 'O': "1110110111",
    'P': "1110110111", 'Q': "1110110111", 'R': "1110110111", 'S': "1110110111",
    'T': "1110110111", 'U': "1110110111", 'V': "1110110111", 'W': "1110110111",
    'X': "1110110111", 'Y': "1110110111", 'Z': "1110110111", '[': "1110110111",
    '\\': "1110110111", ']': "1110110111", '^': "1110110111", '_': "1110110111",
    '`': "1110110111", 'a': "1110110111", 'b': "1110110111", 'c': "1110110111",
    'd': "1110110111", 'e': "1110110111", 'f': "1110110111", 'g': "1110110111",
    'h': "1110110111", 'i': "1110110111", 'j': "1110110111", 'k': "1110110111",
    'l': "1110110111", 'm': "1110110111", 'n': "1110110111", 'o': "1110110111",
    'p': "1110110111", 'q': "1110110111", 'r': "1110110111", 's': "1110110111",
    't': "1110110111", 'u': "1110110111", 'v': "1110110111", 'w': "1110110111",
    'x': "1110110111", 'y': "1110110111", 'z': "1110110111", '{': "1110110111",
    '|': "1110110111", '}': "1110110111", '~': "1110110111",
}

CODE128_START_A = "11010000100"
CODE128_START_B = "11010010000"
CODE128_START_C = "11010011100"
CODE128_STOP = "1100011101011"

CODE39_PATTERNS = {
    '0': "101001101101", '1': "110100101011", '2': "101100101011", '3': "110110010101",
    '4': "101001101011", '5': "110100110101", '6': "101100110101", '7': "101001011011",
    '8': "110100101101", '9': "101100101101", 'A': "110101001011", 'B': "101101001011",
    'C': "110110100101", 'D': "101011001011", 'E': "110101100101", 'F': "101101100101",
    'G': "101010011011", 'H': "110101001101", 'I': "101101001101", 'J': "101010110011",
    'K': "110101010011", 'L': "101101010011", 'M': "110110101001", 'N': "101011010011",
    'O': "110101101001", 'P': "101101101001", 'Q': "101010010111", 'R': "110101001011",
    'S': "101101001011", 'T': "110110100101", 'U': "110101010101", 'V': "101101010101",
    'W': "110110101010", 'X': "101011010110", 'Y': "110101101010", 'Z': "101101101010",
    '-': "101010101110", '.': "110101010110", ' ': "101101010110", '$': "101011011010",
    '/': "101101011010", '+': "101011010110", '%': "110101011010", '*': "101011010110",
}

CODE39_START_STOP = "101011010110"


def _code128_encode(text: str) -> str:
    text = text.upper()
    
    has_lower = any(c.islower() for c in text)
    has_digits = any(c.isdigit() for c in text)
    
    if has_digits and not has_lower:
        mode = 'C'
        start = CODE128_START_C
    elif has_lower:
        mode = 'A'
        start = CODE128_START_A
    else:
        mode = 'B'
        start = CODE128_START_B
    
    bars = [start]
    
    for ch in text:
        if ch in CODE128_PATTERNS:
            bars.append(CODE128_PATTERNS[ch])
        else:
            bars.append(CODE128_PATTERNS.get(' ', "11011001100"))
    
    checksum = 0
    if mode == 'C':
        checksum = 105
    elif mode == 'B':
        checksum = 104
    else:
        checksum = 103
    
    for i, ch in enumerate(text):
        val = 0
        if ch in CODE128_PATTERNS:
            idx = list(CODE128_PATTERNS.keys()).index(ch)
            val = idx if idx < 106 else 0
        checksum += val * (i + 1)
    
    checksum = checksum % 103
    checksum_pattern = list(CODE128_PATTERNS.values())[checksum] if checksum < len(CODE128_PATTERNS) else CODE128_PATTERNS[' ']
    bars.append(checksum_pattern)
    bars.append(CODE128_STOP)
    
    return ''.join(bars)


def _code39_encode(text: str) -> str:
    text = text.upper()
    bars = [CODE39_START_STOP]
    
    for ch in text:
        if ch in CODE39_PATTERNS:
            bars.append(CODE39_PATTERNS[ch])
            bars.append('0')
        else:
            bars.append(CODE39_PATTERNS.get(' ', "101101010110"))
            bars.append('0')
    
    bars.append(CODE39_START_STOP)
    return ''.join(bars)


def _render_barcode(pattern: str, height: int = 4, show_text: bool = True, text: str = "") -> str:
    lines = []
    for _ in range(height):
        line = ""
        for bit in pattern:
            if bit == '1':
                line += "█"
            else:
                line += " "
        lines.append(line)
    
    if show_text and text:
        text_line = ""
        char_width = len(pattern) // max(len(text), 1)
        for i, ch in enumerate(text):
            text_line += ch.center(char_width)
        lines.append("")
        lines.append(text_line.center(len(pattern)))
    
    return "\n".join(lines)


def run(kevbin):
    kevbin.box_title("Barcode Generator (Text Art)")
    kevbin.box_print("Generate Code128 or Code39 barcodes as text art")
    
    while True:
        kevbin.box_print("")
        text = kevbin.box_input("Text to encode (or 'q' to quit): ").strip()
        if text.lower() in ('q', 'quit', 'exit'):
            break
        if not text:
            continue
        
        kevbin.box_print("Barcode types:")
        kevbin.box_print("  1. Code128 (alphanumeric, compact)")
        kevbin.box_print("  2. Code39 (alphanumeric, wider)")
        
        btype = kevbin.box_input("Select type [1]: ").strip() or "1"
        
        height = kevbin.box_input("Bar height (rows) [4]: ").strip()
        try:
            height = int(height) if height else 4
            height = max(1, min(10, height))
        except:
            height = 4
        
        show_text = kevbin.box_input("Show text below? (y/n) [y]: ").strip().lower() != 'n'
        
        try:
            if btype == "1":
                pattern = _code128_encode(text)
                kevbin.box_print("\n[cyan]Code128 Barcode:[/cyan]")
            else:
                pattern = _code39_encode(text)
                kevbin.box_print("\n[cyan]Code39 Barcode:[/cyan]")
            
            rendered = _render_barcode(pattern, height, show_text, text)
            kevbin.box_code(rendered)
            
            kevbin.box_print(f"[dim]Pattern length: {len(pattern)} bars[/dim]")
            
        except Exception as e:
            kevbin.box_print(f"[red]Error: {e}[/red]")


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
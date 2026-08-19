import re

ROMAN_NUMERALS = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
]

ROMAN_PATTERN = re.compile(r'^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$', re.I)


def int_to_roman(num: int) -> str:
    if not 1 <= num <= 3999:
        raise ValueError("Roman numerals only support 1-3999")
    result = ""
    for value, numeral in ROMAN_NUMERALS:
        count, num = divmod(num, value)
        result += numeral * count
    return result


def roman_to_int(roman: str) -> int:
    roman = roman.upper().strip()
    if not ROMAN_PATTERN.match(roman):
        raise ValueError("Invalid Roman numeral")
    
    result = 0
    i = 0
    while i < len(roman):
        if i + 1 < len(roman):
            two_char = roman[i:i+2]
            for value, numeral in ROMAN_NUMERALS:
                if numeral == two_char:
                    result += value
                    i += 2
                    break
            else:
                for value, numeral in ROMAN_NUMERALS:
                    if numeral == roman[i]:
                        result += value
                        i += 1
                        break
        else:
            for value, numeral in ROMAN_NUMERALS:
                if numeral == roman[i]:
                    result += value
                    i += 1
                    break
    return result


def roman(kevbin):
    kevbin.box_title("Roman Numeral Converter")
    kevbin.box_print("Convert between Roman numerals and integers (1-3999)")
    
    while True:
        kevbin.box_print("")
        inp = kevbin.box_input("Enter number or Roman numeral (or 'q' to quit): ").strip()
        if inp.lower() in ('q', 'quit', 'exit'):
            break
        if not inp:
            continue
        
        try:
            num = int(inp)
            result = int_to_roman(num)
            kevbin.box_print(f"[green]{num} = {result}[/green]")
        except ValueError:
            try:
                result = roman_to_int(inp)
                kevbin.box_print(f"[green]{inp.upper()} = {result}[/green]")
            except ValueError as e:
                kevbin.box_print(f"[red]{e}[/red]")


def convert(kevbin):
    kevbin.box_title("Number System Converter")
    kevbin.box_print("Convert between decimal, hexadecimal, binary, octal")
    
    bases = {
        "dec": (10, "Decimal"),
        "hex": (16, "Hexadecimal"),
        "bin": (2, "Binary"),
        "oct": (8, "Octal"),
    }
    
    while True:
        kevbin.box_print("")
        inp = kevbin.box_input("Enter number (prefix with 0x, 0b, 0o or 'q' to quit): ").strip()
        if inp.lower() in ('q', 'quit', 'exit'):
            break
        if not inp:
            continue
        
        try:
            if inp.lower().startswith("0x"):
                value = int(inp, 16)
            elif inp.lower().startswith("0b"):
                value = int(inp, 2)
            elif inp.lower().startswith("0o"):
                value = int(inp, 8)
            else:
                value = int(inp)
            
            rows = [["Base", "Value"]]
            for key, (base, name) in bases.items():
                if base == 10:
                    rows.append([name, str(value)])
                elif base == 16:
                    rows.append([name, f"0x{value:X}"])
                elif base == 2:
                    rows.append([name, f"0b{value:b}"])
                elif base == 8:
                    rows.append([name, f"0o{value:o}"])
            
            kevbin.box_table(rows, title="Number Conversions")
            
        except ValueError:
            kevbin.box_print("[red]Invalid number format[/red]")


def run(kevbin):
    kevbin.box_title("Numerals Tools")
    kevbin.box_print("Select a tool:")
    kevbin.box_print("  1. Roman Numerals ↔ Integer")
    kevbin.box_print("  2. Number System Converter (dec/hex/bin/oct)")
    
    choice = kevbin.box_input("Choice [1]: ").strip() or "1"
    
    if choice == "1":
        roman(kevbin)
    elif choice == "2":
        convert(kevbin)
    else:
        kevbin.box_print("[red]Invalid choice[/red]")


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
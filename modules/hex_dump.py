"""Hex Dump — View file/memory hex dumps."""


def _hexdump(data, width=16):
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"  {i:08x}  {hex_part:<{width*3}}  {ascii_part}")
    return '\n'.join(lines)


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🛡️', 'HEX DUMP')
    kevbin.cprint(kevbin.t.secondary, "  [1]  Dump file")
    kevbin.cprint(kevbin.t.secondary, "  [2]  Dump text as hex")
    kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
    kevbin.line()
    choice = kevbin.input_choice()
    if choice == '0': return

    if choice == '1':
        import os
        path = kevbin.input_choice("  File path: ").strip().strip('"')
        if not path or not os.path.isfile(path):
            kevbin.cprint(kevbin.t.error, "  [X] File not found.")
            kevbin.pause()
            return
        with open(path, 'rb') as f:
            data = f.read(512)
        kevbin.cprint(kevbin.t.accent, f"\n  Hex dump of {os.path.basename(path)} ({len(data)} bytes):\n")
        print(_hexdump(data))
        if os.path.getsize(path) > 512:
            kevbin.cprint(kevbin.t.dim, f"  ... ({os.path.getsize(path) - 512} more bytes)")
        kevbin.pause()

    elif choice == '2':
        text = kevbin.input_choice("  Text: ")
        if text:
            kevbin.cprint(kevbin.t.accent, f"\n  Hex dump:\n")
            print(_hexdump(text.encode()))
        kevbin.pause()


def binary(kevbin):
    run(kevbin)

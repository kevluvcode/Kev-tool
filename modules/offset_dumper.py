import os
import sys
import struct
import binascii
import time

try:
    import kevbin
    from kevbin import box_table, box, txt, num, head, sub, prompt, cprint, color
except ImportError:
    class _C:
        def __getattr__(self, _): return lambda *a, **kw: None
    kevbin = _C()
    def box_table(*a, **kw): pass
    def box(*a, **kw): pass
    def txt(*a): return str(a)
    def num(*a): return str(a)
    def head(*a): return str(a)
    def sub(*a): return str(a)
    def prompt(*a): return input()
    def cprint(*a, **kw): print(*[x for x in a if isinstance(x, str)])

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    try:
        kevbin.pause()
    except:
        input("\n\033[90mPress Enter to continue...\033[0m")

def format_hex_line(offset, chunk, bytes_per_line=16):
    hex_part = ""
    ascii_part = ""
    for i, b in enumerate(chunk):
        hex_part += f"{b:02x} "
        ascii_part += chr(b) if 32 <= b <= 126 else '.'
        if i == bytes_per_line // 2 - 1:
            hex_part += " "
    padding = "   " * (bytes_per_line - len(chunk))
    return f"  {offset:08x}  {hex_part}{padding} |{ascii_part}|"

def hexdump(data, start_offset=0, bytes_per_line=16):
    lines = []
    for i in range(0, len(data), bytes_per_line):
        chunk = data[i:i+bytes_per_line]
        lines.append(format_hex_line(start_offset + i, chunk, bytes_per_line))
    return '\n'.join(lines)

def search_bytes(data, pattern, start=0):
    results = []
    idx = start
    while idx < len(data):
        pos = data.find(pattern, idx)
        if pos == -1:
            break
        results.append(pos)
        idx = pos + 1
        if len(results) >= 100:
            break
    return results

def find_pe_sections(data):
    if data[:2] != b'MZ':
        return []
    try:
        pe_offset = struct.unpack_from('<I', data, 0x3C)[0]
        if data[pe_offset:pe_offset+4] != b'PE\x00\x00':
            return []
        num_sections = struct.unpack_from('<H', data, pe_offset + 6)[0]
        opt_offset = pe_offset + 24
        is_64 = struct.unpack_from('<H', data, opt_offset)[0] == 0x20B
        section_offset = opt_offset + (112 if is_64 else 96)
        sections = []
        for i in range(min(num_sections, 20)):
            off = section_offset + i * 40
            name = data[off:off+8].rstrip(b'\x00').decode('ascii', errors='replace')
            vsize = struct.unpack_from('<I', data, off + 8)[0]
            vaddr = struct.unpack_from('<I', data, off + 12)[0]
            raw_size = struct.unpack_from('<I', data, off + 16)[0]
            raw_ptr = struct.unpack_from('<I', data, off + 20)[0]
            chars = struct.unpack_from('<I', data, off + 36)[0]
            flags = []
            if chars & 0x20: flags.append("CODE")
            if chars & 0x40: flags.append("INIT")
            if chars & 0x80: flags.append("DATA")
            if chars & 0x20000000: flags.append("EXEC")
            if chars & 0x40000000: flags.append("READ")
            if chars & 0x80000000: flags.append("WRITE")
            sections.append({
                "name": name, "vaddr": vaddr, "vsize": vsize,
                "raw_ptr": raw_ptr, "raw_size": raw_size,
                "flags": flags, "chars": chars,
            })
        return sections
    except:
        return []

def find_elf_sections(data):
    if data[:4] != b'\x7fELF':
        return []
    try:
        is_64 = data[4] == 2
        if is_64:
            e_shoff = struct.unpack_from('<Q', data, 40)[0]
            e_shentsize = struct.unpack_from('<H', data, 58)[0]
            e_shnum = struct.unpack_from('<H', data, 60)[0]
            e_shstrndx = struct.unpack_from('<H', data, 62)[0]
        else:
            e_shoff = struct.unpack_from('<I', data, 32)[0]
            e_shentsize = struct.unpack_from('<H', data, 46)[0]
            e_shnum = struct.unpack_from('<H', data, 48)[0]
            e_shstrndx = struct.unpack_from('<H', data, 50)[0]

        if e_shnum == 0 or e_shentsize == 0:
            return []

        str_sh_off = e_shoff + e_shstrndx * e_shentsize
        if is_64:
            str_offset = struct.unpack_from('<Q', data, str_sh_off + 24)[0]
        else:
            str_offset = struct.unpack_from('<I', data, str_sh_off + 16)[0]

        sections = []
        for i in range(min(e_shnum, 50)):
            off = e_shoff + i * e_shentsize
            if is_64:
                sh_name_idx = struct.unpack_from('<I', data, off)[0]
                sh_addr = struct.unpack_from('<Q', data, off + 16)[0]
                sh_size = struct.unpack_from('<Q', data, off + 32)[0]
                sh_offset = struct.unpack_from('<Q', data, off + 24)[0]
            else:
                sh_name_idx = struct.unpack_from('<I', data, off)[0]
                sh_addr = struct.unpack_from('<I', data, off + 12)[0]
                sh_size = struct.unpack_from('<I', data, off + 16)[0]
                sh_offset = struct.unpack_from('<I', data, off + 20)[0]

            name_end = data.find(b'\00', str_offset + sh_name_idx)
            if name_end == -1:
                name_end = str_offset + sh_name_idx + 16
            name = data[str_offset + sh_name_idx:name_end].decode('ascii', errors='replace')
            sections.append({
                "name": name, "addr": sh_addr, "size": sh_size, "offset": sh_offset,
            })
        return sections
    except:
        return []

def run():
    while True:
        clear()
        cprint("  \u2554" + "\u2550" * 50 + "\u2557", "yellow")
        cprint("  \u2551         OFFSET DUMPER / HEX VIEWER               \u2551", "yellow")
        cprint("  \u255a" + "\u2550" * 50 + "\u255d", "yellow")
        print()
        cprint("  [1]  Hexdump file (full or range)", "white")
        cprint("  [2]  Jump to offset", "white")
        cprint("  [3]  Search for bytes / string", "white")
        cprint("  [4]  Find all occurrences", "white")
        cprint("  [5]  Dump PE sections (.exe/.dll)", "white")
        cprint("  [6]  Dump ELF sections (Linux)", "white")
        cprint("  [7]  File info + magic bytes", "white")
        cprint("  [8]  Compare two files (binary diff)", "white")
        cprint("  [9]  Extract data at offset + length", "white")
        cprint("  [0]  Back", "red")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '1':
            path = prompt("\033[33m  file path > \033[0m").strip().strip('"').strip("'")
            if not os.path.isfile(path):
                cprint("  [X] File not found", "red")
                pause()
                continue
            with open(path, 'rb') as f:
                data = f.read()
            cprint(f"\n  File: {os.path.basename(path)} ({len(data):,} bytes)", "cyan")
            raw = prompt("\033[33m  range (e.g. 0x00-0x100, or blank for first 512 bytes) > \033[0m")
            if raw and '-' in raw:
                try:
                    parts = raw.replace('0x', '').split('-')
                    start = int(parts[0], 16)
                    end = int(parts[1], 16)
                except:
                    start, end = 0, min(512, len(data))
            else:
                start, end = 0, min(512, len(data))
            end = min(end, len(data))
            clear()
            cprint(f"\n  === HEXDUMP: {os.path.basename(path)} [0x{start:08x} - 0x{end:08x}] ===\n", "cyan")
            print(hexdump(data[start:end], start))
            pause()
        elif choice == '2':
            path = prompt("\033[33m  file path > \033[0m").strip().strip('"').strip("'")
            if not os.path.isfile(path):
                cprint("  [X] File not found", "red")
                pause()
                continue
            offset_str = prompt("\033[33m  offset (hex, e.g. 0x1A00) > \033[0m") or "0x0"
            try:
                offset = int(offset_str.replace('0x', ''), 16)
            except:
                offset = 0
            with open(path, 'rb') as f:
                f.seek(offset)
                data = f.read(256)
            clear()
            cprint(f"\n  === OFFSET 0x{offset:08x} ({os.path.basename(path)}) ===\n", "cyan")
            print(hexdump(data, offset))
            pause()
        elif choice == '3':
            path = prompt("\033[33m  file path > \033[0m").strip().strip('"').strip("'")
            if not os.path.isfile(path):
                cprint("  [X] File not found", "red")
                pause()
                continue
            query = prompt("\033[33m  search (text or hex, e.g. '48 65 6c 6c 6f') > \033[0m")
            if not query:
                cprint("  [X] Need search term", "red")
                pause()
                continue
            with open(path, 'rb') as f:
                data = f.read()
            try:
                if ' ' in query and all(c in '0123456789abcdefABCDEF ' for c in query):
                    pattern = bytes.fromhex(query.replace(' ', ''))
                else:
                    pattern = query.encode()
            except:
                pattern = query.encode()
            positions = search_bytes(data, pattern)
            clear()
            cprint(f"\n  === SEARCH: {query[:50]} ({os.path.basename(path)}) ===", "cyan")
            cprint(f"  Pattern: {pattern.hex()}", "white")
            cprint(f"  Found: {len(positions)} match(es)\n", "white")
            for pos in positions[:30]:
                context_start = max(0, pos - 16)
                context = data[context_start:pos + len(pattern) + 16]
                hex_before = data[context_start:pos].hex()
                hex_match = data[pos:pos+len(pattern)].hex()
                hex_after = data[pos+len(pattern):pos+len(pattern)+16].hex()
                cprint(f"    0x{pos:08x}  ...{hex_before} \033[91m[{hex_match}]\033[0m {hex_after}...", "white")
            if len(positions) > 30:
                cprint(f"\n    ... and {len(positions) - 30} more matches", "yellow")
            print()
            pause()
        elif choice == '4':
            path = prompt("\033[33m  file path > \033[0m").strip().strip('"').strip("'")
            if not os.path.isfile(path):
                cprint("  [X] File not found", "red")
                pause()
                continue
            query = prompt("\033[33m  search (text or hex) > \033[0m")
            if not query:
                cprint("  [X] Need search term", "red")
                pause()
                continue
            with open(path, 'rb') as f:
                data = f.read()
            try:
                if ' ' in query and all(c in '0123456789abcdefABCDEF ' for c in query):
                    pattern = bytes.fromhex(query.replace(' ', ''))
                else:
                    pattern = query.encode()
            except:
                pattern = query.encode()
            positions = search_bytes(data, pattern)
            clear()
            cprint(f"\n  === ALL MATCHES: {query[:40]} ({len(positions)} found) ===\n", "cyan")
            for pos in positions[:100]:
                cprint(f"    0x{pos:08x}  ({pos})", "white")
            if len(positions) > 100:
                cprint(f"\n    ... and {len(positions) - 100} more", "yellow")
            print()
            pause()
        elif choice == '5':
            path = prompt("\033[33m  PE file path (.exe/.dll) > \033[0m").strip().strip('"').strip("'")
            if not os.path.isfile(path):
                cprint("  [X] File not found", "red")
                pause()
                continue
            with open(path, 'rb') as f:
                data = f.read()
            if data[:2] != b'MZ':
                cprint("  [X] Not a PE file (missing MZ header)", "red")
                pause()
                continue
            sections = find_pe_sections(data)
            clear()
            cprint(f"\n  === PE SECTIONS: {os.path.basename(path)} ===\n", "cyan")
            cprint(f"  {'Name':<10} {'Virtual Addr':<14} {'Virtual Size':<14} {'Raw Ptr':<10} {'Raw Size':<10} Flags", "cyan")
            cprint("  " + "-" * 80, "white")
            for s in sections:
                flags = ", ".join(s['flags']) if s['flags'] else "NONE"
                cprint(f"  {s['name']:<10} 0x{s['vaddr']:08x}     {s['vsize']:>10,}     0x{s['raw_ptr']:08x}  {s['raw_size']:>10,}  {flags}", "white")
            print()
            pause()
        elif choice == '6':
            path = prompt("\033[33m  ELF file path > \033[0m").strip().strip('"').strip("'")
            if not os.path.isfile(path):
                cprint("  [X] File not found", "red")
                pause()
                continue
            with open(path, 'rb') as f:
                data = f.read()
            if data[:4] != b'\x7fELF':
                cprint("  [X] Not an ELF file", "red")
                pause()
                continue
            sections = find_elf_sections(data)
            clear()
            cprint(f"\n  === ELF SECTIONS: {os.path.basename(path)} ===\n", "cyan")
            cprint(f"  {'Name':<20} {'Address':<14} {'Size':<14} {'File Offset':<14}", "cyan")
            cprint("  " + "-" * 65, "white")
            for s in sections:
                cprint(f"  {s['name']:<20} 0x{s['addr']:08x}     {s['size']:>10,}     0x{s['offset']:08x}", "white")
            print()
            pause()
        elif choice == '7':
            path = prompt("\033[33m  file path > \033[0m").strip().strip('"').strip("'")
            if not os.path.isfile(path):
                cprint("  [X] File not found", "red")
                pause()
                continue
            with open(path, 'rb') as f:
                data = f.read(512)
            clear()
            cprint(f"\n  === FILE INFO: {os.path.basename(path)} ===\n", "cyan")
            cprint(f"  Size:        {os.path.getsize(path):,} bytes", "white")
            magic_hex = data[:16].hex()
            magic_ascii = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data[:16])
            cprint(f"  Magic (hex): {magic_hex}", "yellow")
            cprint(f"  Magic (asc): {magic_ascii}", "yellow")

            if data[:2] == b'MZ':
                cprint("  Type:        PE executable (Windows)", "green")
                try:
                    pe_off = struct.unpack_from('<I', data, 0x3C)[0]
                    machine = struct.unpack_from('<H', data, pe_off + 4)[0]
                    machine_names = {0x14c: "x86 (32-bit)", 0x8664: "x64 (64-bit)", 0xAA64: "ARM64", 0x1C0: "ARM"}
                    cprint(f"  Machine:     {machine_names.get(machine, f'0x{machine:04x}')}", "white")
                except:
                    pass
            elif data[:4] == b'\x7fELF':
                cprint("  Type:        ELF executable (Linux)", "green")
                bits = "64-bit" if data[4] == 2 else "32-bit"
                endian = "Little-endian" if data[5] == 1 else "Big-endian"
                cprint(f"  Arch:        {bits}, {endian}", "white")
            elif data[:4] == b'\xfe\xed\xfa\xce' or data[:4] == b'\xfe\xed\xfa\xcf':
                cprint("  Type:        Mach-O executable (macOS)", "green")
            elif data[:2] == b'PK':
                cprint("  Type:        ZIP archive / APK / JAR", "green")
            elif data[:4] == b'\x89PNG':
                cprint("  Type:        PNG image", "green")
            elif data[:3] == b'\xff\xd8\xff':
                cprint("  Type:        JPEG image", "green")
            elif data[:4] == b'%PDF':
                cprint("  Type:        PDF document", "green")
            else:
                cprint("  Type:        Unknown", "yellow")

            md5 = __import__('hashlib').md5(data).hexdigest()
            sha1 = __import__('hashlib').sha1(data).hexdigest()
            sha256 = __import__('hashlib').sha256(data).hexdigest()
            cprint(f"\n  MD5:    {md5}", "white")
            cprint(f"  SHA1:   {sha1}", "white")
            cprint(f"  SHA256: {sha256}", "white")
            print()
            pause()
        elif choice == '8':
            path1 = prompt("\033[33m  file 1 > \033[0m").strip().strip('"').strip("'")
            path2 = prompt("\033[33m  file 2 > \033[0m").strip().strip('"').strip("'")
            if not os.path.isfile(path1) or not os.path.isfile(path2):
                cprint("  [X] File not found", "red")
                pause()
                continue
            with open(path1, 'rb') as f:
                data1 = f.read()
            with open(path2, 'rb') as f:
                data2 = f.read()
            clear()
            cprint(f"\n  === BINARY DIFF ===", "cyan")
            cprint(f"  {os.path.basename(path1)}: {len(data1):,} bytes", "white")
            cprint(f"  {os.path.basename(path2)}: {len(data2):,} bytes", "white")
            max_len = max(len(data1), len(data2))
            diffs = []
            for i in range(max_len):
                b1 = data1[i] if i < len(data1) else None
                b2 = data2[i] if i < len(data2) else None
                if b1 != b2:
                    diffs.append((i, b1, b2))
            cprint(f"\n  Differences: {len(diffs)} byte(s)\n", "yellow")
            for offset, b1, b2 in diffs[:50]:
                v1 = f"0x{b1:02x} ({chr(b1) if b1 and 32 <= b1 <= 126 else '?'})" if b1 is not None else "EOF"
                v2 = f"0x{b2:02x} ({chr(b2) if b2 and 32 <= b2 <= 126 else '?'})" if b2 is not None else "EOF"
                cprint(f"    0x{offset:08x}  {v1:<20} ->  {v2}", "white")
            if len(diffs) > 50:
                cprint(f"\n    ... and {len(diffs) - 50} more differences", "yellow")
            print()
            pause()
        elif choice == '9':
            path = prompt("\033[33m  file path > \033[0m").strip().strip('"').strip("'")
            if not os.path.isfile(path):
                cprint("  [X] File not found", "red")
                pause()
                continue
            offset_str = prompt("\033[33m  offset (hex) > \033[0m") or "0x0"
            length_str = prompt("\033[33m  length (hex or decimal) > \033[0m") or "64"
            try:
                offset = int(offset_str.replace('0x', ''), 16)
            except:
                offset = 0
            try:
                length = int(length_str.replace('0x', ''), 16) if '0x' in length_str else int(length_str)
            except:
                length = 64
            with open(path, 'rb') as f:
                f.seek(offset)
                data = f.read(length)
            clear()
            cprint(f"\n  === EXTRACTED DATA: 0x{offset:08x} ({length} bytes) ===\n", "cyan")
            print(hexdump(data, offset))
            cprint(f"\n  Hex: {data.hex()}", "yellow")
            try:
                cprint(f"  ASCII: {data.decode('ascii', errors='replace')}", "green")
            except:
                pass
            print()
            pause()
        else:
            cprint("  invalid choice", "red")
            time.sleep(0.5)

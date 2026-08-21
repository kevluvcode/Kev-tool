import os
import sys
import base64
import hashlib
import struct
import math
import time
import shutil

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

def entropy(data):
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    ent = 0.0
    for f in freq:
        if f > 0:
            p = f / len(data)
            ent -= p * math.log2(p)
    return ent

def xor_decrypt(data, key):
    kb = key if isinstance(key, bytes) else key.encode()
    return bytes(b ^ kb[i % len(kb)] for i, b in enumerate(data))

def rot_n(data, n):
    out = bytearray()
    for b in data:
        if 65 <= b <= 90:
            out.append((b - 65 - n) % 26 + 65)
        elif 97 <= b <= 122:
            out.append((b - 97 - n) % 26 + 97)
        else:
            out.append(b)
    return bytes(out)

def detect_file(data):
    if data[:2] == b'MZ':
        return "PE"
    if data[:4] == b'\x7fELF':
        return "ELF"
    if data[:4] in (b'\xfe\xed\xfa\xce', b'\xfe\xed\xfa\xcf'):
        return "Mach-O"
    return "Unknown"

# ─── PE Section Reader ───────────────────────────────────────────────
def read_pe_sections(data):
    try:
        pe_off = struct.unpack_from('<I', data, 0x3C)[0]
        if data[pe_off:pe_off+4] != b'PE\x00\x00':
            return None, []
        num_sec = struct.unpack_from('<H', data, pe_off + 6)[0]
        opt_off = pe_off + 24
        is_64 = struct.unpack_from('<H', data, opt_off)[0] == 0x20B
        sec_off = opt_off + (112 if is_64 else 96)
        hdr_size = struct.unpack_from('<H', data, pe_off + 20)[0]
        sections = []
        for i in range(min(num_sec, 96)):
            off = sec_off + i * 40
            name = data[off:off+8].rstrip(b'\x00').decode('ascii', errors='replace')
            vsize = struct.unpack_from('<I', data, off + 8)[0]
            vaddr = struct.unpack_from('<I', data, off + 12)[0]
            raw_size = struct.unpack_from('<I', data, off + 16)[0]
            raw_ptr = struct.unpack_from('<I', data, off + 20)[0]
            chars = struct.unpack_from('<I', data, off + 36)[0]
            sections.append({
                "index": i, "name": name, "vaddr": vaddr, "vsize": vsize,
                "raw_ptr": raw_ptr, "raw_size": raw_size, "chars": chars,
                "offset": off,
            })
        return pe_off, sections
    except:
        return None, []

def patch_pe_bytes(data, section, new_data):
    data = bytearray(data)
    raw_ptr = section['raw_ptr']
    raw_size = section['raw_size']
    if raw_ptr == 0 or raw_size == 0:
        return bytes(data)
    if len(new_data) <= raw_size:
        data[raw_ptr:raw_ptr + len(new_data)] = new_data
    else:
        data[raw_ptr:raw_ptr + raw_size] = new_data[:raw_size]
    return bytes(data)

# ─── ELF Section Reader ──────────────────────────────────────────────
def read_elf_sections(data):
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
        str_sh = e_shoff + e_shstrndx * e_shentsize
        if is_64:
            str_off = struct.unpack_from('<Q', data, str_sh + 24)[0]
        else:
            str_off = struct.unpack_from('<I', data, str_sh + 16)[0]
        sections = []
        for i in range(min(e_shnum, 96)):
            off = e_shoff + i * e_shentsize
            if is_64:
                name_idx = struct.unpack_from('<I', data, off)[0]
                addr = struct.unpack_from('<Q', data, off + 16)[0]
                size = struct.unpack_from('<Q', data, off + 32)[0]
                ptr = struct.unpack_from('<Q', data, off + 24)[0]
            else:
                name_idx = struct.unpack_from('<I', data, off)[0]
                addr = struct.unpack_from('<I', data, off + 12)[0]
                size = struct.unpack_from('<I', data, off + 16)[0]
                ptr = struct.unpack_from('<I', data, off + 20)[0]
            ne = data.find(b'\00', str_off + name_idx)
            if ne == -1:
                ne = str_off + name_idx + 16
            name = data[str_off + name_idx:ne].decode('ascii', errors='replace')
            sections.append({
                "index": i, "name": name, "addr": addr,
                "size": size, "offset": ptr, "sh_off": off,
            })
        return sections
    except:
        return []

# ─── Decryption strategies ───────────────────────────────────────────
def try_xor_keys(data, log):
    """Try common XOR keys on a data block."""
    common_keys = [
        bytes([i]) for i in range(1, 256)
    ] + [
        bytes([i, j]) for i in range(1, 256) for j in range(1, 32)
    ] + [
        b'\xde\xad\xbe\xef', b'\xca\xfe\xba\xbe', b'\x90\x90\x90\x90',
        b'flag', b'FLAG', b'key\x00', b'KEY\x00',
        bytes(range(1, 17)), bytes(range(0x41, 0x51)),
    ]
    best_key = None
    best_score = 0
    best_dec = None
    tested = 0
    for key in common_keys:
        dec = xor_decrypt(data, key)
        score = sum(1 for b in dec[:512] if 32 <= b <= 126) / min(512, len(dec))
        # prefer keys that produce printable ascii AND keep some structure
        if score > best_score:
            best_score = score
            best_key = key
            best_dec = dec
        tested += 1
        if tested >= 5000:
            break
    if best_key and best_score > 0.75:
        log.append(f"    XOR key: 0x{best_key.hex()}  (printability: {best_score:.0%})")
        return best_key, best_dec, best_score
    return None, None, 0

def try_rot(data, log):
    """Try ROT1-25."""
    best_n = 0
    best_score = 0
    best_dec = None
    for n in range(1, 26):
        dec = rot_n(data, n)
        score = sum(1 for b in dec[:512] if 32 <= b <= 126) / min(512, len(dec))
        if score > best_score:
            best_score = score
            best_n = n
            best_dec = dec
    if best_n and best_score > 0.8:
        log.append(f"    ROT-{best_n}  (printability: {best_score:.0%})")
        return best_n, best_dec, best_score
    return None, None, 0

def try_byte_add_sub(data, log):
    """Try single-byte ADD/SUB ciphers."""
    for key in range(1, 256):
        dec = bytes((b - key) & 0xFF for b in data)
        score = sum(1 for b in dec[:512] if 32 <= b <= 126) / min(512, len(dec))
        if score > 0.85:
            log.append(f"    SUB 0x{key:02x}  (printability: {score:.0%})")
            return key, dec, score
    return None, None, 0

def try_byte_xor_add(data, log):
    """Try XOR + byte-add combinations."""
    for xor_key in [b'\xff', b'\x55', b'\xaa', b'\x01']:
        dec = xor_decrypt(data, xor_key)
        for add in range(1, 256):
            dec2 = bytes((b + add) & 0xFF for b in dec)
            score = sum(1 for b in dec2[:512] if 32 <= b <= 126) / min(512, len(dec2))
            if score > 0.85:
                log.append(f"    XOR 0x{xor_key[0]:02x} + ADD 0x{add:02x}  (printability: {score:.0%})")
                return (xor_key, add), dec2, score
    return None, None, 0

def try_base64_section(data, log):
    """Try base64-decoding a section."""
    try:
        cleaned = data.rstrip(b'\x00').strip()
        if len(cleaned) % 4 != 0:
            cleaned += b'=' * (4 - len(cleaned) % 4)
        dec = base64.b64decode(cleaned)
        score = sum(1 for b in dec[:512] if 32 <= b <= 126) / min(512, len(dec))
        if score > 0.7:
            log.append(f"    Base64 decode  (printability: {score:.0%})")
            return "b64", dec, score
    except:
        pass
    return None, None, 0

def try_aes_detect(data, log):
    """Check if data looks AES-encrypted (uniform high entropy)."""
    ent = entropy(data)
    if ent > 7.5 and len(data) >= 16:
        freq = [0] * 256
        for b in data:
            freq[b] += 1
        max_freq = max(freq) / len(data)
        if max_freq < 0.02:
            log.append(f"    POSSIBLE AES/STRONG CIPHER (entropy={ent:.2f}, uniform distribution)")
            return True
    return False

# ─── Section-by-section analysis ─────────────────────────────────────
def analyze_section(name, raw_data, log):
    ent = entropy(raw_data)
    log.append(f"\n  [{name}]  size={len(raw_data):,}  entropy={ent:.2f}")

    if ent < 5.5:
        log.append(f"    -> Low entropy, likely plaintext/code — no decryption needed")
        return None, None

    if ent >= 7.5:
        log.append(f"    -> HIGH ENTROPY — likely encrypted or compressed")
    elif ent >= 6.0:
        log.append(f"    -> Moderate entropy — possible lightweight encryption")

    key, dec, score = try_xor_keys(raw_data, log)
    if dec:
        return "xor", dec

    n, dec, score = try_rot(raw_data, log)
    if dec:
        return "rot", dec

    key, dec, score = try_byte_add_sub(raw_data, log)
    if dec:
        return "sub", dec

    key, dec, score = try_byte_xor_add(raw_data, log)
    if dec:
        return "xor_add", dec

    method, dec, score = try_base64_section(raw_data, log)
    if dec:
        return "base64", dec

    is_aes = try_aes_detect(raw_data, log)
    if is_aes:
        log.append(f"    -> Cannot auto-decrypt (likely AES/strong cipher — need key)")
        return "encrypted", None

    log.append(f"    -> Could not auto-decrypt")
    return None, None

# ─── Main decrypt + rebuild ──────────────────────────────────────────
def decrypt_and_rebuild(filepath, output_path=None, log=None):
    if log is None:
        log = []

    basename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        data = f.read()

    ftype = detect_file(data)
    log.append(f"{'='*70}")
    log.append(f"  APP UNPACKER / DECRYPTER / REBUILDER")
    log.append(f"  File:     {basename}")
    log.append(f"  Size:     {len(data):,} bytes")
    log.append(f"  Type:     {ftype}")
    log.append(f"  MD5:      {hashlib.md5(data).hexdigest()}")
    log.append(f"  SHA256:   {hashlib.sha256(data).hexdigest()[:32]}...")
    log.append(f"  Entropy:  {entropy(data):.4f}/8.0")
    log.append(f"  Time:     {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.append(f"{'='*70}\n")

    patched = bytearray(data)
    patches_made = 0
    sections_decrypted = []

    if ftype == "PE":
        pe_off, sections = read_pe_sections(data)
        if not sections:
            log.append("[!] Could not parse PE sections")
            return None, log

        log.append(f"[PE] {len(sections)} sections found:\n")
        for sec in sections:
            raw_ptr = sec['raw_ptr']
            raw_size = sec['raw_size']
            if raw_ptr == 0 or raw_size == 0:
                log.append(f"  {sec['name']:<10}  (empty/no raw data)")
                continue
            raw_data = data[raw_ptr:raw_ptr + raw_size]
            method, dec_data = analyze_section(sec['name'], raw_data, log)
            if method and dec_data and method != "encrypted":
                patched[raw_ptr:raw_ptr + min(len(dec_data), raw_size)] = dec_data[:raw_size]
                patches_made += 1
                sections_decrypted.append(sec['name'])
                log.append(f"    -> PATCHED '{sec['name']}' with {method} decryption")

        log.append(f"\n[PE] Sections decrypted: {patches_made}")

    elif ftype == "ELF":
        sections = read_elf_sections(data)
        if not sections:
            log.append("[!] Could not parse ELF sections")
            return None, log

        log.append(f"[ELF] {len(sections)} sections found:\n")
        for sec in sections:
            ptr = sec['offset']
            size = sec['size']
            if ptr == 0 or size == 0:
                continue
            raw_data = data[ptr:ptr + size]
            method, dec_data = analyze_section(sec['name'], raw_data, log)
            if method and dec_data and method != "encrypted":
                patched[ptr:ptr + min(len(dec_data), size)] = dec_data[:size]
                patches_made += 1
                sections_decrypted.append(sec['name'])
                log.append(f"    -> PATCHED '{sec['name']}' with {method} decryption")

        log.append(f"\n[ELF] Sections decrypted: {patches_made}")

    else:
        log.append(f"[!] Unsupported file type: {ftype}")
        log.append("[*] Attempting full-file analysis...\n")

        raw_data = data
        method, dec_data = analyze_section("FULL_FILE", raw_data, log)
        if method and dec_data:
            patched = bytearray(dec_data)
            patches_made = 1
            sections_decrypted.append("FULL_FILE")
            log.append(f"    -> DECRYPTED entire file with {method}")

        if patches_made == 0:
            log.append("\n[*] Full-file decryption failed, trying offset-based approach...\n")
            ent_map = []
            chunk_size = 1024
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i+chunk_size]
                ent_map.append((i, chunk, entropy(chunk)))

            for offset, chunk, ent in ent_map:
                if ent < 6.0:
                    continue
                method, dec_data = analyze_section(f"chunk@0x{offset:08x}", chunk, log)
                if method and dec_data:
                    patched[offset:offset + min(len(dec_data), chunk_size)] = dec_data[:chunk_size]
                    patches_made += 1

    log.append(f"\n{'='*70}")
    log.append(f"  RESULTS")
    log.append(f"  Sections decrypted: {patches_made}")
    if sections_decrypted:
        log.append(f"  Modified sections:  {', '.join(sections_decrypted)}")
    log.append(f"  Original entropy:  {entropy(data):.4f}")
    log.append(f"  New entropy:       {entropy(bytes(patched)):.4f}")
    log.append(f"{'='*70}")

    if output_path is None:
        name, ext = os.path.splitext(filepath)
        output_path = name + "_decrypted" + ext

    with open(output_path, 'wb') as f:
        f.write(bytes(patched))

    log.append(f"\n[+] OUTPUT: {output_path}")
    log.append(f"[+] Size:   {len(patched):,} bytes")
    log.append(f"[+] MD5:    {hashlib.md5(bytes(patched)).hexdigest()}")

    return output_path, log

# ─── CLI ──────────────────────────────────────────────────────────────
def run(self=None):
    while True:
        clear()
        cprint("  \u2554" + "\u2550" * 50 + "\u2557", "yellow")
        cprint("  \u2551      APP DECRYPTER / UNPACKER / REBUILDER         \u2551", "yellow")
        cprint("  \u255a" + "\u2550" * 50 + "\u255d", "yellow")
        print()
        cprint("  [1]  Full decrypt + rebuild (.exe/.dll/.so)", "white")
        cprint("       Scans all sections, decrypts what it can,", "white")
        cprint("       rebuilds the binary with decrypted sections", "white")
        cprint("  [2]  Quick decrypt (auto-detect + patch)", "white")
        cprint("  [3]  Analyze only (no rebuild, just report)", "white")
        cprint("  [4]  Decrypt specific section by name", "white")
        cprint("  [5]  Batch decrypt (folder of executables)", "white")
        cprint("  [0]  Back", "red")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice in ('1', '2'):
            path = prompt("\033[33m  file path (.exe/.dll/.so/.bin) > \033[0m").strip().strip('"').strip("'")
            if not os.path.isfile(path):
                cprint("  [X] File not found", "red")
                pause()
                continue
            clear()
            cprint("\n  Decrypting and rebuilding...\n", "cyan")
            output_path = None
            if choice == '1':
                name, ext = os.path.splitext(path)
                output_path = prompt(f"\033[33m  output path (default: {name}_decrypted{ext}) > \033[0m") or f"{name}_decrypted{ext}"
            else:
                output_path = os.path.splitext(path)[0] + "_decrypted" + os.path.splitext(path)[1]

            out, log = decrypt_and_rebuild(path, output_path)
            log_path = os.path.splitext(output_path)[0] + "_log.txt"
            with open(log_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write('\n'.join(log))
            clear()
            if out:
                cprint(f"\n  DECRYPT COMPLETE", "green")
                cprint(f"  Output:   {out}", "green")
                cprint(f"  Log:      {log_path}", "cyan")
                cprint(f"  Sections: {len([l for l in log if 'PATCHED' in l])} decrypted", "white")
            else:
                cprint(f"\n  Could not decrypt/rebuild", "red")
                cprint(f"  Check log: {log_path}", "yellow")
            pause()
        elif choice == '3':
            path = prompt("\033[33m  file path > \033[0m").strip().strip('"').strip("'")
            if not os.path.isfile(path):
                cprint("  [X] File not found", "red")
                pause()
                continue
            clear()
            cprint("\n  Analyzing...\n", "cyan")
            out, log = decrypt_and_rebuild(path, os.devnull)
            clear()
            print('\n'.join(log))
            pause()
        elif choice == '4':
            path = prompt("\033[33m  file path > \033[0m").strip().strip('"').strip("'")
            if not os.path.isfile(path):
                cprint("  [X] File not found", "red")
                pause()
                continue
            sec_name = prompt("\033[33m  section name (e.g. .text, .rdata, .data) > \033[0m") or ".text"
            with open(path, 'rb') as f:
                data = f.read()
            ftype = detect_file(data)
            sections = []
            if ftype == "PE":
                _, sections = read_pe_sections(data)
                for sec in sections:
                    if sec['name'] == sec_name:
                        raw_data = data[sec['raw_ptr']:sec['raw_ptr'] + sec['raw_size']]
                        log = []
                        method, dec_data = analyze_section(sec_name, raw_data, log)
                        clear()
                        print('\n'.join(log))
                        if method and dec_data:
                            out_path = os.path.splitext(path)[0] + f"_{sec_name.replace('.','')}_decrypted" + os.path.splitext(path)[1]
                            patched = bytearray(data)
                            patched[sec['raw_ptr']:sec['raw_ptr'] + min(len(dec_data), sec['raw_size'])] = dec_data[:sec['raw_size']]
                            with open(out_path, 'wb') as f:
                                f.write(bytes(patched))
                            cprint(f"\n  Saved to: {out_path}", "green")
                        break
                else:
                    cprint(f"  Section '{sec_name}' not found", "red")
            pause()
        elif choice == '5':
            folder = prompt("\033[33m  folder path > \033[0m").strip().strip('"').strip("'")
            if not os.path.isdir(folder):
                cprint("  [X] Folder not found", "red")
                pause()
                continue
            exts = ('.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.com')
            files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if os.path.isfile(os.path.join(folder, f)) and any(f.lower().endswith(e) for e in exts)]
            if not files:
                cprint("  [X] No executable files found in folder", "red")
                pause()
                continue
            out_dir = os.path.join(folder, "decrypted_output")
            os.makedirs(out_dir, exist_ok=True)
            clear()
            cprint(f"\n  Batch decrypt: {len(files)} files\n", "cyan")
            log_all = []
            for i, fp in enumerate(files, 1):
                cprint(f"  [{i}/{len(files)}] {os.path.basename(fp)}...", "white")
                out_path = os.path.join(out_dir, os.path.basename(fp))
                out, log = decrypt_and_rebuild(fp, out_path)
                patched_count = len([l for l in log if 'PATCHED' in l])
                log_all.append(f"\n--- {os.path.basename(fp)}: {patched_count} sections ---")
                log_all.extend(log)
                cprint(f"    -> {patched_count} sections decrypted", "green" if patched_count else "yellow")
            log_path = os.path.join(out_dir, "batch_log.txt")
            with open(log_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write('\n'.join(log_all))
            cprint(f"\n  Batch complete! Output in: {out_dir}", "green")
            pause()
        else:
            cprint("  invalid choice", "red")
            time.sleep(0.5)

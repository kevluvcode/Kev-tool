import os
import sys
import struct
import hashlib
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

def detect_file_type(data):
    if data[:4] == b'\x7fELF':
        if data[4] == 1:
            return "ELF32"
        elif data[4] == 2:
            return "ELF64"
        return "ELF"
    if data[:2] in (b'MZ', b'ZM'):
        return "PE (Windows EXE/DLL)"
    if data[:4] in (b'\xfe\xed\xfa\xce', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xcf\xfa\xed\xfe'):
        return "Mach-O (macOS/iOS)"
    if data[:4] == b'\x50\x4b\x03\x04':
        exts = set()
        for name in [b'classes.dex', b'AndroidManifest.xml', b'lib/']:
            if name in data:
                exts.add("APK")
        if exts:
            return "APK (Android Package)"
        if b'META-INF/' in data and b'classes.dex' in data:
            return "APK (Android Package)"
        return "ZIP Archive"
    if data[:4] == b'\x30\x82' or data[:2] == b'\x30\x82':
        if b'\x06\x09\x2a\x86\x48\x86\xf7\x0d' in data[:100]:
            return "DER Certificate"
        return "Possible PKCS/ASN.1"
    if data[:6] in (b'<?xml', b'<!DOCT', b'<html', b'<HTML'):
        return "XML/HTML Document"
    if data[:5] == b'%PDF-':
        return "PDF Document"
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return "PNG Image"
    if data[:2] == b'\xff\xd8':
        return "JPEG Image"
    if data[:4] == b'GIF8':
        return "GIF Image"
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return "WebP Image"
    if b'SQLite' in data[:16]:
        return "SQLite Database"
    if data[:6] in (b'\x1f\x8b\x08', b'\x1f\x8b\x08\x00'):
        return "GZIP Archive"
    if data[:3] == b'BZh':
        return "BZIP2 Archive"
    if data[:4] == b'\xfd7zXZ':
        return "XZ Archive"
    if data[:4] == b'PK\x03\x04':
        if b'classes.dex' in data or b'AndroidManifest' in data:
            return "APK (Android)"
        return "ZIP-based format"
    return "Unknown"

def find_strings(data, min_len=4):
    strings = []
    current = []
    for b in data:
        if 32 <= b < 127:
            current.append(chr(b))
        else:
            if len(current) >= min_len:
                strings.append(''.join(current))
            current = []
    return strings

def find_encryption_patterns(data):
    patterns = []
    markers = {
        b'\x00\x01\x00\x00': "RSA-1024 public key",
        b'\x30\x82\x01\x22\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x0b': "RSA-2048 key header",
        b'\x30\x82\x01\x22\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x0c': "RSA-2048 with SHA256",
        b'\x30\x82\x02\x22\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x0b': "RSA-4096 key header",
        b'\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x07\x02': "PKCS#7 signed data",
        b'\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x05\x01': "PKCS#5 password-based encryption",
        b'\x06\x09\x60\x86\x48\x01\x65\x03\x04\x01': "AES (OID detected)",
        b'\x06\x09\x2b\x06\x01\x04\x01\xd6\x79\x02\x04\x02': "HMAC-SHA256",
        b'Condado': "Condado encryption (mobile)",
        b'ProGuard': "ProGuard obfuscation marker",
        b'R8\x00': "R8 compiler obfuscation",
        b'\xac\xed\x00\x05': "Java serialized data",
        b'----BEGIN CERTIFICATE': "PEM certificate",
        b'----BEGIN RSA PRIVATE': "RSA private key (PEM)",
        b'----BEGIN PRIVATE': "Private key (PEM)",
        b'----BEGIN ENCRYPTED': "Encrypted private key (PEM)",
        b'\x00\x00\x00\x00\x00\x00\x00\x00': "Null padding (possible encrypted block)",
        b'\xff\xff\xff\xff': "High entropy block (possible encrypted data)",
    }
    for pat, desc in markers.items():
        offset = 0
        while True:
            idx = data.find(pat, offset)
            if idx == -1:
                break
            patterns.append((idx, desc))
            offset = idx + 1
            if len(patterns) > 500:
                break
    return sorted(patterns, key=lambda x: x[0])

def find_strings_c(data, min_len=4):
    results = []
    current = []
    start = 0
    for i, b in enumerate(data):
        if 32 <= b < 127:
            if not current:
                start = i
            current.append(chr(b))
        else:
            if len(current) >= min_len:
                results.append((start, ''.join(current)))
            current = []
    return results

def analyze_strings_interesting(strings_list):
    interesting = []
    keywords = [
        'encrypt', 'decrypt', 'cipher', 'aes', 'des', 'rsa', 'hmac', 'sha', 'md5',
        'password', 'passwd', 'secret', 'key', 'token', 'auth', 'login', 'credential',
        'api_key', 'apikey', 'private', 'public_key', 'ssl', 'tls', 'cert',
        'http://', 'https://', 'ftp://', 'tcp://', 'udp://',
        '0x', '0000', 'ffff', 'deadbeef', 'cafebabe',
        '.so', '.dll', '.dylib', '.framework',
        'libcrypto', 'libssl', 'openssl', 'boringssl', 'sodium',
        'base64', 'hex_decode', 'xor', 'rc4', 'blowfish', 'twofish',
        'googleapis', 'firebase', 'supabase', 'aws', 'azure', 'gcp',
        'sqlite', 'mysql', 'postgres', 'mongodb', 'redis',
    ]
    for offset, s in strings_list:
        sl = s.lower()
        for kw in keywords:
            if kw in sl:
                interesting.append((offset, s, kw))
                break
    return interesting[:200]

def dump_hex_range(data, start, length=256):
    lines = []
    for i in range(start, min(start + length, len(data)), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"  {i:08x}  {hex_part:<48s}  {ascii_part}")
    return '\n'.join(lines)

def entropy_analysis(data):
    import math
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    length = len(data)
    ent = 0.0
    for f in freq:
        if f > 0:
            p = f / length
            ent -= p * math.log2(p)
    return ent

def section_entropy_map(data, chunk_size=1024):
    results = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        ent = entropy_analysis(chunk)
        results.append((i, ent))
    return results

def run():
    while True:
        clear()
        cprint("  \u2554" + "\u2550" * 52 + "\u2557", "cyan")
        cprint("  \u2551          APP DECRYPTER / BINARY ANALYZER          \u2551", "cyan")
        cprint("  \u255a" + "\u2550" * 52 + "\u255d", "cyan")
        print()
        cprint("  [1]  Analyze file (type, strings, encryption patterns)", "white")
        cprint("  [2]  Hex dump at offset", "white")
        cprint("  [3]  Entropy map (find encrypted/compressed sections)", "white")
        cprint("  [4]  Extract all strings (save to file)", "white")
        cprint("  [5]  Find crypto keys and certificates", "white")
        cprint("  [6]  Full analysis (everything above)", "white")
        cprint("  [7]  Quick peek (first 4KB hex)", "white")
        cprint("  [0]  Back", "red")
        print()
        choice = prompt("\033[33m  file path (or menu #) > \033[0m")
        if choice == '0':
            return
        fpath = choice.strip().strip('"').strip("'")
        if not fpath or not os.path.isfile(fpath):
            cprint("  [X] File not found.", "red")
            pause()
            continue
        try:
            with open(fpath, 'rb') as f:
                data = f.read()
        except Exception as e:
            cprint(f"  [X] Cannot read file: {e}", "red")
            pause()
            continue
        fname = os.path.basename(fpath)
        fsize = len(data)

        if choice in ('1', '6'):
            clear()
            cprint(f"\n  === ANALYSIS: {fname} ===", "cyan")
            cprint(f"  Path:   {fpath}", "white")
            cprint(f"  Size:   {fsize:,} bytes ({fsize/1024:.1f} KB)", "white")
            cprint(f"  MD5:    {hashlib.md5(data).hexdigest()}", "yellow")
            cprint(f"  SHA256: {hashlib.sha256(data).hexdigest()[:32]}...", "yellow")
            ft = detect_file_type(data)
            cprint(f"  Type:   {ft}", "green")
            ent = entropy_analysis(data)
            cprint(f"  Entropy: {ent:.4f} / 8.0", "green" if ent < 6.0 else "yellow" if ent < 7.5 else "red")
            if ent >= 7.5:
                cprint("  \u26a0  High entropy \u2014 likely encrypted/compressed data", "red")
            elif ent >= 6.0:
                cprint("  \u2139  Moderate entropy \u2014 mixed content", "yellow")
            else:
                cprint("  \u2713  Low entropy \u2014 likely plaintext/code", "green")
            print()
            patterns = find_encryption_patterns(data)
            if patterns:
                cprint(f"  Encryption/Crypto patterns found: {len(patterns)}", "yellow")
                for offset, desc in patterns[:20]:
                    cprint(f"    0x{offset:08x}  {desc}", "white")
            else:
                cprint("  No known crypto patterns detected.", "white")
            if choice == '6':
                print()
                strings_list = find_strings_c(data, 6)
                interesting = analyze_strings_interesting(strings_list)
                if interesting:
                    cprint(f"  Interesting strings found: {len(interesting)}", "cyan")
                    for offset, s, kw in interesting[:30]:
                        cprint(f"    0x{offset:08x}  [{kw}]  {s[:80]}", "white")
                print()
                ent_map = section_entropy_map(data, 4096)
                high_ent = [(o, e) for o, e in ent_map if e >= 7.0]
                if high_ent:
                    cprint(f"  High-entropy sections (likely encrypted):", "yellow")
                    for o, e in high_ent[:15]:
                        cprint(f"    0x{o:08x}  entropy={e:.2f}  ({o//1024}KB)", "white")
            pause()

        elif choice in ('2', '7'):
            if choice == '7':
                offset = 0
                length = 4096
            else:
                o = prompt("\033[33m  offset (hex 0x... or decimal) > \033[0m") or "0"
                try:
                    offset = int(o, 16) if o.startswith('0x') or o.startswith('0X') else int(o)
                except:
                    offset = 0
                l = prompt("\033[33m  length in bytes (default 256) > \033[0m") or "256"
                try:
                    length = int(l)
                except:
                    length = 256
            clear()
            cprint(f"\n  === HEX DUMP: {fname} @ 0x{offset:08x} ===", "cyan")
            print()
            cprint(dump_hex_range(data, offset, length), "white")
            print()
            pause()

        elif choice == '3':
            try:
                cs = prompt("\033[33m  chunk size in bytes (default 1024) > \033[0m") or "1024"
                chunk_size = int(cs)
            except:
                chunk_size = 1024
            clear()
            cprint(f"\n  === ENTROPY MAP: {fname} (chunks of {chunk_size} bytes) ===", "cyan")
            print()
            ent_map = section_entropy_map(data, chunk_size)
            max_chunks = min(len(ent_map), 80)
            for i in range(max_chunks):
                offset, ent = ent_map[i]
                bar_len = int(ent / 8.0 * 40)
                bar = "\u2588" * bar_len + "\u2591" * (40 - bar_len)
                color = "green" if ent < 5.5 else "yellow" if ent < 7.0 else "red"
                cprint(f"  0x{offset:08x}  {bar}  {ent:.2f}", color)
            if len(ent_map) > max_chunks:
                cprint(f"\n  ... {len(ent_map) - max_chunks} more chunks", "white")
            high = [(o, e) for o, e in ent_map if e >= 7.0]
            cprint(f"\n  Summary: {len(ent_map)} chunks analyzed, {len(high)} high-entropy (>=7.0)", "yellow")
            if high:
                cprint("  High entropy ranges (likely encrypted/compressed):", "red")
                for o, e in high[:10]:
                    cprint(f"    0x{o:08x} - 0x{o+chunk_size-1:08x}  entropy={e:.2f}", "white")
            print()
            pause()

        elif choice == '4':
            fname_out = prompt("\033[33m  output filename (default: strings.txt) > \033[0m") or "strings.txt"
            try:
                ml = int(prompt("\033[33m  min string length (default 4) > \033[0m") or "4")
            except:
                ml = 4
            strings_list = find_strings_c(data, ml)
            lines = [f"=== STRINGS FROM: {fname} ===", f"Path: {fpath}", f"Min length: {ml}", f"Total: {len(strings_list)} strings\n"]
            for offset, s in strings_list:
                lines.append(f"0x{offset:08x}  {s}")
            with open(fname_out, 'w', encoding='utf-8', errors='replace') as f:
                f.write('\n'.join(lines))
            clear()
            cprint(f"\n  Extracted {len(strings_list)} strings to {fname_out}", "green")
            pause()

        elif choice == '5':
            clear()
            cprint(f"\n  === CRYPTO KEY SCAN: {fname} ===", "cyan")
            print()
            patterns = find_encryption_patterns(data)
            if patterns:
                cprint(f"  Found {len(patterns)} crypto-related patterns:\n", "yellow")
                for offset, desc in patterns:
                    cprint(f"    0x{offset:08x}  {desc}", "white")
            else:
                cprint("  No known crypto patterns found.", "white")
            print()
            pem_keys = []
            for marker in [b'-----BEGIN', b'-----END']:
                idx = 0
                while True:
                    idx = data.find(marker, idx)
                    if idx == -1:
                        break
                    end = data.find(b'\n', idx)
                    if end == -1:
                        end = idx + 80
                    pem_keys.append((idx, data[idx:min(end+1, idx+200)].decode('ascii', errors='replace')))
                    idx += 1
            if pem_keys:
                cprint(f"  PEM key boundaries found: {len(pem_keys)//2 if len(pem_keys) >= 2 else len(pem_keys)}", "cyan")
                for offset, header in pem_keys[:10]:
                    cprint(f"    0x{offset:08x}  {header[:60]}", "white")
            print()
            strings_list = find_strings_c(data, 6)
            crypto_strings = [(o, s) for o, s in strings_list if any(
                kw in s.lower() for kw in ['key', 'secret', 'token', 'password', 'hash', 'salt', 'iv', 'nonce']
            )]
            if crypto_strings:
                cprint(f"  Potential key/secret strings: {len(crypto_strings)}", "yellow")
                for offset, s in crypto_strings[:30]:
                    cprint(f"    0x{offset:08x}  {s[:80]}", "white")
            print()
            pause()

        else:
            cprint("  invalid choice", "red")
            time.sleep(0.5)

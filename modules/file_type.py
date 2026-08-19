MAGIC_BYTES = {
    b'\x89PNG\r\n\x1a\n': 'PNG',
    b'\xff\xd8\xff': 'JPEG',
    b'GIF87a': 'GIF',
    b'GIF89a': 'GIF',
    b'%PDF': 'PDF',
    b'PK\x03\x04': 'ZIP',
    b'PK\x05\x06': 'ZIP (empty)',
    b'PK\x07\x08': 'ZIP (spanned)',
    b'Rar!\x1a\x07\x00': 'RAR',
    b'Rar!\x1a\x07\x01\x00': 'RAR5',
    b'7z\xbc\xaf\x27\x1c': '7Z',
    b'\x1f\x8b\x08': 'GZIP',
    b'BZh': 'BZIP2',
    b'\xfd7zXZ\x00': 'XZ',
    b'BM': 'BMP',
    b'II\x2a\x00': 'TIFF (little-endian)',
    b'MM\x00\x2a': 'TIFF (big-endian)',
    b'RIFF': 'RIFF (WAV/AVI)',
    b'\x00\x00\x01\x00': 'ICO',
    b'\x00\x00\x02\x00': 'CUR',
    b'ID3': 'MP3 (ID3v2)',
    b'\xff\xfb': 'MP3',
    b'\xff\xf3': 'MP3',
    b'\xff\xf2': 'MP3',
    b'fLaC': 'FLAC',
    b'OggS': 'OGG',
    b'\x1aE\xdf\xa3': 'MKV/WebM',
    b'ftyp': 'MP4/MOV',
    b'SQLite format 3\x00': 'SQLite',
    b'MZ': 'PE (EXE/DLL)',
    b'\x7fELF': 'ELF',
    b'\xca\xfe\xba\xbe': 'Mach-O (Java class)',
    b'\xfe\xed\xfa\xce': 'Mach-O 32-bit',
    b'\xce\xfa\xed\xfe': 'Mach-O 64-bit',
    b'#!/bin/sh': 'Shell script',
    b'#!/bin/bash': 'Bash script',
    b'#!/usr/bin/env python': 'Python script',
    b'#!/usr/bin/env node': 'Node.js script',
    b'<!DOCTYPE html': 'HTML',
    b'<?xml': 'XML',
    b'{\n': 'JSON',
    b'{\r': 'JSON',
}

def run(kevbin):
    kevbin.box.title("File Type Detector")
    path = kevbin.box.input("File path: ")
    if not path:
        return
    
    try:
        with open(path, 'rb') as f:
            header = f.read(32)
    except Exception as e:
        kevbin.box.error(f"Failed to read file: {e}")
        return
    
    detected = "Unknown"
    for magic, ftype in MAGIC_BYTES.items():
        if header.startswith(magic):
            detected = ftype
            break
    
    if detected == "Unknown" and header[:4] == b'RIFF':
        if header[8:12] == b'WAVE':
            detected = "WAV"
        elif header[8:12] == b'AVI ':
            detected = "AVI"
        elif header[8:12] == b'WEBP':
            detected = "WEBP"
    
    if detected == "Unknown" and header[:4] == b'ftyp':
        if b'isom' in header or b'mp41' in header or b'mp42' in header:
            detected = "MP4"
        elif b'qt  ' in header:
            detected = "MOV"
    
    kevbin.box.table(
        ["Property", "Value"],
        [["File", path], ["Detected Type", detected], ["Header (hex)", header[:16].hex().upper()], ["Header (ascii)", ''.join(chr(b) if 32 <= b < 127 else '.' for b in header[:16])]]
    )
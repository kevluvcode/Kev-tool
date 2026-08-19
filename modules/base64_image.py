"""Base64 Image — Encode/decode images to/from Base64."""

import os
import base64


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🛡️', 'BASE64 IMAGE')
    kevbin.cprint(kevbin.t.secondary, "  [1]  Image -> Base64 string")
    kevbin.cprint(kevbin.t.secondary, "  [2]  Base64 string -> Image")
    kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
    kevbin.line()
    choice = kevbin.input_choice()
    if choice == '0': return

    if choice == '1':
        path = kevbin.input_choice("  Image path: ").strip().strip('"')
        if not path or not os.path.isfile(path):
            kevbin.cprint(kevbin.t.error, "  [X] File not found.")
            kevbin.pause()
            return
        with open(path, 'rb') as f:
            data = base64.b64encode(f.read()).decode()
        ext = os.path.splitext(path)[1].lower()
        mime = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
                '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml'}.get(ext, 'image/png')
        out = f"data:{mime};base64,{data}"
        out_path = path + '.b64.txt'
        with open(out_path, 'w') as f:
            f.write(out)
        kevbin.cprint(kevbin.t.success, f"\n  [✓] Saved: {out_path} ({len(data)} chars)")
        kevbin.pause()
    elif choice == '2':
        b64 = kevbin.input_choice("  Base64 data (or file path): ").strip()
        if os.path.isfile(b64):
            with open(b64, 'r') as f:
                b64 = f.read().strip()
        out = kevbin.input_choice("  Output filename (default decoded.png): ").strip() or 'decoded.png'
        try:
            if ',' in b64:
                b64 = b64.split(',', 1)[1]
            with open(out, 'wb') as f:
                f.write(base64.b64decode(b64))
            kevbin.cprint(kevbin.t.success, f"\n  [✓] Saved: {out}")
        except Exception as e:
            kevbin.cprint(kevbin.t.error, f"  [X] {e}")
        kevbin.pause()

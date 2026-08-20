"""QR Generator — Create QR codes + decode from image."""

import os

try:
    import qrcode
except ImportError:
    qrcode = None

try:
    from PIL import Image
except ImportError:
    Image = None


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('📷', 'QR CODE TOOL')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Generate QR code")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Generate styled QR")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Decode QR from image")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0':
            return

        if choice in ('1', '2'):
            if qrcode is None:
                kevbin.cprint(kevbin.t.error, "  [X] pip install qrcode[pil]")
                kevbin.pause()
                return

            data = kevbin.input_choice("  Data/URL: ").strip()
            if not data:
                continue

            out = kevbin.input_choice("  Filename [qr.png]: ").strip() or 'qr.png'

            if choice == '2':
                fg = kevbin.input_choice("  Foreground hex [000000]: ").strip() or '000000'
                bg = kevbin.input_choice("  Background hex [ffffff]: ").strip() or 'ffffff'
                box_size = kevbin.input_choice("  Box size [10]: ").strip() or '10'
                border = kevbin.input_choice("  Border [4]: ").strip() or '4'
                try:
                    box_size = int(box_size)
                    border = int(border)
                except ValueError:
                    box_size, border = 10, 4
                qr = qrcode.QRCode(version=1, box_size=box_size, border=border)
                qr.add_data(data)
                qr.make(fit=True)
                img = qr.make_image(fill_color=f'#{fg}', back_color=f'#{bg}')
            else:
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(data)
                qr.make(fit=True)
                img = qr.make_image(fill_color='black', back_color='white')

            img.save(os.path.join(os.getcwd(), out))
            size = os.path.getsize(out)
            kevbin.cprint(kevbin.t.success, f"\n  [+] Saved: {out} ({size:,} bytes)")
            kevbin.cprint(kevbin.t.dim, f"  Version: {qr.version}  Mode: {qr.mode}")
            kevbin.cprint(kevbin.t.dim, f"  Error correction: {qr.error_correction}")
            kevbin.pause()

        elif choice == '3':
            path = kevbin.input_choice("  Image path: ").strip().strip('"').strip("'")
            if not path or not os.path.isfile(path):
                kevbin.cprint(kevbin.t.error, "  [X] File not found.")
                kevbin.pause()
                continue
            try:
                import subprocess
                result = subprocess.run(
                    ['python', '-c', f"""
import sys
try:
    from pyzbar.pyzbar import decode
    from PIL import Image
    img = Image.open(r"{path}")
    results = decode(img)
    for r in results:
        print(f"Type: {{r.type}}")
        print(f"Data: {{r.data.decode()}}")
except ImportError:
    print("NEED_PYZBAR")
"""],
                    capture_output=True, text=True, timeout=10
                )
                if 'NEED_PYZBAR' in result.stdout:
                    kevbin.cprint(kevbin.t.error, "  [X] pip install pyzbar Pillow")
                elif result.stdout.strip():
                    kevbin.cprint(kevbin.t.accent, f"\n  Decoded:")
                    kevbin.cprint(kevbin.t.txt, f"  {result.stdout.strip()}")
                else:
                    kevbin.cprint(kevbin.t.warning, "  [!] No QR code found in image.")
            except Exception as e:
                kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()

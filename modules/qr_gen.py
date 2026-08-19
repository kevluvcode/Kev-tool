"""QR Generator — Create QR codes."""

import os

try:
    import qrcode
except ImportError:
    qrcode = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🛡️', 'QR GENERATOR')

    if qrcode is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install qrcode[pil]")
        kevbin.pause()
        return

    data = kevbin.input_choice("  Data/URL: ").strip()
    if not data:
        return

    out = kevbin.input_choice("  Filename (default qr.png): ").strip() or 'qr.png'
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    img.save(os.path.join(os.getcwd(), out))
    kevbin.cprint(kevbin.t.success, f"\n  [✓] Saved: {out}")
    kevbin.pause()

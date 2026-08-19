"""QR Generator — Create QR codes."""

import os

try:
    import qrcode
except ImportError:
    qrcode = None


def run(navi):
    navi.clear()
    navi.section_header('🛡️', 'QR GENERATOR')

    if qrcode is None:
        navi.cprint(navi.t.error, "  [X] pip install qrcode[pil]")
        navi.pause()
        return

    data = navi.input_choice("  Data/URL: ").strip()
    if not data:
        return

    out = navi.input_choice("  Filename (default qr.png): ").strip() or 'qr.png'
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    img.save(os.path.join(os.getcwd(), out))
    navi.cprint(navi.t.success, f"\n  [✓] Saved: {out}")
    navi.pause()

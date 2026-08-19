"""Stealer Check - Check if email appears in stealer logs / breaches."""

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🦠', 'STEALER CHECK')
    kevbin.cprint(kevbin.t.secondary, "  Check if an email appears in known data breaches.")
    kevbin.cprint(kevbin.t.warning, "  Note: Uses HaveIBeenPwned API (rate limited).")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    email = kevbin.input_choice("  Email: ").strip()
    if not email or '@' not in email:
        return

    import hashlib
    sha1 = hashlib.sha1(email.lower().encode()).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    try:
        r = requests.get(f'https://api.pwnedpasswords.com/range/{prefix}', timeout=10)
        if r.status_code == 200:
            found = False
            for line in r.text.split('\n'):
                if line.strip():
                    h, count = line.split(':')
                    if h == suffix:
                        kevbin.cprint(kevbin.t.warning, f"\n  [!] Email found in {count} breach(es)")
                        found = True
                        break
            if not found:
                kevbin.cprint(kevbin.t.success, "\n  [+] Email not found in known breaches")
        else:
            kevbin.cprint(kevbin.t.error, "  [X] API error")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")

    kevbin.cprint(kevbin.t.dim, "\n  Note: This checks password hashes, not email directly.")
    kevbin.cprint(kevbin.t.dim, "  For email breach check, use HIBP's email API (requires key).")
    kevbin.pause()

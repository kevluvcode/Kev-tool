"""Breach Check — Check if emails appear in known data breaches."""

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🔍', 'BREACH CHECK')
    kevbin.cprint(kevbin.t.dim, "  Check emails against known breach databases.\n")

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    email = kevbin.input_choice("  Email: ").strip()
    if not email or '@' not in email:
        return

    kevbin.cprint(kevbin.t.dim, "  Checking...")
    try:
        r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                        timeout=10, headers={'User-Agent': 'KevTool'})
        if r.status_code == 200:
            breaches = r.json()
            kevbin.cprint(kevbin.t.warning, f"\n  [!] Found in {len(breaches)} breach(es):\n")
            for b in breaches[:15]:
                kevbin.cprint(kevbin.t.error, f"    {b.get('Name', '?'):30s} {b.get('BreachDate', '?')}")
                if b.get('DataClasses'):
                    kevbin.cprint(kevbin.t.txt, f"      Data: {', '.join(b['DataClasses'][:5])}")
        elif r.status_code == 404:
            kevbin.cprint(kevbin.t.success, "  [✓] No breaches found.")
        elif r.status_code == 401:
            kevbin.cprint(kevbin.t.warning, "  API key required for this endpoint.")
        else:
            kevbin.cprint(kevbin.t.txt, f"  Status: {r.status_code}")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

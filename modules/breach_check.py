"""Breach Check — Check if emails appear in known data breaches."""

try:
    import requests
except ImportError:
    requests = None


def run(navi):
    navi.clear()
    navi.section_header('🔍', 'BREACH CHECK')
    navi.cprint(navi.t.dim, "  Check emails against known breach databases.\n")

    if requests is None:
        navi.cprint(navi.t.error, "  [X] pip install requests")
        navi.pause()
        return

    email = navi.input_choice("  Email: ").strip()
    if not email or '@' not in email:
        return

    navi.cprint(navi.t.dim, "  Checking...")
    try:
        r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                        timeout=10, headers={'User-Agent': 'KevTool'})
        if r.status_code == 200:
            breaches = r.json()
            navi.cprint(navi.t.warning, f"\n  [!] Found in {len(breaches)} breach(es):\n")
            for b in breaches[:15]:
                navi.cprint(navi.t.error, f"    {b.get('Name', '?'):30s} {b.get('BreachDate', '?')}")
                if b.get('DataClasses'):
                    navi.cprint(navi.t.dim, f"      Data: {', '.join(b['DataClasses'][:5])}")
        elif r.status_code == 404:
            navi.cprint(navi.t.success, "  [✓] No breaches found.")
        elif r.status_code == 401:
            navi.cprint(navi.t.dim, "  API key required for this endpoint.")
        else:
            navi.cprint(navi.t.dim, f"  Status: {r.status_code}")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] {e}")
    navi.pause()

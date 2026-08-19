"""Email Tools — Validate email format + check MX records + reputation."""

import re
import socket

try:
    import requests
except ImportError:
    requests = None


def run(navi):
    while True:
        navi.clear()
        navi.section_header('🔍', 'EMAIL TOOLS')
        navi.cprint(navi.t.secondary, "  [1]  Validate Email Format")
        navi.cprint(navi.t.secondary, "  [2]  Check MX Records")
        navi.cprint(navi.t.secondary, "  [3]  Email Reputation Check")
        navi.cprint(navi.t.secondary, "  [0]  Back")
        navi.line()
        choice = navi.input_choice()
        if choice == '0': return

        if choice == '1':
            email = navi.input_choice("  Email: ").strip()
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(pattern, email):
                navi.cprint(navi.t.success, f"\n  [✓] Valid format: {email}")
                domain = email.split('@')[1]
                navi.cprint(navi.t.dim, f"  Domain: {domain}")
            else:
                navi.cprint(navi.t.error, f"\n  [X] Invalid format: {email}")
            navi.pause()

        elif choice == '2':
            domain = navi.input_choice("  Domain: ").strip()
            if not domain:
                continue
            navi.cprint(navi.t.dim, f"\n  MX records for {domain}:")
            try:
                import dns.resolver
                answers = dns.resolver.resolve(domain, 'MX')
                for r in sorted(answers, key=lambda x: x.preference):
                    navi.cprint(navi.t.accent, f"    {r.preference:3d} {r.exchange}")
            except ImportError:
                navi.cprint(navi.t.error, "  [X] pip install dnspython")
            except dns.resolver.NoAnswer:
                navi.cprint(navi.t.warning, "  [!] No MX records found.")
            except Exception as e:
                navi.cprint(navi.t.error, f"  [X] {e}")
            navi.pause()

        elif choice == '3' and requests:
            email = navi.input_choice("  Email: ").strip()
            if '@' not in email:
                continue
            domain = email.split('@')[1]
            navi.cprint(navi.t.dim, f"\n  Checking {domain}...")
            try:
                mx_records = []
                import dns.resolver
                for r in dns.resolver.resolve(domain, 'MX'):
                    mx_records.append(str(r.exchange).rstrip('.'))
            except Exception:
                mx_records = []

            if mx_records:
                navi.cprint(navi.t.success, f"  MX: {', '.join(mx_records[:3])}")
                provider = mx_records[0].lower()
                if 'google' in provider or 'gmail' in provider:
                    navi.cprint(navi.t.accent, "  Provider: Google Workspace / Gmail")
                elif 'outlook' in provider or 'microsoft' in provider:
                    navi.cprint(navi.t.accent, "  Provider: Microsoft 365")
                elif 'proton' in provider:
                    navi.cprint(navi.t.accent, "  Provider: ProtonMail")
                else:
                    navi.cprint(navi.t.accent, f"  Provider: {provider}")
            else:
                navi.cprint(navi.t.warning, "  [!] No MX records — may be invalid.")
            navi.pause()

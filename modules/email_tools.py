"""Email Tools — Validate email format + check MX records + reputation."""

import re
import socket

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🔍', 'EMAIL TOOLS')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Validate Email Format")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Check MX Records")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Email Reputation Check")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0': return

        if choice == '1':
            email = kevbin.input_choice("  Email: ").strip()
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(pattern, email):
                kevbin.cprint(kevbin.t.success, f"\n  [✓] Valid format: {email}")
                domain = email.split('@')[1]
                kevbin.cprint(kevbin.t.txt, f"  Domain: {domain}")
            else:
                kevbin.cprint(kevbin.t.error, f"\n  [X] Invalid format: {email}")
            kevbin.pause()

        elif choice == '2':
            domain = kevbin.input_choice("  Domain: ").strip()
            if not domain:
                continue
            kevbin.cprint(kevbin.t.txt, f"\n  MX records for {domain}:")
            try:
                import dns.resolver
                answers = dns.resolver.resolve(domain, 'MX')
                for r in sorted(answers, key=lambda x: x.preference):
                    kevbin.cprint(kevbin.t.accent, f"    {r.preference:3d} {r.exchange}")
            except ImportError:
                kevbin.cprint(kevbin.t.error, "  [X] pip install dnspython")
            except dns.resolver.NoAnswer:
                kevbin.cprint(kevbin.t.warning, "  [!] No MX records found.")
            except Exception as e:
                kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()

        elif choice == '3' and requests:
            email = kevbin.input_choice("  Email: ").strip()
            if '@' not in email:
                continue
            domain = email.split('@')[1]
            kevbin.cprint(kevbin.t.dim, f"\n  Checking {domain}...")
            try:
                mx_records = []
                import dns.resolver
                for r in dns.resolver.resolve(domain, 'MX'):
                    mx_records.append(str(r.exchange).rstrip('.'))
            except Exception:
                mx_records = []

            if mx_records:
                kevbin.cprint(kevbin.t.success, f"  MX: {', '.join(mx_records[:3])}")
                provider = mx_records[0].lower()
                if 'google' in provider or 'gmail' in provider:
                    kevbin.cprint(kevbin.t.accent, "  Provider: Google Workspace / Gmail")
                elif 'outlook' in provider or 'microsoft' in provider:
                    kevbin.cprint(kevbin.t.accent, "  Provider: Microsoft 365")
                elif 'proton' in provider:
                    kevbin.cprint(kevbin.t.accent, "  Provider: ProtonMail")
                else:
                    kevbin.cprint(kevbin.t.accent, f"  Provider: {provider}")
            else:
                kevbin.cprint(kevbin.t.warning, "  [!] No MX records — may be invalid.")
            kevbin.pause()


def validate(kevbin):
    run(kevbin)


def reputation(kevbin):
    run(kevbin)

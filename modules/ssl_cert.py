"""SSL Cert — Check SSL certificate info for any domain."""

import ssl
import socket
import datetime

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🛡️', 'SSL CERTIFICATE INFO')

    domain = kevbin.input_choice("  Domain: ").strip().replace('https://', '').replace('http://', '').rstrip('/')
    if not domain:
        return

    kevbin.cprint(kevbin.t.dim, f"  Checking SSL for {domain}...")

    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(10)
            s.connect((domain, 443))
            cert = s.getpeercert()

        kevbin.cprint(kevbin.t.highlight + kevbin.t.B, f"\n  ┌─ SSL CERTIFICATE {'─' * 35}")
        subject = dict(x[0] for x in cert.get('subject', []))
        issuer = dict(x[0] for x in cert.get('issuer', []))
        kevbin.cprint(kevbin.t.secondary, f"  │ Domain:      {subject.get('commonName', '?')}")
        kevbin.cprint(kevbin.t.secondary, f"  │ Issuer:      {issuer.get('organizationName', '?')}")
        kevbin.cprint(kevbin.t.secondary, f"  │ Issuer CN:   {issuer.get('commonName', '?')}")

        not_before = cert.get('notBefore', '?')
        not_after = cert.get('notAfter', '?')
        kevbin.cprint(kevbin.t.secondary, f"  │ Valid From:  {not_before}")
        kevbin.cprint(kevbin.t.secondary, f"  │ Valid Until: {not_after}")

        sans = cert.get('subjectAltName', [])
        if sans:
            kevbin.cprint(kevbin.t.secondary, f"  │ SANs:        {len(sans)} domains")
            for san_type, san_val in sans[:5]:
                kevbin.cprint(kevbin.t.dim, f"  │   {san_val}")
            if len(sans) > 5:
                kevbin.cprint(kevbin.t.dim, f"  │   ... +{len(sans)-5} more")

        serial = cert.get('serialNumber', '?')
        kevbin.cprint(kevbin.t.secondary, f"  │ Serial:      {serial}")
        kevbin.cprint(kevbin.t.highlight, f"  └{'─' * 53}")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] SSL connection failed: {e}")
    kevbin.pause()

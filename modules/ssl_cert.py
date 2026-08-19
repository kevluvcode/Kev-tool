"""SSL Cert — Check SSL certificate info for any domain."""

import ssl
import socket
import datetime

try:
    import requests
except ImportError:
    requests = None


def run(navi):
    navi.clear()
    navi.section_header('🛡️', 'SSL CERTIFICATE INFO')

    domain = navi.input_choice("  Domain: ").strip().replace('https://', '').replace('http://', '').rstrip('/')
    if not domain:
        return

    navi.cprint(navi.t.dim, f"  Checking SSL for {domain}...")

    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(10)
            s.connect((domain, 443))
            cert = s.getpeercert()

        navi.cprint(navi.t.highlight + navi.t.B, f"\n  ┌─ SSL CERTIFICATE {'─' * 35}")
        subject = dict(x[0] for x in cert.get('subject', []))
        issuer = dict(x[0] for x in cert.get('issuer', []))
        navi.cprint(navi.t.secondary, f"  │ Domain:      {subject.get('commonName', '?')}")
        navi.cprint(navi.t.secondary, f"  │ Issuer:      {issuer.get('organizationName', '?')}")
        navi.cprint(navi.t.secondary, f"  │ Issuer CN:   {issuer.get('commonName', '?')}")

        not_before = cert.get('notBefore', '?')
        not_after = cert.get('notAfter', '?')
        navi.cprint(navi.t.secondary, f"  │ Valid From:  {not_before}")
        navi.cprint(navi.t.secondary, f"  │ Valid Until: {not_after}")

        sans = cert.get('subjectAltName', [])
        if sans:
            navi.cprint(navi.t.secondary, f"  │ SANs:        {len(sans)} domains")
            for san_type, san_val in sans[:5]:
                navi.cprint(navi.t.dim, f"  │   {san_val}")
            if len(sans) > 5:
                navi.cprint(navi.t.dim, f"  │   ... +{len(sans)-5} more")

        serial = cert.get('serialNumber', '?')
        navi.cprint(navi.t.secondary, f"  │ Serial:      {serial}")
        navi.cprint(navi.t.highlight, f"  └{'─' * 53}")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] SSL connection failed: {e}")
    navi.pause()

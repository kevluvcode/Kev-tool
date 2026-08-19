"""OSINT — Whois, DNS, IP info, email lookup, metadata scan, username check."""

import os
import json
import socket
import time

try:
    import requests
except ImportError:
    requests = None


def whois_lookup(navi):
    navi.clear()
    navi.section_header('🔍', 'WHOIS LOOKUP')
    domain = navi.input_choice("  Domain: ").strip().replace('https://', '').replace('http://', '').rstrip('/')
    if not domain:
        return

    navi.cprint(navi.t.dim, "  Querying...")
    try:
        import whois
        w = whois.whois(domain)
        navi.cprint(navi.t.highlight + navi.t.B, f"\n  ┌─ WHOIS: {domain} {'─' * (40 - len(domain))}")
        for key in ['domain_name', 'registrar', 'creation_date', 'expiration_date', 'name_servers', 'org', 'country', 'emails']:
            val = w.get(key, 'N/A')
            if isinstance(val, list):
                val = ', '.join(str(v) for v in val[:5])
            navi.cprint(navi.t.secondary, f"  │ {str(key):20s} {str(val)[:60]}")
        navi.cprint(navi.t.highlight, f"  └{'─' * 53}")
    except ImportError:
        navi.cprint(navi.t.error, "  [X] Install: pip install python-whois")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] Error: {e}")
    navi.pause()


def dns_resolver(navi):
    navi.clear()
    navi.section_header('🔍', 'DNS RESOLVER')
    domain = navi.input_choice("  Domain: ").strip()
    if not domain:
        return

    navi.cprint(navi.t.dim, "  Resolving...")
    try:
        import dns.resolver
        types = ['A', 'AAAA', 'MX', 'TXT', 'CNAME', 'NS', 'SOA']
        navi.cprint(navi.t.highlight + navi.t.B, f"\n  ┌─ DNS: {domain} {'─' * (42 - len(domain))}")
        for rtype in types:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                for r in answers:
                    navi.cprint(navi.t.accent, f"  │ {rtype:6s} {str(r)}")
            except Exception:
                pass
        navi.cprint(navi.t.highlight, f"  └{'─' * 53}")
    except ImportError:
        navi.cprint(navi.t.error, "  [X] Install: pip install dnspython")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] Error: {e}")
    navi.pause()


def ip_info(navi):
    navi.clear()
    navi.section_header('🔍', 'IP INFO')
    navi.cprint(navi.t.dim, "  Fetching your public IP...\n")

    if requests is None:
        navi.cprint(navi.t.error, "  [X] 'requests' not installed.")
        navi.pause()
        return

    try:
        r = requests.get('https://ipinfo.io/json', timeout=10)
        data = r.json()
        navi.cprint(navi.t.highlight + navi.t.B, f"  ┌─ IP INFO {'─' * 42}")
        for key in ['ip', 'city', 'region', 'country', 'loc', 'org', 'timezone', 'postal']:
            val = data.get(key, 'N/A')
            navi.cprint(navi.t.secondary, f"  │ {key:12s} {val}")
        navi.cprint(navi.t.highlight, f"  └{'─' * 53}")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] Error: {e}")
    navi.pause()


def email_lookup(navi):
    navi.clear()
    navi.section_header('🔍', 'EMAIL LOOKUP')
    navi.cprint(navi.t.dim, "  Check if an email has been in known data breaches.\n")

    if requests is None:
        navi.cprint(navi.t.error, "  [X] 'requests' not installed.")
        navi.pause()
        return

    email = navi.input_choice("  Email address: ").strip()
    if not email or '@' not in email:
        return

    navi.cprint(navi.t.dim, "  Checking...")
    try:
        resp = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", timeout=10,
                           headers={'User-Agent': 'KevTool-OSINT'})
        if resp.status_code == 200:
            breaches = resp.json()
            navi.cprint(navi.t.warning, f"\n  [!] Found in {len(breaches)} breach(es):")
            for b in breaches[:10]:
                navi.cprint(navi.t.error, f"    - {b.get('Name', '?')} ({b.get('BreachDate', '?')})")
        elif resp.status_code == 404:
            navi.cprint(navi.t.success, "  [✓] No breaches found for this email.")
        else:
            navi.cprint(navi.t.dim, f"  Status: {resp.status_code}")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] Error: {e}")
    navi.pause()


def metadata_scan(navi):
    navi.clear()
    navi.section_header('🔍', 'METADATA SCANNER')
    navi.cprint(navi.t.dim, "  Extract EXIF metadata from images.\n")

    path = navi.input_choice("  File path: ").strip().strip('"').strip("'")
    if not path or not os.path.isfile(path):
        navi.cprint(navi.t.error, "  [X] File not found.")
        navi.pause()
        return

    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        img = Image.open(path)
        exif_data = img._getexif()
        if exif_data:
            navi.cprint(navi.t.highlight + navi.t.B, f"\n  ┌─ METADATA: {os.path.basename(path)}")
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, str(tag_id))
                val = str(value)[:60]
                navi.cprint(navi.t.secondary, f"  │ {tag:25s} {val}")
            navi.cprint(navi.t.highlight, f"  └{'─' * 53}")
        else:
            navi.cprint(navi.t.warning, "  [!] No EXIF data found.")
    except ImportError:
        navi.cprint(navi.t.error, "  [X] Install: pip install Pillow")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] Error: {e}")
    navi.pause()


def username_check(navi):
    navi.clear()
    navi.section_header('🔍', 'USERNAME CHECKER')
    navi.cprint(navi.t.dim, "  Check username availability across platforms.\n")

    username = navi.input_choice("  Username: ").strip()
    if not username:
        return

    if requests is None:
        navi.cprint(navi.t.error, "  [X] 'requests' not installed.")
        navi.pause()
        return

    platforms = [
        ('GitHub', f'https://github.com/{username}', 200, 404),
        ('Twitter', f'https://twitter.com/{username}', 200, 404),
        ('Reddit', f'https://www.reddit.com/user/{username}', 200, 404),
        ('Instagram', f'https://www.instagram.com/{username}/', 200, 404),
        ('TikTok', f'https://www.tiktok.com/@{username}', 200, 404),
        ('YouTube', f'https://www.youtube.com/@{username}', 200, 404),
        ('Twitch', f'https://www.twitch.tv/{username}', 200, 404),
        ('Discord', f'https://discord.com', 200, 404),
    ]

    navi.cprint(navi.t.highlight + navi.t.B, f"\n  Checking '{username}'...\n")
    for name, url, taken_code, avail_code in platforms:
        try:
            resp = requests.head(url, timeout=8, allow_redirects=True,
                               headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == taken_code:
                navi.cprint(navi.t.error, f"    ✗ {name:12s}  TAKEN")
            else:
                navi.cprint(navi.t.success, f"    ✓ {name:12s}  AVAILABLE (or undetermined)")
        except Exception:
            navi.cprint(navi.t.dim, f"    ? {name:12s}  ERROR")
        time.sleep(0.3)

    navi.cprint(navi.t.dim, "\n  Note: Results may vary. Some platforms block automated checks.")
    navi.pause()

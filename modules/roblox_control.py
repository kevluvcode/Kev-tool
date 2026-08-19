"""Roblox Control — Cookie login and asset downloader."""

import json
import os

try:
    import requests
except ImportError:
    requests = None


def _headers(cookie=''):
    h = {'User-Agent': 'KevTool/1.0'}
    if cookie:
        h['Cookie'] = f'.ROBLOSECURITY={cookie}'
    return h


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🎮', 'COOKIE LOGIN')

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    cookie = kevbin.input_choice("  .ROBLOSECURITY: ").strip()
    if not cookie:
        return

    kevbin.cprint(kevbin.t.dim, "  Validating...")
    try:
        r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=_headers(cookie), timeout=10)
        if r.status_code == 200:
            d = r.json()
            kevbin.cprint(kevbin.t.success, f"\n  [✓] Valid!")
            rows = [('Name', d.get('name', '?')), ('Display', d.get('displayName', '?')),
                    ('ID', d.get('id', '?')), ('Created', d.get('created', '?'))]
            kevbin.cprint(kevbin.t.highlight + kevbin.t.B, f"  ┌─ ACCOUNT {'─' * 42}")
            for k, v in rows:
                kevbin.cprint(kevbin.t.secondary, f"  │ {k:12s} {v}")
            kevbin.cprint(kevbin.t.highlight, f"  └{'─' * 53}")
        else:
            kevbin.cprint(kevbin.t.error, "  [X] Invalid/expired cookie.")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()


def asset_download(kevbin):
    kevbin.clear()
    kevbin.section_header('🎮', 'ASSET DOWNLOADER')

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    aid = kevbin.input_choice("  Asset ID: ").strip()
    if not aid or not aid.isdigit():
        kevbin.cprint(kevbin.t.error, "  [X] Invalid ID.")
        kevbin.pause()
        return

    cookie = kevbin.input_choice("  Cookie (optional): ").strip()
    out = kevbin.input_choice("  Filename (default asset.rbxl): ").strip() or 'asset.rbxl'

    kevbin.cprint(kevbin.t.dim, "  Downloading...")
    try:
        r = requests.get(f"https://assetdelivery.roblox.com/v1/asset?id={aid}", headers=_headers(cookie), timeout=30, stream=True)
        if r.status_code == 200:
            with open(out, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            kevbin.cprint(kevbin.t.success, f"\n  [✓] {out} ({os.path.getsize(out):,} bytes)")
        else:
            kevbin.cprint(kevbin.t.error, f"  [X] HTTP {r.status_code}")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

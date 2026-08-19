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


def run(navi):
    navi.clear()
    navi.section_header('🎮', 'COOKIE LOGIN')

    if requests is None:
        navi.cprint(navi.t.error, "  [X] pip install requests")
        navi.pause()
        return

    cookie = navi.input_choice("  .ROBLOSECURITY: ").strip()
    if not cookie:
        return

    navi.cprint(navi.t.dim, "  Validating...")
    try:
        r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=_headers(cookie), timeout=10)
        if r.status_code == 200:
            d = r.json()
            navi.cprint(navi.t.success, f"\n  [✓] Valid!")
            rows = [('Name', d.get('name', '?')), ('Display', d.get('displayName', '?')),
                    ('ID', d.get('id', '?')), ('Created', d.get('created', '?'))]
            navi.cprint(navi.t.highlight + navi.t.B, f"  ┌─ ACCOUNT {'─' * 42}")
            for k, v in rows:
                navi.cprint(navi.t.secondary, f"  │ {k:12s} {v}")
            navi.cprint(navi.t.highlight, f"  └{'─' * 53}")
        else:
            navi.cprint(navi.t.error, "  [X] Invalid/expired cookie.")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] {e}")
    navi.pause()


def asset_download(navi):
    navi.clear()
    navi.section_header('🎮', 'ASSET DOWNLOADER')

    if requests is None:
        navi.cprint(navi.t.error, "  [X] pip install requests")
        navi.pause()
        return

    aid = navi.input_choice("  Asset ID: ").strip()
    if not aid or not aid.isdigit():
        navi.cprint(navi.t.error, "  [X] Invalid ID.")
        navi.pause()
        return

    cookie = navi.input_choice("  Cookie (optional): ").strip()
    out = navi.input_choice("  Filename (default asset.rbxl): ").strip() or 'asset.rbxl'

    navi.cprint(navi.t.dim, "  Downloading...")
    try:
        r = requests.get(f"https://assetdelivery.roblox.com/v1/asset?id={aid}", headers=_headers(cookie), timeout=30, stream=True)
        if r.status_code == 200:
            with open(out, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            navi.cprint(navi.t.success, f"\n  [✓] {out} ({os.path.getsize(out):,} bytes)")
        else:
            navi.cprint(navi.t.error, f"  [X] HTTP {r.status_code}")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] {e}")
    navi.pause()

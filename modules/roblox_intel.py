"""Roblox Intel — User info, group info, inventory, game info."""

import json

try:
    import requests
except ImportError:
    requests = None

BASE = "https://users.roblox.com"
GROUPS = "https://groups.roblox.com"
INVENTORY = "https://inventory.roblox.com"
THUMBS = "https://thumbnails.roblox.com"
GAMES = "https://games.roblox.com"
ECONOMY = "https://economy.roblox.com"


def _get(url, params=None):
    if requests is None:
        return None
    try:
        r = requests.get(url, headers={'User-Agent': 'KevTool/1.0'}, params=params, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def _print_box(navi, title, rows):
    navi.cprint(navi.t.highlight + navi.t.B, f"\n  ┌─ {title} {'─' * max(1, 48 - len(title))}")
    for k, v in rows:
        navi.cprint(navi.t.secondary, f"  │ {k:16s} {str(v)[:55]}")
    navi.cprint(navi.t.highlight, f"  └{'─' * 53}")


def run(navi):
    navi.clear()
    navi.section_header('🎮', 'USER INTEL')
    username = navi.input_choice("  Roblox username: ").strip()
    if not username:
        return
    navi.cprint(navi.t.dim, "  Looking up...")
    data = _get(f"{BASE}/v1/usernames/users", params={'usernames': json.dumps([username])})
    if data and data.get('data'):
        d = data['data'][0]
        _print_box(navi, 'USER INFO', [
            ('Name', d.get('name', '?')),
            ('Display', d.get('displayName', '?')),
            ('ID', d.get('id', '?')),
            ('Created', d.get('created', '?')),
            ('Banned', d.get('isBanned', False)),
            ('Bio', (d.get('description', '') or '')[:55]),
        ])
    else:
        navi.cprint(navi.t.error, "  [X] User not found.")
    navi.pause()


def group_lookup(navi):
    navi.clear()
    navi.section_header('🎮', 'GROUP INTEL')
    gid = navi.input_choice("  Group ID: ").strip()
    if not gid or not gid.isdigit():
        navi.cprint(navi.t.error, "  [X] Invalid ID.")
        navi.pause()
        return
    data = _get(f"{GROUPS}/v2/groups/{gid}")
    if data:
        _print_box(navi, 'GROUP INFO', [
            ('Name', data.get('name', '?')),
            ('ID', data.get('id', '?')),
            ('Owner', data.get('owner', {}).get('username', '?')),
            ('Members', data.get('memberCount', '?')),
            ('Shout', (data.get('shout', {}).get('body', 'None') or '')[:55]),
        ])
    else:
        navi.cprint(navi.t.error, "  [X] Group not found.")
    navi.pause()


def inventory_view(navi):
    navi.clear()
    navi.section_header('🎮', 'INVENTORY VIEWER')
    username = navi.input_choice("  Username: ").strip()
    if not username:
        return
    data = _get(f"{BASE}/v1/usernames/users", params={'usernames': json.dumps([username])})
    if not data or not data.get('data'):
        navi.cprint(navi.t.error, "  [X] User not found.")
        navi.pause()
        return
    uid = data['data'][0]['id']
    inv = _get(f"{INVENTORY}/v2/users/{uid}/inventory/0", params={'limit': 25})
    if inv and inv.get('data'):
        navi.cprint(navi.t.highlight + navi.t.B, f"\n  ── INVENTORY ({username}) ──")
        for item in inv['data'][:25]:
            navi.cprint(navi.t.accent, f"  {item.get('name', '?')[:40]} (ID: {item.get('id', '?')})")
    else:
        navi.cprint(navi.t.warning, "  [!] Private or empty.")
    navi.pause()


def game_info(navi):
    navi.clear()
    navi.section_header('🎮', 'GAME INFO')
    gid = navi.input_choice("  Game/Experience ID: ").strip()
    if not gid or not gid.isdigit():
        navi.cprint(navi.t.error, "  [X] Invalid ID.")
        navi.pause()
        return
    data = _get(f"{GAMES}/v1/games?universeIds={gid}")
    if data and data.get('data'):
        d = data['data'][0]
        _print_box(navi, 'GAME INFO', [
            ('Name', d.get('name', '?')),
            ('Creator', d.get('creator', {}).get('name', '?')),
            ('Visits', f"{d.get('playing', 0):,} playing / {d.get('visits', 0):,} total"),
            ('Rating', f"{d.get('favoritedCount', 0):,} favorites"),
            ('Genre', d.get('genre', '?')),
            ('Created', d.get('created', '?')),
            ('Updated', d.get('updated', '?')),
            ('Max Players', d.get('maxPlayers', '?')),
            ('VIP Server', d.get('vipMembershipAccessible', '?')),
        ])
    else:
        navi.cprint(navi.t.error, "  [X] Game not found.")
    navi.pause()

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
    kevbin.cprint(kevbin.t.highlight + kevbin.t.B, f"\n  ┌─ {title} {'─' * max(1, 48 - len(title))}")
    for k, v in rows:
        kevbin.cprint(kevbin.t.secondary, f"  │ {k:16s} {str(v)[:55]}")
    kevbin.cprint(kevbin.t.highlight, f"  └{'─' * 53}")


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🎮', 'USER INTEL')
    username = kevbin.input_choice("  Roblox username: ").strip()
    if not username:
        return
    kevbin.cprint(kevbin.t.dim, "  Looking up...")
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
        kevbin.cprint(kevbin.t.error, "  [X] User not found.")
    kevbin.pause()


def group_lookup(kevbin):
    kevbin.clear()
    kevbin.section_header('🎮', 'GROUP INTEL')
    gid = kevbin.input_choice("  Group ID: ").strip()
    if not gid or not gid.isdigit():
        kevbin.cprint(kevbin.t.error, "  [X] Invalid ID.")
        kevbin.pause()
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
        kevbin.cprint(kevbin.t.error, "  [X] Group not found.")
    kevbin.pause()


def inventory_view(kevbin):
    kevbin.clear()
    kevbin.section_header('🎮', 'INVENTORY VIEWER')
    username = kevbin.input_choice("  Username: ").strip()
    if not username:
        return
    data = _get(f"{BASE}/v1/usernames/users", params={'usernames': json.dumps([username])})
    if not data or not data.get('data'):
        kevbin.cprint(kevbin.t.error, "  [X] User not found.")
        kevbin.pause()
        return
    uid = data['data'][0]['id']
    inv = _get(f"{INVENTORY}/v2/users/{uid}/inventory/0", params={'limit': 25})
    if inv and inv.get('data'):
        kevbin.cprint(kevbin.t.highlight + kevbin.t.B, f"\n  ── INVENTORY ({username}) ──")
        for item in inv['data'][:25]:
            kevbin.cprint(kevbin.t.accent, f"  {item.get('name', '?')[:40]} (ID: {item.get('id', '?')})")
    else:
        kevbin.cprint(kevbin.t.warning, "  [!] Private or empty.")
    kevbin.pause()


def game_info(kevbin):
    kevbin.clear()
    kevbin.section_header('🎮', 'GAME INFO')
    gid = kevbin.input_choice("  Game/Experience ID: ").strip()
    if not gid or not gid.isdigit():
        kevbin.cprint(kevbin.t.error, "  [X] Invalid ID.")
        kevbin.pause()
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
        kevbin.cprint(kevbin.t.error, "  [X] Game not found.")
    kevbin.pause()

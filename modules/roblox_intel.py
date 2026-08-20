"""Roblox Intel â€” User info, group info, inventory, game info."""

import json
import re

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


def _print_box(kevbin, title, rows):
    w = kevbin._bw()
    kevbin.box_top(w)
    kevbin.box_row(f" {title} ", w)
    kevbin.box_mid(w)
    for k, v in rows:
        kevbin.box_row(f" {k:<12}{str(v)[:max(8, w - 18)]}", w)
    kevbin.box_bottom(w)


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('ðŸŽ®', 'USER INTEL')
    username = kevbin.input_choice("  Roblox username: ").strip()
    if not username:
        return
    kevbin.cprint(kevbin.t.dim, "  Looking up...")
    data = _get(f"{BASE}/v1/usernames/users", params={'usernames': json.dumps([username])})
    if data and data.get('data'):
        d = data['data'][0]
        _print_box(kevbin, 'USER INFO', [
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
    kevbin.section_header('ðŸŽ®', 'GROUP INTEL')
    gid = kevbin.input_choice("  Group ID: ").strip()
    if not gid or not gid.isdigit():
        kevbin.cprint(kevbin.t.error, "  [X] Invalid ID.")
        kevbin.pause()
        return
    data = _get(f"{GROUPS}/v2/groups/{gid}")
    if data:
        _print_box(kevbin, 'GROUP INFO', [
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
    kevbin.section_header('ðŸŽ®', 'INVENTORY VIEWER')
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
        kevbin.cprint(kevbin.t.highlight + kevbin.t.B, f"\n  â”€â”€ INVENTORY ({username}) â”€â”€")
        for item in inv['data'][:25]:
            kevbin.cprint(kevbin.t.accent, f"  {item.get('name', '?')[:40]} (ID: {item.get('id', '?')})")
    else:
        kevbin.cprint(kevbin.t.warning, "  [!] Private or empty.")
    kevbin.pause()


def game_info(kevbin):
    kevbin.clear()
    kevbin.section_header('ðŸŽ®', 'GAME INFO')
    gid = kevbin.input_choice("  Game/Experience ID: ").strip()
    if not gid or not gid.isdigit():
        kevbin.cprint(kevbin.t.error, "  [X] Invalid ID.")
        kevbin.pause()
        return
    data = _get(f"{GAMES}/v1/games?universeIds={gid}")
    if data and data.get('data'):
        d = data['data'][0]
        _print_box(kevbin, 'GAME INFO', [
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


def name_history(kevbin):
    kevbin.clear()
    kevbin.section_header('🎮', 'NAME HISTORY')
    username = kevbin.input_choice("  Roblox username: ").strip()
    if not username:
        return
    data = _get(f"{BASE}/v1/usernames/users", params={'usernames': json.dumps([username])})
    if not data or not data.get('data'):
        kevbin.cprint(kevbin.t.error, "  [X] User not found.")
        kevbin.pause()
        return
    uid = data['data'][0]['id']
    kevbin.cprint(kevbin.t.dim, "  Fetching previous names...")
    hist = _get(f"{BASE}/v1/users/{uid}/username-history", params={'limit': 100})
    if hist and hist.get('data'):
        names = [n.get('name', '?') for n in hist['data']]
        kevbin.cprint(kevbin.t.highlight + kevbin.t.B,
                      f"\n  ── {len(names)} PREVIOUS NAME(S) ──")
        for i, n in enumerate(names, 1):
            kevbin.cprint(kevbin.t.accent, f"  {i:>3}. {n}")
    else:
        kevbin.cprint(kevbin.t.success, "  [+] No previous names found.")
    kevbin.pause()


def username_check(kevbin):
    kevbin.clear()
    kevbin.section_header('🎮', 'USERNAME CHECK')
    username = kevbin.input_choice("  Username to check: ").strip()
    if not username:
        return
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        kevbin.cprint(kevbin.t.error, "  [X] Invalid username (3-20 chars, letters/numbers/_ ).")
        kevbin.pause()
        return
    kevbin.cprint(kevbin.t.dim, f"  Checking '{username}'...")
    data = _get(f"{BASE}/v1/users/username-availability", params={'username': username})
    if data is None:
        kevbin.cprint(kevbin.t.warning, "  [!] Could not reach Roblox API.")
    elif data.get('data'):
        kevbin.cprint(kevbin.t.success, f"\n  [+] '{username}' is AVAILABLE!")
    else:
        kevbin.cprint(kevbin.t.error, f"\n  [X] '{username}' is TAKEN.")
    kevbin.pause()

"""Discord Operations — Webhook info, token decoder, account info, server info, status rotator."""

import json
import re
import base64
import time

try:
    import requests
except ImportError:
    requests = None


def _headers(token=''):
    h = {'User-Agent': 'KevTool/1.0', 'Content-Type': 'application/json'}
    if token:
        h['Authorization'] = token
    return h


def webhook_info(navi):
    navi.clear()
    navi.section_header('📡', 'WEBHOOK INFO')
    navi.cprint(navi.t.dim, "  View Discord webhook details (read-only).\n")

    url = navi.input_choice("  Webhook URL: ").strip()
    if not url or 'discord' not in url:
        navi.cprint(navi.t.error, "  [X] Invalid webhook URL.")
        navi.pause()
        return

    if requests is None:
        navi.cprint(navi.t.error, "  [X] 'requests' not installed. pip install requests")
        navi.pause()
        return

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            navi.cprint(navi.t.highlight + navi.t.B, f"\n  ┌─ WEBHOOK INFO {'─' * 37}")
            navi.cprint(navi.t.secondary, f"  │ Name:       {data.get('name', '?')}")
            navi.cprint(navi.t.secondary, f"  │ Channel:    {data.get('channel_id', '?')}")
            navi.cprint(navi.t.secondary, f"  │ Guild:      {data.get('guild_id', '?')}")
            navi.cprint(navi.t.secondary, f"  │ Token:      {data.get('token', '?')[:20]}...")
            avatar = data.get('avatar', '')
            navi.cprint(navi.t.secondary, f"  │ Avatar:     {'Yes' if avatar else 'None'}")
            navi.cprint(navi.t.secondary, f"  │ Created:    {data.get('created_at', '?')}")
            navi.cprint(navi.t.highlight, f"  └{'─' * 53}")
        else:
            navi.cprint(navi.t.error, f"  [X] HTTP {resp.status_code} — webhook may be deleted.")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] Error: {e}")
    navi.pause()


def token_decode(navi):
    navi.clear()
    navi.section_header('📡', 'TOKEN DECODER')
    navi.cprint(navi.t.dim, "  Decode Discord token structure (educational).\n")

    token = navi.input_choice("  Discord token: ").strip()
    if not token:
        return

    parts = token.split('.')
    if len(parts) < 2:
        navi.cprint(navi.t.error, "  [X] Invalid token format.")
        navi.pause()
        return

    navi.cprint(navi.t.highlight + navi.t.B, f"\n  ┌─ TOKEN ANALYSIS {'─' * 36}")
    navi.cprint(navi.t.secondary, f"  │ Parts:      {len(parts)}")
    navi.cprint(navi.t.secondary, f"  │ Length:     {len(token)} chars")

    for i, part in enumerate(parts[:3]):
        try:
            decoded = base64.urlsafe_b64decode(part + '==')
            navi.cprint(navi.t.accent, f"  │ Part {i}: {decoded}")
        except Exception:
            navi.cprint(navi.t.dim, f"  │ Part {i}: (binary, {len(part)} chars)")

    if len(parts) >= 2:
        try:
            user_id = base64.urlsafe_b64decode(parts[0] + '==').decode()
            navi.cprint(navi.t.success, f"  │ User ID (approx): {user_id}")
        except Exception:
            pass

    navi.cprint(navi.t.dim, f"  │ Note: Tokens encode user ID, timestamps, and HMAC.")
    navi.cprint(navi.t.highlight, f"  └{'─' * 53}")
    navi.pause()


def account_info(navi):
    navi.clear()
    navi.section_header('📡', 'ACCOUNT INFO')
    navi.cprint(navi.t.dim, "  Fetch Discord account info from token (read-only).\n")

    if requests is None:
        navi.cprint(navi.t.error, "  [X] 'requests' not installed.")
        navi.pause()
        return

    token = navi.input_choice("  Discord token: ").strip()
    if not token:
        return

    try:
        resp = requests.get("https://discord.com/api/v10/users/@me", headers=_headers(token), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            navi.cprint(navi.t.highlight + navi.t.B, f"\n  ┌─ ACCOUNT INFO {'─' * 38}")
            navi.cprint(navi.t.secondary, f"  │ Username:    {data.get('username', '?')}#{data.get('discriminator', '0')}")
            navi.cprint(navi.t.secondary, f"  │ Display:     {data.get('global_name', '?')}")
            navi.cprint(navi.t.secondary, f"  │ ID:          {data.get('id', '?')}")
            navi.cprint(navi.t.secondary, f"  │ Email:       {data.get('email', 'hidden')}")
            navi.cprint(navi.t.secondary, f"  │ Verified:    {data.get('verified', False)}")
            navi.cprint(navi.t.secondary, f"  │ MFA:         {data.get('mfa_enabled', False)}")
            navi.cprint(navi.t.secondary, f"  │ Flags:       {data.get('public_flags', 0)}")
            navi.cprint(navi.t.highlight, f"  └{'─' * 53}")
        else:
            navi.cprint(navi.t.error, f"  [X] HTTP {resp.status_code} — invalid or expired token.")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] Error: {e}")
    navi.pause()


def server_info(navi):
    navi.clear()
    navi.section_header('📡', 'SERVER INFO')
    navi.cprint(navi.t.dim, "  Fetch Discord server details via bot token.\n")

    if requests is None:
        navi.cprint(navi.t.error, "  [X] 'requests' not installed.")
        navi.pause()
        return

    token = navi.input_choice("  Bot token: ").strip()
    server_id = navi.input_choice("  Server ID: ").strip()
    if not token or not server_id:
        return

    try:
        resp = requests.get(f"https://discord.com/api/v10/guilds/{server_id}", headers=_headers(token), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            navi.cprint(navi.t.highlight + navi.t.B, f"\n  ┌─ SERVER INFO {'─' * 40}")
            navi.cprint(navi.t.secondary, f"  │ Name:        {data.get('name', '?')}")
            navi.cprint(navi.t.secondary, f"  │ ID:          {data.get('id', '?')}")
            navi.cprint(navi.t.secondary, f"  │ Owner ID:    {data.get('owner_id', '?')}")
            navi.cprint(navi.t.secondary, f"  │ Members:     {data.get('approximate_member_count', '?')}")
            navi.cprint(navi.t.secondary, f"  │ Online:      {data.get('approximate_presence_count', '?')}")
            navi.cprint(navi.t.secondary, f"  │ Boosts:      {data.get('premium_subscription_count', 0)}")
            navi.cprint(navi.t.secondary, f"  │ Boost Lvl:   {data.get('premium_tier', 0)}")
            navi.cprint(navi.t.highlight, f"  └{'─' * 53}")
        else:
            navi.cprint(navi.t.error, f"  [X] HTTP {resp.status_code} — check token/permissions.")
    except Exception as e:
        navi.cprint(navi.t.error, f"  [X] Error: {e}")
    navi.pause()


def status_rotator(navi):
    navi.clear()
    navi.section_header('📡', 'STATUS ROTATOR')
    navi.cprint(navi.t.dim, "  Rotate through custom statuses (set one, then loop).\n")
    navi.cprint(navi.t.warning, "  This tool is read-only in educational mode.")
    navi.cprint(navi.t.dim, "  To rotate statuses, use Discord's API directly with your token.")
    navi.cprint(navi.t.dim, "  Endpoint: PATCH https://discord.com/api/v10/users/@me/settings")
    navi.cprint(navi.t.dim, '  Body: {"custom_status": {"text": "your status"}}')
    navi.pause()

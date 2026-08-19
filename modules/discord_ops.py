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


def webhook_info(kevbin):
    kevbin.clear()
    kevbin.section_header('📡', 'WEBHOOK INFO')
    kevbin.cprint(kevbin.t.dim, "  View Discord webhook details (read-only).\n")

    url = kevbin.input_choice("  Webhook URL: ").strip()
    if not url or 'discord' not in url:
        kevbin.cprint(kevbin.t.error, "  [X] Invalid webhook URL.")
        kevbin.pause()
        return

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] 'requests' not installed. pip install requests")
        kevbin.pause()
        return

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            kevbin.cprint(kevbin.t.highlight + kevbin.t.B, f"\n  ┌─ WEBHOOK INFO {'─' * 37}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Name:       {data.get('name', '?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Channel:    {data.get('channel_id', '?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Guild:      {data.get('guild_id', '?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Token:      {data.get('token', '?')[:20]}...")
            avatar = data.get('avatar', '')
            kevbin.cprint(kevbin.t.secondary, f"  │ Avatar:     {'Yes' if avatar else 'None'}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Created:    {data.get('created_at', '?')}")
            kevbin.cprint(kevbin.t.highlight, f"  └{'─' * 53}")
        else:
            kevbin.cprint(kevbin.t.error, f"  [X] HTTP {resp.status_code} — webhook may be deleted.")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] Error: {e}")
    kevbin.pause()


def token_decode(kevbin):
    kevbin.clear()
    kevbin.section_header('📡', 'TOKEN DECODER')
    kevbin.cprint(kevbin.t.dim, "  Decode Discord token structure (educational).\n")

    token = kevbin.input_choice("  Discord token: ").strip()
    if not token:
        return

    parts = token.split('.')
    if len(parts) < 2:
        kevbin.cprint(kevbin.t.error, "  [X] Invalid token format.")
        kevbin.pause()
        return

    kevbin.cprint(kevbin.t.highlight + kevbin.t.B, f"\n  ┌─ TOKEN ANALYSIS {'─' * 36}")
    kevbin.cprint(kevbin.t.secondary, f"  │ Parts:      {len(parts)}")
    kevbin.cprint(kevbin.t.secondary, f"  │ Length:     {len(token)} chars")

    for i, part in enumerate(parts[:3]):
        try:
            decoded = base64.urlsafe_b64decode(part + '==')
            kevbin.cprint(kevbin.t.accent, f"  │ Part {i}: {decoded}")
        except Exception:
            kevbin.cprint(kevbin.t.dim, f"  │ Part {i}: (binary, {len(part)} chars)")

    if len(parts) >= 2:
        try:
            user_id = base64.urlsafe_b64decode(parts[0] + '==').decode()
            kevbin.cprint(kevbin.t.success, f"  │ User ID (approx): {user_id}")
        except Exception:
            pass

    kevbin.cprint(kevbin.t.dim, f"  │ Note: Tokens encode user ID, timestamps, and HMAC.")
    kevbin.cprint(kevbin.t.highlight, f"  └{'─' * 53}")
    kevbin.pause()


def account_info(kevbin):
    kevbin.clear()
    kevbin.section_header('📡', 'ACCOUNT INFO')
    kevbin.cprint(kevbin.t.dim, "  Fetch Discord account info from token (read-only).\n")

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] 'requests' not installed.")
        kevbin.pause()
        return

    token = kevbin.input_choice("  Discord token: ").strip()
    if not token:
        return

    try:
        resp = requests.get("https://discord.com/api/v10/users/@me", headers=_headers(token), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            kevbin.cprint(kevbin.t.highlight + kevbin.t.B, f"\n  ┌─ ACCOUNT INFO {'─' * 38}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Username:    {data.get('username', '?')}#{data.get('discriminator', '0')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Display:     {data.get('global_name', '?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ ID:          {data.get('id', '?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Email:       {data.get('email', 'hidden')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Verified:    {data.get('verified', False)}")
            kevbin.cprint(kevbin.t.secondary, f"  │ MFA:         {data.get('mfa_enabled', False)}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Flags:       {data.get('public_flags', 0)}")
            kevbin.cprint(kevbin.t.highlight, f"  └{'─' * 53}")
        else:
            kevbin.cprint(kevbin.t.error, f"  [X] HTTP {resp.status_code} — invalid or expired token.")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] Error: {e}")
    kevbin.pause()


def server_info(kevbin):
    kevbin.clear()
    kevbin.section_header('📡', 'SERVER INFO')
    kevbin.cprint(kevbin.t.dim, "  Fetch Discord server details via bot token.\n")

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] 'requests' not installed.")
        kevbin.pause()
        return

    token = kevbin.input_choice("  Bot token: ").strip()
    server_id = kevbin.input_choice("  Server ID: ").strip()
    if not token or not server_id:
        return

    try:
        resp = requests.get(f"https://discord.com/api/v10/guilds/{server_id}", headers=_headers(token), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            kevbin.cprint(kevbin.t.highlight + kevbin.t.B, f"\n  ┌─ SERVER INFO {'─' * 40}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Name:        {data.get('name', '?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ ID:          {data.get('id', '?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Owner ID:    {data.get('owner_id', '?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Members:     {data.get('approximate_member_count', '?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Online:      {data.get('approximate_presence_count', '?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Boosts:      {data.get('premium_subscription_count', 0)}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Boost Lvl:   {data.get('premium_tier', 0)}")
            kevbin.cprint(kevbin.t.highlight, f"  └{'─' * 53}")
        else:
            kevbin.cprint(kevbin.t.error, f"  [X] HTTP {resp.status_code} — check token/permissions.")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] Error: {e}")
    kevbin.pause()


def status_rotator(kevbin):
    kevbin.clear()
    kevbin.section_header('📡', 'STATUS ROTATOR')
    kevbin.cprint(kevbin.t.dim, "  Rotate through custom statuses (set one, then loop).\n")
    kevbin.cprint(kevbin.t.warning, "  This tool is read-only in educational mode.")
    kevbin.cprint(kevbin.t.dim, "  To rotate statuses, use Discord's API directly with your token.")
    kevbin.cprint(kevbin.t.dim, "  Endpoint: PATCH https://discord.com/api/v10/users/@me/settings")
    kevbin.cprint(kevbin.t.dim, '  Body: {"custom_status": {"text": "your status"}}')
    kevbin.pause()

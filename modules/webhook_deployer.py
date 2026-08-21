"""Webhook Deployer — Create, test, and manage Discord webhooks."""

import os
import sys
import time
import json
import urllib.request
import urllib.error

try:
    from kevbin import clear, cprint, prompt, pause
except ImportError:
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    def cprint(*a, **kw):
        msg = ' '.join(str(x) for x in a if isinstance(x, str))
        sys.stdout.write(msg + '\n'); sys.stdout.flush()
    def prompt(msg=''):
        if msg: sys.stdout.write(msg); sys.stdout.flush()
        return input()
    def pause():
        prompt('\n  \033[90mPress Enter to continue...\033[0m'); input()

def _req(url, data=None, headers=None, method="GET"):
    h = {"User-Agent": "KevTool", "Content-Type": "application/json"}
    if headers: h.update(headers)
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode()) if resp.read(1) else {}, resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try: return json.loads(body), e.code
        except: return {"error": body[:200]}, e.code

def create_webhook(channel_id, token, name="KevTool"):
    url = f"https://discord.com/api/v10/channels/{channel_id}/webhooks"
    return _req(url, {"name": name}, {"Authorization": f"Bot {token}"}, "POST")

def list_webhooks(channel_id, token):
    url = f"https://discord.com/api/v10/channels/{channel_id}/webhooks"
    return _req(url, headers={"Authorization": f"Bot {token}"})

def delete_webhook(webhook_id, token):
    url = f"https://discord.com/api/v10/webhooks/{webhook_id}"
    return _req(url, headers={"Authorization": f"Bot {token}"}, method="DELETE")

def test_webhook(webhook_url, message="Test from KevTool"):
    return _req(webhook_url, {"content": message})

def send_embed(webhook_url, title, description, color=0x00ff00):
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "footer": {"text": f"KevTool | {time.strftime('%Y-%m-%d %H:%M:%S')}"}
    }
    return _req(webhook_url, {"embeds": [embed]})

def send_file_webhook(webhook_url, filepath, msg=""):
    try:
        boundary = "----WebhookBoundary"
        filename = os.path.basename(filepath)
        with open(filepath, 'rb') as f:
            file_data = f.read()
        body = b""
        if msg:
            body += f"--{boundary}\r\n".encode()
            body += b'Content-Disposition: form-data; name="content"\r\n\r\n'
            body += msg.encode()
            body += b"\r\n"
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
        body += b"Content-Type: application/octet-stream\r\n\r\n"
        body += file_data
        body += f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(webhook_url, data=body,
                                     headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        resp = urllib.request.urlopen(req, timeout=30)
        return {}, resp.status
    except Exception as e:
        return {"error": str(e)}, 0

def get_webhook_info(webhook_url):
    try:
        req = urllib.request.Request(webhook_url, headers={"User-Agent": "KevTool"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        return data, 200
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}"}, e.code
    except Exception as e:
        return {"error": str(e)}, 0

def run(kevbin=None):
    while True:
        clear()
        cprint("  \033[93m\u2554" + "\u2550"*50 + "\u2557")
        cprint("  \033[93m\u2551       WEBHOOK DEPLOYER                    \u2551")
        cprint("  \033[93m\u255a" + "\u2550"*50 + "\u255d")
        print()
        cprint("  \033[97m[1]  Test Webhook\033[0m")
        cprint("  \033[97m[2]  Send Embed\033[0m")
        cprint("  \033[97m[3]  Send File\033[0m")
        cprint("  \033[97m[4]  Get Webhook Info\033[0m")
        cprint("  \033[97m[5]  Create Webhook (needs bot token)\033[0m")
        cprint("  \033[97m[6]  List Webhooks (needs bot token)\033[0m")
        cprint("  \033[97m[7]  Delete Webhook (needs bot token)\033[0m")
        cprint("  \033[97m[8]  Mass Spam Webhook\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0': return
        elif choice == '1':
            clear()
            url = prompt("  \033[96mWebhook URL: \033[0m").strip()
            if not url: continue
            msg = prompt("  \033[96mMessage (default: Test): \033[0m").strip() or "Test from KevTool"
            cprint("  \033[36m[*] Sending test...\033[0m")
            result, code = test_webhook(url, msg)
            if code in (200, 204):
                cprint("  \033[92m[X] Sent successfully\033[0m")
            else:
                cprint(f"  \033[91m[X] Failed: {code} {result}\033[0m")
        elif choice == '2':
            clear()
            url = prompt("  \033[96mWebhook URL: \033[0m").strip()
            if not url: continue
            title = prompt("  \033[96mEmbed title: \033[0m").strip() or "KevTool"
            desc = prompt("  \033[96mEmbed description: \033[0m").strip() or "Hello from KevTool"
            color_hex = prompt("  \033[96mColor hex (default 00ff00): \033[0m").strip() or "00ff00"
            try: color = int(color_hex, 16)
            except: color = 0x00ff00
            cprint("  \033[36m[*] Sending embed...\033[0m")
            result, code = send_embed(url, title, desc, color)
            if code in (200, 204):
                cprint("  \033[92m[X] Embed sent\033[0m")
            else:
                cprint(f"  \033[91m[X] Failed: {code}\033[0m")
        elif choice == '3':
            clear()
            url = prompt("  \033[96mWebhook URL: \033[0m").strip()
            if not url: continue
            path = prompt("  \033[96mFile path: \033[0m").strip().strip('"')
            if not path or not os.path.isfile(path):
                cprint("  \033[91m[X] File not found\033[0m"); pause(); continue
            msg = prompt("  \033[96mCaption (optional): \033[0m").strip()
            cprint(f"  \033[36m[*] Uploading {os.path.basename(path)} ({os.path.getsize(path):,} bytes)...\033[0m")
            result, code = send_file_webhook(url, path, msg)
            if code in (200, 204):
                cprint("  \033[92m[X] File sent\033[0m")
            else:
                cprint(f"  \033[91m[X] Failed: {code} {result}\033[0m")
        elif choice == '4':
            clear()
            url = prompt("  \033[96mWebhook URL: \033[0m").strip()
            if not url: continue
            cprint("  \033[36m[*] Fetching info...\033[0m")
            result, code = get_webhook_info(url)
            if code == 200:
                cprint(f"  \033[97m  Name:     {result.get('name', '?')}\033[0m")
                cprint(f"  \033[97m  Channel:  {result.get('channel_id', '?')}\033[0m")
                cprint(f"  \033[97m  Guild:    {result.get('guild_id', '?')}\033[0m")
                cprint(f"  \033[97m  ID:       {result.get('id', '?')}\033[0m")
                cprint(f"  \033[97m  Token:    {result.get('token', '?')[:20]}...\033[0m")
                avatar = result.get('avatar', '')
                cprint(f"  \033[97m  Avatar:   {avatar or 'none'}\033[0m")
            else:
                cprint(f"  \033[91m[X] Failed: {code} {result}\033[0m")
        elif choice == '5':
            clear()
            token = prompt("  \033[96mBot Token: \033[0m").strip()
            if not token: continue
            channel = prompt("  \033[96mChannel ID: \033[0m").strip()
            if not channel: continue
            name = prompt("  \033[96mWebhook name (default: KevTool): \033[0m").strip() or "KevTool"
            cprint("  \033[36m[*] Creating webhook...\033[0m")
            result, code = create_webhook(channel, token, name)
            if code in (200, 201):
                wh_url = f"https://discord.com/api/webhooks/{result.get('id')}/{result.get('token')}"
                cprint(f"  \033[92m[X] Webhook created\033[0m")
                cprint(f"  \033[97m  URL: {wh_url}\033[0m")
            else:
                cprint(f"  \033[91m[X] Failed: {code} {result}\033[0m")
        elif choice == '6':
            clear()
            token = prompt("  \033[96mBot Token: \033[0m").strip()
            if not token: continue
            channel = prompt("  \033[96mChannel ID: \033[0m").strip()
            if not channel: continue
            cprint("  \033[36m[*] Listing webhooks...\033[0m")
            result, code = list_webhooks(channel, token)
            if code == 200:
                if isinstance(result, list):
                    for wh in result:
                        cprint(f"  \033[97m  {wh.get('name','?'):20} ID: {wh.get('id','?')}\033[0m")
                    cprint(f"\n  \033[90m  Total: {len(result)}\033[0m")
                else:
                    cprint(f"  \033[90m  {result}\033[0m")
            else:
                cprint(f"  \033[91m[X] Failed: {code}\033[0m")
        elif choice == '7':
            clear()
            token = prompt("  \033[96mBot Token: \033[0m").strip()
            if not token: continue
            wh_id = prompt("  \033[96mWebhook ID: \033[0m").strip()
            if not wh_id: continue
            cprint("  \033[36m[*] Deleting...\033[0m")
            result, code = delete_webhook(wh_id, token)
            if code in (200, 204):
                cprint("  \033[92m[X] Deleted\033[0m")
            else:
                cprint(f"  \033[91m[X] Failed: {code}\033[0m")
        elif choice == '8':
            clear()
            url = prompt("  \033[96mWebhook URL: \033[0m").strip()
            if not url: continue
            msg = prompt("  \033[96mMessage: \033[0m").strip() or "Spam from KevTool"
            try:
                count = int(prompt("  \033[96mCount (1-100): \033[0m").strip() or '10')
            except: count = 10
            count = max(1, min(100, count))
            try:
                delay = float(prompt("  \033[96mDelay sec (0.5-10): \033[0m").strip() or '1')
            except: delay = 1
            delay = max(0.5, min(10, delay))
            ok = 0
            for i in range(count):
                result, code = test_webhook(url, msg)
                if code in (200, 204):
                    ok += 1
                    sys.stdout.write(f"\r  \033[92m[{i+1}/{count}]\033[0m Sent OK  ")
                else:
                    sys.stdout.write(f"\r  \033[91m[{i+1}/{count}]\033[0m Failed   ")
                sys.stdout.flush()
                if delay > 0 and i < count - 1:
                    time.sleep(delay)
            cprint(f"\n\n  \033[92m[X] Done: {ok}/{count} sent\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m"); time.sleep(0.5)
        pause()

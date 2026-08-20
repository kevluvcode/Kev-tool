"""JWT Tools — Decode and generate JWT tokens."""

import base64
import json
import hashlib
import hmac
import time


def _b64url_decode(data):
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)


def _b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🛡️', 'JWT TOOLS')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Decode JWT")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Generate JWT (HMAC-SHA256)")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0': return

        if choice == '1':
            token = kevbin.input_choice("  JWT token: ").strip()
            parts = token.split('.')
            if len(parts) < 2:
                kevbin.cprint(kevbin.t.error, "  [X] Invalid JWT format.")
                kevbin.pause()
                continue

            try:
                header = json.loads(_b64url_decode(parts[0]))
                payload = json.loads(_b64url_decode(parts[1]))
                kevbin.cprint(kevbin.t.highlight, "\n  ┌─ HEADER ─────────────────────────")
                for k, v in header.items():
                    kevbin.cprint(kevbin.t.accent, f"  │ {k}: {v}")
                kevbin.cprint(kevbin.t.highlight, "  ├─ PAYLOAD ────────────────────────")
                for k, v in payload.items():
                    val = str(v)[:60]
                    if k == 'exp' and isinstance(v, (int, float)):
                        val += f" ({time.strftime('%Y-%m-%d %H:%M', time.gmtime(v))})"
                    kevbin.cprint(kevbin.t.accent, f"  │ {k}: {val}")
                kevbin.cprint(kevbin.t.highlight, "  └──────────────────────────────────")
                kevbin.cprint(kevbin.t.dim, "  ⚠ Signature NOT verified (read-only decode)")
            except Exception as e:
                kevbin.cprint(kevbin.t.error, f"  [X] Decode error: {e}")
            kevbin.pause()

        elif choice == '2':
            payload_text = kevbin.input_choice("  Payload (JSON or key=value,key=value): ").strip()
            secret = kevbin.input_choice("  Secret key: ").strip()
            if not payload_text or not secret:
                continue

            try:
                if payload_text.startswith('{'):
                    payload = json.loads(payload_text)
                else:
                    payload = {}
                    for item in payload_text.split(','):
                        if '=' in item:
                            k, v = item.split('=', 1)
                            payload[k.strip()] = v.strip()
            except json.JSONDecodeError:
                kevbin.cprint(kevbin.t.error, "  [X] Invalid JSON.")
                kevbin.pause()
                continue

            if 'iat' not in payload:
                payload['iat'] = int(time.time())
            if 'exp' not in payload:
                payload['exp'] = int(time.time()) + 3600

            header = {"alg": "HS256", "typ": "JWT"}
            h = _b64url_encode(json.dumps(header).encode())
            p = _b64url_encode(json.dumps(payload).encode())
            sig = _b64url_encode(hmac.new(secret.encode(), f'{h}.{p}'.encode(), hashlib.sha256).digest())
            token = f'{h}.{p}.{sig}'

            kevbin.cprint(kevbin.t.accent, f"\n  Token:\n  {token}")
            kevbin.pause()

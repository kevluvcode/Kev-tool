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


def run(navi):
    while True:
        navi.clear()
        navi.section_header('🛡️', 'JWT TOOLS')
        navi.cprint(navi.t.secondary, "  [1]  Decode JWT")
        navi.cprint(navi.t.secondary, "  [2]  Generate JWT (HMAC-SHA256)")
        navi.cprint(navi.t.secondary, "  [0]  Back")
        navi.line()
        choice = navi.input_choice()
        if choice == '0': return

        if choice == '1':
            token = navi.input_choice("  JWT token: ").strip()
            parts = token.split('.')
            if len(parts) < 2:
                navi.cprint(navi.t.error, "  [X] Invalid JWT format.")
                navi.pause()
                continue

            try:
                header = json.loads(_b64url_decode(parts[0]))
                payload = json.loads(_b64url_decode(parts[1]))
                navi.cprint(navi.t.highlight + navi.t.B, "\n  ┌─ HEADER ─────────────────────────")
                for k, v in header.items():
                    navi.cprint(navi.t.accent, f"  │ {k}: {v}")
                navi.cprint(navi.t.highlight, "  ├─ PAYLOAD ────────────────────────")
                for k, v in payload.items():
                    val = str(v)[:60]
                    if k == 'exp' and isinstance(v, (int, float)):
                        val += f" ({time.strftime('%Y-%m-%d %H:%M', time.gmtime(v))})"
                    navi.cprint(navi.t.accent, f"  │ {k}: {val}")
                navi.cprint(navi.t.highlight, "  └──────────────────────────────────")
                navi.cprint(navi.t.dim, "  ⚠ Signature NOT verified (read-only decode)")
            except Exception as e:
                navi.cprint(navi.t.error, f"  [X] Decode error: {e}")
            navi.pause()

        elif choice == '2':
            payload_text = navi.input_choice("  Payload (JSON or key=value,key=value): ").strip()
            secret = navi.input_choice("  Secret key: ").strip()
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
                navi.cprint(navi.t.error, "  [X] Invalid JSON.")
                navi.pause()
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

            navi.cprint(navi.t.accent, f"\n  Token:\n  {token}")
            navi.pause()

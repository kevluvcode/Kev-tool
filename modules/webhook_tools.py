"""Webhook Tools - Test and delete webhooks."""

try:
    import requests
except ImportError:
    requests = None


def tester(kevbin):
    kevbin.clear()
    kevbin.section_header('🪝', 'WEBHOOK TESTER')
    kevbin.cprint(kevbin.t.secondary, "  Send a test POST to a webhook URL.")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    url = kevbin.input_choice("  Webhook URL: ").strip()
    if not url:
        return

    content = kevbin.input_choice("  Message (default: test): ").strip() or 'test from KevTool'

    try:
        payload = {'content': content, 'username': 'KevTool'}
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code in (200, 204):
            kevbin.cprint(kevbin.t.success, f"\n  [+] Webhook sent successfully ({r.status_code})")
        else:
            kevbin.cprint(kevbin.t.error, f"\n  [X] Failed: {r.status_code} - {r.text}")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()


def delete(kevbin):
    kevbin.clear()
    kevbin.section_header('🗑️', 'WEBHOOK DELETE')
    kevbin.cprint(kevbin.t.warning, "  Delete a Discord webhook (requires token in URL).")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    url = kevbin.input_choice("  Webhook URL (with token): ").strip()
    if not url:
        return

    confirm = kevbin.input_choice("  Confirm delete? (y/n): ").strip().lower()
    if confirm != 'y':
        return

    try:
        r = requests.delete(url, timeout=10)
        if r.status_code in (200, 204):
            kevbin.cprint(kevbin.t.success, "\n  [+] Webhook deleted")
        else:
            kevbin.cprint(kevbin.t.error, f"\n  [X] Failed: {r.status_code} - {r.text}")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🪝', 'WEBHOOK TOOLS')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Test Webhook")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Delete Webhook")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0': return
        if choice == '1': tester(kevbin)
        elif choice == '2': delete(kevbin)

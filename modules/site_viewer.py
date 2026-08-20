"""Site Viewer - View website source and headers."""

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🔍', 'SITE VIEWER')
    kevbin.cprint(kevbin.t.secondary, "  Enter a URL to view source and headers.")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    url = kevbin.input_choice("  URL: ").strip()
    if not url:
        return

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})

        kevbin.cprint(kevbin.t.highlight, f"\n  +------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Field            | Value                            |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.secondary, f"  | Status           | {r.status_code:<34} |")
        kevbin.cprint(kevbin.t.secondary, f"  | Final URL        | {r.url[:34]:<34} |")
        kevbin.cprint(kevbin.t.secondary, f"  | Encoding         | {r.encoding:<34} |")
        kevbin.cprint(kevbin.t.secondary, f"  | Size             | {len(r.content):<34} |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")

        kevbin.cprint(kevbin.t.accent, "\n  Response Headers:")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Header           | Value                            |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")
        for k, v in sorted(r.headers.items()):
            kevbin.cprint(kevbin.t.secondary, f"  | {k:<16} | {v[:34]:<34} |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")

        kevbin.cprint(kevbin.t.accent, "\n  HTML Source (first 2000 chars):")
        kevbin.cprint(kevbin.t.txt, f"  {r.text[:2000]}")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

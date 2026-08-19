"""WebRTC Leak - Show public IP and explain WebRTC leak concept."""

try:
    import requests
except ImportError:
    requests = None


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🌐', 'WEBRTC LEAK INFO')
    kevbin.cprint(kevbin.t.secondary, "  WebRTC can leak your real IP even behind VPN.")
    kevbin.cprint(kevbin.t.dim, "  This tool shows your public IP via API.")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    try:
        r = requests.get('https://ipinfo.io/json', timeout=5)
        data = r.json()
        ip = data.get('ip', '?')
        city = data.get('city', '?')
        region = data.get('region', '?')
        country = data.get('country', '?')
        org = data.get('org', '?')

        kevbin.cprint(kevbin.t.highlight, f"\n  +------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Property         | Value                            |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.secondary, f"  | Public IP        | {ip:<34} |")
        kevbin.cprint(kevbin.t.secondary, f"  | Location         | {city}, {region}, {country:<24} |")
        kevbin.cprint(kevbin.t.secondary, f"  | ISP/Org          | {org[:34]:<34} |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+----------------------------------+")

        kevbin.cprint(kevbin.t.accent, "\n  WebRTC Leak Explanation:")
        kevbin.cprint(kevbin.t.dim, "  - WebRTC enables P2P connections in browsers")
        kevbin.cprint(kevbin.t.dim, "  - It can bypass VPN/proxy and reveal real IP")
        kevbin.cprint(kevbin.t.dim, "  - Test in browser: https://browserleaks.com/webrtc")
        kevbin.cprint(kevbin.t.dim, "  - Disable in Firefox: media.peerconnection.enabled=false")
        kevbin.cprint(kevbin.t.dim, "  - Chrome: Use extension 'WebRTC Network Limiter'")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

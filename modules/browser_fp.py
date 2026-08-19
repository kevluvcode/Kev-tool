"""Browser Fingerprint - Display system fingerprint info."""

import platform
import sys
import time
import socket


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🖥️', 'BROWSER FINGERPRINT')
    kevbin.cprint(kevbin.t.secondary, "  System fingerprint information:")
    kevbin.line()

    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        hostname = '?'
        local_ip = '?'

    info = [
        ('OS', platform.system()),
        ('OS Version', platform.version()),
        ('OS Release', platform.release()),
        ('Architecture', platform.machine()),
        ('Processor', platform.processor()),
        ('Python Version', sys.version.split()[0]),
        ('Python Implementation', platform.python_implementation()),
        ('Hostname', hostname),
        ('Local IP', local_ip),
        ('Timezone', time.tzname[0]),
        ('UTC Offset', f'{abs(time.timezone)//3600}:00'),
    ]

    kevbin.cprint(kevbin.t.highlight, f"\n  +----------------------+----------------------------------+")
    kevbin.cprint(kevbin.t.highlight, f"  | Property           | Value                            |")
    kevbin.cprint(kevbin.t.highlight, f"  +----------------------+----------------------------------+")
    for k, v in info:
        kevbin.cprint(kevbin.t.secondary, f"  | {k:<20} | {str(v)[:34]:<34} |")
    kevbin.cprint(kevbin.t.highlight, f"  +----------------------+----------------------------------+")

    kevbin.cprint(kevbin.t.dim, "\n  Note: This is CLI fingerprint, not browser JS fingerprint.")
    kevbin.cprint(kevbin.t.dim, "  Browser fingerprint requires JavaScript execution.")
    kevbin.pause()

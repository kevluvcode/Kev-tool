"""Traceroute — Network traceroute to a host."""

import socket
import struct
import time
import os
import sys


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🔍', 'TRACEROUTE')

    host = kevbin.input_choice("  Target host: ").strip()
    if not host:
        return

    try:
        target = socket.gethostbyname(host)
    except socket.gaierror:
        kevbin.cprint(kevbin.t.error, f"  [X] Could not resolve: {host}")
        kevbin.pause()
        return

    kevbin.cprint(kevbin.t.dim, f"  Tracing to {target} ({host})...\n")

    if os.name == 'nt':
        os.system(f'traceroute -d {target}')
    else:
        os.system(f'traceroute {target}')
    kevbin.pause()

"""Traceroute — Network traceroute to a host."""

import socket
import struct
import time
import os
import sys


def run(navi):
    navi.clear()
    navi.section_header('🔍', 'TRACEROUTE')

    host = navi.input_choice("  Target host: ").strip()
    if not host:
        return

    try:
        target = socket.gethostbyname(host)
    except socket.gaierror:
        navi.cprint(navi.t.error, f"  [X] Could not resolve: {host}")
        navi.pause()
        return

    navi.cprint(navi.t.dim, f"  Tracing to {target} ({host})...\n")

    if os.name == 'nt':
        os.system(f'traceroute -d {target}')
    else:
        os.system(f'traceroute {target}')
    navi.pause()

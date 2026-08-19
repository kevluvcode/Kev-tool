"""IP Pinger - ICMP ping using system ping command."""

import subprocess
import platform


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🏓', 'IP PINGER')
    kevbin.cprint(kevbin.t.secondary, "  Enter an IP or hostname to ping.")
    kevbin.cprint(kevbin.t.dim, "  Uses system ping command (ICMP).")
    kevbin.line()

    target = kevbin.input_choice("  Target: ").strip()
    if not target:
        return

    count = kevbin.input_choice("  Count (default 4): ").strip()
    count = int(count) if count.isdigit() else 4

    system = platform.system().lower()
    if system == 'windows':
        cmd = ['ping', '-n', str(count), target]
    else:
        cmd = ['ping', '-c', str(count), target]

    kevbin.cprint(kevbin.t.dim, f"\n  Running: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    kevbin.cprint(kevbin.t.secondary, f"  {line}")
        if result.stderr:
            kevbin.cprint(kevbin.t.error, f"  {result.stderr.strip()}")

        if result.returncode == 0:
            kevbin.cprint(kevbin.t.success, "\n  [+] Ping successful")
        else:
            kevbin.cprint(kevbin.t.error, "\n  [X] Ping failed")
    except subprocess.TimeoutExpired:
        kevbin.cprint(kevbin.t.error, "  [X] Ping timeout")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()

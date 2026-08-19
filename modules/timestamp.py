"""Timestamp — Unix timestamp converter + epoch tools."""

import time
import datetime


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🛡️', 'TIMESTAMP TOOL')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Current Timestamp")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Timestamp -> Human Date")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Human Date -> Timestamp")
        kevbin.cprint(kevbin.t.secondary, "  [4]  Relative Time (ago/until)")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0': return

        if choice == '1':
            now = time.time()
            kevbin.cprint(kevbin.t.accent, f"\n  Unix:     {int(now)}")
            kevbin.cprint(kevbin.t.accent, f"  Decimal:  {now:.6f}")
            kevbin.cprint(kevbin.t.accent, f"  ISO:      {datetime.datetime.utcnow().isoformat()}Z")
            kevbin.cprint(kevbin.t.accent, f"  Human:    {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
            kevbin.pause()

        elif choice == '2':
            ts = kevbin.input_choice("  Timestamp: ").strip()
            try:
                t = float(ts)
                if t > 1e12:
                    t /= 1000
                kevbin.cprint(kevbin.t.accent, f"\n  UTC:   {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t))}")
                kevbin.cprint(kevbin.t.accent, f"  Local: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))}")
                kevbin.cprint(kevbin.t.accent, f"  ISO:   {datetime.datetime.utcfromtimestamp(t).isoformat()}Z")
                diff = t - time.time()
                if diff > 0:
                    kevbin.cprint(kevbin.t.accent, f"  In:    {int(diff//86400)}d {int(diff%86400//3600)}h {int(diff%3600//60)}m")
                else:
                    kevbin.cprint(kevbin.t.accent, f"  Ago:   {int(-diff//86400)}d {int(-diff%86400//3600)}h {int(-diff%3600//60)}m")
            except ValueError:
                kevbin.cprint(kevbin.t.error, "  [X] Invalid timestamp.")
            kevbin.pause()

        elif choice == '3':
            date_str = kevbin.input_choice("  Date (YYYY-MM-DD HH:MM:SS): ").strip()
            try:
                dt = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                ts = dt.timestamp()
                kevbin.cprint(kevbin.t.accent, f"\n  Unix: {int(ts)}")
                kevbin.cprint(kevbin.t.accent, f"  ISO:  {dt.isoformat()}")
            except ValueError:
                kevbin.cprint(kevbin.t.error, "  [X] Invalid format.")
            kevbin.pause()

        elif choice == '4':
            ts = kevbin.input_choice("  Timestamp: ").strip()
            try:
                t = float(ts)
                if t > 1e12: t /= 1000
                diff = time.time() - t
                if diff > 0:
                    days = int(diff // 86400)
                    hours = int(diff % 86400 // 3600)
                    mins = int(diff % 3600 // 60)
                    kevbin.cprint(kevbin.t.accent, f"\n  {days}d {hours}h {mins}m ago")
                else:
                    diff = -diff
                    days = int(diff // 86400)
                    hours = int(diff % 86400 // 3600)
                    mins = int(diff % 3600 // 60)
                    kevbin.cprint(kevbin.t.accent, f"\n  In {days}d {hours}h {mins}m")
            except ValueError:
                kevbin.cprint(kevbin.t.error, "  [X] Invalid timestamp.")
            kevbin.pause()

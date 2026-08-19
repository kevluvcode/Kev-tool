"""Timestamp — Unix timestamp converter + epoch tools."""

import time
import datetime


def run(navi):
    while True:
        navi.clear()
        navi.section_header('🛡️', 'TIMESTAMP TOOL')
        navi.cprint(navi.t.secondary, "  [1]  Current Timestamp")
        navi.cprint(navi.t.secondary, "  [2]  Timestamp -> Human Date")
        navi.cprint(navi.t.secondary, "  [3]  Human Date -> Timestamp")
        navi.cprint(navi.t.secondary, "  [4]  Relative Time (ago/until)")
        navi.cprint(navi.t.secondary, "  [0]  Back")
        navi.line()
        choice = navi.input_choice()
        if choice == '0': return

        if choice == '1':
            now = time.time()
            navi.cprint(navi.t.accent, f"\n  Unix:     {int(now)}")
            navi.cprint(navi.t.accent, f"  Decimal:  {now:.6f}")
            navi.cprint(navi.t.accent, f"  ISO:      {datetime.datetime.utcnow().isoformat()}Z")
            navi.cprint(navi.t.accent, f"  Human:    {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
            navi.pause()

        elif choice == '2':
            ts = navi.input_choice("  Timestamp: ").strip()
            try:
                t = float(ts)
                if t > 1e12:
                    t /= 1000
                navi.cprint(navi.t.accent, f"\n  UTC:   {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t))}")
                navi.cprint(navi.t.accent, f"  Local: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))}")
                navi.cprint(navi.t.accent, f"  ISO:   {datetime.datetime.utcfromtimestamp(t).isoformat()}Z")
                diff = t - time.time()
                if diff > 0:
                    navi.cprint(navi.t.accent, f"  In:    {int(diff//86400)}d {int(diff%86400//3600)}h {int(diff%3600//60)}m")
                else:
                    navi.cprint(navi.t.accent, f"  Ago:   {int(-diff//86400)}d {int(-diff%86400//3600)}h {int(-diff%3600//60)}m")
            except ValueError:
                navi.cprint(navi.t.error, "  [X] Invalid timestamp.")
            navi.pause()

        elif choice == '3':
            date_str = navi.input_choice("  Date (YYYY-MM-DD HH:MM:SS): ").strip()
            try:
                dt = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                ts = dt.timestamp()
                navi.cprint(navi.t.accent, f"\n  Unix: {int(ts)}")
                navi.cprint(navi.t.accent, f"  ISO:  {dt.isoformat()}")
            except ValueError:
                navi.cprint(navi.t.error, "  [X] Invalid format.")
            navi.pause()

        elif choice == '4':
            ts = navi.input_choice("  Timestamp: ").strip()
            try:
                t = float(ts)
                if t > 1e12: t /= 1000
                diff = time.time() - t
                if diff > 0:
                    days = int(diff // 86400)
                    hours = int(diff % 86400 // 3600)
                    mins = int(diff % 3600 // 60)
                    navi.cprint(navi.t.accent, f"\n  {days}d {hours}h {mins}m ago")
                else:
                    diff = -diff
                    days = int(diff // 86400)
                    hours = int(diff % 86400 // 3600)
                    mins = int(diff % 3600 // 60)
                    navi.cprint(navi.t.accent, f"\n  In {days}d {hours}h {mins}m")
            except ValueError:
                navi.cprint(navi.t.error, "  [X] Invalid timestamp.")
            navi.pause()

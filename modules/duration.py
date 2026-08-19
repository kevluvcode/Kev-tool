import re
from datetime import timedelta


UNITS = {
    's': ('seconds', 1),
    'sec': ('seconds', 1),
    'second': ('seconds', 1),
    'seconds': ('seconds', 1),
    'm': ('minutes', 60),
    'min': ('minutes', 60),
    'minute': ('minutes', 60),
    'minutes': ('minutes', 60),
    'h': ('hours', 3600),
    'hr': ('hours', 3600),
    'hour': ('hours', 3600),
    'hours': ('hours', 3600),
    'd': ('days', 86400),
    'day': ('days', 86400),
    'days': ('days', 86400),
    'w': ('weeks', 604800),
    'wk': ('weeks', 604800),
    'week': ('weeks', 604800),
    'weeks': ('weeks', 604800),
}


def _parse_duration(text: str) -> int:
    text = text.strip().lower()
    
    if ':' in text:
        parts = text.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 3600 + int(parts[1]) * 60
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    
    pattern = r'(\d+(?:\.\d+)?)\s*([a-z]+)'
    matches = re.findall(pattern, text)
    
    if not matches:
        try:
            return int(float(text))
        except:
            raise ValueError(f"Cannot parse duration: {text}")
    
    total_seconds = 0
    for value_str, unit in matches:
        value = float(value_str)
        unit = unit.rstrip('s')
        if unit in UNITS:
            _, multiplier = UNITS[unit]
            total_seconds += value * multiplier
        else:
            raise ValueError(f"Unknown unit: {unit}")
    
    return int(total_seconds)


def _format_duration(seconds: int, style: str = 'full') -> str:
    if seconds < 0:
        return "-" + _format_duration(-seconds, style)
    
    weeks = seconds // 604800
    seconds %= 604800
    days = seconds // 86400
    seconds %= 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    
    parts = []
    if weeks:
        parts.append(f"{weeks}w")
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    
    if style == 'short':
        return " ".join(parts)
    elif style == 'colon':
        if weeks or days:
            return f"{weeks*7 + days}d {hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    elif style == 'verbose':
        verbose_parts = []
        if weeks:
            verbose_parts.append(f"{weeks} week{'s' if weeks != 1 else ''}")
        if days:
            verbose_parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            verbose_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes:
            verbose_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds or not verbose_parts:
            verbose_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        return ", ".join(verbose_parts)
    
    return " ".join(parts)


def run(kevbin):
    kevbin.box_title("Duration Calculator")
    kevbin.box_print("Add/subtract time durations, convert between units")
    kevbin.box_print("Formats: 1h30m, 90m, 5400s, 1:30:00, 1.5h, etc.")
    
    while True:
        kevbin.box_print("")
        kevbin.box_print("Modes:")
        kevbin.box_print("  1. Add durations")
        kevbin.box_print("  2. Subtract durations")
        kevbin.box_print("  3. Convert duration to all units")
        kevbin.box_print("  4. Time between two timestamps")
        
        mode = kevbin.box_input("Select mode [1]: ").strip() or "1"
        if mode.lower() in ('q', 'quit', 'exit'):
            break
        
        try:
            if mode == "1":
                kevbin.box_print("Enter durations to add (empty line to finish):")
                durations = []
                while True:
                    d = kevbin.box_input(f"  Duration {len(durations)+1}: ").strip()
                    if not d:
                        break
                    durations.append(_parse_duration(d))
                
                if not durations:
                    continue
                
                total = sum(durations)
                
                rows = [["#", "Input", "Seconds"]]
                for i, d in enumerate(durations, 1):
                    rows.append([str(i), _format_duration(d, 'verbose'), str(d)])
                rows.append(["", "TOTAL", str(total)])
                rows.append(["", _format_duration(total, 'verbose'), _format_duration(total, 'short')])
                
                kevbin.box_table(rows, title="Addition Result")
                
            elif mode == "2":
                d1 = kevbin.box_input("From duration: ").strip()
                d2 = kevbin.box_input("Subtract duration: ").strip()
                
                sec1 = _parse_duration(d1)
                sec2 = _parse_duration(d2)
                result = sec1 - sec2
                
                rows = [
                    ["Operation", "Duration", "Seconds"],
                    ["From", _format_duration(sec1, 'verbose'), str(sec1)],
                    ["Subtract", _format_duration(sec2, 'verbose'), str(sec2)],
                    ["Result", _format_duration(result, 'verbose'), str(result)],
                ]
                kevbin.box_table(rows, title="Subtraction Result")
                
            elif mode == "3":
                d = kevbin.box_input("Duration to convert: ").strip()
                if not d:
                    continue
                
                seconds = _parse_duration(d)
                
                rows = [
                    ["Format", "Value"],
                    ["Verbose", _format_duration(seconds, 'verbose')],
                    ["Short", _format_duration(seconds, 'short')],
                    ["Colon (HH:MM:SS)", _format_duration(seconds, 'colon')],
                    ["Total seconds", str(seconds)],
                    ["Total minutes", f"{seconds/60:.2f}"],
                    ["Total hours", f"{seconds/3600:.4f}"],
                    ["Total days", f"{seconds/86400:.4f}"],
                    ["Total weeks", f"{seconds/604800:.4f}"],
                ]
                kevbin.box_table(rows, title="Duration Conversion")
                
            elif mode == "4":
                kevbin.box_print("Enter timestamps (YYYY-MM-DD HH:MM:SS or HH:MM:SS):")
                t1 = kevbin.box_input("Start: ").strip()
                t2 = kevbin.box_input("End: ").strip()
                
                def parse_ts(ts):
                    ts = ts.strip()
                    if ' ' in ts:
                        date_part, time_part = ts.split(' ', 1)
                    else:
                        date_part = None
                        time_part = ts
                    
                    h, m, s = 0, 0, 0
                    parts = time_part.split(':')
                    h = int(parts[0])
                    if len(parts) > 1:
                        m = int(parts[1])
                    if len(parts) > 2:
                        s = int(parts[2])
                    
                    total = h * 3600 + m * 60 + s
                    if date_part:
                        y, mo, d = map(int, date_part.split('-'))
                        from datetime import datetime
                        dt = datetime(y, mo, d, h, m, s)
                        return int(dt.timestamp())
                    return total
                
                ts1 = parse_ts(t1)
                ts2 = parse_ts(t2)
                diff = abs(ts2 - ts1)
                
                rows = [
                    ["Timestamp", "Value"],
                    ["Start", t1],
                    ["End", t2],
                    ["Difference", _format_duration(diff, 'verbose')],
                    ["", _format_duration(diff, 'short')],
                    ["Total seconds", str(diff)],
                ]
                kevbin.box_table(rows, title="Time Difference")
                
            else:
                kevbin.box_print("[red]Invalid mode[/red]")
                
        except ValueError as e:
            kevbin.box_print(f"[red]{e}[/red]")
        except Exception as e:
            kevbin.box_print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    class MockKevbin:
        def box_title(self, t): print(f"\n=== {t} ===")
        def box_print(self, t): print(t)
        def box_input(self, t): return input(t + " ")
        def box_table(self, rows, title=""):
            if title: print(f"\n{title}")
            for row in rows:
                print(" | ".join(str(c) for c in row))
        def box_code(self, code, language=""): print(code)
    
    run(MockKevbin())
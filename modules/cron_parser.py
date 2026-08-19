import datetime

def _parse_field(field, min_v, max_v):
    if field == "*":
        return list(range(min_v, max_v + 1))
    
    result = set()
    for part in field.split(','):
        part = part.strip()
        if '/' in part:
            base, step = part.split('/')
            step = int(step)
            if base == "*":
                base_min, base_max = min_v, max_v
            elif '-' in base:
                base_min, base_max = map(int, base.split('-'))
            else:
                base_min = base_max = int(base)
            for v in range(base_min, base_max + 1, step):
                if min_v <= v <= max_v:
                    result.add(v)
        elif '-' in part:
            start, end = map(int, part.split('-'))
            for v in range(start, end + 1):
                if min_v <= v <= max_v:
                    result.add(v)
        else:
            v = int(part)
            if min_v <= v <= max_v:
                result.add(v)
    return sorted(result)

def _matches(cron_parts, dt):
    minute, hour, day, month, weekday = cron_parts
    if dt.minute not in minute: return False
    if dt.hour not in hour: return False
    if dt.day not in day: return False
    if dt.month not in month: return False
    if dt.weekday() not in weekday and (dt.weekday() + 1) % 7 not in weekday: return False
    return True

def run(kevbin):
    kevbin.box.title("Cron Parser")
    cron = kevbin.box.input("Enter cron expression: ")
    if not cron:
        return
    
    parts = cron.strip().split()
    if len(parts) != 5:
        kevbin.box.error("Invalid cron format (need 5 fields)")
        return
    
    try:
        minute = _parse_field(parts[0], 0, 59)
        hour = _parse_field(parts[1], 0, 23)
        day = _parse_field(parts[2], 1, 31)
        month = _parse_field(parts[3], 1, 12)
        weekday = _parse_field(parts[4], 0, 6)
    except Exception as e:
        kevbin.box.error(f"Parse error: {e}")
        return
    
    cron_parts = (minute, hour, day, month, weekday)
    now = datetime.datetime.now()
    
    kevbin.box.table(
        ["Field", "Values"],
        [["Minute", ", ".join(map(str, minute))],
         ["Hour", ", ".join(map(str, hour))],
         ["Day", ", ".join(map(str, day))],
         ["Month", ", ".join(map(str, month))],
         ["Weekday", ", ".join(map(str, weekday))]]
    )
    
    kevbin.box.title("Next 5 Execution Times")
    results = []
    check = now
    count = 0
    while count < 5 and count < 10000:
        check += datetime.timedelta(minutes=1)
        if _matches(cron_parts, check):
            results.append([str(count + 1), check.strftime("%Y-%m-%d %H:%M:%S")])
            count += 1
    
    kevbin.box.table(["#", "Execution Time"], results)
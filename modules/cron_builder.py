def run(kevbin):
    kevbin.box.title("Cron Expression Builder")
    kevbin.box.info("Enter values for each field (leave blank for *)")
    
    minute = kevbin.box.input("Minute (0-59): ")
    hour = kevbin.box.input("Hour (0-23): ")
    day = kevbin.box.input("Day of month (1-31): ")
    month = kevbin.box.input("Month (1-12): ")
    weekday = kevbin.box.input("Day of week (0-7) (Sun=0 or 7): ")
    
    def validate(field, value, min_v, max_v, name):
        if not value:
            return "*"
        parts = value.split(',')
        for p in parts:
            if '/' in p:
                p = p.split('/')[0]
            if '-' in p:
                start, end = p.split('-')
                try:
                    s, e = int(start), int(end)
                    if s < min_v or e > max_v or s > e:
                        raise ValueError
                except:
                    kevbin.box.error(f"Invalid {name} range: {p}")
                    return None
            else:
                try:
                    v = int(p)
                    if v < min_v or v > max_v:
                        raise ValueError
                except:
                    kevbin.box.error(f"Invalid {name} value: {p}")
                    return None
        return value
    
    minute = validate("minute", minute, 0, 59, "minute")
    hour = validate("hour", hour, 0, 23, "hour")
    day = validate("day", day, 1, 31, "day")
    month = validate("month", month, 1, 12, "month")
    weekday = validate("weekday", weekday, 0, 7, "weekday")
    
    if None in [minute, hour, day, month, weekday]:
        return
    
    cron = f"{minute} {hour} {day} {month} {weekday}"
    kevbin.box.success(f"Cron expression: {cron}")
    
    desc = []
    if minute != "*": desc.append(f"minute {minute}")
    if hour != "*": desc.append(f"hour {hour}")
    if day != "*": desc.append(f"day {day}")
    if month != "*": desc.append(f"month {month}")
    if weekday != "*": desc.append(f"weekday {weekday}")
    
    if desc:
        kevbin.box.info("Runs " + ", ".join(desc))
    else:
        kevbin.box.info("Runs every minute")
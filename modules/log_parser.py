"""Log Parser — Analyze and parse log files."""

import os
import re
from collections import Counter, defaultdict


def _parse_apache_log(line):
    pat = r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) [^"]*" (\d{3}) (\d+|-)'
    m = re.match(pat, line)
    if m:
        return {
            'ip': m.group(1), 'time': m.group(2), 'method': m.group(3),
            'path': m.group(4), 'status': int(m.group(5)),
            'size': int(m.group(6)) if m.group(6) != '-' else 0
        }
    return None


def _parse_generic_log(line):
    ts_pat = r'(\d{4}[-/]\d{2}[-/]\d{2}[T ]\d{2}:\d{2}:\d{2})'
    m = re.search(ts_pat, line)
    timestamp = m.group(1) if m else ''

    level = ''
    for l in ['ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'CRITICAL', 'FATAL']:
        if l in line.upper():
            level = l
            break

    ip_pat = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    ip_m = re.search(ip_pat, line)
    ip = ip_m.group(1) if ip_m else ''

    return {'time': timestamp, 'level': level, 'ip': ip, 'raw': line.strip()}


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('📋', 'LOG PARSER')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Analyze log file")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Filter by level/IP")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Top offenders (IPs)")
        kevbin.cprint(kevbin.t.secondary, "  [4]  Status code breakdown")
        kevbin.cprint(kevbin.t.secondary, "  [5]  Search pattern")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0':
            return

        filepath = kevbin.input_choice("  Log file path: ").strip().strip('"').strip("'")
        if not filepath or not os.path.isfile(filepath):
            kevbin.cprint(kevbin.t.error, "  [X] File not found.")
            kevbin.pause()
            continue

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()
            continue

        kevbin.cprint(kevbin.t.dim, f"  Loaded {len(lines):,} lines\n")

        if choice == '1':
            _analyze(kevbin, lines)
        elif choice == '2':
            _filter(kevbin, lines)
        elif choice == '3':
            _top_offenders(kevbin, lines)
        elif choice == '4':
            _status_breakdown(kevbin, lines)
        elif choice == '5':
            _search(kevbin, lines)

        kevbin.pause()


def _analyze(kevbin, lines):
    parsed = [_parse_apache_log(l) for l in lines]
    generic = [_parse_generic_log(l) for l in lines]

    apache_count = sum(1 for p in parsed if p)
    generic_count = sum(1 for g in generic if g['level'])

    kevbin.cprint(kevbin.t.accent, "  Log Analysis:\n")

    if apache_count > 0:
        statuses = Counter(p['status'] for p in parsed if p)
        methods = Counter(p['method'] for p in parsed if p)
        ips = Counter(p['ip'] for p in parsed if p)
        paths = Counter(p['path'] for p in parsed if p)

        kevbin.cprint(kevbin.t.accent, "  Apache/Nginx format detected:")
        rows = [
            ("Total requests", f"{apache_count:,}"),
            ("Unique IPs", str(len(ips))),
            ("Unique paths", str(len(paths))),
            ("Top IP", ips.most_common(1)[0] if ips else '-'),
            ("Top status", statuses.most_common(1)[0] if statuses else '-'),
        ]
        kevbin.box_table(rows, title="Summary")

        kevbin.cprint(kevbin.t.accent, "\n  Top 10 IPs:")
        for ip, count in ips.most_common(10):
            bar = '█' * min(30, count // max(1, apache_count // 30))
            kevbin.cprint(kevbin.t.txt, f"    {ip:<16} {count:>6}  {bar}")

    if generic_count > 0:
        levels = Counter(g['level'] for g in generic if g['level'])
        kevbin.cprint(kevbin.t.accent, "\n  Log levels:")
        for level, count in levels.most_common():
            bar = '█' * min(30, count // max(1, generic_count // 30))
            kevbin.cprint(kevbin.t.txt, f"    {level:<12} {count:>6}  {bar}")


def _filter(kevbin, lines):
    level_filter = kevbin.input_choice("  Filter by level (ERROR/WARN/INFO/DEBUG, empty=all): ").strip().upper()
    ip_filter = kevbin.input_choice("  Filter by IP (empty=all): ").strip()

    filtered = []
    for line in lines:
        if level_filter and level_filter not in line.upper():
            continue
        if ip_filter and ip_filter not in line:
            continue
        filtered.append(line.strip())

    kevbin.cprint(kevbin.t.accent, f"\n  {len(filtered)} matching lines (out of {len(lines):,}):\n")
    for line in filtered[:50]:
        kevbin.cprint(kevbin.t.txt, f"    {line[:100]}")
    if len(filtered) > 50:
        kevbin.cprint(kevbin.t.dim, f"    ... +{len(filtered) - 50} more")


def _top_offenders(kevbin, lines):
    ip_pat = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    ips = Counter()
    for line in lines:
        m = ip_pat.search(line)
        if m:
            ips[m.group(1)] += 1

    top = ips.most_common(20)
    if not top:
        kevbin.cprint(kevbin.t.warning, "  [!] No IPs found.")
        return

    kevbin.cprint(kevbin.t.accent, "  Top Offending IPs:\n")
    max_count = top[0][1] if top else 1
    for ip, count in top:
        bar_len = int(30 * count / max_count) if max_count else 0
        bar = '█' * bar_len
        kevbin.cprint(kevbin.t.txt, f"    {ip:<16} {count:>6}  {bar}")

    save = kevbin.input_choice("\n  Save IP list? (y/n): ").strip().lower()
    if save == 'y':
        out = kevbin.input_choice("  Path [ips.txt]: ").strip() or 'ips.txt'
        try:
            with open(out, 'w') as f:
                for ip, count in top:
                    f.write(f"{ip}\t{count}\n")
            kevbin.cprint(kevbin.t.success, f"  [✓] Saved to {out}")
        except Exception as e:
            kevbin.cprint(kevbin.t.error, f"  [X] {e}")


def _status_breakdown(kevbin, lines):
    statuses = Counter()
    for line in lines:
        m = re.search(r'" (\d{3}) ', line)
        if m:
            statuses[m.group(1)] += 1
    if not statuses:
        m2 = re.findall(r'(\d{3})', line)
        for code in m2:
            if len(code) == 3 and code[0] in '12345':
                statuses[code] += 1

    if not statuses:
        kevbin.cprint(kevbin.t.warning, "  [!] No HTTP status codes found.")
        return

    kevbin.cprint(kevbin.t.accent, "  HTTP Status Code Breakdown:\n")
    total = sum(statuses.values())
    for code, count in sorted(statuses.items()):
        pct = count / total * 100 if total else 0
        bar = '█' * min(30, int(pct / 3.3))
        color = kevbin.t.success if code.startswith('2') else kevbin.t.warning if code.startswith('3') else kevbin.t.error
        kevbin.cprint(color, f"    {code}  {count:>6}  ({pct:5.1f}%)  {bar}")


def _search(kevbin, lines):
    pattern = kevbin.input_choice("  Search pattern (regex): ").strip()
    if not pattern:
        return
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        kevbin.cprint(kevbin.t.error, f"  [X] Invalid regex: {e}")
        return

    matches = [(i, line) for i, line in enumerate(lines, 1) if compiled.search(line)]
    kevbin.cprint(kevbin.t.accent, f"\n  {len(matches)} matches:\n")
    for lineno, line in matches[:40]:
        kevbin.cprint(kevbin.t.txt, f"    L{lineno:<6}{line.strip()[:90]}")
    if len(matches) > 40:
        kevbin.cprint(kevbin.t.dim, f"    ... +{len(matches) - 40} more")

"""Regex Tester — Test regular expressions in real-time."""

import re


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🛡️', 'REGEX TESTER')

    pattern = kevbin.input_choice("  Regex pattern: ").strip()
    if not pattern:
        return

    flags_str = kevbin.input_choice("  Flags (i=ignorecase, m=multiline, s=dotall): ").strip()
    flags = 0
    if 'i' in flags_str: flags |= re.IGNORECASE
    if 'm' in flags_str: flags |= re.MULTILINE
    if 's' in flags_str: flags |= re.DOTALL

    try:
        compiled = re.compile(pattern, flags)
    except re.error as e:
        kevbin.cprint(kevbin.t.error, f"  [X] Invalid regex: {e}")
        kevbin.pause()
        return

    kevbin.cprint(kevbin.t.success, "  [✓] Valid regex")
    kevbin.cprint(kevbin.t.dim, "  Enter text to test (empty line to finish):\n")

    lines = []
    while True:
        line = kevbin.input_choice("  ")
        if line == '':
            break
        lines.append(line)

    text = '\n'.join(lines)
    if not text:
        kevbin.pause()
        return

    matches = compiled.findall(text)
    kevbin.cprint(kevbin.t.accent, f"\n  Matches: {len(matches)}")
    for i, m in enumerate(matches[:20], 1):
        if isinstance(m, tuple):
            kevbin.cprint(kevbin.t.secondary, f"  {i}. {m}")
        else:
            kevbin.cprint(kevbin.t.secondary, f"  {i}. {m}")

    spans = list(compiled.finditer(text))
    if spans:
        kevbin.cprint(kevbin.t.dim, "\n  Positions:")
        for s in spans[:10]:
            kevbin.cprint(kevbin.t.dim, f"    {s.start()}-{s.end()}: '{s.group()}'")
    kevbin.pause()

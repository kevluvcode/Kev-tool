"""Regex Tester — Test regular expressions in real-time."""

import re


def run(navi):
    navi.clear()
    navi.section_header('🛡️', 'REGEX TESTER')

    pattern = navi.input_choice("  Regex pattern: ").strip()
    if not pattern:
        return

    flags_str = navi.input_choice("  Flags (i=ignorecase, m=multiline, s=dotall): ").strip()
    flags = 0
    if 'i' in flags_str: flags |= re.IGNORECASE
    if 'm' in flags_str: flags |= re.MULTILINE
    if 's' in flags_str: flags |= re.DOTALL

    try:
        compiled = re.compile(pattern, flags)
    except re.error as e:
        navi.cprint(navi.t.error, f"  [X] Invalid regex: {e}")
        navi.pause()
        return

    navi.cprint(navi.t.success, "  [✓] Valid regex")
    navi.cprint(navi.t.dim, "  Enter text to test (empty line to finish):\n")

    lines = []
    while True:
        line = navi.input_choice("  ")
        if line == '':
            break
        lines.append(line)

    text = '\n'.join(lines)
    if not text:
        navi.pause()
        return

    matches = compiled.findall(text)
    navi.cprint(navi.t.accent, f"\n  Matches: {len(matches)}")
    for i, m in enumerate(matches[:20], 1):
        if isinstance(m, tuple):
            navi.cprint(navi.t.secondary, f"  {i}. {m}")
        else:
            navi.cprint(navi.t.secondary, f"  {i}. {m}")

    spans = list(compiled.finditer(text))
    if spans:
        navi.cprint(navi.t.dim, "\n  Positions:")
        for s in spans[:10]:
            navi.cprint(navi.t.dim, f"    {s.start()}-{s.end()}: '{s.group()}'")
    navi.pause()

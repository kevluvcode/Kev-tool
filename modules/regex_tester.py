"""Regex Tester — Test, replace, group capture, cheat sheet."""

import re


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🛡️', 'REGEX TESTER')

    pattern = kevbin.input_choice("  Regex pattern: ").strip()
    if not pattern:
        return

    flags_str = kevbin.input_choice("  Flags (i=ignorecase m=multiline s=dotall): ").strip()
    flags = 0
    if 'i' in flags_str:
        flags |= re.IGNORECASE
    if 'm' in flags_str:
        flags |= re.MULTILINE
    if 's' in flags_str:
        flags |= re.DOTALL

    try:
        compiled = re.compile(pattern, flags)
    except re.error as e:
        kevbin.cprint(kevbin.t.error, f"  [X] Invalid regex: {e}")
        kevbin.pause()
        return

    kevbin.cprint(kevbin.t.success, "  [+] Valid regex\n")
    kevbin.cprint(kevbin.t.dim, "  Enter text (empty line to finish):\n")

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
    iter_matches = list(compiled.finditer(text))

    kevbin.cprint(kevbin.t.accent, f"\n  Matches: {len(matches)}")
    if iter_matches:
        kevbin.cprint(kevbin.t.dim, "  Full matches:")
        for i, m in enumerate(iter_matches[:20], 1):
            kevbin.cprint(kevbin.t.txt, f"    {i}. [{m.start()}:{m.end()}] '{m.group()}'")
            if m.groups():
                for gi, g in enumerate(m.groups(), 1):
                    kevbin.cprint(kevbin.t.dim, f"       Group {gi}: '{g}'")

    replace_mode = kevbin.input_choice("\n  Replace mode? (y/n): ").strip().lower()
    if replace_mode == 'y':
        repl = kevbin.input_choice("  Replacement string: ")
        result, count = compiled.subn(repl, text)
        kevbin.cprint(kevbin.t.accent, f"\n  Replaced {count} occurrence(s):")
        kevbin.box_code(result[:500])

        save = kevbin.input_choice("\n  Save result? (y/n): ").strip().lower()
        if save == 'y':
            path = kevbin.input_choice("  Path: ").strip().strip('"')
            if path:
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(result)
                    kevbin.cprint(kevbin.t.success, f"  [+] Saved to {path}")
                except Exception as e:
                    kevbin.cprint(kevbin.t.error, f"  [X] {e}")

    if iter_matches:
        show_spans = kevbin.input_choice("\n  Show positions? (y/n): ").strip().lower()
        if show_spans == 'y':
            kevbin.cprint(kevbin.t.dim, "\n  Positions in text:")
            highlighted = text
            offset = 0
            for m in iter_matches[:10]:
                start = m.start() + offset
                end = m.end() + offset
                kevbin.cprint(kevbin.t.dim, f"    {m.start()}-{m.end()}: '{m.group()[:50]}'")

    kevbin.pause()

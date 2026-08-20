"""Batch Renamer — Batch file renaming utility with preview."""

import os
import re
import glob


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('📁', 'BATCH RENAMER')

    directory = kevbin.input_choice("  Directory (empty = current): ").strip() or '.'
    if not os.path.isdir(directory):
        kevbin.cprint(kevbin.t.error, "  [X] Not a directory.")
        kevbin.pause()
        return

    pattern = kevbin.input_choice("  File pattern [*.*]: ").strip() or '*.*'
    files = sorted(glob.glob(os.path.join(directory, pattern)))

    if not files:
        kevbin.cprint(kevbin.t.warning, "  [!] No files match.")
        kevbin.pause()
        return

    kevbin.cprint(kevbin.t.dim, f"  {len(files)} files found.\n")
    kevbin.cprint(kevbin.t.secondary, "  [1] Find & replace in names")
    kevbin.cprint(kevbin.t.secondary, "  [2] Add prefix")
    kevbin.cprint(kevbin.t.secondary, "  [3] Add suffix (before extension)")
    kevbin.cprint(kevbin.t.secondary, "  [4] Number sequentially")
    kevbin.cprint(kevbin.t.secondary, "  [5] Lowercase all names")
    kevbin.cprint(kevbin.t.secondary, "  [6] Uppercase all names")
    kevbin.cprint(kevbin.t.secondary, "  [7] Remove pattern")
    kevbin.cprint(kevbin.t.secondary, "  [8] Regex rename")
    kevbin.line()

    mode = kevbin.input_choice("  Mode: ").strip()

    renames = []
    for filepath in files:
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)
        new_name = basename

        if mode == '1':
            find = kevbin.input_choice("  Find: ").strip()
            replace = kevbin.input_choice("  Replace with: ").strip()
            new_name = basename.replace(find, replace)

        elif mode == '2':
            if len(renames) == 0:
                prefix = kevbin.input_choice("  Prefix: ").strip()
            new_name = prefix + basename

        elif mode == '3':
            if len(renames) == 0:
                suffix = kevbin.input_choice("  Suffix: ").strip()
            new_name = name + suffix + ext

        elif mode == '4':
            if len(renames) == 0:
                start = kevbin.input_choice("  Start number [1]: ").strip() or '1'
                try:
                    start = int(start)
                except ValueError:
                    start = 1
                pad = kevbin.input_choice("  Zero-pad width [3]: ").strip() or '3'
                try:
                    pad = int(pad)
                except ValueError:
                    pad = 3
                sep = kevbin.input_choice("  Separator [ - ]: ").strip() or ' - '
            idx = start + len(renames)
            new_name = f"{str(idx).zfill(pad)}{sep}{basename}"

        elif mode == '5':
            new_name = basename.lower()

        elif mode == '6':
            new_name = basename.upper()

        elif mode == '7':
            if len(renames) == 0:
                remove = kevbin.input_choice("  Pattern to remove: ").strip()
            new_name = basename.replace(remove, '')

        elif mode == '8':
            if len(renames) == 0:
                regex_pat = kevbin.input_choice("  Regex pattern: ").strip()
                regex_rep = kevbin.input_choice("  Replacement: ").strip()
            try:
                new_name = re.sub(regex_pat, regex_rep, basename)
            except re.error:
                kevbin.cprint(kevbin.t.error, "  [X] Invalid regex.")
                kevbin.pause()
                return

        if new_name and new_name != basename:
            new_path = os.path.join(dirname, new_name)
            renames.append((filepath, new_path, basename, new_name))

    if not renames:
        kevbin.cprint(kevbin.t.warning, "\n  [!] No changes to make.")
        kevbin.pause()
        return

    kevbin.cprint(kevbin.t.accent, f"\n  Preview ({len(renames)} renames):\n")
    max_show = min(30, len(renames))
    for old, new, old_name, new_name in renames[:max_show]:
        kevbin.cprint(kevbin.t.txt, f"    {old_name[:40]:<42} -> {new_name[:40]}")
    if len(renames) > max_show:
        kevbin.cprint(kevbin.t.dim, f"    ... +{len(renames) - max_show} more")

    confirm = kevbin.input_choice("\n  Apply renames? (y/n): ").strip().lower()
    if confirm != 'y':
        kevbin.cprint(kevbin.t.warning, "  Cancelled.")
        kevbin.pause()
        return

    success = 0
    for old_path, new_path, old_name, new_name in renames:
        try:
            if os.path.exists(new_path):
                kevbin.cprint(kevbin.t.warning, f"  [!] Skipped (exists): {new_name}")
                continue
            os.rename(old_path, new_path)
            success += 1
        except Exception as e:
            kevbin.cprint(kevbin.t.error, f"  [X] {old_name}: {e}")

    kevbin.cprint(kevbin.t.success, f"\n  [✓] Renamed {success}/{len(renames)} files.")
    kevbin.pause()

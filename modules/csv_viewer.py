import csv
import io
import os

def run(kevbin):
    kevbin.clear()
    kevbin.section_header("📊", "CSV Viewer")
    
    kevbin.cprint(kevbin.t.primary, "  1. Paste CSV text")
    kevbin.cprint(kevbin.t.primary, "  2. Load from file")
    kevbin.line()
    choice = kevbin.input_choice("Select input method")
    
    csv_text = ""
    if choice == "1":
        kevbin.cprint(kevbin.t.dim, "Enter CSV (empty line to finish):")
        lines = []
        while True:
            line = kevbin.input_choice("> ")
            if line == "":
                break
            lines.append(line)
        csv_text = "\n".join(lines)
    elif choice == "2":
        path = kevbin.input_choice("File path")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                csv_text = f.read()
        except Exception as e:
            kevbin.cprint(kevbin.t.error, f"Error reading file: {e}")
            kevbin.pause()
            return
    else:
        return
    
    if not csv_text.strip():
        kevbin.cprint(kevbin.t.warning, "No CSV data provided")
        kevbin.pause()
        return
    
    try:
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"CSV parse error: {e}")
        kevbin.pause()
        return
    
    if not rows:
        kevbin.cprint(kevbin.t.warning, "Empty CSV")
        kevbin.pause()
        return
    
    col_widths = _calc_widths(rows)
    
    kevbin.clear()
    kevbin.section_header("📊", f"CSV Viewer ({len(rows)} rows, {len(rows[0])} cols)")
    
    for i, row in enumerate(rows):
        padded = [cell.ljust(col_widths[j]) for j, cell in enumerate(row)]
        line = " │ ".join(padded)
        if i == 0:
            kevbin.box_top()
            kevbin.cprint(kevbin.t.primary, f" {line}")
            kevbin.box_mid()
        else:
            kevbin.box_row("", line)
    
    kevbin.box_bottom()
    kevbin.pause()

def _calc_widths(rows, max_width=100):
    if not rows:
        return []
    n_cols = max(len(r) for r in rows)
    widths = [0] * n_cols
    for row in rows:
        for j, cell in enumerate(row):
            widths[j] = max(widths[j], len(str(cell)))
    
    total = sum(widths) + 3 * (n_cols - 1)
    if total > max_width:
        scale = max_width / total
        widths = [max(3, int(w * scale)) for w in widths]
    
    return widths
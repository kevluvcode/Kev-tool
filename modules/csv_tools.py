import csv
import json
import io


def _read_csv(path: str, delimiter: str = ','):
    with open(path, 'r', encoding='utf-8') as f:
        sample = f.read(1024)
        f.seek(0)
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample)
            delimiter = dialect.delimiter
        except:
            pass
        f.seek(0)
        reader = csv.DictReader(f, delimiter=delimiter)
        return list(reader), reader.fieldnames


def _write_csv(path: str, rows, fieldnames, delimiter: str = ','):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def run(kevbin):
    kevbin.box_title("CSV Tools")
    kevbin.box_print("Merge, filter, sort, and convert CSV files")
    
    while True:
        kevbin.box_print("")
        kevbin.box_print("Operations:")
        kevbin.box_print("  1. Merge multiple CSVs")
        kevbin.box_print("  2. Filter rows")
        kevbin.box_print("  3. Sort by column")
        kevbin.box_print("  4. Convert CSV to JSON")
        kevbin.box_print("  5. View CSV info")
        
        op = kevbin.box_input("Select operation [1]: ").strip() or "1"
        if op.lower() in ('q', 'quit', 'exit'):
            break
        
        if op == "1":
            kevbin.box_print("Enter CSV file paths (empty to finish):")
            files = []
            while True:
                path = kevbin.box_input(f"  File {len(files)+1}: ").strip().strip('"')
                if not path:
                    break
                files.append(path)
            
            if len(files) < 2:
                kevbin.box_print("[yellow]Need at least 2 files to merge[/yellow]")
                continue
            
            all_rows = []
            all_fields = set()
            
            for f in files:
                try:
                    rows, fields = _read_csv(f)
                    all_rows.extend(rows)
                    if fields:
                        all_fields.update(fields)
                except Exception as e:
                    kevbin.box_print(f"[red]Error reading {f}: {e}[/red]")
            
            if not all_rows:
                kevbin.box_print("[red]No data to merge[/red]")
                continue
            
            fieldnames = list(all_fields)
            out_path = kevbin.box_input("Output file path: ").strip().strip('"')
            if out_path:
                try:
                    _write_csv(out_path, all_rows, fieldnames)
                    kevbin.box_print(f"[green]Merged {len(all_rows)} rows into {out_path}[/green]")
                except Exception as e:
                    kevbin.box_print(f"[red]Write error: {e}[/red]")
            
        elif op == "2":
            path = kevbin.box_input("CSV file path: ").strip().strip('"')
            try:
                rows, fields = _read_csv(path)
            except Exception as e:
                kevbin.box_print(f"[red]Error: {e}[/red]")
                continue
            
            if not fields:
                kevbin.box_print("[red]No columns found[/red]")
                continue
            
            kevbin.box_print(f"Columns: {', '.join(fields)}")
            col = kevbin.box_input("Filter column: ").strip()
            if col not in fields:
                kevbin.box_print("[red]Invalid column[/red]")
                continue
            
            kevbin.box_print("Operators: ==, !=, contains, startswith, endswith, >, <, >=, <=")
            operator = kevbin.box_input("Operator: ").strip()
            value = kevbin.box_input("Value: ").strip()
            
            filtered = []
            for row in rows:
                cell = row.get(col, "")
                match = False
                if operator == "==":
                    match = cell == value
                elif operator == "!=":
                    match = cell != value
                elif operator == "contains":
                    match = value.lower() in cell.lower()
                elif operator == "startswith":
                    match = cell.lower().startswith(value.lower())
                elif operator == "endswith":
                    match = cell.lower().endswith(value.lower())
                elif operator in (">", "<", ">=", "<="):
                    try:
                        cval = float(cell)
                        vval = float(value)
                        if operator == ">": match = cval > vval
                        elif operator == "<": match = cval < vval
                        elif operator == ">=": match = cval >= vval
                        elif operator == "<=": match = cval <= vval
                    except:
                        pass
                if match:
                    filtered.append(row)
            
            kevbin.box_print(f"[green]Matched {len(filtered)} of {len(rows)} rows[/green]")
            
            out_path = kevbin.box_input("Output file (empty to preview): ").strip().strip('"')
            if out_path:
                try:
                    _write_csv(out_path, filtered, fields)
                    kevbin.box_print(f"[green]Saved to {out_path}[/green]")
                except Exception as e:
                    kevbin.box_print(f"[red]Write error: {e}[/red]")
            else:
                preview = min(10, len(filtered))
                table_rows = [fields] + [[r.get(f, "") for f in fields] for r in filtered[:preview]]
                kevbin.box_table(table_rows, title=f"Preview (first {preview} rows)")
        
        elif op == "3":
            path = kevbin.box_input("CSV file path: ").strip().strip('"')
            try:
                rows, fields = _read_csv(path)
            except Exception as e:
                kevbin.box_print(f"[red]Error: {e}[/red]")
                continue
            
            kevbin.box_print(f"Columns: {', '.join(fields)}")
            col = kevbin.box_input("Sort by column: ").strip()
            if col not in fields:
                kevbin.box_print("[red]Invalid column[/red]")
                continue
            
            reverse = kevbin.box_input("Descending? (y/n) [n]: ").strip().lower() == 'y'
            
            def sort_key(row):
                val = row.get(col, "")
                try:
                    return float(val)
                except:
                    return val.lower()
            
            try:
                rows.sort(key=sort_key, reverse=reverse)
            except Exception as e:
                kevbin.box_print(f"[red]Sort error: {e}[/red]")
                continue
            
            out_path = kevbin.box_input("Output file (empty to preview): ").strip().strip('"')
            if out_path:
                try:
                    _write_csv(out_path, rows, fields)
                    kevbin.box_print(f"[green]Saved to {out_path}[/green]")
                except Exception as e:
                    kevbin.box_print(f"[red]Write error: {e}[/red]")
            else:
                preview = min(10, len(rows))
                table_rows = [fields] + [[r.get(f, "") for f in fields] for r in rows[:preview]]
                kevbin.box_table(table_rows, title=f"Preview (first {preview} rows)")
        
        elif op == "4":
            path = kevbin.box_input("CSV file path: ").strip().strip('"')
            try:
                rows, fields = _read_csv(path)
            except Exception as e:
                kevbin.box_print(f"[red]Error: {e}[/red]")
                continue
            
            out_path = kevbin.box_input("Output JSON file (empty to print): ").strip().strip('"')
            
            json_data = json.dumps(rows, indent=2)
            
            if out_path:
                try:
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(json_data)
                    kevbin.box_print(f"[green]Saved to {out_path}[/green]")
                except Exception as e:
                    kevbin.box_print(f"[red]Write error: {e}[/red]")
            else:
                kevbin.box_code(json_data[:5000], language="json")
                if len(json_data) > 5000:
                    kevbin.box_print(f"[dim]... ({len(rows)} total rows)[/dim]")
        
        elif op == "5":
            path = kevbin.box_input("CSV file path: ").strip().strip('"')
            try:
                rows, fields = _read_csv(path)
            except Exception as e:
                kevbin.box_print(f"[red]Error: {e}[/red]")
                continue
            
            rows_data = [[f, str(len([r for r in rows if r.get(f, "") != ""])), str(len(rows))] for f in fields]
            table_rows = [["Column", "Non-empty", "Total Rows"]] + rows_data
            kevbin.box_table(table_rows, title=f"CSV Info: {len(rows)} rows, {len(fields)} columns")
        
        else:
            kevbin.box_print("[red]Invalid operation[/red]")


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
import uuid
import secrets


def run(kevbin):
    kevbin.box_title("UUID Generator")
    kevbin.box_print("Generate UUID v4 strings")
    
    while True:
        kevbin.box_print("")
        count_input = kevbin.box_input("How many UUIDs to generate? [1]: ").strip()
        if count_input.lower() in ('q', 'quit', 'exit'):
            break
        
        try:
            count = int(count_input) if count_input else 1
            if count < 1 or count > 1000:
                kevbin.box_print("[red]Please enter 1-1000[/red]")
                continue
        except ValueError:
            kevbin.box_print("[red]Invalid number[/red]")
            continue
        
        format_choice = kevbin.box_input("Format (standard/short/urn/bytes) [standard]: ").strip().lower() or "standard"
        
        uuids = []
        for _ in range(count):
            u = uuid.uuid4()
            if format_choice == "short":
                uuids.append(str(u).replace('-', ''))
            elif format_choice == "urn":
                uuids.append(f"urn:uuid:{u}")
            elif format_choice == "bytes":
                uuids.append(u.bytes.hex())
            else:
                uuids.append(str(u))
        
        if count == 1:
            kevbin.box_print(f"\n[green]{uuids[0]}[/green]")
        else:
            rows = [["#", "UUID"]]
            for i, u in enumerate(uuids, 1):
                rows.append([str(i), u])
            kevbin.box_table(rows, title=f"Generated {count} UUIDs")
        
        save = kevbin.box_input("\nSave to file? (path or empty): ").strip().strip('"')
        if save:
            try:
                with open(save, 'w', encoding='utf-8') as f:
                    f.write("\n".join(uuids))
                kevbin.box_print(f"[green]Saved {count} UUIDs to {save}[/green]")
            except Exception as e:
                kevbin.box_print(f"[red]Save error: {e}[/red]")
        
        another = kevbin.box_input("\nGenerate more? (y/n) [y]: ").strip().lower()
        if another in ('n', 'no'):
            break


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
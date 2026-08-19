def run(kevbin):
    kevbin.box_title("Percentage Calculator")
    kevbin.box_print("Calculate percentages: X% of Y, X is what % of Y, % change from X to Y")
    
    while True:
        kevbin.box_print("")
        kevbin.box_print("Modes:")
        kevbin.box_print("  1. X% of Y (e.g., 15% of 200)")
        kevbin.box_print("  2. X is what % of Y (e.g., 30 is what % of 200)")
        kevbin.box_print("  3. % change from X to Y (e.g., from 100 to 150)")
        kevbin.box_print("  4. Increase X by Y%")
        kevbin.box_print("  5. Decrease X by Y%")
        
        mode = kevbin.box_input("Select mode [1]: ").strip() or "1"
        if mode.lower() in ('q', 'quit', 'exit'):
            break
        
        try:
            if mode == "1":
                x = float(kevbin.box_input("Percentage (X%): ").strip())
                y = float(kevbin.box_input("Value (Y): ").strip())
                result = (x / 100) * y
                rows = [
                    ["Expression", f"{x}% of {y}"],
                    ["Result", f"{result}"],
                    ["Formula", f"({x} / 100) × {y} = {result}"]
                ]
                kevbin.box_table(rows, title="Percentage Calculation")
                
            elif mode == "2":
                x = float(kevbin.box_input("Part (X): ").strip())
                y = float(kevbin.box_input("Whole (Y): ").strip())
                if y == 0:
                    kevbin.box_print("[red]Cannot divide by zero[/red]")
                    continue
                result = (x / y) * 100
                rows = [
                    ["Expression", f"{x} is what % of {y}"],
                    ["Result", f"{result:.2f}%"],
                    ["Formula", f"({x} / {y}) × 100 = {result:.2f}%"]
                ]
                kevbin.box_table(rows, title="Percentage Calculation")
                
            elif mode == "3":
                x = float(kevbin.box_input("From (X): ").strip())
                y = float(kevbin.box_input("To (Y): ").strip())
                if x == 0:
                    kevbin.box_print("[red]Cannot calculate % change from zero[/red]")
                    continue
                change = y - x
                pct = (change / x) * 100
                direction = "increase" if pct >= 0 else "decrease"
                rows = [
                    ["Expression", f"% change from {x} to {y}"],
                    ["Change", f"{change:+.2f}"],
                    ["Result", f"{pct:+.2f}% ({direction})"],
                    ["Formula", f"(({y} - {x}) / {x}) × 100 = {pct:.2f}%"]
                ]
                kevbin.box_table(rows, title="Percentage Change")
                
            elif mode == "4":
                x = float(kevbin.box_input("Base value (X): ").strip())
                y = float(kevbin.box_input("Increase by (%): ").strip())
                result = x * (1 + y / 100)
                rows = [
                    ["Expression", f"Increase {x} by {y}%"],
                    ["Result", f"{result:.2f}"],
                    ["Formula", f"{x} × (1 + {y}/100) = {result:.2f}"]
                ]
                kevbin.box_table(rows, title="Percentage Increase")
                
            elif mode == "5":
                x = float(kevbin.box_input("Base value (X): ").strip())
                y = float(kevbin.box_input("Decrease by (%): ").strip())
                result = x * (1 - y / 100)
                rows = [
                    ["Expression", f"Decrease {x} by {y}%"],
                    ["Result", f"{result:.2f}"],
                    ["Formula", f"{x} × (1 - {y}/100) = {result:.2f}"]
                ]
                kevbin.box_table(rows, title="Percentage Decrease")
                
            else:
                kevbin.box_print("[red]Invalid mode[/red]")
                
        except ValueError:
            kevbin.box_print("[red]Invalid number[/red]")
        except Exception as e:
            kevbin.box_print(f"[red]Error: {e}[/red]")


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
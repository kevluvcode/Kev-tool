import random
import secrets
import string
import uuid


def run(kevbin):
    kevbin.box_title("Random Data Generator")
    kevbin.box_print("Generate random numbers, strings, choices, UUIDs, and more")
    
    while True:
        kevbin.box_print("")
        kevbin.box_print("Generators:")
        kevbin.box_print("  1. Random number in range")
        kevbin.box_print("  2. Random string")
        kevbin.box_print("  3. Random choice from list")
        kevbin.box_print("  4. Random UUID")
        kevbin.box_print("  5. Shuffle list")
        kevbin.box_print("  6. Random sample (unique)")
        kevbin.box_print("  7. Random bytes (hex)")
        kevbin.box_print("  8. Dice roll")
        kevbin.box_print("  9. Coin flip")
        
        choice = kevbin.box_input("Select generator [1]: ").strip() or "1"
        if choice.lower() in ('q', 'quit', 'exit'):
            break
        
        try:
            if choice == "1":
                min_val = float(kevbin.box_input("Minimum: ").strip())
                max_val = float(kevbin.box_input("Maximum: ").strip())
                count = int(kevbin.box_input("How many? [1]: ").strip() or "1")
                count = max(1, min(100, count))
                
                is_int = kevbin.box_input("Integers only? (y/n) [y]: ").strip().lower() != 'n'
                
                results = []
                for _ in range(count):
                    if is_int:
                        results.append(str(random.randint(int(min_val), int(max_val))))
                    else:
                        results.append(f"{random.uniform(min_val, max_val):.4f}")
                
                if count == 1:
                    kevbin.box_print(f"\n[green]{results[0]}[/green]")
                else:
                    rows = [["#", "Value"]]
                    for i, v in enumerate(results, 1):
                        rows.append([str(i), v])
                    kevbin.box_table(rows, title=f"{count} Random Numbers")
            
            elif choice == "2":
                length = int(kevbin.box_input("Length [16]: ").strip() or "16")
                length = max(1, min(200, length))
                
                charset = kevbin.box_input("Charset (alphanumeric/hex/alpha/digits/custom) [alphanumeric]: ").strip().lower() or "alphanumeric"
                
                if charset == "alphanumeric":
                    chars = string.ascii_letters + string.digits
                elif charset == "hex":
                    chars = string.hexdigits.lower()
                elif charset == "alpha":
                    chars = string.ascii_letters
                elif charset == "digits":
                    chars = string.digits
                elif charset == "custom":
                    chars = kevbin.box_input("Custom characters: ").strip()
                    if not chars:
                        kevbin.box_print("[red]No characters provided[/red]")
                        continue
                else:
                    chars = string.ascii_letters + string.digits
                
                count = int(kevbin.box_input("How many? [1]: ").strip() or "1")
                count = max(1, min(50, count))
                
                use_secrets = kevbin.box_input("Cryptographically secure? (y/n) [y]: ").strip().lower() != 'n'
                rand_func = secrets.choice if use_secrets else random.choice
                
                results = []
                for _ in range(count):
                    results.append("".join(rand_func(chars) for _ in range(length)))
                
                if count == 1:
                    kevbin.box_print(f"\n[green]{results[0]}[/green]")
                else:
                    rows = [["#", "String"]]
                    for i, v in enumerate(results, 1):
                        rows.append([str(i), v])
                    kevbin.box_table(rows, title=f"{count} Random Strings")
            
            elif choice == "3":
                items_input = kevbin.box_input("Items (comma-separated): ").strip()
                if not items_input:
                    kevbin.box_print("[red]No items provided[/red]")
                    continue
                items = [item.strip() for item in items_input.split(",")]
                
                count = int(kevbin.box_input("How many choices? [1]: ").strip() or "1")
                count = max(1, min(len(items) * 2, 50))
                
                allow_repeat = kevbin.box_input("Allow repeats? (y/n) [y]: ").strip().lower() != 'n'
                
                results = []
                if allow_repeat:
                    for _ in range(count):
                        results.append(random.choice(items))
                else:
                    pool = items.copy()
                    for _ in range(min(count, len(items))):
                        results.append(pool.pop(random.randrange(len(pool))))
                
                if count == 1:
                    kevbin.box_print(f"\n[green]{results[0]}[/green]")
                else:
                    rows = [["#", "Choice"]]
                    for i, v in enumerate(results, 1):
                        rows.append([str(i), v])
                    kevbin.box_table(rows, title=f"{count} Random Choices")
            
            elif choice == "4":
                count = int(kevbin.box_input("How many UUIDs? [1]: ").strip() or "1")
                count = max(1, min(100, count))
                
                format_opt = kevbin.box_input("Format (standard/short/urn) [standard]: ").strip().lower() or "standard"
                
                results = []
                for _ in range(count):
                    u = uuid.uuid4()
                    if format_opt == "short":
                        results.append(str(u).replace('-', ''))
                    elif format_opt == "urn":
                        results.append(f"urn:uuid:{u}")
                    else:
                        results.append(str(u))
                
                if count == 1:
                    kevbin.box_print(f"\n[green]{results[0]}[/green]")
                else:
                    rows = [["#", "UUID"]]
                    for i, v in enumerate(results, 1):
                        rows.append([str(i), v])
                    kevbin.box_table(rows, title=f"{count} UUIDs")
            
            elif choice == "5":
                items_input = kevbin.box_input("Items to shuffle (comma-separated): ").strip()
                if not items_input:
                    kevbin.box_print("[red]No items provided[/red]")
                    continue
                items = [item.strip() for item in items_input.split(",")]
                
                random.shuffle(items)
                rows = [["#", "Item"]]
                for i, v in enumerate(items, 1):
                    rows.append([str(i), v])
                kevbin.box_table(rows, title="Shuffled List")
            
            elif choice == "6":
                items_input = kevbin.box_input("Items (comma-separated): ").strip()
                if not items_input:
                    kevbin.box_print("[red]No items provided[/red]")
                    continue
                items = [item.strip() for item in items_input.split(",")]
                
                sample_size = int(kevbin.box_input(f"Sample size (max {len(items)}): ").strip())
                sample_size = max(1, min(sample_size, len(items)))
                
                sample = random.sample(items, sample_size)
                rows = [["#", "Item"]]
                for i, v in enumerate(sample, 1):
                    rows.append([str(i), v])
                kevbin.box_table(rows, title=f"Random Sample ({sample_size} of {len(items)})")
            
            elif choice == "7":
                num_bytes = int(kevbin.box_input("Number of bytes [16]: ").strip() or "16")
                num_bytes = max(1, min(256, num_bytes))
                
                count = int(kevbin.box_input("How many? [1]: ").strip() or "1")
                count = max(1, min(20, count))
                
                results = []
                for _ in range(count):
                    results.append(secrets.token_hex(num_bytes))
                
                if count == 1:
                    kevbin.box_print(f"\n[green]{results[0]}[/green]")
                else:
                    rows = [["#", "Hex Bytes"]]
                    for i, v in enumerate(results, 1):
                        rows.append([str(i), v])
                    kevbin.box_table(rows, title=f"{count} Random Byte Strings")
            
            elif choice == "8":
                sides = int(kevbin.box_input("Dice sides [6]: ").strip() or "6")
                sides = max(2, min(100, sides))
                
                count = int(kevbin.box_input("Number of dice [1]: ").strip() or "1")
                count = max(1, min(20, count))
                
                rolls = [random.randint(1, sides) for _ in range(count)]
                total = sum(rolls)
                
                if count == 1:
                    kevbin.box_print(f"\n[green]🎲 Rolled: {rolls[0]}[/green]")
                else:
                    rows = [["Die", "Result"]]
                    for i, r in enumerate(rolls, 1):
                        rows.append([str(i), str(r)])
                    rows.append(["Total", str(total)])
                    kevbin.box_table(rows, title=f"{count}d{sides} Roll")
            
            elif choice == "9":
                count = int(kevbin.box_input("Number of flips [1]: ").strip() or "1")
                count = max(1, min(100, count))
                
                results = ["Heads" if random.random() < 0.5 else "Tails" for _ in range(count)]
                heads = results.count("Heads")
                tails = results.count("Tails")
                
                if count == 1:
                    kevbin.box_print(f"\n[green]🪙 {results[0]}[/green]")
                else:
                    rows = [["#", "Result"]]
                    for i, v in enumerate(results, 1):
                        rows.append([str(i), v])
                    rows.append(["", ""])
                    rows.append(["Heads", str(heads)])
                    rows.append(["Tails", str(tails)])
                    kevbin.box_table(rows, title=f"{count} Coin Flips")
            
            else:
                kevbin.box_print("[red]Invalid choice[/red]")
                
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
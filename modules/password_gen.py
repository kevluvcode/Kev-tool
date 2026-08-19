import secrets
import string


def _generate_password(length: int, use_upper: bool, use_lower: bool, use_digits: bool, use_symbols: bool, exclude_ambiguous: bool) -> str:
    chars = ""
    if use_upper:
        chars += string.ascii_uppercase
    if use_lower:
        chars += string.ascii_lowercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if exclude_ambiguous:
        ambiguous = "il1Lo0O"
        chars = "".join(c for c in chars if c not in ambiguous)
    
    if not chars:
        raise ValueError("At least one character type must be selected")
    
    return "".join(secrets.choice(chars) for _ in range(length))


def _password_strength(password: str) -> tuple:
    score = 0
    checks = []
    
    if len(password) >= 8:
        score += 1
        checks.append("✓ Length ≥ 8")
    else:
        checks.append("✗ Length ≥ 8")
    
    if len(password) >= 12:
        score += 1
        checks.append("✓ Length ≥ 12")
    else:
        checks.append("✗ Length ≥ 12")
    
    if any(c.islower() for c in password):
        score += 1
        checks.append("✓ Lowercase")
    else:
        checks.append("✗ Lowercase")
    
    if any(c.isupper() for c in password):
        score += 1
        checks.append("✓ Uppercase")
    else:
        checks.append("✗ Uppercase")
    
    if any(c.isdigit() for c in password):
        score += 1
        checks.append("✓ Digits")
    else:
        checks.append("✗ Digits")
    
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
        checks.append("✓ Symbols")
    else:
        checks.append("✗ Symbols")
    
    ratings = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"]
    rating = ratings[min(score, 5)]
    
    return rating, score, checks


def run(kevbin):
    kevbin.box_title("Secure Password Generator")
    kevbin.box_print("Generate cryptographically secure random passwords")
    
    while True:
        kevbin.box_print("")
        
        length_input = kevbin.box_input("Password length [16]: ").strip()
        if length_input.lower() in ('q', 'quit', 'exit'):
            break
        
        try:
            length = int(length_input) if length_input else 16
            if length < 4 or length > 128:
                kevbin.box_print("[red]Length must be 4-128[/red]")
                continue
        except ValueError:
            kevbin.box_print("[red]Invalid number[/red]")
            continue
        
        use_upper = kevbin.box_input("Include uppercase? (y/n) [y]: ").strip().lower() != 'n'
        use_lower = kevbin.box_input("Include lowercase? (y/n) [y]: ").strip().lower() != 'n'
        use_digits = kevbin.box_input("Include digits? (y/n) [y]: ").strip().lower() != 'n'
        use_symbols = kevbin.box_input("Include symbols? (y/n) [y]: ").strip().lower() != 'n'
        exclude_ambiguous = kevbin.box_input("Exclude ambiguous chars (il1Lo0O)? (y/n) [n]: ").strip().lower() == 'y'
        
        count_input = kevbin.box_input("How many passwords? [1]: ").strip()
        try:
            count = int(count_input) if count_input else 1
            count = max(1, min(50, count))
        except ValueError:
            count = 1
        
        passwords = []
        for _ in range(count):
            try:
                pwd = _generate_password(length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous)
                passwords.append(pwd)
            except ValueError as e:
                kevbin.box_print(f"[red]{e}[/red]")
                break
        else:
            if count == 1:
                pwd = passwords[0]
                rating, score, checks = _password_strength(pwd)
                
                kevbin.box_print(f"\n[green]{pwd}[/green]")
                kevbin.box_print(f"\nStrength: {rating} ({score}/6)")
                for check in checks:
                    kevbin.box_print(f"  {check}")
                
                copy = kevbin.box_input("\nCopy to clipboard? (y/n) [n]: ").strip().lower()
                if copy == 'y':
                    kevbin.box_print("[green]Copied![/green] (Note: actual clipboard copy not implemented)")
            else:
                rows = [["#", "Password", "Strength"]]
                for i, pwd in enumerate(passwords, 1):
                    rating, _, _ = _password_strength(pwd)
                    rows.append([str(i), pwd, rating])
                kevbin.box_table(rows, title=f"Generated {count} Passwords")
            
            save = kevbin.box_input("\nSave to file? (path or empty): ").strip().strip('"')
            if save:
                try:
                    with open(save, 'w', encoding='utf-8') as f:
                        f.write("\n".join(passwords))
                    kevbin.box_print(f"[green]Saved {count} passwords to {save}[/green]")
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
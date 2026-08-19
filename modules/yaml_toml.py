import json
import sys

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import tomllib
    HAS_TOML_READ = True
except ImportError:
    try:
        import tomli as tomllib
        HAS_TOML_READ = True
    except ImportError:
        HAS_TOML_READ = False

try:
    import tomli_w
    HAS_TOML_WRITE = True
except ImportError:
    HAS_TOML_WRITE = False


def _load_yaml(content: str):
    if not HAS_YAML:
        raise RuntimeError("PyYAML not installed. Run: pip install pyyaml")
    return yaml.safe_load(content)


def _dump_yaml(data):
    if not HAS_YAML:
        raise RuntimeError("PyYAML not installed. Run: pip install pyyaml")
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def _load_toml(content: str):
    if not HAS_TOML_READ:
        raise RuntimeError("tomli not installed. Run: pip install tomli")
    return tomllib.loads(content)


def _dump_toml(data):
    if not HAS_TOML_WRITE:
        raise RuntimeError("tomli-w not installed. Run: pip install tomli-w")
    return tomli_w.dumps(data)


def _detect_format(content: str) -> str:
    content = content.strip()
    if content.startswith('{') or content.startswith('['):
        return 'json'
    if content.startswith('---') or '\n- ' in content or content.lstrip().startswith('- '):
        return 'yaml'
    if '=' in content and not content.startswith('{'):
        return 'toml'
    return 'unknown'


def run(kevbin):
    kevbin.box_title("YAML ↔ TOML Converter")
    kevbin.box_print("Convert between YAML, TOML, and JSON formats")
    
    if not HAS_YAML:
        kevbin.box_print("[yellow]Warning: PyYAML not installed (pip install pyyaml)[/yellow]")
    if not HAS_TOML_READ:
        kevbin.box_print("[yellow]Warning: tomli not installed (pip install tomli)[/yellow]")
    if not HAS_TOML_WRITE:
        kevbin.box_print("[yellow]Warning: tomli-w not installed (pip install tomli-w)[/yellow]")
    
    while True:
        kevbin.box_print("")
        kevbin.box_print("Input methods:")
        kevbin.box_print("  1. Paste content directly")
        kevbin.box_print("  2. Load from file")
        
        method = kevbin.box_input("Select method [1]: ").strip() or "1"
        if method.lower() in ('q', 'quit', 'exit'):
            break
        
        content = ""
        if method == "1":
            kevbin.box_print("Paste content (empty line to finish):")
            lines = []
            while True:
                line = kevbin.box_input("")
                if not line and lines:
                    break
                lines.append(line)
            content = "\n".join(lines)
        elif method == "2":
            path = kevbin.box_input("File path: ").strip().strip('"')
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                kevbin.box_print(f"[red]Error reading file: {e}[/red]")
                continue
        else:
            kevbin.box_print("[red]Invalid method[/red]")
            continue
        
        if not content.strip():
            kevbin.box_print("[red]No content provided[/red]")
            continue
        
        fmt = _detect_format(content)
        kevbin.box_print(f"[dim]Detected format: {fmt.upper()}[/dim]")
        
        data = None
        try:
            if fmt == 'json':
                data = json.loads(content)
            elif fmt == 'yaml':
                data = _load_yaml(content)
            elif fmt == 'toml':
                data = _load_toml(content)
            else:
                kevbin.box_print("[red]Could not detect format[/red]")
                continue
        except Exception as e:
            kevbin.box_print(f"[red]Parse error: {e}[/red]")
            continue
        
        kevbin.box_print("\nOutput formats:")
        kevbin.box_print("  1. YAML")
        kevbin.box_print("  2. TOML")
        kevbin.box_print("  3. JSON")
        
        out_choice = kevbin.box_input("Select output [1]: ").strip() or "1"
        
        try:
            if out_choice == "1":
                output = _dump_yaml(data)
                kevbin.box_code(output, language="yaml")
            elif out_choice == "2":
                output = _dump_toml(data)
                kevbin.box_code(output, language="toml")
            elif out_choice == "3":
                output = json.dumps(data, indent=2)
                kevbin.box_code(output, language="json")
            else:
                kevbin.box_print("[red]Invalid choice[/red]")
                continue
            
            save = kevbin.box_input("\nSave to file? (path or empty to skip): ").strip().strip('"')
            if save:
                try:
                    with open(save, 'w', encoding='utf-8') as f:
                        f.write(output)
                    kevbin.box_print(f"[green]Saved to {save}[/green]")
                except Exception as e:
                    kevbin.box_print(f"[red]Save error: {e}[/red]")
                    
        except Exception as e:
            kevbin.box_print(f"[red]Conversion error: {e}[/red]")


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
import unicodedata

def run(kevbin):
    kevbin.clear()
    kevbin.section_header("🔤", "Unicode Lookup")
    
    kevbin.cprint(kevbin.t.primary, "  1. Character → Info")
    kevbin.cprint(kevbin.t.primary, "  2. Codepoint → Character")
    kevbin.cprint(kevbin.t.primary, "  3. Search by name")
    kevbin.line()
    choice = kevbin.input_choice("Select mode")
    
    if choice == "1":
        _char_to_info(kevbin)
    elif choice == "2":
        _codepoint_to_char(kevbin)
    elif choice == "3":
        _search_by_name(kevbin)

def _char_to_info(kevbin):
    kevbin.clear()
    kevbin.section_header("🔤", "Character Info")
    char = kevbin.input_choice("Enter a character")
    if not char:
        return
    
    char = char[0]
    codepoint = ord(char)
    name = unicodedata.name(char, "UNKNOWN")
    category = unicodedata.category(char)
    
    kevbin.box_top()
    kevbin.box_row("Character", char)
    kevbin.box_row("Codepoint", f"U+{codepoint:04X}")
    kevbin.box_row("Decimal", str(codepoint))
    kevbin.box_row("UTF-8", char.encode('utf-8').hex().upper())
    kevbin.box_row("UTF-16", char.encode('utf-16be').hex().upper())
    kevbin.box_row("Name", name)
    kevbin.box_row("Category", f"{category} ({_category_name(category)})")
    if char.isprintable() and not char.isspace():
        kevbin.box_row("Repr", repr(char))
    kevbin.box_bottom()
    kevbin.pause()

def _codepoint_to_char(kevbin):
    kevbin.clear()
    kevbin.section_header("🔤", "Codepoint to Character")
    cp = kevbin.input_choice("Enter codepoint (hex or decimal)")
    if not cp:
        return
    
    try:
        if cp.startswith('U+') or cp.startswith('0x') or cp.startswith('0X'):
            codepoint = int(cp.replace('U+', '').replace('0x', '').replace('0X', ''), 16)
        else:
            codepoint = int(cp)
    except ValueError:
        kevbin.cprint(kevbin.t.error, "Invalid codepoint")
        kevbin.pause()
        return
    
    if codepoint < 0 or codepoint > 0x10FFFF:
        kevbin.cprint(kevbin.t.error, "Codepoint out of range")
        kevbin.pause()
        return
    
    char = chr(codepoint)
    name = unicodedata.name(char, "UNKNOWN")
    category = unicodedata.category(char)
    
    kevbin.box_top()
    kevbin.box_row("Codepoint", f"U+{codepoint:04X}")
    kevbin.box_row("Character", char if char.isprintable() else "(non-printable)")
    kevbin.box_row("Name", name)
    kevbin.box_row("Category", f"{category} ({_category_name(category)})")
    kevbin.box_row("UTF-8", char.encode('utf-8').hex().upper())
    kevbin.box_row("UTF-16", char.encode('utf-16be').hex().upper())
    kevbin.box_bottom()
    kevbin.pause()

def _search_by_name(kevbin):
    kevbin.clear()
    kevbin.section_header("🔍", "Search by Name")
    query = kevbin.input_choice("Search term").lower()
    if not query:
        return
    
    results = []
    for codepoint in range(0x10FFFF + 1):
        try:
            char = chr(codepoint)
            name = unicodedata.name(char, "").lower()
            if query in name:
                results.append((codepoint, char, name.upper()))
            if len(results) >= 50:
                break
        except ValueError:
            pass
    
    kevbin.clear()
    kevbin.section_header("🔍", f"Search Results ({len(results)} found)")
    kevbin.box_top()
    for cp, char, name in results[:30]:
        display = char if char.isprintable() and not char.isspace() else "?"
        kevbin.box_row(f"U+{cp:04X}", f"{display}  {name}")
    if len(results) > 30:
        kevbin.box_row("...", f"and {len(results) - 30} more")
    kevbin.box_bottom()
    kevbin.pause()

def _category_name(cat):
    categories = {
        'Lu': 'Uppercase Letter', 'Ll': 'Lowercase Letter', 'Lt': 'Titlecase Letter',
        'Lm': 'Modifier Letter', 'Lo': 'Other Letter', 'Mn': 'Nonspacing Mark',
        'Mc': 'Spacing Mark', 'Me': 'Enclosing Mark', 'Nd': 'Decimal Number',
        'Nl': 'Letter Number', 'No': 'Other Number', 'Pc': 'Connector Punctuation',
        'Pd': 'Dash Punctuation', 'Ps': 'Open Punctuation', 'Pe': 'Close Punctuation',
        'Pi': 'Initial Punctuation', 'Pf': 'Final Punctuation', 'Po': 'Other Punctuation',
        'Sm': 'Math Symbol', 'Sc': 'Currency Symbol', 'Sk': 'Modifier Symbol',
        'So': 'Other Symbol', 'Zs': 'Space Separator', 'Zl': 'Line Separator',
        'Zp': 'Paragraph Separator', 'Cc': 'Control', 'Cf': 'Format',
        'Cs': 'Surrogate', 'Co': 'Private Use', 'Cn': 'Unassigned',
    }
    return categories.get(cat, cat)
"""Dox Tool — Person-of-interest tracker and dox report creator."""

import json
import os
import sys
import time
import glob as globmod
from datetime import datetime

try:
    from kevbin import clear, cprint, prompt, pause
except ImportError:
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    def cprint(*a, **kw):
        msg = ' '.join(str(x) for x in a if isinstance(x, str))
        sys.stdout.write(msg + '\n'); sys.stdout.flush()
    def prompt(msg=''):
        if msg: sys.stdout.write(msg); sys.stdout.flush()
        return input()
    def pause():
        prompt('\n  \033[90mPress Enter to continue...\033[0m'); input()

def _save(dox, name):
    path = f"dox_{name.replace(' ','_').lower()}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dox, f, indent=2, ensure_ascii=False)
    return path

def _load(name):
    path = f"dox_{name.replace(' ','_').lower()}.json"
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def _list_dox():
    return sorted(globmod.glob("dox_*.json"))

def _print_field(label, val, color="97"):
    if isinstance(val, list):
        val = ', '.join(str(v) for v in val) if val else 'N/A'
    elif isinstance(val, dict):
        val = json.dumps(val, ensure_ascii=False) if val else 'N/A'
    elif val is None or val == '':
        val = 'N/A'
    cprint(f"  \033[{color}m{label + ':':<16} \033[97m{val}")

def _create():
    clear()
    cprint("  \033[93m┌── CREATE NEW DOX ──────────────────────────┐\033[0m")
    name = prompt("  \033[96mName/Alias: \033[0m").strip()
    if not name:
        cprint("  \033[91m[X] Need a name\033[0m"); return
    dox = {
        "name": name, "aliases": [], "age": "", "dob": "",
        "location": "", "address": "", "phones": [], "emails": [],
        "social_media": {}, "notes": [],
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat()
    }
    aliases = prompt("  \033[96mAliases (comma-separated, or empty): \033[0m").strip()
    if aliases:
        dox["aliases"] = [a.strip() for a in aliases.split(',')]
    dox["age"] = prompt("  \033[96mAge: \033[0m").strip()
    dox["dob"] = prompt("  \033[96mDate of Birth: \033[0m").strip()
    dox["location"] = prompt("  \033[96mLocation (city/country): \033[0m").strip()
    dox["address"] = prompt("  \033[96mAddress: \033[0m").strip()
    phones = prompt("  \033[96mPhones (comma-separated): \033[0m").strip()
    if phones:
        dox["phones"] = [p.strip() for p in phones.split(',')]
    emails = prompt("  \033[96mEmails (comma-separated): \033[0m").strip()
    if emails:
        dox["emails"] = [e.strip() for e in emails.split(',')]
    cprint("  \033[90mSocial media (enter platform:value, empty to stop):\033[0m")
    while True:
        entry = prompt("  \033[96m> \033[0m").strip()
        if not entry:
            break
        if ':' in entry:
            k, v = entry.split(':', 1)
            dox["social_media"][k.strip()] = v.strip()
    cprint("  \033[90mNotes (empty line to stop):\033[0m")
    while True:
        note = prompt("  \033[96m> \033[0m").strip()
        if not note:
            break
        dox["notes"].append(note)
    path = _save(dox, name)
    cprint(f"  \033[92m[X] Saved to {path}\033[0m")

def _view():
    clear()
    cprint("  \033[93m┌── VIEW DOX ────────────────────────────────┐\033[0m")
    files = _list_dox()
    if not files:
        cprint("  \033[91m[X] No dox files found\033[0m"); return
    for i, f in enumerate(files, 1):
        cprint(f"  \033[97m[{i}] {f}\033[0m")
    try:
        idx = int(prompt("\033[33m  select # > \033[0m")) - 1
    except:
        return
    if 0 <= idx < len(files):
        with open(files[idx], 'r', encoding='utf-8') as f:
            dox = json.load(f)
        clear()
        cprint(f"  \033[93m┌── {dox.get('name','?').upper()} ─────────────────────────┐\033[0m")
        _print_field("Name", dox.get('name'))
        _print_field("Aliases", dox.get('aliases'))
        _print_field("Age", dox.get('age'))
        _print_field("DOB", dox.get('dob'))
        _print_field("Location", dox.get('location'))
        _print_field("Address", dox.get('address'))
        _print_field("Phones", dox.get('phones'))
        _print_field("Emails", dox.get('emails'))
        _print_field("Social Media", dox.get('social_media'))
        _print_field("Notes", dox.get('notes'))
        _print_field("Created", dox.get('created'))
        cprint(f"  \033[93m└{'─' * 45}┘\033[0m")

def _add_info():
    clear()
    cprint("  \033[93m┌── ADD INFO ────────────────────────────────┐\033[0m")
    name = prompt("  \033[96mDox name: \033[0m").strip()
    dox = _load(name)
    if not dox:
        cprint("  \033[91m[X] Not found\033[0m"); return
    field = prompt("  \033[96mField to add/update (phones/emails/notes/social_media/...): \033[0m").strip()
    value = prompt("  \033[96mValue: \033[0m").strip()
    if field in ('phones', 'emails', 'aliases', 'notes'):
        if field not in dox:
            dox[field] = []
        dox[field].append(value)
    elif field == 'social_media':
        if ':' in value:
            k, v = value.split(':', 1)
            dox.setdefault('social_media', {})[k.strip()] = v.strip()
    else:
        dox[field] = value
    dox["modified"] = datetime.now().isoformat()
    _save(dox, name)
    cprint(f"  \033[92m[X] Updated {field}\033[0m")

def _search():
    clear()
    cprint("  \033[93m┌── SEARCH DOX ──────────────────────────────┐\033[0m")
    kw = prompt("  \033[96mSearch keyword: \033[0m").strip().lower()
    if not kw:
        return
    files = _list_dox()
    found = []
    for fp in files:
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        if kw in content.lower():
            with open(fp, 'r', encoding='utf-8') as f:
                dox = json.load(f)
            found.append((fp, dox))
    if not found:
        cprint("  \033[93mNo results\033[0m"); return
    cprint(f"  \033[92mFound {len(found)} match(es):\033[0m\n")
    for fp, dox in found:
        cprint(f"  \033[97m* {fp}\033[0m — {dox.get('name','?')} | {dox.get('location','?')}")

def _export():
    clear()
    cprint("  \033[93m┌── EXPORT REPORT ───────────────────────────┐\033[0m")
    name = prompt("  \033[96mDox name: \033[0m").strip()
    dox = _load(name)
    if not dox:
        cprint("  \033[91m[X] Not found\033[0m"); return
    out = f"dox_report_{name.replace(' ','_').lower()}_{int(time.time())}.txt"
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"  DOX REPORT: {dox.get('name','?')}")
    lines.append(f"  Generated: {datetime.now().isoformat()}")
    lines.append(f"{'='*60}\n")
    for k, v in dox.items():
        if k in ('created', 'modified', 'social_media', 'notes'):
            if k == 'social_media' and isinstance(v, dict):
                lines.append(f"Social Media:")
                for sk, sv in v.items():
                    lines.append(f"  {sk}: {sv}")
            elif k == 'notes' and isinstance(v, list):
                lines.append(f"Notes:")
                for n in v:
                    lines.append(f"  - {n}")
            elif k not in ('created', 'modified'):
                lines.append(f"{k}: {v}")
        else:
            if isinstance(v, list):
                lines.append(f"{k}: {', '.join(str(x) for x in v)}")
            else:
                lines.append(f"{k}: {v}")
    lines.append(f"\n{'='*60}")
    lines.append(f"  Created:  {dox.get('created','?')}")
    lines.append(f"  Modified: {dox.get('modified','?')}")
    lines.append(f"{'='*60}")
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    cprint(f"  \033[92m[X] Exported to {out}\033[0m")

def _list_all():
    clear()
    cprint("  \033[93m┌── ALL DOX FILES ───────────────────────────┐\033[0m")
    files = _list_dox()
    if not files:
        cprint("  \033[91m[X] No dox files found\033[0m"); return
    for i, fp in enumerate(files, 1):
        sz = os.path.getsize(fp)
        mt = datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%Y-%m-%d %H:%M')
        cprint(f"  \033[97m[{i}] \033[96m{fp}\033[0m \033[90m{mt} ({sz} bytes)\033[0m")
    cprint(f"  \033[90mTotal: {len(files)} file(s)\033[0m")

def run(kevbin=None):
    while True:
        clear()
        cprint("  \033[93m╔══════════════════════════════════════════════╗\033[0m")
        cprint("  \033[93m║         DOX TRACKER & CREATOR               ║\033[0m")
        cprint("  \033[93m╚══════════════════════════════════════════════╝\033[0m")
        print()
        cprint("  \033[97m[1]  Create New Dox\033[0m")
        cprint("  \033[97m[2]  View Dox\033[0m")
        cprint("  \033[97m[3]  Add Info to Existing Dox\033[0m")
        cprint("  \033[97m[4]  Search Dox Files\033[0m")
        cprint("  \033[97m[5]  Export Dox Report\033[0m")
        cprint("  \033[97m[6]  List All Dox\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '1':
            _create()
        elif choice == '2':
            _view()
        elif choice == '3':
            _add_info()
        elif choice == '4':
            _search()
        elif choice == '5':
            _export()
        elif choice == '6':
            _list_all()
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

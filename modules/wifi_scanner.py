"""WiFi Scanner — Scan and display saved WiFi profiles with passwords."""

import os
import sys
import time
import subprocess

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

def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout, r.returncode
    except: return "", 1

def scan_networks():
    out, _ = _run("netsh wlan show networks mode=bssid")
    networks = []
    current = {}
    for line in out.split('\n'):
        line = line.strip()
        if line.startswith("SSID") and "BSSID" not in line:
            if current.get("SSID"):
                networks.append(current)
            current = {"SSID": line.split(":")[-1].strip(), "Signal": "", "Auth": "", "Cipher": ""}
        elif "Signal" in line:
            current["Signal"] = line.split(":")[-1].strip()
        elif "Authentication" in line:
            current["Auth"] = line.split(":")[-1].strip()
        elif "Encryption" in line:
            current["Cipher"] = line.split(":")[-1].strip()
    if current.get("SSID"):
        networks.append(current)
    return networks

def scan_saved():
    out, _ = _run("netsh wlan show profiles")
    profiles = []
    for line in out.split('\n'):
        if "All User Profile" in line:
            name = line.split(":")[-1].strip()
            if name:
                profiles.append(name)
    results = []
    for name in profiles:
        out2, _ = _run(f'netsh wlan show profile name="{name}" key=clear')
        pwd = ""
        for line in out2.split('\n'):
            if "Key Content" in line:
                pwd = line.split(":")[-1].strip()
        auth = ""
        for line in out2.split('\n'):
            if "Authentication" in line:
                auth = line.split(":")[-1].strip()
        results.append({"SSID": name, "Password": pwd or "(none)", "Auth": auth})
    return results

def run(kevbin=None):
    while True:
        clear()
        cprint("  \033[93m\u2554" + "\u2550"*50 + "\u2557")
        cprint("  \033[93m\u2551       WIFI SCANNER                         \u2551")
        cprint("  \033[93m\u255a" + "\u2550"*50 + "\u255d")
        print()
        cprint("  \033[97m[1]  Scan Available Networks\033[0m")
        cprint("  \033[97m[2]  Show Saved Profiles + Passwords\033[0m")
        cprint("  \033[97m[3]  Scan + Export All\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0': return
        elif choice == '1':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  AVAILABLE NETWORKS\033[0m")
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[36m[*] Scanning...\033[0m")
            nets = scan_networks()
            if not nets:
                cprint("  \033[93m[X] No networks found\033[0m")
            else:
                for n in nets:
                    sig = n.get('Signal', '?')
                    bar_w = 10
                    try:
                        filled = int(float(sig.replace('%','')) / 100 * bar_w)
                    except: filled = 0
                    bar = "\033[92m" + "\u2588"*filled + "\033[90m" + "\u2591"*(bar_w-filled) + "\033[0m"
                    cprint(f"  \033[96m{n['SSID']:30}\033[0m {bar} {sig:5} | {n.get('Auth','')}")
        elif choice == '2':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  SAVED WIFI PROFILES\033[0m")
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[36m[*] Loading profiles...\033[0m")
            results = scan_saved()
            if not results:
                cprint("  \033[93m[X] No saved profiles\033[0m")
            else:
                for r in results:
                    pwd = r['Password']
                    color = "\033[92m" if pwd != "(none)" else "\033[90m"
                    cprint(f"  {color}{r['SSID']:30} {pwd:25} {r['Auth']}\033[0m")
                cprint(f"\n  \033[90m  Total: {len(results)} profiles\033[0m")
        elif choice == '3':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  FULL WIFI EXPORT\033[0m")
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[36m[*] Scanning...\033[0m")
            nets = scan_networks()
            saved = scan_saved()
            out_file = f"wifi_export_{int(time.time())}.txt"
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(f"WiFi Export — {time.strftime('%Y-%m-%d %H:%M:%S')}\n{'='*50}\n\n")
                f.write("SAVED PROFILES:\n")
                for r in saved:
                    f.write(f"  {r['SSID']:30} Password: {r['Password']:25} Auth: {r['Auth']}\n")
                f.write(f"\nAVAILABLE NETWORKS:\n")
                for n in nets:
                    f.write(f"  {n['SSID']:30} Signal: {n.get('Signal','?'):5} Auth: {n.get('Auth','')}\n")
            cprint(f"  \033[92m[X] Exported to {out_file}\033[0m")
            cprint(f"  \033[90m  Saved: {len(saved)} | Available: {len(nets)}\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m"); time.sleep(0.5)
        pause()

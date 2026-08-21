"""HWID Spoofer — Spoof Windows HWID identifiers with backup/restore."""

import os
import sys
import time
import uuid
import random
import string
import subprocess
import json

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

BACKUP_DIR = os.path.join(os.environ.get("APPDATA", "."), "KevTool_HWID_Backups")

def _run_ps(cmd):
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                           capture_output=True, text=True, timeout=15)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return str(e), 1

def _run_reg(cmd):
    try:
        r = subprocess.run(["reg", cmd], capture_output=True, text=True, timeout=10)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return str(e), 1

def _random_mac():
    return "02:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255), random.randint(0, 255),
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def _random_serial(length=20):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def _random_uuid():
    return str(uuid.uuid4()).upper()

def get_current_hwid():
    hwid = {}
    out, _ = _run_ps("Get-CimInstance Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID")
    hwid['UUID'] = out if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_BaseBoard | Select-Object -ExpandProperty SerialNumber")
    hwid['BaseBoard'] = out if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_BIOS | Select-Object -ExpandProperty SerialNumber")
    hwid['BIOS'] = out if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_Processor | Select-Object -ExpandProperty ProcessorId")
    hwid['CPU'] = out if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_DiskDrive | Select-Object -First 1 -ExpandProperty SerialNumber")
    hwid['Disk'] = out.strip() if out else "N/A"
    out, _ = _run_ps("(Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -First 1).MacAddress")
    hwid['MAC'] = out if out else "N/A"
    out, _ = _run_ps("[System.Environment]::GetEnvironmentVariable('COMPUTERNAME')")
    hwid['Hostname'] = out if out else "N/A"
    return hwid

def backup_hwid():
    if not os.path.isdir(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)
    hwid = get_current_hwid()
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(BACKUP_DIR, f"hwid_backup_{ts}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(hwid, f, indent=4)
    return path, hwid

def list_backups():
    if not os.path.isdir(BACKUP_DIR):
        return []
    backups = []
    for fname in sorted(os.listdir(BACKUP_DIR)):
        if fname.endswith('.json'):
            path = os.path.join(BACKUP_DIR, fname)
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                backups.append((fname, data, path))
            except: pass
    return backups

def restore_hwid(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return False, f"Failed to read backup: {e}"
    results = []
    mac = data.get('MAC', '')
    if mac and mac != "N/A":
        out, code = _run_ps(f"""$adapter = Get-NetAdapter | Where-Object {{$_.Status -eq 'Up'}} | Select-Object -First 1
if ($adapter) {{ Set-NetAdapter -Name $adapter.Name -MacAddress '{mac.replace(':', '-').upper()}' -Confirm:$false }}
""")
        results.append(f"MAC restore: {'OK' if code == 0 else 'FAILED'}")
    hostname = data.get('Hostname', '')
    if hostname and hostname != "N/A":
        out, code = _run_ps(f"""$current = [System.Environment]::GetEnvironmentVariable('COMPUTERNAME')
if ($current -ne '{hostname}') {{
    New-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\ComputerName\\ComputerName' -Name 'ComputerName' -Value '{hostname}' -Force -ErrorAction SilentlyContinue
}}
""")
        results.append(f"Hostname restore: {'OK' if code == 0 else 'FAILED'}")
    return True, results

def spoof_hwid(debug=False):
    results = []
    new_mac = _random_mac()
    if debug:
        results.append(f"[*] Generating random MAC: {new_mac}")
    out, code = _run_ps(f"""$adapter = Get-NetAdapter | Where-Object {{$_.Status -eq 'Up'}} | Select-Object -First 1
if ($adapter) {{
    Set-NetAdapter -Name $adapter.Name -MacAddress '{new_mac.replace(':', '-').upper()}' -Confirm:$false
    Write-Output "MAC_OK"
}} else {{
    Write-Output "MAC_FAIL_NO_ADAPTER"
}}""")
    if "MAC_OK" in out:
        results.append(f"[OK] MAC spoofed -> {new_mac}")
    else:
        results.append(f"[X] MAC spoof failed: {out[:60]}")

    new_uuid = _random_uuid()
    if debug:
        results.append(f"[*] Generating UUID: {new_uuid}")
    out, code = _run_ps(f"""$prod = Get-WmiObject Win32_ComputerSystemProduct
if ($prod) {{
    $prod.UUID = '{new_uuid}'
    $prod.Put() | Out-Null
    Write-Output "UUID_OK"
}} else {{
    Write-Output "UUID_FAIL"
}}""")
    if "UUID_OK" in out:
        results.append(f"[OK] UUID spoofed -> {new_uuid}")
    else:
        out2, code2 = _run_reg(f'add "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid /t REG_SZ /d "{new_uuid}" /f')
        if code2 == 0:
            results.append(f"[OK] MachineGuid spoofed -> {new_uuid}")
        else:
            results.append(f"[X] UUID spoof failed (registry fallback also failed)")

    new_serial = _random_serial(10)
    out, code = _run_reg(f'add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion" /v {"".join(random.choices(string.ascii_letters, k=8))} /t REG_SZ /d "{new_serial}" /f')
    if debug:
        results.append(f"[*] Registry noise entry written")

    new_hostname = "DESKTOP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
    if debug:
        results.append(f"[*] Generating hostname: {new_hostname}")
    results.append(f"[INFO] Hostname spoof requires reboot + admin")
    results.append(f"[INFO] New hostname would be: {new_hostname}")

    results.append(f"\n[*] Spoofed values:")
    results.append(f"    MAC:  {new_mac}")
    results.append(f"    UUID: {new_uuid}")
    results.append(f"    Serial: {new_serial}")
    results.append(f"    Hostname: {new_hostname}")
    results.append(f"\n[!] Some changes require reboot to take effect")
    return results


def run(kevbin=None):
    debug_mode = False
    while True:
        clear()
        dbg = " \033[91m[DEBUG]\033[0m" if debug_mode else ""
        cprint("  \033[93m\u2554" + "\u2550"*50 + "\u2557")
        cprint(f"  \033[93m\u2551       HWID SPOOFER{dbg}" + " "*(34-len(dbg)) + "\u2551")
        cprint("  \033[93m\u255a" + "\u2550"*50 + "\u255d")
        cprint("  \033[91m[!] Run as Administrator for full spoofing\033[0m")
        print()
        cprint("  \033[97m[1]  View Current HWID\033[0m")
        cprint("  \033[97m[2]  Backup Current HWID\033[0m")
        cprint("  \033[97m[3]  Spoof HWID (Random)\033[0m")
        cprint("  \033[97m[4]  Spoof HWID (Custom)\033[0m")
        cprint("  \033[97m[5]  Restore from Backup\033[0m")
        cprint("  \033[97m[6]  List Backups\033[0m")
        cprint("  \033[97m[7]  Toggle Debug Mode\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '7':
            debug_mode = not debug_mode
            state = "\033[92mON\033[0m" if debug_mode else "\033[91mOFF\033[0m"
            cprint(f"  Debug: {state}")
            time.sleep(0.5)
            continue
        elif choice == '1':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  CURRENT HWID\033[0m")
            cprint("  \033[93m\u2550"*54)
            if debug_mode:
                cprint("  \033[90m[DBG] Querying system identifiers...\033[0m")
            hwid = get_current_hwid()
            for key, val in hwid.items():
                cprint(f"  \033[96m{key:12}\033[0m: {val}")
            if debug_mode:
                cprint(f"  \033[90m[DBG] All queries complete\033[0m")
        elif choice == '2':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  BACKUP HWID\033[0m")
            cprint("  \033[93m\u2550"*54)
            if debug_mode:
                cprint("  \033[90m[DBG] Creating backup...\033[0m")
            path, hwid = backup_hwid()
            cprint(f"  \033[92m[X] Backup saved: {path}\033[0m")
            for key, val in hwid.items():
                cprint(f"  \033[90m{key:12}: {val}\033[0m")
            if debug_mode:
                cprint(f"  \033[90m[DBG] File size: {os.path.getsize(path)} bytes\033[0m")
        elif choice == '3':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  SPOOF HWID (RANDOM)\033[0m")
            cprint("  \033[93m\u2550"*54)
            if debug_mode:
                cprint("  \033[90m[DBG] Starting spoof routine...\033[0m")
            results = spoof_hwid(debug=debug_mode)
            for line in results:
                if "[OK]" in line:
                    cprint(f"  \033[92m{line}\033[0m")
                elif "[X]" in line:
                    cprint(f"  \033[91m{line}\033[0m")
                elif "[!]" in line:
                    cprint(f"  \033[93m{line}\033[0m")
                else:
                    cprint(f"  \033[90m{line}\033[0m")
        elif choice == '4':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  SPOOF HWID (CUSTOM)\033[0m")
            cprint("  \033[93m\u2550"*54)
            mac = prompt("  \033[96mCustom MAC (empty=random): \033[0m").strip()
            uuid_val = prompt("  \033[96mCustom UUID (empty=random): \033[0m").strip()
            serial = prompt("  \033[96mCustom Serial (empty=random): \033[0m").strip()
            hostname = prompt("  \033[96mCustom Hostname (empty=random): \033[0m").strip()
            if debug_mode:
                cprint(f"  \033[90m[DBG] MAC={mac or 'random'} UUID={uuid_val or 'random'}\033[0m")
            results = []
            target_mac = mac if mac else _random_mac()
            target_uuid = uuid_val if uuid_val else _random_uuid()
            target_serial = serial if serial else _random_serial(10)
            target_host = hostname if hostname else "DESKTOP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            out, code = _run_ps(f"""$adapter = Get-NetAdapter | Where-Object {{$_.Status -eq 'Up'}} | Select-Object -First 1
if ($adapter) {{ Set-NetAdapter -Name $adapter.Name -MacAddress '{target_mac.replace(':', '-').upper()}' -Confirm:$false }}""")
            results.append(f"[{'OK' if code == 0 else 'X'}] MAC -> {target_mac}")
            out, code = _run_reg(f'add "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid /t REG_SZ /d "{target_uuid}" /f')
            results.append(f"[{'OK' if code == 0 else 'X'}] UUID -> {target_uuid}")
            results.append(f"[*] Serial -> {target_serial}")
            results.append(f"[*] Hostname -> {target_host} (requires reboot)")
            for line in results:
                if "[OK]" in line:
                    cprint(f"  \033[92m{line}\033[0m")
                elif "[X]" in line:
                    cprint(f"  \033[91m{line}\033[0m")
                else:
                    cprint(f"  \033[90m{line}\033[0m")
        elif choice == '5':
            clear()
            backups = list_backups()
            if not backups:
                cprint("  \033[93m[X] No backups found\033[0m"); pause(); continue
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  RESTORE FROM BACKUP\033[0m")
            cprint("  \033[93m\u2550"*54)
            for i, (fname, data, path) in enumerate(backups):
                ts = fname.replace("hwid_backup_", "").replace(".json", "")
                cprint(f"  \033[97m[{i+1}]  {ts}  MAC: {data.get('MAC','?')[:17]}\033[0m")
            print()
            sel = prompt(f"  \033[96mSelect (1-{len(backups)}): \033[0m").strip()
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(backups):
                    if debug_mode:
                        cprint(f"  \033[90m[DBG] Restoring from {backups[idx][0]}\033[0m")
                    ok, msg = restore_hwid(backups[idx][2])
                    if ok:
                        cprint(f"  \033[92m[X] Restored\033[0m")
                        for line in msg:
                            cprint(f"  \033[90m{line}\033[0m")
                    else:
                        cprint(f"  \033[91m[X] {msg}\033[0m")
                else:
                    cprint("  \033[91m[X] Invalid selection\033[0m")
            except: cprint("  \033[91m[X] Invalid input\033[0m")
        elif choice == '6':
            clear()
            backups = list_backups()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  HWID BACKUPS\033[0m")
            cprint("  \033[93m\u2550"*54)
            if not backups:
                cprint("  \033[93mNo backups found\033[0m")
            else:
                for fname, data, path in backups:
                    ts = fname.replace("hwid_backup_", "").replace(".json", "")
                    cprint(f"  \033[90m{ts}  UUID: {data.get('UUID','?')[:8]}...  MAC: {data.get('MAC','?')[:17]}\033[0m")
                cprint(f"\n  \033[90mBackup dir: {BACKUP_DIR}\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

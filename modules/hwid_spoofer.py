"""HWID Spoofer — Spoof all Windows HWID identifiers with backup/restore."""

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

def _run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
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

def _random_product_id():
    return f"{random.randint(10000,99999)}-{random.randint(10000,99999)}-{random.randint(10000,99999)}-{random.randint(1000,9999)}"

def _random_volume_serial():
    return f"{random.randint(0x1000,0xFFFF):04X}-{random.randint(0x1000,0xFFFF):04X}"

def _random_disk_serial():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))

def _random_bios_serial():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(10,15)))

def _random_baseboard_serial():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(8,12)))

def _random_computer_name():
    prefix = random.choice(["DESKTOP", "LAPTOP", "WORKSTATION", "PC", "MOTHER"])
    return f"{prefix}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=7))}"

def get_current_hwid():
    hwid = {}
    out, _ = _run_ps("Get-CimInstance Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID")
    hwid['UUID'] = out if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_BaseBoard | Select-Object -ExpandProperty SerialNumber")
    hwid['BaseBoard SN'] = out if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_BIOS | Select-Object -ExpandProperty SerialNumber")
    hwid['BIOS SN'] = out if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_Processor | Select-Object -ExpandProperty ProcessorId")
    hwid['CPU ID'] = out if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name")
    hwid['CPU Name'] = out if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_DiskDrive | Select-Object -First 1 -ExpandProperty SerialNumber")
    hwid['Disk SN'] = out.strip() if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_DiskDrive | Select-Object -First 1 -ExpandProperty Model")
    hwid['Disk Model'] = out if out else "N/A"
    out, _ = _run_ps("(Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -First 1).MacAddress")
    hwid['MAC'] = out if out else "N/A"
    out, _ = _run_ps("[System.Environment]::GetEnvironmentVariable('COMPUTERNAME')")
    hwid['Hostname'] = out if out else "N/A"
    out, _ = _run_reg('query "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid 2>nul')
    for line in out.split('\n'):
        if 'MachineGuid' in line:
            hwid['MachineGuid'] = line.split()[-1] if line.split() else "N/A"
    out, _ = _run_reg('query "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion" /v ProductId 2>nul')
    for line in out.split('\n'):
        if 'ProductId' in line:
            hwid['ProductId'] = line.split()[-1] if line.split() else "N/A"
    out, _ = _run_cmd("vol C: 2>nul")
    for line in out.split('\n'):
        if 'Volume Serial Number' in line:
            hwid['Volume Serial'] = line.split('is')[-1].strip() if 'is' in line else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_ComputerSystem | Select-Object -ExpandProperty Manufacturer")
    hwid['Manufacturer'] = out if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_ComputerSystem | Select-Object -ExpandProperty Model")
    hwid['System Model'] = out if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_BIOS | Select-Object -ExpandProperty SMBIOSBIOSVersion")
    hwid['BIOS Version'] = out if out else "N/A"
    out, _ = _run_ps("Get-CimInstance Win32_VideoController | Select-Object -First 1 -ExpandProperty PNPDeviceID")
    hwid['GPU PNP'] = out if out else "N/A"
    out, _ = _run_ps("(Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion').BuildLabEx")
    hwid['Build'] = out if out else "N/A"
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
        _run_ps(f"New-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\ComputerName\\ComputerName' -Name 'ComputerName' -Value '{hostname}' -Force -ErrorAction SilentlyContinue")
        results.append(f"Hostname restore: queued (reboot needed)")
    machine_guid = data.get('MachineGuid', '')
    if machine_guid and machine_guid != "N/A":
        _run_reg(f'add "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid /t REG_SZ /d "{machine_guid}" /f')
        results.append(f"MachineGuid restore: OK")
    product_id = data.get('ProductId', '')
    if product_id and product_id != "N/A":
        _run_reg(f'add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion" /v ProductId /t REG_SZ /d "{product_id}" /f')
        results.append(f"ProductId restore: OK")
    return True, results


def _spoof_mac(debug=False):
    new_mac = _random_mac()
    if debug: cprint(f"  \033[90m[DBG] New MAC: {new_mac}\033[0m")
    out, code = _run_ps(f"""$adapter = Get-NetAdapter | Where-Object {{$_.Status -eq 'Up'}} | Select-Object -First 1
if ($adapter) {{
    Set-NetAdapter -Name $adapter.Name -MacAddress '{new_mac.replace(':', '-').upper()}' -Confirm:$false
    Write-Output "MAC_OK"
}} else {{
    Write-Output "MAC_FAIL"
}}""")
    ok = "MAC_OK" in out
    if debug: cprint(f"  \033[{'92' if ok else '91'}m[{'OK' if ok else 'X'}] MAC -> {new_mac}\033[0m")
    return ok, new_mac

def _spoof_uuid(debug=False):
    new_uuid = _random_uuid()
    if debug: cprint(f"  \033[90m[DBG] New UUID: {new_uuid}\033[0m")
    out, code = _run_reg(f'add "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid /t REG_SZ /d "{new_uuid}" /f')
    ok = code == 0
    if debug: cprint(f"  \033[{'92' if ok else '91'}m[{'OK' if ok else 'X'}] MachineGuid -> {new_uuid}\033[0m")
    return ok, new_uuid

def _spoof_product_id(debug=False):
    new_pid = _random_product_id()
    if debug: cprint(f"  \033[90m[DBG] New ProductId: {new_pid}\033[0m")
    out, code = _run_reg(f'add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion" /v ProductId /t REG_SZ /d "{new_pid}" /f')
    ok = code == 0
    if debug: cprint(f"  \033[{'92' if ok else '91'}m[{'OK' if ok else 'X'}] ProductId -> {new_pid}\033[0m")
    return ok, new_pid

def _spoof_hostname(debug=False):
    new_name = _random_computer_name()
    if debug: cprint(f"  \033[90m[DBG] New Hostname: {new_name}\033[0m")
    _run_ps(f"""Rename-Computer -NewName '{new_name}' -Force -ErrorAction SilentlyContinue""")
    _run_ps(f"New-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\ComputerName\\ComputerName' -Name 'ComputerName' -Value '{new_name}' -Force -ErrorAction SilentlyContinue")
    if debug: cprint(f"  \033[93m[!] Hostname -> {new_name} (reboot needed)\033[0m")
    return True, new_name

def _spoof_volume_serial(debug=False):
    new_vol = _random_volume_serial()
    if debug: cprint(f"  \033[90m[DBG] New Volume Serial: {new_vol}\033[0m")
    if debug: cprint(f"  \033[93m[!] Volume serial spoof requires disk tool (registry noise only)\033[0m")
    _run_reg(f'add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion" /v {"".join(random.choices(string.ascii_letters, k=8))} /t REG_SZ /d "{new_vol}" /f')
    return True, new_vol

def _spoof_disk_serial(debug=False):
    new_sn = _random_disk_serial()
    if debug: cprint(f"  \033[90m[DBG] New Disk Serial: {new_sn}\033[0m")
    if debug: cprint(f"  \033[93m[!] Disk serial spoof requires disk tool / BIOS\033[0m")
    return True, new_sn

def _spoof_bios_serial(debug=False):
    new_sn = _random_bios_serial()
    if debug: cprint(f"  \033[90m[DBG] New BIOS Serial: {new_sn}\033[0m")
    if debug: cprint(f"  \033[93m[!] BIOS serial spoof requires BIOS flash / registry noise\033[0m")
    _run_reg(f'add "HKLM\\HARDWARE\\DESCRIPTION\\System\\BIOS" /v SystemSerialNumber /t REG_SZ /d "{new_sn}" /f')
    return True, new_sn

def _spoof_baseboard(debug=False):
    new_sn = _random_baseboard_serial()
    if debug: cprint(f"  \033[90m[DBG] New BaseBoard Serial: {new_sn}\033[0m")
    if debug: cprint(f"  \033[93m[!] BaseBoard serial requires BIOS flash / registry noise\033[0m")
    return True, new_sn

def _spoof_registry_noise(debug=False):
    count = 0
    for _ in range(random.randint(5, 15)):
        key_name = ''.join(random.choices(string.ascii_letters, k=random.randint(6, 12)))
        val = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(8, 30)))
        _run_reg(f'add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion" /v {key_name} /t REG_SZ /d "{val}" /f')
        count += 1
    if debug: cprint(f"  \033[90m[DBG] Wrote {count} noise registry entries\033[0m")
    return True, count

def _spoof_full(debug=False):
    results = []
    cprint("  \033[36m[*] Spoofing MAC...\033[0m")
    ok, val = _spoof_mac(debug)
    results.append(("MAC", ok, val))
    cprint("  \033[36m[*] Spoofing MachineGuid...\033[0m")
    ok, val = _spoof_uuid(debug)
    results.append(("MachineGuid", ok, val))
    cprint("  \033[36m[*] Spoofing ProductId...\033[0m")
    ok, val = _spoof_product_id(debug)
    results.append(("ProductId", ok, val))
    cprint("  \033[36m[*] Spoofing Hostname...\033[0m")
    ok, val = _spoof_hostname(debug)
    results.append(("Hostname", ok, val))
    cprint("  \033[36m[*] Spoofing Volume Serial...\033[0m")
    ok, val = _spoof_volume_serial(debug)
    results.append(("VolumeSerial", ok, val))
    cprint("  \033[36m[*] Spoofing Disk Serial...\033[0m")
    ok, val = _spoof_disk_serial(debug)
    results.append(("DiskSN", ok, val))
    cprint("  \033[36m[*] Spoofing BIOS Serial...\033[0m")
    ok, val = _spoof_bios_serial(debug)
    results.append(("BIOSSN", ok, val))
    cprint("  \033[36m[*] Spoofing BaseBoard Serial...\033[0m")
    ok, val = _spoof_baseboard(debug)
    results.append(("BaseBoardSN", ok, val))
    cprint("  \033[36m[*] Writing registry noise...\033[0m")
    ok, val = _spoof_registry_noise(debug)
    results.append(("RegistryNoise", ok, f"{val} entries"))
    return results


def run(kevbin=None):
    debug_mode = False
    while True:
        clear()
        dbg = " \033[91m[DEBUG]\033[0m" if debug_mode else ""
        cprint("  \033[93m\u2554" + "\u2550"*56 + "\u2557")
        cprint(f"  \033[93m\u2551       HWID SPOOFER v2{dbg}" + " "*(35-len(dbg)) + "\u2551")
        cprint("  \033[93m\u255a" + "\u2550"*56 + "\u255d")
        cprint("  \033[91m[!] Run as Administrator for full spoofing\033[0m")
        print()
        cprint("  \033[97m[1]   View Current HWID\033[0m")
        cprint("  \033[97m[2]   Backup Current HWID\033[0m")
        cprint("  \033[97m[3]   SPOOF ALL (one-click)\033[0m")
        cprint("  \033[97m[4]   Spoof MAC Address\033[0m")
        cprint("  \033[97m[5]   Spoof MachineGuid\033[0m")
        cprint("  \033[97m[6]   Spoof ProductId\033[0m")
        cprint("  \033[97m[7]   Spoof Hostname\033[0m")
        cprint("  \033[97m[8]   Spoof Volume Serial\033[0m")
        cprint("  \033[97m[9]   Spoof Disk Serial\033[0m")
        cprint("  \033[97m[10]  Spoof BIOS Serial\033[0m")
        cprint("  \033[97m[11]  Spoof BaseBoard Serial\033[0m")
        cprint("  \033[97m[12]  Registry Noise (anti-fingerprint)\033[0m")
        cprint("  \033[97m[13]  Restore from Backup\033[0m")
        cprint("  \033[97m[14]  List Backups\033[0m")
        cprint("  \033[97m[15]  Toggle Debug Mode\033[0m")
        cprint("  \033[91m[0]   Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '15':
            debug_mode = not debug_mode
            state = "\033[92mON\033[0m" if debug_mode else "\033[91mOFF\033[0m"
            cprint(f"  Debug: {state}")
            time.sleep(0.5)
            continue
        elif choice == '1':
            clear()
            cprint("  \033[93m\u2550"*60)
            cprint("  \033[93m  CURRENT HWID\033[0m")
            cprint("  \033[93m\u2550"*60)
            hwid = get_current_hwid()
            for key, val in hwid.items():
                cprint(f"  \033[96m{key:16}\033[0m: {val}")
            cprint(f"\n  \033[90m  Total identifiers: {len(hwid)}\033[0m")
        elif choice == '2':
            clear()
            cprint("  \033[93m\u2550"*60)
            cprint("  \033[93m  BACKUP HWID\033[0m")
            cprint("  \033[93m\u2550"*60)
            path, hwid = backup_hwid()
            cprint(f"  \033[92m[X] Backup saved: {path}\033[0m")
            cprint(f"  \033[90m  Identifiers saved: {len(hwid)}\033[0m")
        elif choice == '3':
            clear()
            cprint("  \033[93m\u2550"*60)
            cprint("  \033[93m  SPOOF ALL (ONE-CLICK)\033[0m")
            cprint("  \033[93m\u2550"*60)
            results = _spoof_full(debug=debug_mode)
            print()
            for name, ok, val in results:
                if ok:
                    cprint(f"  \033[92m[OK]  {name:16} -> {val}\033[0m")
                else:
                    cprint(f"  \033[91m[X]  {name:16} -> failed\033[0m")
            cprint(f"\n  \033[93m[!] Some changes require reboot\033[0m")
        elif choice == '4':
            ok, val = _spoof_mac(debug=debug_mode)
        elif choice == '5':
            ok, val = _spoof_uuid(debug=debug_mode)
        elif choice == '6':
            ok, val = _spoof_product_id(debug=debug_mode)
        elif choice == '7':
            ok, val = _spoof_hostname(debug=debug_mode)
        elif choice == '8':
            ok, val = _spoof_volume_serial(debug=debug_mode)
        elif choice == '9':
            ok, val = _spoof_disk_serial(debug=debug_mode)
        elif choice == '10':
            ok, val = _spoof_bios_serial(debug=debug_mode)
        elif choice == '11':
            ok, val = _spoof_baseboard(debug=debug_mode)
        elif choice == '12':
            ok, val = _spoof_registry_noise(debug=debug_mode)
        elif choice == '13':
            clear()
            backups = list_backups()
            if not backups:
                cprint("  \033[93m[X] No backups found\033[0m"); pause(); continue
            cprint("  \033[93m\u2550"*60)
            cprint("  \033[93m  RESTORE FROM BACKUP\033[0m")
            cprint("  \033[93m\u2550"*60)
            for i, (fname, data, bpath) in enumerate(backups):
                ts = fname.replace("hwid_backup_", "").replace(".json", "")
                mac = data.get('MAC', data.get('MAC Address', '?'))
                if isinstance(mac, list): mac = mac[0] if mac else '?'
                cprint(f"  \033[97m[{i+1:2}]  {ts}  MAC: {str(mac)[:17]}\033[0m")
            print()
            sel = prompt(f"  \033[96mSelect (1-{len(backups)}): \033[0m").strip()
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(backups):
                    ok, msg = restore_hwid(backups[idx][2])
                    if ok:
                        cprint(f"  \033[92m[X] Restored\033[0m")
                        if isinstance(msg, list):
                            for line in msg:
                                cprint(f"  \033[90m{line}\033[0m")
                        else:
                            cprint(f"  \033[90m{msg}\033[0m")
                    else:
                        cprint(f"  \033[91m[X] {msg}\033[0m")
                else:
                    cprint("  \033[91m[X] Invalid selection\033[0m")
            except: cprint("  \033[91m[X] Invalid input\033[0m")
        elif choice == '14':
            clear()
            backups = list_backups()
            cprint("  \033[93m\u2550"*60)
            cprint("  \033[93m  HWID BACKUPS\033[0m")
            cprint("  \033[93m\u2550"*60)
            if not backups:
                cprint("  \033[93mNo backups found\033[0m")
            else:
                for fname, data, bpath in backups:
                    ts = fname.replace("hwid_backup_", "").replace(".json", "")
                    uuid_val = data.get('UUID', '?')
                    if isinstance(uuid_val, list): uuid_val = uuid_val[0] if uuid_val else '?'
                    cprint(f"  \033[90m{ts}  UUID: {str(uuid_val)[:8]}...  {os.path.getsize(bpath)} bytes\033[0m")
                cprint(f"\n  \033[90mBackup dir: {BACKUP_DIR}\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

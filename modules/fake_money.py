import os
import sys
import secrets
import random
import string
import time

try:
    import kevbin
    from kevbin import box_table, box, txt, num, head, sub, prompt, cprint, color
except ImportError:
    class _C:
        def __getattr__(self, _): return lambda *a, **kw: None
    kevbin = _C()
    def box_table(*a, **kw): pass
    def box(*a, **kw): pass
    def txt(*a): return str(a)
    def num(*a): return str(a)
    def head(*a): return str(a)
    def sub(*a): return str(a)
    def prompt(*a): return input()
    def cprint(*a, **kw): print(*[x for x in a if isinstance(x, str)])

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    try:
        kevbin.pause()
    except:
        input("\n\033[90mPress Enter to continue...\033[0m")

CURRENCIES = {
    "USD": {"name": "US Dollar", "symbol": "$", "denoms": [1, 2, 5, 10, 20, 50, 100]},
    "EUR": {"name": "Euro", "symbol": "\u20ac", "denoms": [5, 10, 20, 50, 100, 200, 500]},
    "GBP": {"name": "British Pound", "symbol": "\u00a3", "denoms": [5, 10, 20, 50, 100]},
    "JPY": {"name": "Japanese Yen", "symbol": "\u00a5", "denoms": [1000, 5000, 10000]},
    "CAD": {"name": "Canadian Dollar", "symbol": "C$", "denoms": [5, 10, 20, 50, 100]},
    "AUD": {"name": "Australian Dollar", "symbol": "A$", "denoms": [5, 10, 20, 50, 100]},
    "CHF": {"name": "Swiss Franc", "symbol": "CHF", "denoms": [10, 20, 50, 100, 200]},
    "INR": {"name": "Indian Rupee", "symbol": "\u20b9", "denoms": [10, 20, 50, 100, 200, 500, 2000]},
    "BTC": {"name": "Bitcoin (sim)", "symbol": "\u20bf", "denoms": [0.001, 0.01, 0.1, 1]},
    "RUB": {"name": "Russian Ruble", "symbol": "\u20bd", "denoms": [50, 100, 200, 500, 1000]},
}

PORTRAITS = [
    "J. Morrison", "R. Hayes", "T. Sterling", "D. Washington", "L. Park",
    "M. Chen", "A. Blackwell", "S. Nkomo", "K. Tanaka", "J. Rodriguez",
    "C. Anderson", "W. Okafor", "B. Lindqvist", "E. Dubois", "F. Santos",
]

USD_COLORS = {
    1: ("\033[37m", "George Washington", "One Dollar Bill"),
    2: ("\033[32m", "Thomas Jefferson", "Two Dollar Bill"),
    5: ("\033[33m", "Abraham Lincoln", "Five Dollar Bill"),
    10: ("\033[36m", "Alexander Hamilton", "Ten Dollar Bill"),
    20: ("\033[33m", "Andrew Jackson", "Twenty Dollar Bill"),
    50: ("\033[35m", "Ulysses S. Grant", "Fifty Dollar Bill"),
    100: ("\033[33m", "Benjamin Franklin", "One Hundred Dollar Bill"),
}

TREASURERS = ["J. Carranza", "S. Mnuchin", "R.G. Rios", "L.W. Lew", "H. Paulson", "J.W. Snow"]

def gen_serial():
    prefix = random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
    region = random.randint(1, 12)
    nums = ''.join(random.choices("0123456789", k=8))
    return f"{prefix}{region:02d}{nums}{random.choice('ABCD')}"

def gen_seal():
    return str(random.randint(10000000, 99999999))

def render_bill(denom, currency="USD"):
    cur = CURRENCIES[currency]
    serial = gen_serial()
    seal = gen_seal()
    treasurer = random.choice(TREASURERS)
    if currency == "USD" and denom in USD_COLORS:
        cc, person, bill_name = USD_COLORS[denom]
    else:
        cc = "\033[33m"
        person = random.choice(PORTRAITS)
        bill_name = f"{cur['symbol']}{denom} Note"
    w = 60
    border_h = "\u2550" * w
    print()
    cprint(f"  \u2554{border_h}\u2557", cc)
    cprint(f"  \u2551{'':^{w}}\u2551", cc)
    cprint(f"  \u2551   {bill_name:<35}  {cur['name']:>16}  \u2551", cc)
    cprint(f"  \u2551{'':^{w}}\u2551", cc)
    cprint(f"  \u2551   SERIAL: {serial:<18}  SEAL: {seal:<14}    \u2551", cc)
    cprint(f"  \u2551{'':^{w}}\u2551", cc)
    cprint(f"  \u2551   {person:^{w-4}}  \u2551", cc)
    cprint(f"  \u2551{'':^{w}}\u2551", cc)
    cprint(f"  \u2551   {cur['symbol']}{denom:^{w-5}}  \u2551", cc)
    cprint(f"  \u2551{'':^{w}}\u2551", cc)
    cprint(f"  \u2551   Treasurer: {treasurer:<{w-14}}  \u2551", cc)
    cprint(f"  \u2551{'':^{w}}\u2551", cc)
    cprint(f"  \u2551   \033[90m[ FOR LARP / PROP / SIMULATION USE ONLY ]\033[0m{'':<{w-44}}  \u2551", cc)
    cprint(f"  \u255a{border_h}\u255d", cc)
    print()
    return serial

def render_stack(denom, count, currency="USD"):
    cur = CURRENCIES[currency]
    print()
    cprint(f"  === {count}x {cur['symbol']}{denom} {cur['name']} Bills ===", "cyan")
    print()
    total = 0
    for i in range(min(count, 5)):
        s = gen_serial()
        cprint(f"    Bill {i+1}: Serial {s}  |  {cur['symbol']}{denom}  |  {random.choice(PORTRAITS)}", "yellow")
        total += denom
    if count > 5:
        cprint(f"    ... and {count - 5} more bills", "yellow")
        total = denom * count
    cprint(f"\n  Total face value: {cur['symbol']}{total:,.2f}", "green")
    print()

def counterfeit_check():
    print()
    cprint("  \u2554" + "\u2550" * 50 + "\u2557", "red")
    cprint("  \u2551          COUNTERFEIT DETECTION REPORT             \u2551", "red")
    cprint("  \u255a" + "\u2550" * 50 + "\u255d", "red")
    print()
    checks = [
        ("Paper texture", ["PASS","PASS","PASS","SUSPICIOUS"]),
        ("Watermark", ["PASS","PASS","PASS","MISSING"]),
        ("Security thread", ["PASS","PASS","PASS","ABSENT"]),
        ("Color-shifting ink", ["PASS","PASS","SUSPICIOUS","MISSING"]),
        ("Micro-printing", ["PASS","PASS","PASS","BLURRY"]),
        ("3D security ribbon", ["PASS","ABSENT","MISSING","PASS"]),
        ("Raised print", ["PASS","PASS","FLAT","PASS"]),
        ("UV fluorescence", ["PASS","PASS","PASS","WRONG COLOR"]),
        ("IR reflectivity", ["PASS","FAIL","PASS","PASS"]),
        ("Size check", ["PASS","PASS","PASS","WRONG SIZE"]),
    ]
    fails = 0
    for name, opts in checks:
        result = random.choice(opts)
        color = "green" if result == "PASS" else "red"
        if result != "PASS":
            fails += 1
        cprint(f"    {name:<25} [{result}]", color)
    print()
    if fails == 0:
        cprint("  Result: ALL CHECKS PASSED (simulated)", "green")
    elif fails <= 2:
        cprint(f"  Result: {fails} SUSPICIOUS \u2014 manual inspection recommended", "yellow")
    else:
        cprint(f"  Result: {fails} FAILURES \u2014 likely counterfeit", "red")
    cprint("\n  \033[90m(This is a simulation \u2014 no actual detection is performed)\033[0m")
    print()

def money_counter(bills):
    cprint("\n  === MONEY COUNTER ===", "cyan")
    total = sum(bills)
    counts = {}
    for b in bills:
        counts[b] = counts.get(b, 0) + 1
    print()
    for d in sorted(counts.keys()):
        c = counts[d]
        cprint(f"    {d:>8} x {c:>4} = {d*c:>12,.2f}", "yellow")
    cprint(f"\n    {'TOTAL':>8}   {len(bills):>4}   {total:>12,.2f}", "green")
    print()

def run():
    while True:
        clear()
        cprint("  \u2554" + "\u2550" * 50 + "\u2557", "yellow")
        cprint("  \u2551           FAKE MONEY GENERATOR                  \u2551", "yellow")
        cprint("  \u2551           LARP / PROP / SIMULATION              \u2551", "yellow")
        cprint("  \u255a" + "\u2550" * 50 + "\u255d", "yellow")
        print()
        cprint("  [1]  Generate a single bill", "white")
        cprint("  [2]  Generate stack of bills", "white")
        cprint("  [3]  Custom bill (name + value)", "white")
        cprint("  [4]  Money counter", "white")
        cprint("  [5]  Counterfeit detection test", "white")
        cprint("  [6]  Batch generate (save to file)", "white")
        cprint("  [7]  Multi-currency overview", "white")
        cprint("  [8]  Casino chip generator", "white")
        cprint("  [9]  Check / gift card generator", "white")
        cprint("  [0]  Back", "red")
        print()
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '1':
            print()
            cprint("  Available currencies:", "cyan")
            keys = list(CURRENCIES.keys())
            for i, k in enumerate(keys, 1):
                c = CURRENCIES[k]
                cprint(f"    [{i}] {k} \u2014 {c['name']} ({c['symbol']})", "white")
            ci = prompt("\033[33m  currency > \033[0m")
            try:
                currency = keys[int(ci)-1]
            except:
                currency = "USD"
            cur = CURRENCIES[currency]
            print(f"\n  Denominations: {cur['denoms']}")
            di = prompt("\033[33m  denomination > \033[0m")
            try:
                denom = float(di)
            except:
                denom = cur['denoms'][0]
            clear()
            render_bill(denom, currency)
            pause()
        elif choice == '2':
            print()
            keys = list(CURRENCIES.keys())
            for i, k in enumerate(keys, 1):
                c = CURRENCIES[k]
                cprint(f"    [{i}] {k} \u2014 {c['name']}", "white")
            ci = prompt("\033[33m  currency > \033[0m")
            try:
                currency = keys[int(ci)-1]
            except:
                currency = "USD"
            cur = CURRENCIES[currency]
            di = prompt("\033[33m  denomination > \033[0m")
            try:
                denom = float(di)
            except:
                denom = cur['denoms'][0]
            ni = prompt("\033[33m  count (1-100) > \033[0m")
            try:
                count = max(1, min(100, int(ni)))
            except:
                count = 10
            clear()
            render_stack(denom, count, currency)
            pause()
        elif choice == '3':
            name = prompt("\033[33m  bill name > \033[0m") or "FEDERAL RESERVE NOTE"
            val = prompt("\033[33m  face value > \033[0m") or "100"
            person = prompt("\033[33m  portrait > \033[0m") or random.choice(PORTRAITS)
            serial = gen_serial()
            clear()
            w = 60
            print()
            cprint(f"  \u2554{'='*w}\u2557", "yellow")
            cprint(f"  \u2551{'':^{w}}\u2551", "yellow")
            cprint(f"  \u2551   {name.upper():<{w-4}}  \u2551", "yellow")
            cprint(f"  \u2551{'':^{w}}\u2551", "yellow")
            cprint(f"  \u2551   SERIAL: {serial:<{w-8}}  \u2551", "yellow")
            cprint(f"  \u2551{'':^{w}}\u2551", "yellow")
            cprint(f"  \u2551   {person:^{w-4}}  \u2551", "yellow")
            cprint(f"  \u2551{'':^{w}}\u2551", "yellow")
            cprint(f"  \u2551   {val:^{w-4}}  \u2551", "yellow")
            cprint(f"  \u2551{'':^{w}}\u2551", "yellow")
            cprint(f"  \u2551   \033[90m[ FOR LARP / PROP / SIMULATION USE ONLY ]\033[0m{'':<{w-44}}  \u2551", "yellow")
            cprint(f"  \u255a{'='*w}\u255d", "yellow")
            print()
            pause()
        elif choice == '4':
            print()
            cprint("  Enter bills (comma-separated, e.g. 20,20,50,100,5)", "cyan")
            raw = prompt("\033[33m  bills > \033[0m")
            try:
                bills = [float(x.strip()) for x in raw.split(",") if x.strip()]
            except:
                bills = [20, 20, 50, 100, 5]
            clear()
            money_counter(bills)
            pause()
        elif choice == '5':
            clear()
            counterfeit_check()
            pause()
        elif choice == '6':
            try:
                count = int(prompt("\033[33m  how many? (1-500) > \033[0m"))
                count = max(1, min(500, count))
            except:
                count = 50
            fname = prompt("\033[33m  filename (default: fake_money.txt) > \033[0m") or "fake_money.txt"
            lines = [f"=== FAKE MONEY BATCH \u2014 {time.strftime('%Y-%m-%d %H:%M:%S')} ==="]
            lines.append("=== SIMULATED PROP MONEY FOR LARP/TESTING ===\n")
            for i in range(count):
                currency = random.choice(list(CURRENCIES.keys()))
                cur = CURRENCIES[currency]
                denom = random.choice(cur['denoms'])
                serial = gen_serial()
                portrait = random.choice(PORTRAITS)
                lines.append(f"Bill {i+1}: {currency} {cur['symbol']}{denom}  Serial: {serial}  Portrait: {portrait}")
            with open(fname, 'w') as f:
                f.write('\n'.join(lines))
            clear()
            cprint(f"\n  Saved {count} fake bills to {fname}", "green")
            pause()
        elif choice == '7':
            clear()
            print()
            cprint("  \u2554" + "\u2550" * 70 + "\u2557", "cyan")
            cprint("  \u2551              MULTI-CURRENCY OVERVIEW                              \u2551", "cyan")
            cprint("  \u255a" + "\u2550" * 70 + "\u255d", "cyan")
            print()
            cprint(f"  {'Code':<6} {'Name':<25} {'Symbol':<8} {'Denominations'}", "cyan")
            cprint("  " + "-" * 70, "white")
            for code, data in CURRENCIES.items():
                denoms = ", ".join(str(d) for d in data['denoms'])
                cprint(f"  {code:<6} {data['name']:<25} {data['symbol']:<8} {denoms}", "white")
            print()
            pause()
        elif choice == '8':
            clear()
            print()
            chip_colors = ["\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[35m", "\033[36m"]
            chip_values = [1, 5, 10, 25, 50, 100, 500, 1000]
            cprint("  \u2554" + "\u2550" * 50 + "\u2557", "yellow")
            cprint("  \u2551            CASINO CHIP GENERATOR               \u2551", "yellow")
            cprint("  \u255a" + "\u2550" * 50 + "\u255d", "yellow")
            print()
            for val in chip_values:
                col = random.choice(chip_colors)
                cid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                cprint(f"    {col}\u25cf \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 \u25cf\033[0m")
                cprint(f"    {col}\u2502  CASINO ROYALE          \u2502\033[0m")
                cprint(f"    {col}\u2502                         \u2502\033[0m")
                cprint(f"    {col}\u2502       ${val:>6,}            \u2502\033[0m")
                cprint(f"    {col}\u2502                         \u2502\033[0m")
                cprint(f"    {col}\u2502  ID: {cid}      \u2502\033[0m")
                cprint(f"    {col}\u25cf \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 \u25cf\033[0m")
                print()
            pause()
        elif choice == '9':
            clear()
            print()
            cprint("  \u2554" + "\u2550" * 50 + "\u2557", "cyan")
            cprint("  \u2551         CHECK / GIFT CARD GENERATOR              \u2551", "cyan")
            cprint("  \u255a" + "\u2550" * 50 + "\u255d", "cyan")
            print()
            card_types = ["VISA GIFT CARD", "MASTERCARD GIFT", "AMAZON GIFT CARD", "STEAM GIFT CARD",
                          "APPLE GIFT CARD", "GOOGLE PLAY CARD", "XBOX GIFT CARD", "PSN GIFT CARD",
                          "NETFLIX GIFT CARD", "DISNEY+ GIFT CARD", "CUSTOM CHECK"]
            cprint("  Card types:", "cyan")
            for i, ct in enumerate(card_types, 1):
                cprint(f"    [{i}] {ct}", "white")
            ci = prompt("\033[33m  type > \033[0m")
            try:
                card_type = card_types[int(ci)-1]
            except:
                card_type = card_types[0]
            try:
                balance = float(prompt("\033[33m  balance/value > \033[0m") or "50.00")
            except:
                balance = 50.00
            card_num = '-'.join(''.join(random.choices("0123456789", k=4)) for _ in range(4))
            cvv = ''.join(random.choices("0123456789", k=3))
            pin = ''.join(random.choices("0123456789", k=4))
            exp = f"{random.randint(1,12):02d}/{random.randint(25,30)}"
            clear()
            print()
            cprint(f"  \u2554{'='*54}\u2557", "cyan")
            cprint(f"  \u2551{'':^54}\u2551", "cyan")
            cprint(f"  \u2551   {card_type:^48}  \u2551", "cyan")
            cprint(f"  \u2551{'':^54}\u2551", "cyan")
            cprint(f"  \u2551   Card #:  {card_num:<42}  \u2551", "cyan")
            cprint(f"  \u2551   Exp:     {exp:<42}  \u2551", "cyan")
            cprint(f"  \u2551   CVV:     {cvv:<42}  \u2551", "cyan")
            cprint(f"  \u2551   PIN:     {pin:<42}  \u2551", "cyan")
            cprint(f"  \u2551   Balance: ${balance:,.2f}{'':<39}\u2551", "cyan")
            cprint(f"  \u2551{'':^54}\u2551", "cyan")
            cprint(f"  \u2551   \033[90m[ FOR LARP / PROP / SIMULATION USE ONLY ]\033[0m{'':<10}\u2551", "cyan")
            cprint(f"  \u255a{'='*54}\u255d", "cyan")
            print()
            pause()
        else:
            cprint("  invalid choice", "red")
            time.sleep(0.5)

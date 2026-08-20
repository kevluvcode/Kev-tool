import random
import string
import json
import time


FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
               "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
               "Thomas", "Sarah", "Christopher", "Karen", "Daniel", "Lisa", "Matthew", "Nancy",
               "Anthony", "Betty", "Mark", "Margaret", "Donald", "Sandra", "Steven", "Ashley",
               "Paul", "Dorothy", "Andrew", "Kimberly", "Joshua", "Emily", "Kenneth", "Donna"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
              "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
              "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com",
           "icloud.com", "aol.com", "mail.com", "zoho.com", "yandex.com"]
STREETS = ["Main St", "Oak Ave", "Pine Rd", "Elm St", "Cedar Blvd", "Maple Dr",
           "Washington Ave", "Park Pl", "Lake Shore Dr", "Broadway", "Highland Ave",
           "Forest Ln", "Sunset Blvd", "River Rd", "Cherry Ln", "Hill St"]
CITIES = ["Springfield", "Franklin", "Greenville", "Bristol", "Clinton", "Salem",
          "Madison", "Georgetown", "Arlington", "Riverside", "Burlington", "Manchester",
          "Nashua", "Lexington", "Augusta", "Trenton", "Albany", "Boise", "Helena"]
STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
          "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
          "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
          "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
          "WI", "WY"]
LOREM_WORDS = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing",
               "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore",
               "et", "dolore", "magna", "aliqua", "enim", "ad", "minim", "veniam",
               "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi",
               "aliquip", "ex", "ea", "commodo", "consequat", "duis", "aute", "irure",
               "reprehenderit", "voluptate", "velit", "esse", "cillum", "fugiat",
               "nulla", "pariatur", "excepteur", "sint", "occaecat", "cupidatat"]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
]
TLD_LIST = [".com", ".net", ".org", ".io", ".co", ".dev", ".app", ".xyz", ".me", ".info"]
BREACH_SITES = ["adobe.com", "linkedin.com", "myspace.com", "dropbox.com", "tumblr.com",
                "yahoo.com", "lastfm.com", "dailymotion.com", "twitter.com", "facebook.com",
                "iggames.com", "zomato.com", "canva.com", "discordapp.com", "roblox.com"]
DOMAINS_WORDS = ["tech", "cloud", "data", "sync", "byte", "pixel", "code", "dev",
                 "hub", "lab", "net", "web", "app", "sys", "ops", "pro", "io", "ai"]
HEX_CHARS = "0123456789abcdef"
WALLET_PREFIXES = {
    "Bitcoin (BTC)": "1",
    "Ethereum (ETH)": "0x",
    "Litecoin (LTC)": "L",
    "Ripple (XRP)": "r",
    "Solana (SOL)": "",
    "Cardano (ADA)": "addr1",
    "Polkadot (DOT)": "1",
}
CC_PREFIXES = {
    "Visa": ("4", 16),
    "Mastercard": ("5", 16),
    "American Express": ("34", 15),
    "Discover": ("6011", 16),
    "Diners Club": ("300", 14),
    "JCB": ("3528", 16),
}
GAMERTAG_PREFIX = ["xX", "xx", "xD", "The", "Real", "Pro", "Mlg", "Swag", "Epic", "Dark",
                   "Shadow", "Night", "Storm", "Fire", "Ice", "Blood", "Ghost", "Silent",
                   "Lone", "Rapid", "Blitz", "Viper", "Hawk", "Wolf", "Dragon", "Fury"]
GAMERTAG_SUFFIX = ["Xx", "xx", "lol", "YT", "TTV", "GG", "HD", "OG", "XD", "YT",
                   "Sniper", "Killer", "Legend", "God", "King", "Ninja", "Shotz",
                   "Frag", "Blitz", "Storm", "Wolf", "Rush", "Clutch", "Ace"]
GAMERTAG_BODY = ["Phoenix", "Raven", "Viper", "Blaze", "Storm", "Shadow", "Titan",
                 "Frost", "Surge", "Volt", "Apex", "Wraith", "Spectre", "Pulse",
                 "Flux", "Nebula", "Zenith", "Orbit", "Prism", "Echo"]


def _luhn_checksum(card_num):
    digits = [int(d) for d in str(card_num)]
    odd = digits[-1::-2]
    even = digits[-2::-2]
    total = sum(odd)
    for d in even:
        total += sum(int(x) for x in str(d * 2))
    return total % 10


def _luhn_generate(prefix, length):
    card = [int(d) for d in str(prefix)]
    while len(card) < length - 1:
        card.append(random.randint(0, 9))
    check = (10 - _luhn_checksum(int(''.join(map(str, card))) * 10)) % 10
    card.append(check)
    return ''.join(map(str, card))


def _random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def _random_email(name):
    base = name.lower().replace(" ", ".")
    num = random.randint(1, 9999)
    return f"{base}{num}@{random.choice(DOMAINS)}"


def _random_address():
    return f"{random.randint(100, 9999)} {random.choice(STREETS)}, {random.choice(CITIES)}, {random.choice(STATES)} {random.randint(10000, 99999)}"


def _random_phone():
    area = random.choice([201, 202, 203, 206, 207, 208, 209, 210, 212, 213, 214, 215,
                          216, 217, 218, 219, 224, 225, 228, 229, 231, 234, 239, 240,
                          248, 253, 254, 256, 260, 262, 267, 269, 270, 276, 281, 301,
                          302, 303, 304, 305, 307, 308, 309, 310, 312, 313, 314, 315,
                          316, 317, 318, 319, 320, 321, 323, 325, 330, 331, 334, 336,
                          337, 339, 346, 347, 351, 352, 360, 361, 364, 385, 386, 401,
                          402, 404, 405, 406, 407, 408, 409, 410, 412, 413, 414, 415,
                          417, 419, 423, 424, 425, 430, 432, 434, 435, 440, 442, 443,
                          469, 470, 475, 478, 479, 480, 484, 501, 502, 503, 504, 505,
                          507, 508, 509, 510, 512, 513, 515, 516, 517, 518, 520, 530,
                          531, 534, 539, 540, 541, 551, 559, 561, 562, 563, 567, 570,
                          571, 573, 574, 575, 580, 585, 586, 601, 602, 603, 605, 606,
                          607, 608, 609, 610, 612, 614, 615, 616, 617, 618, 619, 620,
                          623, 626, 628, 629, 630, 631, 636, 641, 646, 650, 651, 657,
                          660, 661, 662, 667, 669, 678, 681, 682, 701, 702, 703, 704,
                          706, 707, 708, 712, 713, 714, 715, 716, 717, 718, 719, 720,
                          724, 725, 727, 731, 732, 734, 737, 740, 743, 747, 754, 757,
                          760, 762, 763, 765, 769, 770, 772, 773, 774, 775, 779, 781,
                          785, 786, 801, 802, 803, 804, 805, 808, 810, 812, 813, 814,
                          815, 816, 817, 818, 828, 830, 831, 832, 843, 845, 847, 848,
                          850, 854, 856, 857, 858, 859, 860, 862, 863, 864, 865, 870,
                          872, 878, 901, 903, 904, 906, 907, 908, 909, 910, 912, 913,
                          914, 915, 916, 917, 918, 919, 920, 925, 928, 929, 930, 931,
                          936, 937, 938, 940, 941, 947, 949, 951, 952, 954, 956, 959,
                          970, 971, 972, 973, 975, 978, 979, 980, 984, 985, 800, 833,
                          844, 855, 866, 877, 888])
    return f"({area}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"


def _random_ssn():
    return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"


def _random_ip():
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def _random_mac():
    return ':'.join(f'{random.randint(0, 255):02x}' for _ in range(6))


def _random_useragent():
    return random.choice(USER_AGENTS)


def _random_domain():
    word = random.choice(DOMAINS_WORDS)
    tld = random.choice(TLD_LIST)
    num = random.randint(0, 999)
    return f"{word}{num}{tld}"


def _random_guid():
    return '-'.join(''.join(random.choices(HEX_CHARS, k=n)) for n in [8, 4, 4, 4, 12])


def _random_md5():
    return ''.join(random.choices(HEX_CHARS, k=32))


def _random_sha1():
    return ''.join(random.choices(HEX_CHARS, k=40))


def _random_sha256():
    return ''.join(random.choices(HEX_CHARS, k=64))


def _lorem_ipsum(paragraphs=3, sentences_per=5):
    result = []
    for _ in range(paragraphs):
        sent = []
        for _ in range(sentences_per):
            words = random.choices(LOREM_WORDS, k=random.randint(6, 18))
            sent.append(" ".join(words).capitalize() + ".")
        result.append(" ".join(sent))
    return "\n\n".join(result)


def _fake_cc():
    card_type = random.choice(list(CC_PREFIXES.keys()))
    prefix, length = CC_PREFIXES[card_type]
    number = _luhn_generate(prefix, length)
    month = f"{random.randint(1, 12):02d}"
    year = f"{random.randint(25, 32):02d}"
    cvv = f"{random.randint(100, 999)}" if card_type != "American Express" else f"{random.randint(1000, 9999)}"
    return {"type": card_type, "number": number, "exp": f"{month}/{year}", "cvv": cvv}


def _fake_wallet():
    coin, prefix = random.choice(list(WALLET_PREFIXES.items()))
    if coin == "Solana (SOL)":
        addr = ''.join(random.choices(string.ascii_letters + string.digits, k=44))
    elif coin.startswith("Cardano"):
        addr = "addr1" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=58))
    elif coin.startswith("Ethereum"):
        addr = "0x" + ''.join(random.choices(HEX_CHARS, k=40))
    else:
        addr = prefix + ''.join(random.choices(string.ascii_letters + string.digits, k=33))
    return coin, addr


def _fake_username():
    patterns = [
        lambda: f"{random.choice(FIRST_NAMES).lower()}{random.choice(LAST_NAMES).lower()}{random.randint(1, 9999)}",
        lambda: f"{random.choice(['xX', 'Xx', ''])}{''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 12)))}{random.choice(['Xx', 'xX', ''])}",
        lambda: f"{''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 7)))}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(4, 8)))}",
        lambda: f"{random.choice(GAMERTAG_BODY).lower()}{random.randint(10, 9999)}",
        lambda: f"{random.choice(['ii', 'x', ''])}{random.choice(GAMERTAG_BODY).lower()}{random.choice(['x', 'ii', ''])}",
    ]
    return random.choice(patterns)()


def _fake_password(length=16):
    upper = random.choices(string.ascii_uppercase, k=random.randint(2, length // 3))
    lower = random.choices(string.ascii_lowercase, k=random.randint(2, length // 3))
    digits = random.choices(string.digits, k=random.randint(1, length // 4))
    specials = random.choices("!@#$%^&*()_+-=[]{}|;:,.<>?", k=random.randint(1, length // 4))
    pool = upper + lower + digits + specials
    random.shuffle(pool)
    remaining = length - len(pool)
    if remaining > 0:
        pool += random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=remaining)
    random.shuffle(pool)
    return ''.join(pool[:length])


def _fake_breach():
    site = random.choice(BREACH_SITES)
    date = f"{random.randint(2015, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    records = random.randint(10000, 500000000)
    return {"site": site, "date": date, "records": f"{records:,}", "types": "Email, Password, IP"}


def _gamertag():
    prefix = random.choice(GAMERTAG_PREFIX)
    body = random.choice(GAMERTAG_BODY)
    suffix = random.choice(GAMERTAG_SUFFIX)
    num = random.randint(0, 9999)
    sep = random.choice(['', '_', ' ', '.', '-', 'x'])
    return f"{prefix}{sep}{body}{sep}{suffix}{num}"


def identity_gen(kevbin):
    kevbin.section_header('\U0001f3ad', 'IDENTITY GENERATOR')
    name = _random_name()
    email = _random_email(name)
    address = _random_address()
    phone = _random_phone()
    ssn = _random_ssn()
    dob = f"{random.randint(1960, 2005):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    kevbin.box.table(
        ["Field", "Value"],
        [["Full Name", name], ["Email", email], ["Phone", phone],
         ["DOB", dob], ["SSN", ssn], ["Address", address]]
    )
    kevbin.pause()


def credit_card_gen(kevbin):
    kevbin.section_header('\U0001f4b3', 'CREDIT CARD GENERATOR')
    count = 5
    rows = []
    for _ in range(count):
        card = _fake_cc()
        rows.append([card["type"], card["number"], card["exp"], card["cvv"]])
    kevbin.box.table(["Type", "Number", "Exp", "CVV"], rows)
    kevbin.pause()


def wallet_gen(kevbin):
    kevbin.section_header('\U0001f4b0', 'CRYPTO WALLET GENERATOR')
    count = 5
    rows = []
    for _ in range(count):
        coin, addr = _fake_wallet()
        rows.append([coin, addr[:60]])
    kevbin.box.table(["Coin", "Address"], rows)
    kevbin.pause()


def username_gen(kevbin):
    kevbin.section_header('\U0001f464', 'USERNAME GENERATOR')
    count = 15
    rows = [[str(i + 1), _fake_username()] for i in range(count)]
    kevbin.box.table(["#", "Username"], rows)
    kevbin.pause()


def password_gen(kevbin):
    kevbin.section_header('\U0001f510', 'PASSWORD GENERATOR')
    length_str = kevbin.input_choice("  Length [16]: ") or "16"
    try:
        length = max(8, min(128, int(length_str)))
    except ValueError:
        length = 16
    count = 5
    rows = []
    for _ in range(count):
        pwd = _fake_password(length)
        rows.append([pwd[:50], str(len(pwd))])
    kevbin.box.table(["Password", "Len"], rows)
    kevbin.pause()


def lorem_ipsum(kevbin):
    kevbin.section_header('\U0001f4dd', 'LOREM IPSUM')
    paras_str = kevbin.input_choice("  Paragraphs [3]: ") or "3"
    try:
        paras = max(1, min(20, int(paras_str)))
    except ValueError:
        paras = 3
    text = _lorem_ipsum(paras)
    kevbin.box.code(text)
    kevbin.pause()


def fake_nitro(kevbin):
    kevbin.section_header('\U0001f680', 'NITRO CODE GENERATOR')
    count = 10
    rows = []
    for i in range(count):
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        rows.append([str(i + 1), f"discord.gift/{code}"])
    kevbin.box.table(["#", "Code"], rows)
    kevbin.pause()


def server_template(kevbin):
    kevbin.section_header('\U0001f4e6', 'DISCORD SERVER TEMPLATE')
    templates = [
        {"name": "Gaming Hub", "roles": ["Owner", "Admin", "Moderator", "Member", "VIP"],
         "channels": ["general", "memes", "looking-for-group", "clips", "voice-chat", "bot-commands", "announcements"]},
        {"name": "Study Group", "roles": ["Admin", "Moderator", "Student", "TA"],
         "channels": ["general", "resources", "homework-help", "study-sessions", "music", "off-topic"]},
        {"name": "Dev Community", "roles": ["Owner", "Core Dev", "Contributor", "Member"],
         "channels": ["general", "showcase", "help", "resources", "jobs", "code-review", "off-topic"]},
        {"name": "Music Server", "roles": ["Owner", "DJ", "Producer", "Listener"],
         "channels": ["general", "production", "sample-packs", "feedback", "collabs", "releases"]},
    ]
    t = random.choice(templates)
    template = {
        "name": t["name"],
        "roles": t["roles"],
        "channels": [{"name": c, "type": "text"} for c in t["channels"]],
        "categories": [{"name": "Information", "channels": ["announcements", "rules"]},
                       {"name": "Chat", "channels": t["channels"][:3]}]
    }
    kevbin.box.code(json.dumps(template, indent=2))
    kevbin.pause()


def fake_mail(kevbin):
    kevbin.section_header('\u2709\ufe0f', 'EMAIL GENERATOR')
    name = _fake_username()
    domain = random.choice(["mailto.plus", "tempmail.com", "guerrillamail.com", "mailinator.com", "yopmail.com"])
    pwd = _fake_password(14)
    kevbin.box.table(
        ["Field", "Value"],
        [["Email", f"{name}@{domain}"], ["Password", pwd],
         ["Username", name], ["Domain", domain]]
    )
    kevbin.pause()


def fake_ddos(kevbin):
    kevbin.section_header('\u26a1', 'NETWORK STRESS TEST')
    target = kevbin.input_choice("  Target IP/Host: ") or "127.0.0.1"
    duration_str = kevbin.input_choice("  Duration (sec) [10]: ") or "10"
    try:
        duration = max(1, min(60, int(duration_str)))
    except ValueError:
        duration = 10
    threads_str = kevbin.input_choice("  Threads [50]: ") or "50"
    try:
        threads = max(1, min(200, int(threads_str)))
    except ValueError:
        threads = 50
    kevbin.cprint(kevbin.t.dim, f"\n  Target: {target}")
    kevbin.cprint(kevbin.t.dim, f"  Duration: {duration}s | Threads: {threads}")
    kevbin.cprint(kevbin.t.dim, f"  Initializing...\n")
    total_sent = 0
    for sec in range(1, duration + 1):
        batch = random.randint(threads * 50, threads * 200)
        total_sent += batch
        elapsed_pct = int(sec / duration * 100)
        kevbin.cprint(kevbin.t.secondary, f"  [{elapsed_pct:3d}%] sec {sec:>2d}/{duration} | "
                      f"sent {total_sent:>10,} packets | "
                      f"peak {batch:>6,}/s | "
                      f"avg {total_sent // sec:>6,}/s")
        time.sleep(0.08)
    kevbin.cprint(kevbin.t.highlight, f"\n  Complete — {total_sent:,} packets in {duration}s")
    kevbin.cprint(kevbin.t.txt, f"  Avg throughput: {total_sent // duration:,} pps")
    kevbin.pause()


def fake_wallet_miner(kevbin):
    kevbin.section_header('\u26cf\ufe0f', 'WALLET MINER')
    wallet = _fake_wallet()[1]
    kevbin.cprint(kevbin.t.dim, f"  Wallet: {wallet[:40]}...")
    kevbin.cprint(kevbin.t.dim, f"  Algorithm: Ethash | Pool: f2pool.com\n")
    hashrate = 0.0
    accepted = 0
    for i in range(1, 16):
        hashrate += random.uniform(3.5, 5.8)
        shares = random.randint(8, 25)
        accepted += shares
        temp = random.randint(58, 78)
        fan = random.randint(45, 85)
        kevbin.cprint(kevbin.t.secondary,
                      f"  [{i:2d}/15] {hashrate:.2f} MH/s | "
                      f"accepted {accepted:>4d} | "
                      f"temp {temp}C | fan {fan}%")
        time.sleep(0.06)
    balance = random.uniform(0.0001, 0.005)
    usd = balance * random.uniform(2800, 3500)
    kevbin.cprint(kevbin.t.highlight, f"\n  Session complete — {accepted} shares accepted")
    kevbin.cprint(kevbin.t.success, f"  Balance: {balance:.8f} BTC (~${usd:.2f})")
    kevbin.pause()


def social_botter(kevbin):
    kevbin.section_header('\U0001f4ca', 'SOCIAL VIEW BOTTER')
    url = kevbin.input_choice("  Target URL: ") or "https://example.com"
    platform = random.choice(["TikTok", "YouTube", "Instagram", "Twitter", "Twitch"])
    kevbin.cprint(kevbin.t.dim, f"  Platform: {platform}")
    kevbin.cprint(kevbin.t.dim, f"  Target: {url[:50]}\n")
    views = 0
    likes = 0
    subs = 0
    for i in range(1, 21):
        v = random.randint(500, 3000)
        l = random.randint(20, 200)
        s = random.randint(5, 50)
        views += v
        likes += l
        subs += s
        kevbin.cprint(kevbin.t.secondary,
                      f"  [{i:2d}/20] views {views:>8,} | "
                      f"likes {likes:>6,} | "
                      f"subs {subs:>4,} | "
                      f"+{v}/s")
        time.sleep(0.05)
    kevbin.cprint(kevbin.t.highlight, f"\n  Total: {views:,} views, {likes:,} likes, {subs:,} subs")
    kevbin.pause()


def fake_paypal_otp(kevbin):
    kevbin.section_header('\U0001f4f1', 'OTP GENERATOR')
    phone = _random_phone()
    otp = ''.join(str(random.randint(0, 9)) for _ in range(6))
    kevbin.cprint(kevbin.t.dim, f"  Sent to: {phone}")
    kevbin.cprint(kevbin.t.dim, f"  Carrier: T-Mobile US\n")
    kevbin.box.table(["Code", "Expires", "Phone"], [[otp, "5:00", phone]])
    kevbin.pause()


def fake_account_gen(kevbin):
    kevbin.section_header('\U0001f464', 'ACCOUNT GENERATOR')
    count_str = kevbin.input_choice("  How many [10]: ") or "10"
    try:
        count = max(1, min(50, int(count_str)))
    except ValueError:
        count = 10
    rows = []
    for _ in range(count):
        user = _fake_username()
        email = f"{user}@{random.choice(DOMAINS)}"
        pwd = _fake_password(random.randint(10, 18))
        rows.append([user, email, pwd])
    kevbin.box.table(["Username", "Email", "Password"], rows)
    kevbin.pause()


def fake_fortnite_checker(kevbin):
    kevbin.section_header('\U0001f3ae', 'FORTNITE ACCOUNT CHECKER')
    email = kevbin.input_choice("  Account email: ") or "user@example.com"
    kevbin.cprint(kevbin.t.dim, f"  Checking: {email}\n")
    skins = ["Renegade Raider", "Ghoul Trooper", "Skull Trooper", "Recon Expert",
             "Galaxy", "Purple Skull", "Aerial Assault Trooper", "Black Knight",
             "Limited Samuragi", "Mako", "Havoc", "Criterion"]
    found = random.sample(skins, k=random.randint(3, 7))
    vbucks = random.randint(500, 25000)
    level = random.randint(50, 500)
    for i, skin in enumerate(found, 1):
        kevbin.cprint(kevbin.t.accent, f"  [{i:2d}] {skin}")
        time.sleep(0.04)
    kevbin.cprint(kevbin.t.highlight, f"\n  Account Level: {level}")
    kevbin.cprint(kevbin.t.success, f"  V-Bucks: {vbucks:,}")
    kevbin.cprint(kevbin.t.secondary, f"  Rare skins: {len(found)}")
    kevbin.pause()


def fake_exodus(kevbin):
    kevbin.section_header('\U0001f510', 'WALLET SEED PHRASE')
    wordlist = ("abandon ability able about above absent absorb abstract absurd abuse access "
                "accident account achieve acid acoustic acquire across act action actor actress "
                "actual adapt add addict address adjust admit adult advance advice aerobic affair "
                "afford afraid again age agent agree ahead aim air airport aisle album alcohol "
                "alert alien all alley allow almost alone alpha alpha already also alter always "
                "amateur amazing among among amount amused analyst anchor ancient anger angle angry "
                "animal ankle announce annual another answer antenna antenna anxiety any apart "
                "apology appear apple approve april arch arctic area arena argue arm armed armor "
                "army around arrange arrest arrival article artificial artist artwork ask aspect "
                "assault asset assist assume asthma athlete atom attack attend attitude attract "
                "auction audit august aunt author auto autumn average avocado avoid awake aware "
                "awesome awful awkward axis baby bachelor bacon badge bag balance balcony ball "
                "bamboo banana banner bar barely bargain barrel base basic basket battle beach "
                "bean beauty because become beef before begin behave behind behind belief belong "
                "best betray better between beyond bicycle bike bind biology bird birth bitter "
                "black blade blame blanket blast bleak blessing blind blood blossom blue blur "
                "bluff board boat body boil bomb bone bonus book boost border boring borrow boss "
                "bottom bounce box boy bracket brain brand brass brave bread breeze brick bridge "
                "brief bright bring brisk broken bronze broom brother brown brush bubble buddy "
                "budget buffalo build bulb bulk bullet bundle bunny burden burger burst bus business "
                "busy butter buyer buzz cabbage cabin cable cactus cage cake call calm camera "
                "camp can canal cancel candy cannon canvas canyon capable capital captain car "
                "carbon card cargo carpet carry carrot case cash casino casual cat catalog catch "
                "category cattle caught cause caution cave ceiling celery cement census cereal "
                "certain chalk chapter charge chase cheap check cheese cherry chest chicken chief "
                "child chimney choice choose chunk chimney civil claim clamp clang classic classroom "
                "clean clerk clever click cliff climb clinic clip clock clog close cloth cloud "
                "clown club clump cluster clutch coach coast coconut code coffee coil coin collect "
                "color column combine come comfort comic common company concert conduct confirm "
                "connect consider control convince cook cool copper copy coral core corn correct "
                "cost cotton couch country couple course cousin cover coyote crack cradle craft "
                "cram crane crash crater crawl crazy cream credit crew cricket crime crisp "
                "critic crop cross crouch crowd crude cruel cruise crumble crush cry crystal "
                "cube culture cup cupboard curious current curtain curve cushion custom cute "
                "cycle damage damp dance danger daring dash daughter dawn day debate debris "
                "decade december decide decline decorate decrease deer defense define defy "
                "degree delay deliver demand demise denial dentist deny depart depend deposit "
                "depth deputy derive describe desert design desk despair destroy detail detect "
                "develop device devote diagram dial diamond diary dice dignity dilemma dinner "
                "dinosaur direct dirt disagree discover disease dish dismiss disorder display "
                "distance divert divide divorce dizzy doctor document dog doll dolphin domain "
                "donate donkey donor door dose double draft dragon drama drastic dream dress "
                "drift drill drink drip drive drop drum dry duck dumb dune during dust dutch "
                "duty dwarf dynamic eager eagle early earn earth easily east easy echo ecology "
                "economy edge edit educate effort eight either elbow elder electric elegant "
                "element elephant elevator elite else embark embody embrace emerge emotion "
                "employ empower empty encourage enforce engage engine enhance enjoy enlist "
                "enough enrich enroll ensure enter entire entry envelope episode equal equip "
                "erase erode erosion error erupt escape essay essence estate eternal evidence "
                "evil evoke evolve exact example excess exchange excite exclude excuse execute "
                "exercise exhaust exhibit exile exist exit exotic expand expect expire explain "
                "expose express extend extra eyebrow fabric face faculty fade faint faith fall "
                "false famine fancy fantasy fashion fatigue father fatigue fault favorite feature "
                "february federal feeling female fence festival fetch fever few fiber fiction "
                "field figure file film filter final find finger finish fire firm fiscal fish "
                "fitness fix flag flame flash flat flavor flee flight flip float flock floor "
                "flower fluid flush fly foam focus fog follow food foot force forest forget "
                "fork fortune forum fossil foster found frame frequent fresh friend fringe "
                "frog front frost frown frozen fruit fuel fun funny furnace fury future gadget "
                "gain galaxy gallery game gap garage garbage garden garlic garment gasp gate "
                "gather gauge gaze general genius genre gentle genuine gesture ghost giant gift "
                "giggle ginger giraffe girl give glad glance glare glass glide glimpse globe "
                "gloom glory glove glow glue goat goddess gold good goose gorilla gospel "
                "gossip govern gown grab grace grain grant grape grass gravity great green "
                "grid grief grit grocery group grow grunt guard guess guide guilt guitar gun "
                "gym habit hair half hammer hamster hand happy harbor hard harsh harvest hawk "
                "hazard head health heart heavy hedgehog height hello helmet help hero hidden "
                "high hill hint hire history hobby hockey hold hollow home honey hood hope "
                "horn horror horse hospital host hotel hour hover hub huge human humble humor "
                "hundred hungry hurdle hurry husband hybrid ice icon idea identify idle ignore "
                "ill illegal image imagine imitate immense immune impact impose improve impulse "
                "inch include income increase index indicate indoor industry infant inflict "
                "inform initial inject inmate inner innocent input inquiry insect inside inspire "
                "install intact interest into invest involve issue ivory jacket jaguar january "
                "jazz jealous jeans jelly jewel job join joke journey joy judge juice jump "
                "jungle junior junk just kangaroo keen keep ketchup key kick kid kidney kind "
                "kingdom kiss kit kitchen kite kitten kiwi knee knife knock know label labor "
                "ladder lake lamp language laptop large later laugh laundry lava lawn lawsuit "
                "layer lazy leader leaf learn leave left leg legal legend leisure lemon lens "
                "leopard letter level liberty library license life lift light lilac limit "
                "lion liquid list little live lizard loan lobster local lock logic lonely "
                "long loop lottery loud lounge love loyal lucky luggage lumber lunar lunch "
                "luxury lyrics machine magnetic maid main major make mammal man manage mandate "
                "mango mansion maple marble march margin marine market marriage mask mass master "
                "match material math matrix meat mechanic medium melody membrane memory mention "
                "mentor merchant mercy merge merit metal method middle migrate military milk "
                "million mimic mind minimum minor minor miracle mirror misery miss mistake "
                "mixer mixture mobile model modify mom moment monitor monkey monster month "
                "moon moral morning mosquito mother motion mountain mouse move movie much "
                "muffin multiply muscle museum mushroom music mutual myself mystery myth naive "
                "name napkin narrow nasty nature near neck need negative neglect neither nerve "
                "nest net network neutral never news next nice night noble noise nominee "
                "normal north notable nothing notice novel now nuclear number nurse nut oak "
                "obey object oblige obtain obvious occur ocean october odor off offer office "
                "often olive olympic omit once one onion online only open opera opinion oppose "
                "option orange orbit orchard order ordinary organ orient orphan ostrich other "
                "outdoor outer output outside oval oven over owner oxygen oyster ozone packet "
                "palace palm panda panel panic panther paper parade parent park parrot party "
                "pass patch path patient patrol pattern pause pavement pear peasant pelican "
                "pen penalty pencil people pepper perfect permit person pet phone photo phrase "
                "physical picnic picture piece pilot pink pioneer pipe pistol pitch pizza "
                "place planet plastic plate playful pledge pluck plug plunge poem poet point "
                "polar police pond pony pool popular portion position possible potato pottery "
                "poverty powder power practice prefer prepare present pretty prevent price "
                "pride primary print priority prison private prize problem process produce "
                "profit program project promote proof property prosper protect proud provide "
                "public pudding pull pulp pulse pumpkin punch pupil puppy purchase purity purpose "
                "purse push put puzzle pyramid quality quantum quarter queen question quick quit "
                "quiz quote rabbit raccoon radar radio rain rainbow raise range rapid rather "
                "raven razor ready real reason rebel rebuild recall receive recipe record recycle "
                "reduce reflect reform region regret regular reject relax release relief remain "
                "remains remove render renew repeat replace report require rescue resemble "
                "resist resource response result retire retreat return reunion reveal review "
                "reward rhythm rice rich ride ridge rifle right rigid ring riot ripple risk "
                "ritual rival river road roast robot rogue roman rough round route royal "
                "rubber rude rugby ruler ruler rural saddle safety salmon salon salt salute "
                "same sample sand satisfy satoshi sauce sausage save scale scan scare scatter "
                "scene scheme school science scissors scorpion scout scrap screen script scrub "
                "sea search season seat second segment selection senior sense sentence series "
                "service session settle setup seven shadow shaft shallow share shed shell sheriff "
                "shield shift shine ship shiver shock shoot short shoulder shove shrimp shrug "
                "shuffle sibling siege silk silly silver similar simple since sing siren sister "
                "situate six size skate sketch skill skin skirt skull slab slash slave sleep "
                "slice slide slight slim slogan slot slow slush small smart smile smoke smooth "
                "snake snack solar soldier solid solution solve someone song sonic sorry sort "
                "soul sound soup source south space spare spatial spawn special speed spell "
                "spend sphere spice spike spin spirit split sponsor spoon spot spray spread "
                "spring square squeeze squirrel stable stadium staff stage stairs stamp stand "
                "start state stay steak steel stem step stereo stick still sting stock stomach "
                "stone stool story stove strategy street strike strong struggle student stuff "
                "stumble style subject submit subway success such sudden suffer sugar suggest "
                "suit summer sun sunny super surge sushi switch symbol symptom syrup system "
                "table tackle tag tail talent tank tape target task tattoo taxi teach team "
                "tell ten tenant tennis tent term test text thank that theme then theory "
                "there thick thing think third thorn those though thought three thrive throw "
                "thumb thunder ticket tidy tiger timber time tiny tip tire titan title toast "
                "tobacco today toddler toe together toilet token tomato tomorrow tongue tonight "
                "tool tooth top topic topix torch tornado total tourist toward tower town toy "
                "track trade traffic train transfer trap trash travel tray treat tree trend "
                "trial tribe trick trigger trim trophy trouble truck truly trumpet trust truth "
                "try tube tuna tunnel turkey turn twelve twenty twice twin twist two type typical "
                "ugly umbrella unable unaware uncle under unfair unfold unhappy uniform unique "
                "unit universe unknown unlock until unusual unveil update upgrade uphold upon "
                "upper upset urban usage use used useful useless usual utility vacant vacuum "
                "valuable valley valve vanilla various vast vault vehicle velvet vendor venture "
                "venue verify version very vessel veteran viable vibrant vicious victory video "
                "view village vintage violin viral virus visa visit visual vital vivid vocal "
                "voice void volcano volume vote wage wait walk wall walnut wander wanted warm "
                "warrior wash wasp waste water wave wealth weapon weather web wedding weekend "
                "weird welcome well west wheat wheel when where whisper wide width wife wild "
                "will win window wine wing winner winter wire wisdom within witness wolf wonder "
                "wood wool word work world worry worth wrap wreck wrestle wrist write wrong yard "
                "year yellow you young youth zebra zero zone zoo")
    words = wordlist.split()
    seed = ' '.join(random.choices(words, k=12))
    kevbin.box.code(seed)
    kevbin.pause()


def hacker_terminal(kevbin):
    kevbin.section_header('\U0001f5a5\ufe0f', 'TERMINAL')
    lines = [
        f"root@{random.choice(['prod-', 'dev-', 'staging-', 'live-'])}{random.choice(['web', 'db', 'api', 'app'])}:/home/admin# id",
        f"uid=0(root) gid=0(root) groups=0(root)",
        f"root@server:~# cat /etc/passwd | head -5",
        f"root:x:0:0:root:/root:/bin/bash",
        f"daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin",
        f"bin:x:2:2:bin:/bin:/usr/sbin/nologin",
        f"sys:x:3:3:sys:/dev:/usr/sbin/nologin",
        f"root@server:~# ss -tlnp | grep LISTEN",
        f"LISTEN  0  128  0.0.0.0:22   0.0.0.0:*  users:((\"sshd\",pid={random.randint(500,9999)}))",
        f"LISTEN  0  128  0.0.0.0:80  0.0.0.0:*  users:((\"nginx\",pid={random.randint(1000,9999)}))",
        f"LISTEN  0  128  0.0.0.0:443 0.0.0.0:*  users:((\"nginx\",pid={random.randint(1000,9999)}))",
        f"LISTEN  0  128  127.0.0.1:3306 0.0.0.0:*  users:((\"mysqld\",pid={random.randint(2000,9999)}))",
        f"root@server:~# uptime",
        f" {random.randint(1,30)}:{random.randint(0,59):02d}:{random.randint(0,59):02d} up {random.randint(1,365)} days, {random.randint(1,23)}:{random.randint(0,59):02d},  {random.randint(1,4)} users,  load average: {random.uniform(0.1,4.0):.2f}, {random.uniform(0.1,4.0):.2f}, {random.uniform(0.1,4.0):.2f}",
        f"root@server:~# df -h /",
        f"Filesystem      Size  Used Avail Use% Mounted on",
        f"/dev/sda1       {random.randint(20,500)}G   {random.randint(5,200)}G  {random.randint(10,300)}G  {random.randint(10,80)}% /",
        f"root@server:~# free -m",
        f"              total        used        free      shared  buff/cache   available",
        f"Mem:          {random.randint(16,256)*1024}      {random.randint(2,64)*1024}      {random.randint(4,128)*1024}         {random.randint(100,5000)}      {random.randint(1,32)*1024}      {random.randint(8,192)*1024}",
        f"root@server:~# nmap -sV -p 22,80,443,3306 {random.choice(['192.168.1.1', '10.0.0.1', _random_ip()])}",
        f"Starting Nmap 7.94 ( https://nmap.org )",
        f"PORT     STATE SERVICE VERSION",
        f"22/tcp   open  ssh     OpenSSH 8.9p1",
        f"80/tcp   open  http    nginx 1.24.0",
        f"443/tcp  open  https   nginx 1.24.0",
        f"3306/tcp open  mysql   MySQL 8.0.35",
    ]
    for ln in lines:
        kevbin.cprint(kevbin.t.secondary, f"  {ln}")
        time.sleep(0.03)
    kevbin.pause()


def ransomware_sim(kevbin):
    kevbin.section_header('\U0001f480', 'FILE ENCRYPTOR')
    target_dir = kevbin.input_choice("  Target directory [/home]: ") or "/home"
    extensions = [".txt", ".doc", ".jpg", ".png", ".pdf", ".zip", ".db", ".key"]
    files_encrypted = random.randint(50, 500)
    total_size = random.randint(100, 5000)
    kevbin.cprint(kevbin.t.dim, f"\n  Scanning: {target_dir}")
    time.sleep(0.3)
    kevbin.cprint(kevbin.t.dim, f"  Found {files_encrypted} files ({total_size} MB)")
    time.sleep(0.2)
    kevbin.cprint(kevbin.t.dim, f"  Extensions: {', '.join(extensions)}")
    time.sleep(0.2)
    kevbin.cprint(kevbin.t.warning, f"\n  Encrypting...")
    for i in range(1, 11):
        pct = i * 10
        bar = '#' * (pct // 5) + '-' * (20 - pct // 5)
        kevbin.cprint(kevbin.t.secondary, f"  [{bar}] {pct}%  ({files_encrypted * pct // 100}/{files_encrypted} files)")
        time.sleep(0.06)
    note = (
        f"\n  !!! ALL YOUR FILES HAVE BEEN ENCRYPTED !!!\n\n"
        f"  Your files have been encrypted with AES-256.\n"
        f"  To decrypt, you need the private key.\n\n"
        f"  Files encrypted: {files_encrypted}\n"
        f"  Total size: {total_size} MB\n"
        f"  Bitcoin wallet: 1{''.join(random.choices(string.ascii_letters + string.digits, k=33))}\n\n"
        f"  Send 0.5 BTC to the address above.\n"
        f"  After payment, email proof to: recovery@protonmail.com\n"
        f"  You have 72 hours before the key is deleted."
    )
    kevbin.cprint(kevbin.t.error, note)
    kevbin.pause()


def fake_bruteforcer(kevbin):
    kevbin.section_header('\U0001f510', 'HASH CRACKER')
    target = kevbin.input_choice("  Hash to crack: ") or _random_sha256()
    algo = random.choice(["MD5", "SHA1", "SHA256", "NTLM"])
    kevbin.cprint(kevbin.t.dim, f"  Hash: {target[:40]}{'...' if len(target) > 40 else ''}")
    kevbin.cprint(kevbin.t.dim, f"  Algorithm: {algo}")
    kevbin.cprint(kevbin.t.dim, f"  Wordlist: rockyou.txt (14,341,564 entries)\n")
    attempts = 0
    speed = random.randint(800000, 3000000)
    common = ["password", "123456", "qwerty", "letmein", "admin", "welcome",
              "monkey", "dragon", "master", "abc123", "iloveyou", "shadow",
              "sunshine", "princess", "football", "charlie", "trustno1"]
    for i in range(1, 16):
        attempts += random.randint(speed // 10, speed // 5)
        guess = random.choice(common) + str(random.randint(0, 999))
        found = i == 14
        if found:
            kevbin.cprint(kevbin.t.success, f"  [{i:2d}/15] {attempts:>12,} hashes/s | trying: {guess}  FOUND!")
        else:
            kevbin.cprint(kevbin.t.secondary, f"  [{i:2d}/15] {attempts:>12,} hashes/s | trying: {guess}")
        time.sleep(0.06)
    if True:
        cracked = random.choice(common) + str(random.randint(0, 99))
        kevbin.cprint(kevbin.t.highlight, f"\n  CRACKED in {attempts:,} attempts")
        kevbin.cprint(kevbin.t.success, f"  Hash:   {target[:40]}")
        kevbin.cprint(kevbin.t.success, f"  Plain:  {cracked}")
        kevbin.cprint(kevbin.t.txt, f"  Time:   {random.randint(1,45)}s | Speed: {speed:,}/s")
    kevbin.pause()

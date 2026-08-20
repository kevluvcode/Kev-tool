import random
import string
import json

def _luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10

def _luhn_generate(prefix, length):
    """Generate a Luhn-valid card number with given prefix."""
    card = [int(d) for d in str(prefix)]
    while len(card) < length - 1:
        card.append(random.randint(0, 9))
    checksum = _luhn_checksum(int(''.join(map(str, card))) * 10)
    check_digit = (10 - checksum) % 10
    card.append(check_digit)
    return ''.join(map(str, card))

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "example.com"]
STREETS = ["Main St", "Oak Ave", "Pine Rd", "Elm St", "Cedar Blvd", "Maple Dr", "Washington Ave", "Park Pl"]
CITIES = ["Springfield", "Franklin", "Greenville", "Bristol", "Clinton", "Salem", "Madison", "Georgetown"]
STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
LOREM_WORDS = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua", "ut", "enim", "ad", "minim", "veniam", "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi", "ut", "aliquip", "ex", "ea", "commodo", "consequat"]

def _random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def _random_email(name):
    base = name.lower().replace(" ", ".")
    return f"{base}{random.randint(1,999)}@{random.choice(DOMAINS)}"

def _random_address():
    return f"{random.randint(100,9999)} {random.choice(STREETS)}, {random.choice(CITIES)}, {random.choice(STATES)} {random.randint(10000,99999)}"

def _random_phone():
    return f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"

def _luhn_checksum(card_num):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_num)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10

def _generate_luhn_valid(prefix, length):
    card = [int(d) for d in prefix]
    while len(card) < length - 1:
        card.append(random.randint(0, 9))
    checksum = _luhn_checksum(int("".join(map(str, card))))
    check_digit = (10 - checksum) % 10
    card.append(check_digit)
    return "".join(map(str, card))

def _fake_cc():
    prefixes = {
        "Visa": "4",
        "Mastercard": "5",
        "Amex": "34",
        "Discover": "6011",
    }
    card_type = random.choice(list(prefixes.keys()))
    prefix = prefixes[card_type]
    length = 15 if card_type == "Amex" else 16
    number = _generate_luhn_valid(prefix, length)
    exp_month = f"{random.randint(1,12):02d}"
    exp_year = f"{random.randint(24,30):02d}"
    cvv = f"{random.randint(100,999)}" if card_type != "Amex" else f"{random.randint(1000,9999)}"
    return {"type": card_type, "number": number, "exp": f"{exp_month}/{exp_year}", "cvv": cvv}

def _fake_wallet():
    coins = {
        "Bitcoin": "1" + "".join(random.choices(string.ascii_letters + string.digits, k=33)),
        "Ethereum": "0x" + "".join(random.choices("0123456789abcdef", k=40)),
        "Litecoin": "L" + "".join(random.choices(string.ascii_letters + string.digits, k=33)),
        "Dogecoin": "D" + "".join(random.choices(string.ascii_letters + string.digits, k=33)),
    }
    return random.choice(list(coins.items()))

def _fake_username():
    patterns = [
        lambda: f"{random.choice(FIRST_NAMES).lower()}{random.choice(LAST_NAMES).lower()}{random.randint(1,999)}",
        lambda: f"{random.choice(['xX', 'Xx', ''])}{''.join(random.choices(string.ascii_lowercase, k=random.randint(5,10)))}{random.choice(['Xx', 'xX', ''])}",
        lambda: f"{''.join(random.choices(string.ascii_lowercase, k=3))}_{''.join(random.choices(string.ascii_lowercase, k=5))}",
    ]
    return random.choice(patterns)()

def _fake_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(random.choices(chars, k=length))

def _lorem_ipsum(paragraphs=3, sentences_per=5):
    result = []
    for _ in range(paragraphs):
        sent = []
        for _ in range(sentences_per):
            words = random.choices(LOREM_WORDS, k=random.randint(4, 12))
            sent.append(" ".join(words).capitalize() + ".")
        result.append(" ".join(sent))
    return "\n\n".join(result)

def _fake_nitro():
    return "".join(random.choices(string.ascii_letters + string.digits, k=16))

def _server_template():
    templates = {
        "gaming": {"name": "Gaming Hub", "icon": "🎮", "channels": ["general", "memes", "looking-for-group", "clips", "voice-chat"]},
        "study": {"name": "Study Group", "icon": "📚", "channels": ["general", "resources", "questions", "study-sessions", "music"]},
        "dev": {"name": "Dev Community", "icon": "💻", "channels": ["general", "showcase", "help", "resources", "jobs", "off-topic"]},
        "anime": {"name": "Anime Club", "icon": "🌸", "channels": ["general", "recommendations", "episodes", "manga", "art", "voice-chat"]},
    }
    t = random.choice(list(templates.values()))
    return json.dumps({
        "name": t["name"],
        "icon": t["icon"],
        "channels": [{"name": c, "type": "text"} for c in t["channels"]],
        "roles": ["@everyone", "Admin", "Mod", "Member"]
    }, indent=2)

def identity_gen(kevbin):
    kevbin.box.title("Identity Generator")
    name = _random_name()
    email = _random_email(name)
    address = _random_address()
    phone = _random_phone()
    kevbin.box.table(
        ["Field", "Value"],
        [["Name", name], ["Email", email], ["Address", address], ["Phone", phone]]
    )

def credit_card_gen(kevbin):
    kevbin.box.title("Credit Card Generator (Test Numbers)")
    card = _fake_cc()
    kevbin.box.table(
        ["Field", "Value"],
        [["Type", card["type"]], ["Number", card["number"]], ["Expires", card["exp"]], ["CVV", card["cvv"]]]
    )

def wallet_gen(kevbin):
    kevbin.box.title("Crypto Wallet Generator")
    coin, addr = _fake_wallet()
    kevbin.box.table(
        ["Coin", "Address"],
        [[coin, addr]]
    )

def username_gen(kevbin):
    kevbin.box.title("Username Generator")
    usernames = [_fake_username() for _ in range(10)]
    kevbin.box.table(
        ["#", "Username"],
        [[str(i+1), u] for i, u in enumerate(usernames)]
    )

def password_gen(kevbin):
    kevbin.box.title("Password Generator")
    length = kevbin.box.input("Length (default 16): ", default="16")
    try:
        length = int(length)
    except:
        length = 16
    pwd = _fake_password(length)
    kevbin.box.table(
        ["Field", "Value"],
        [["Password", pwd], ["Length", str(len(pwd))]]
    )

def lorem_ipsum(kevbin):
    kevbin.box.title("Lorem Ipsum Generator")
    paras = kevbin.box.input("Paragraphs (default 3): ", default="3")
    try:
        paras = int(paras)
    except:
        paras = 3
    text = _lorem_ipsum(paras)
    kevbin.box.code(text)

def fake_nitro(kevbin):
    kevbin.box.title("Fake Nitro Code Generator")
    codes = [_fake_nitro() for _ in range(5)]
    kevbin.box.table(
        ["#", "Code"],
        [[str(i+1), f"discord.gift/{c}"] for i, c in enumerate(codes)]
    )

def server_template(kevbin):
    kevbin.box.title("Discord Server Template")
    template = _server_template()
    kevbin.box.code(template)
def fake_mail(kevbin):
    kevbin.box.title("Fake Mail Generator")
    name = _fake_username()
    kevbin.box.table(
        ["Field", "Value"],
        [["Email", f"{name}@mailto.plus"],
         ["Password", _fake_password(14)],
         ["Username", name],
         ["Domain", "mailto.plus"]]
    )


def fake_ddos(kevbin):
    kevbin.box.title("Fake DDoS Simulator (SIMULATION ONLY)")
    target = kevbin.box.input("Target (e.g. 1.1.1.1): ", "1.1.1.1")
    kevbin.box.warn("Simulated output only - no packets are sent.")
    kevbin.box.info(f"Initializing flood against {target}...")
    for i in range(1, 11):
        kevbin.box.info(f"[{i * 10}%] Sending {i * 137} fake packets (simulated)")
        time.sleep(0.15)
    kevbin.box.success("Simulation complete - nothing was sent.")


def fake_wallet_miner(kevbin):
    kevbin.box.title("Fake Wallet Miner")
    kevbin.box.warn("Simulation only - no crypto is mined.")
    hashrate = 0
    for i in range(1, 9):
        hashrate += 4.25
        kevbin.box.info(f"Hashrate: {hashrate:.2f} MH/s | Accepted shares: {i * 12} (simulated)")
        time.sleep(0.2)
    kevbin.box.success("Simulated balance: 0.00000000 BTC")


def social_botter(kevbin):
    kevbin.box.title("Social Botter (Simulation)")
    url = kevbin.box.input("Target link: ", "https://example.com")
    kevbin.box.warn("Simulated views only - no bot traffic sent.")
    views = 0
    for i in range(1, 13):
        views += 1337
        kevbin.box.info(f"Views: {views:,} | Likes: {views // 10:,} | Subs: {views // 75:,} (simulated)")
        time.sleep(0.12)
    kevbin.box.success("Simulation complete.")


def fake_paypal_otp(kevbin):
    kevbin.box.title("Fake PayPal OTP")
    kevbin.box.warn("SIMULATION - this code is not real and works nowhere.")
    otp = ''.join(str(random.randint(0, 9)) for _ in range(6))
    kevbin.box.table(["Code", "Expires"], [[otp, "60 seconds (simulated)"]])
    kevbin.box.info("No real PayPal account or SMS is involved.")


def fake_account_gen(kevbin):
    kevbin.box.title("Fake Account Generator")
    count = 5
    rows = []
    for _ in range(count):
        user = _fake_username()
        rows.append([user, f"{user}@mailto.plus", _fake_password(14)])
    kevbin.box.table(["Username", "Email", "Password (simulated)"], rows)
    kevbin.box.warn("These are fake credentials for testing only.")


def fake_fortnite_checker(kevbin):
    kevbin.box.title("Fake Fortnite Checker (Simulation)")
    email = kevbin.box.input("Email: ", "test@example.com")
    kevbin.box.warn("Simulation only - no accounts are checked.")
    for combo, skin in [("Default", "Raven"), ("Elite", "Galaxy"), ("Legendary", "Renegade Raider")]:
        kevbin.box.info(f"Checking {combo}... found skin: {skin} (simulated)")
        time.sleep(0.2)
    kevbin.box.info(f"{email} -> qualifies for random skin (simulated result)")


def fake_exodus(kevbin):
    kevbin.box.title("Fake Exodus Seed Phrase")
    kevbin.box.warn("SIMULATION - never type a real seed anywhere. This is fake.")
    words = ("abandon ability able about above absent absorb abstract absurd abuse "
             "access accident account accuse achieve acid acoustic acquire across").split()
    seed = " ".join(random.choice(words) for _ in range(12))
    kevbin.box.code(seed)
    kevbin.box.info("This seed controls no funds and has no value.")


def hacker_terminal(kevbin):
    kevbin.box.title("Hacker Terminal (Movie Mode)")
    kevbin.box.info("Root@kevbin:~$ grep -R topsecret /etc/passwd")
    lines = ["[ OK ] connecting to mainframe...",
             "[ OK ] bypassing firewall (simulated)",
             "[ OK ] injecting payload (visual only)",
             "[ OK ] decrypting traffic (fake)",
             "[ OK ] access granted (not really)"]
    for ln in lines:
        kevbin.box.success(ln)
        time.sleep(0.25)
    kevbin.box.warn("This is a movie-style simulation. Nothing was hacked.")


def ransomware_sim(kevbin):
    kevbin.box.title("Ransomware Simulator (Simulation)")
    kevbin.box.warn("SIMULATION ONLY - no files are encrypted or touched.")
    kevbin.box.info("Simulated ransom note (display only):")
    note = ("!! ATTENTION !!\\nYour files have been declared \"encrypted\" "
            "(simulated).\\nTo \"restore\" them, press Enter. Total: 0 bytes")
    kevbin.box.code(note)
    kevbin.box.input("Press Enter to 'restore' your files...", "")
    kevbin.box.success("Restored - nothing actually happened. Stay safe out there.")


def fake_bruteforcer(kevbin):
    kevbin.box.title("Fake Bruteforcer (Simulation)")
    target = kevbin.box.input("Hash to 'crack': ", "5e884898da28047151d0e56f8dc6292773603d0d")
    kevbin.box.warn("Simulation only - no real cracking is performed.")
    for i in range(1, 13):
        kevbin.box.info(f"[{i * 8}%] Trying pattern {random.choice(['aaaaaa', 'abc123', 'password', 'qwerty'])}... (simulated)")
        time.sleep(0.12)
    kevbin.box.success(f"Cracked (simulated): password  |  hash: {target[:12]}...")

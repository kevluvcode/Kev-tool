# KevTool

a CLI multitool i made for learning/testing. bunch of scripts mostly for osint, security stuff, text encoding, roblox tools, discord stuff, and random generators. nothing crazy but it works.

**version 1.4.1**

---

## heads up

this is strictly for educational and testing use. im not responsible if you do something dumb with it. dont use it on stuff you dont own or have permission to test. youre on your own with this one.

---

## how to install

### the easy way (windows)
1. grab the repo
2. run `install.bat` — it handles the rest
3. launch with `kevtool.bat` or `python kevtool.py`

### the easy way (linux / macOS)
1. grab the repo
2. run `bash install.sh` — it handles the rest
3. launch with `python3 kevtool.py`

### manual
```
git clone https://github.com/kevluvcode/Kev-tool.git
cd Kev-tool
pip install -r requirements.txt
python kevtool.py
```

works on **python 3.6+**, all platforms (windows, linux, macOS). if you dont have python get it from python.org

---

## what it does

207+ tools split into 13 category tabs. loading screen has a progress bar and the kevbin ASCII banner. prompt looks like `username@kevbin` with 100+ themes you can switch between. the tool menus are tabs — `[N]` / `[P]` moves between tabs, the active tab is marked with a `▲` under it and wrapped in `▌▐` (inactive tabs look like `|NAME_`), and the tab bar auto-fits your terminal width so it never wraps. every tool is shown in a centered, narrow grid. entering a tool clears the screen first. on windows the console title randomizes as an anti-close touch.

---

## auto-updating

it auto-checks for updates on every launch. compares local `version.txt` to github. if there's a newer version it downloads the zip archive, extracts to a `KevTool-{version}/` folder, copies your `settings.json` over, and launches the new version. you never lose your theme/settings. can be toggled in settings or with `check_updates: false` in `modules/config/settings.json`.

---

## auto proxy validation

on every boot it fetches the latest proxy list from the proxifly/free-proxy-list, tests them multi-threaded (HTTP via stdlib, SOCKS via PySocks) with 30 threads, and saves working ones to `valid_proxies.txt`. you see the progress live as it tests. this means valid proxies are always fresh without you having to run the checker manually.

---

## obfuscator V3

the python obfuscator has been rebuilt from scratch with multiple layers of protection:
- **XOR + Base64 layers** — multi-round XOR encryption with base64 encoding between each layer
- **ROT + XOR + Base64** — rotation cipher combined with XOR and base64
- **AST mangle** — renames variables/functions to non-obvious names
- **String encrypt** — encrypts string literals at compile time
- **Hex chunk encoding** — breaks strings into hex byte chunks
- **Junk imports** — injects misleading import statements
- **Opaque predicates** — adds dead-code branches that never execute
- **Anti-debug** — detects debuggers and exits

the **Lua obfuscator** was also upgraded with XOR string encrypt, control flow flattening, identifier mangling, opaque predicates, dead code injection, and string concatenation chaos.

---

## proxy scraper/checker

the scraper pulls from **35+ public proxy list sources** (TheSpeedX, proxifly, monogramm, roosterkid, jetkai, mmpx12, Uptox, monosans, zimuq, yuceltoluyan, B4RC0DE-TM, pproxy, H4ck4ss3, and more) covering HTTP, HTTPS, SOCKS4, SOCKS5. saves to `proxies/http.txt`, `https.txt`, `socks4.txt`, `socks5.txt` + a combined `all.txt`. the checker validates them multi-threaded and writes every working one to `valid_proxies.txt`.

---

## themes

100+ themes organized into two tiers:
- **Core themes**: modern, modern red, modern purple, blue, red, purple, green, yellow, rainbow
- **Extended themes**: dracula, monokai, nord, ocean, matrix, midnight, sunset, fire, forest, gold, cyberpunk, synthwave, terminal, high contrast, bubblegum, mint, violet, rust, steel, peacock, ember, aurora, lava, ice, candy, neon green/pink/blue/orange/purple/yellow, blood, toxic, royal, sakura, ocean deep, solarized dark/light, gruvbox, tokyo night, catppuccin, rose pine, everforest, palenight, material ocean, onedark, github dark/light, ayu dark, mellow yellow, deep sea, cherry blossom, emerald, amber, sky, crimson, jade, copper, slate, flame, twilight, spring, autumn, winter, neon rain, blood moon, deep space, sunset burn, electric, phantom, mango, coral reef, arctic fox, volcano, cosmic, jungle, honeycomb, storm, laser, horizon, nova, glacier, rebel, dream, phoenix, nebula, vapor, retro, hacker green, blood diamond, mystic

each theme controls banner gradient, header color, number color, text color, subtitle color, and input color.

---

## all the tools

### 📡 discord operations
- **Webhook Info** — view webhook details
- **Token Decoder** — decode discord tokens
- **Account Info** — pull account info from token
- **Server Info** — get server info with bot
- **Status Rotator** — status rotation reference
- **Bot Invite** — build bot invite URL

### 🔍 osint & intelligence
- **Whois Lookup** — domain registration info
- **DNS Resolver** — A/MX/TXT/CNAME/NS records
- **IP Info** — public IP info
- **Metadata Scanner** — EXIF from images
- **Username Checker** — check usernames across platforms
- **Breach Check** — see if an email got leaked
- **SSL Certificate** — cert info for a domain
- **GeoIP Lookup** — where an IP is from
- **ASN Intel** — ASN and IP range info
- **Email Validate** — check format + MX records
- **Email Reputation** — check email provider
- **Stealer Check** — credential leak lookup
- **Wayback Machine** — old snapshots of websites
- **Tech Stack** — what technologies a site uses
- **Blacklist Check** — is an IP on any blacklists

### 🛡️ security & utilities
- **Obfuscator V3** — multi-layer XOR/B64, AST mangle, anti-debug
- **Web Cloner** — save websites locally
- **Cryptography** — base64/hex/rot13
- **QR Generator** — make QR codes
- **Hash Tool** — hash stuff and look it up online
- **Base64 Image** — encode/decode images to base64
- **Ciphers** — caesar/vigenere/atbash/xor
- **JWT Tools** — decode and make JWT tokens
- **CORS Tester** — test CORS headers
- **Entropy** — shannon entropy analysis
- **Password Check** — strength + breach check
- **Timestamp** — unix timestamp converter
- **Security Headers** — check HTTP security headers
- **CSP Analyzer** — content security policy analysis
- **Honeypot Detector** — detect honeypots
- **HTTP Status** — status code lookup
- **Port Scanner** — TCP scan + banner grab
- **Traceroute** — trace network path
- **Tor Check** — check if IP is a tor exit node
- **Link Tools** — expand/track/info on URLs
- **IP Pinger** — ICMP ping
- **System Info** — CPU/RAM/disk/OS details (no psutil needed)
- **Proxy Scraper** — grab public proxies from 35+ sources → saves to `proxies/`
- **Proxy Checker** — multi-threaded validation → `valid_proxies.txt`

### 🌐 web & network tools
- **Page Clone** — clone full websites
- **Site Viewer** — view source + headers
- **Web Search** — search the web from CLI
- **Webhook Tester** — test webhook endpoints
- **Webhook Delete** — delete webhooks
- **Link Bypass** — bypass link shorteners
- **Link Spoof** — see redirect chains
- **Link Tracker** — track link clicks
- **Browser FP** — browser fingerprinting
- **Webrtc Leak** — detect WebRTC IP leaks
- **DNS over HTTPS** — encrypted DNS queries
- **Subdomain Enum** — find subdomains
- **Subnet Calculator** — CIDR math

### 📝 text & encoding
- **Text Transform** — case/reverse/repeat
- **Slug Generator** — URL-safe slugs
- **Sort Lines** — alphabetical/numeric sort
- **Markdown Preview** — render markdown
- **Diff Tool** — compare two texts
- **CSV Viewer** — parse and display CSV
- **JSON Formatter** — pretty-print JSON
- **SQL Formatter** — format SQL queries
- **Regex Tester** — test regular expressions
- **Word Counter** — word/char/line count
- **Slugify** — convert to slug format
- **HTML Entity** — encode/decode HTML entities
- **URL Encode** — URL encode/decode
- **Unicode Tool** — unicode lookup/conversion
- **Emoji Lookup** — find emoji codes
- **Text Stats** — readability analysis

### 🎨 color & design
- **Color Converter** — HEX/RGB/HSL conversion
- **Gradient Generator** — CSS gradient builder
- **Contrast Checker** — WCAG contrast ratio
- **Color Palette** — generate color palettes
- **Image Colors** — extract colors from an image

### 💾 data & conversion
- **Base-N Encoder** — binary/octal/hex encoding
- **Base64 Decode** — decode base64 strings
- **Roman Numerals** — to/from roman numerals
- **Number System** — dec/hex/bin/oct conversion
- **Percentage Calc** — percentage math
- **YAML ↔ TOML** — convert between formats
- **CSV Tools** — parse/merge CSV files
- **JSON ↔ XML** — convert between formats
- **Receipt Generator** — make fake receipts
- **UUID Generator** — generate UUIDs v4
- **Barcode Generator** — code128/code39
- **Password Generator** — make secure passwords
- **Random Data** — random numbers/strings
- **Duration Calc** — time duration math
- **Age Calculator** — calculate age from DOB

### 🎮 game suite (roblox)
- **User Intel** — look up roblox users
- **Group Intel** — look up roblox groups
- **Name History** — previous usernames
- **Username Check** — is a username available
- **Cookie Login** — validate .ROBLOSECURITY
- **Asset Downloader** — download roblox assets
- **Inventory Viewer** — view user inventories
- **Game Info** — roblox game details

### 🎭 simulation & generators
- **Identity Generator** — realistic fake identities
- **Credit Card Gen** — test card numbers (luhn check)
- **Crypto Wallets** — generate wallet addresses
- **Username Generator** — unique usernames
- **Password Generator** — secure passwords
- **Lorem Ipsum** — placeholder text
- **Fake Nitro Code** — random nitro-style codes
- **Server Template** — discord server JSON
- **Fake Mail** — fake email + password
- **Fake DDoS** — simulated DDoS output (no packets sent)
- **Fake Wallet Miner** — simulated mining rig
- **Social Botter** — simulated view counter
- **Fake PayPal OTP** — fake OTP code
- **Fake Account Gen** — fake credentials
- **Fake Fortnite Check** — simulated skin checker
- **Fake Exodus** — fake crypto seed phrase
- **Hacker Terminal** — movie-style hacker typer
- **Ransomware Sim** — simulated ransomware warn (nothing touched)
- **Fake Bruteforcer** — simulated brute force counter
- **ASCII Art** — text to ASCII art
- **Stealth Art** — zalgo/glitch text
- **Creeper Text** — creeper text effect
- **Small Caps** — small caps text
- **Bubble Text** — bubble unicode text
- **Mirror Text** — flipped/mirrored text

### 📡 network & DNS
- **Port Scanner** — TCP scan + banners
- **Traceroute** — trace network path
- **DNS Resolver** — resolve DNS records
- **DNS over HTTPS** — encrypted DNS
- **Subdomain Enum** — find subdomains
- **Subnet Calculator** — CIDR math
- **Whois** — domain registration lookup
- **IP Pinger** — ICMP ping
- **ASN Lookup** — ASN info
- **Blacklist Check** — IP blacklist check

### 🔧 developer tools
- **Request Builder** — build HTTP requests
- **Header Inspector** — view/edit headers
- **Cookie Inspector** — view/edit cookies
- **JS Obfuscator** — javascript obfuscation
- **Lua Obfuscator** — lua code obfuscation (XOR, flow flatten, mangle, dead code)
- **Lua Sandbox** — run lua code safely
- **Cron Builder** — build cron expressions
- **Cron Parser** — parse cron schedules
- **Code Formatter** — format source code
- **YAML/TOML** — config file conversion
- **JSON Formatter** — pretty-print JSON
- **SQL Formatter** — format SQL queries

### 📁 file & image tools
- **File Type Detector** — identify file types
- **Image to Base64** — encode images to base64
- **Photo Metadata** — EXIF extraction
- **Metadata Stripper** — remove file metadata
- **Hex Dump** — view hex data
- **Steganography** — hide data in images
- **File Checksum** — MD5/SHA hash files
- **Binary Viewer** — view binary data

### ⚙️ themes & settings
- switch between 100+ themes
- auto-update via zip download (preserves settings)
- auto-proxy validation on boot
- check for updates manually
- view version and user info

---

## file structure

```
Kev-tool/
├── kevtool.py          # main app
├── kevtool.bat         # windows launcher
├── valid_proxies.txt   # working proxies (auto-refreshed on boot)
├── proxies/            # scraped proxy lists (runtime output)
└── modules/
    ├── config/         # settings.json
    ├── install.bat     # windows installer
    ├── install.sh      # linux/macOS installer
    ├── version.txt     # version tracking
    ├── requirements.txt# python dependencies
    ├── readme.md       # you're reading this
    ├── system_info.py  # system info
    ├── proxy_scraper.py# proxy grabber (35+ sources)
    ├── proxy_checker.py# proxy validator
    ├── obfuscator.py   # Obfuscator V3 (multi-layer)
    ├── lua_obfuscator.py# lua obfuscation
    ├── discord_ops.py  # discord stuff
    ├── roblox_intel.py # roblox lookups
    ├── faker_suite.py  # simulation/generators
    └── ...             # more modules
```

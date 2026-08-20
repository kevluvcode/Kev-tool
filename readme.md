# KevTool

a CLI multitool i made for learning/testing. bunch of scripts mostly for osint, security stuff, text encoding, roblox tools, discord stuff, and random generators. nothing crazy but it works.

**version 1.5.0**

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

215+ tools split into 13 category tabs. loading screen has a progress bar and the kevbin ASCII banner. prompt looks like `username@kevbin` with 100+ themes you can switch between. the tool menus are tabs — `[N]` / `[P]` moves between tabs, the active tab is marked with a `▲` under it and wrapped in `▌▐` (inactive tabs look like `|NAME_`), and the tab bar auto-fits your terminal width so it never wraps. every tool is shown in a centered, narrow grid. entering a tool clears the screen first. on windows the console title randomizes as an anti-close touch.

---

## auto-updating

it auto-checks for updates on every launch. compares local `version.txt` to github. if there's a newer version it downloads the zip archive, extracts to a `KevTool-{version}/` folder, copies your `settings.json` over, and launches the new version. you never lose your theme/settings. can be toggled in settings or with `check_updates: false` in `modules/config/settings.json`.

---

## auto proxy validation

on every boot it fetches the latest proxy list from **55 sources** in parallel, tests them multi-threaded with 80 threads and 2s socket timeout, and saves working ones to `valid_proxies.txt`. you see a live progress bar as it tests. valid proxies are always fresh without you having to run the checker manually.

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

the **Lua obfuscator** was also upgraded with XOR string encrypt, control flow flattening, identifier mangling, opaque predicates, dead code injection, and string concatenation chaos. now saves output to a file.

---

## v1.5.0 new modules

### hash cracker
hash identification from any length, dictionary attack with built-in 220+ wordlist, file-based wordlist support, multi-threaded brute-force mode. returns hash algorithm, hex/digest, and cracked passwords.

### WAF detector
identifies web application firewalls (Cloudflare, Akamai, AWS WAF, Imperva, Sucuri, etc.) via response headers and HTML signatures. includes a payload testing mode to see which payloads get blocked.

### directory bruteuter
web directory and file brute-forcer. multi-threaded with custom or built-in wordlists, extension appending, status code filtering, hide 403/404, recursive mode, save results to file.

### network scan
local network utility: ARP sweep to find live hosts, port sweep on individual IPs, local IP info. all pure-socket, no external dependencies.

### batch renamer
bulk file renaming with preview. supports find/replace, prefix/suffix, sequence numbering, regex replacement. dry-run mode shows changes before committing.

### log parser
analyze log files (Apache, nginx, etc.). full analysis with status code breakdown, top IPs, top paths, bandwidth. filter by status code, IP, path, keyword search. top-N lists.

### notes tool
XOR-encrypted notes with user password. create, list, read, delete, and search notes stored in `modules/config/notes/`.

### calculator
scientific calculator (sin, cos, tan, log, sqrt, powers), base converter (bin/oct/hex/any base), random number generator with ranges, date calculator, mathematical constants reference.

---

## improved modules

- **Hash Tool** — now supports HMAC, file hashing, CRC32, hash comparison, and all-algorithm hash
- **Ciphers** — expanded to 9 ciphers: Caesar, Vigenere, Atbash, XOR, ROT13, Rail Fence, Baconian, Autokey, plus frequency analysis
- **Password Generator** — added passphrase mode with word lists, batch generation, and strength checker with entropy visualization
- **Port Scanner** — rewritten with presets (Web, Mail, DB, etc.), multi-threaded scanning, 1000+ service port database, banner grabbing
- **Entropy** — added frequency bar chart, string comparison, crack time estimates
- **UUID Generator** — added v1/v3/v5, UUID parsing/decoding, batch with format options
- **Regex Tester** — added replace mode, group capture display, save result to file
- **QR Generator** — added styled QR with custom colors, decode QR from image files

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
- **Web Cloner** — save websites locally with all assets
- **Cryptography** — base64/hex/rot13
- **QR Generator** — make + decode QR codes
- **Hash Tool** — hash files/strings + HMAC + CRC32
- **Base64 Image** — encode/decode images to base64
- **Ciphers** — 9 ciphers + frequency analysis
- **JWT Tools** — decode and make JWT tokens
- **CORS Tester** — test CORS headers
- **Entropy** — frequency analysis + entropy + crack times
- **Password Check** — strength + breach check
- **Timestamp** — unix timestamp converter
- **Security Headers** — check HTTP security headers
- **CSP Analyzer** — content security policy analysis
- **Honeypot Detector** — detect honeypots
- **HTTP Status** — status code lookup
- **Port Scanner** — multi-threaded + service detection
- **Traceroute** — trace network path
- **Tor Check** — check if IP is a tor exit node
- **Link Tools** — expand/track/info on URLs
- **IP Pinger** — ICMP ping
- **System Info** — CPU/RAM/disk/OS details (no psutil needed)
- **Proxy Scraper** — grab public proxies from 35+ sources
- **Proxy Checker** — multi-threaded validation
- **Hash Cracker** — hash ID + wordlist crack + brute-force

### 🌐 web & network tools
- **Web Cloner** — save websites locally with all assets
- **Site Viewer** — view source + headers
- **Web Search** — search the web from CLI
- **Webhook Tester** — test webhook endpoints
- **Webhook Delete** — delete webhooks
- **Link Bypass** — bypass link shorteners
- **Link Spoof** — see redirect chains
- **Link Tracker** — track link clicks
- **Browser FP** — browser fingerprinting
- **WebRTC Leak** — detect WebRTC IP leaks
- **DNS over HTTPS** — encrypted DNS queries
- **Subdomain Enum** — find subdomains
- **Subnet Calculator** — CIDR math
- **Curl Builder** — generate curl commands
- **URL Parser** — break down a URL
- **User-Agent Gen** — random real UAs
- **WAF Detector** — identify web application firewalls
- **Directory Brute** — web directory/file brute forcer
- **Calculator** — scientific calculator + base converter

### 📝 text & encoding
- **Text Transform** — case/reverse/repeat
- **Slug Generator** — URL-safe slugs
- **Sort Lines** — alphabetical/numeric sort
- **Markdown Preview** — render markdown
- **Diff Tool** — compare two texts
- **CSV Viewer** — parse and display CSV
- **JSON Formatter** — pretty-print JSON
- **SQL Formatter** — format SQL queries
- **Regex Tester** — test regular expressions + replace
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
- **UUID Generator** — UUID v1/v3/v4/v5 + parse/decode
- **Barcode Generator** — code128/code39
- **Password Generator** — passphrases + strength checker
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
- **Port Scanner** — multi-threaded + banner grab
- **Traceroute** — trace network path
- **DNS Resolver** — resolve DNS records
- **DNS over HTTPS** — encrypted DNS
- **Subdomain Enum** — find subdomains
- **Subnet Calculator** — CIDR math
- **Whois** — domain registration lookup
- **IP Pinger** — ICMP ping
- **ASN Lookup** — ASN info
- **Blacklist Check** — IP blacklist check
- **Network Scan** — ARP sweep + port sweep

### 🔧 developer tools
- **Request Builder** — build HTTP requests
- **Header Inspector** — view/edit headers
- **Cookie Inspector** — view/edit cookies
- **JS Obfuscator** — javascript obfuscation
- **Lua Obfuscator** — lua code obfuscation (saves to file)
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
- **Batch Renamer** — bulk rename files with preview

### 📋 notes & analysis
- **Notes Tool** — XOR-encrypted notes with password
- **Log Parser** — analyze/filter web server logs
- **Hash Cracker** — hash ID + dictionary/brute attack

### 🧮 calculators & converters
- **Calculator** — scientific calc + base converter + date calc
- **Calculator** — trig, log, sqrt, powers, constants
- **Base Converter** — any base (2-36)
- **Date Calculator** — days between dates
- **Random Number** — ranges, seeds, distributions

### ⚙️ themes & settings
- switch between 100+ themes
- auto-update via zip download (preserves settings)
- auto-proxy validation on boot (55 sources, 80 threads)
- check for updates manually
- view version and user info

---

## file structure

```
Kev-tool/
├── kevtool.py              # main app
├── kevtool.bat             # windows launcher
├── valid_proxies.txt       # working proxies (auto-refreshed on boot)
├── proxies/                # scraped proxy lists (runtime output)
└── modules/
    ├── config/             # settings.json + notes/
    ├── install.bat         # windows installer
    ├── install.sh          # linux/macOS installer
    ├── version.txt         # version tracking
    ├── requirements.txt    # python dependencies
    ├── obfuscator.py       # Obfuscator V3 (multi-layer)
    ├── lua_obfuscator.py   # lua obfuscation (saves to file)
    ├── hash_cracker.py     # hash ID + crack (NEW)
    ├── waf_detect.py       # WAF detection (NEW)
    ├── directory_brute.py  # web dir brute (NEW)
    ├── network_scan.py     # ARP + port scan (NEW)
    ├── batch_renamer.py    # bulk rename (NEW)
    ├── log_parser.py       # log analysis (NEW)
    ├── notes_tool.py       # encrypted notes (NEW)
    ├── calculator.py       # scientific calc (NEW)
    ├── port_scanner.py     # multi-threaded scanner
    ├── password_gen.py     # passphrases + batch + strength
    ├── hash_tool.py        # hash + HMAC + CRC32
    ├── ciphers.py          # 9 ciphers + freq analysis
    ├── entropy.py          # frequency chart + crack times
    ├── uuid_gen.py         # v1/v3/v4/v5 + parse
    ├── regex_tester.py     # regex + replace + groups
    ├── qr_gen.py           # QR gen + decode + styled
    ├── proxy_scraper.py    # proxy grabber (35+ sources)
    ├── proxy_checker.py    # proxy validator
    ├── system_info.py      # system info
    ├── discord_ops.py      # discord stuff
    ├── roblox_intel.py     # roblox lookups
    ├── faker_suite.py      # simulation/generators
    └── ...                 # more modules
```

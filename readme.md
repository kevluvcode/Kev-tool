# KevTool

a CLI multitool for learning/testing. 215+ tools across 14 tabs -- osint, security, malware builders, discord ops, roblox tools, text encoding, generators, and more.

**version 1.9.4**

---

## heads up

this is strictly for educational and testing use. im not responsible if you do something dumb with it. dont use it on stuff you dont own or have permission to test. youre on your own with this one.

---

## how to install

### the easy way (windows)
1. grab the repo
2. run install.bat -- it handles the rest
3. launch with kevtool.bat or python kevtool.py

### the easy way (linux / macOS)
1. grab the repo
2. run bash install.sh -- it handles the rest
3. launch with python3 kevtool.py

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

215+ tools split into 14 category tabs. loading screen has a progress bar and the kevbin ASCII banner. prompt looks like username@kevbin with 100+ themes you can switch between. the tool menus are tabs -- [N] / [P] moves between tabs, the active tab is marked with a triangle under it and wrapped in special chars (inactive tabs look like |NAME_), and the tab bar auto-fits your terminal width so it never wraps. every tool is shown in a centered, narrow grid. entering a tool clears the screen first. on windows the console title randomizes as an anti-close touch.

---

## auto-updating

it auto-checks for updates on every launch. compares local version.txt to github. if there is a newer version it downloads the zip archive, extracts to a KevTool-{version}/ folder, copies your settings.json over, and launches the new version. you never lose your theme/settings. can be toggled in settings or with check_updates: false in modules/config/settings.json.

---

## auto proxy validation

on every boot it fetches the latest proxy list from **150+ sources** in parallel, tests them multi-threaded with 200 threads and 0.8s socket timeout, and saves working ones to valid_proxies.txt. you see a live progress bar with ETA and speed during both the fetch and test phases. valid proxies are always fresh without you having to run the checker manually. skips scan if valid_proxies.txt is less than 1 hour old.

---

## obfuscator V3

the python obfuscator has been rebuilt from scratch with multiple layers of protection:
- **XOR + Base64 layers** -- multi-round XOR encryption with base64 encoding between each layer
- **ROT + XOR + Base64** -- rotation cipher combined with XOR and base64
- **AST mangle** -- renames variables/functions to non-obvious names
- **String encrypt** -- encrypts string literals at compile time
- **Hex chunk encoding** -- breaks strings into hex byte chunks
- **Junk imports** -- injects misleading import statements
- **Opaque predicates** -- adds dead-code branches that never execute
- **Anti-debug** -- detects debuggers and exits

the **Lua obfuscator** was also upgraded with XOR string encrypt, control flow flattening, identifier mangling, opaque predicates, dead code injection, and string concatenation chaos. now saves output to a file.

---

## tab layout (14 tabs)

| # | Tab | Description |
|---|-----|-------------|
| 1 | DISCORD | Discord operations, webhooks, tokens, selfbot tools |
| 2 | OSINT | Whois, DNS, breach check, phone lookup, IP grabber, GitHub dorker |
| 3 | SECURITY | Obfuscator, crypto, ciphers, ports, proxy, scanners |
| 4 | MALWARE | Discord RAT, Token Grabber, Keylogger, Crypto Clipper, Recovery Tool, HWID Spoofer, SQL Scanner, Dox Tool, Email Bomber, DDoS, App Decrypter, Offset Dumper |
| 5 | WEB | Web cloner, DNS over HTTPS, subdomains, viewbot |
| 6 | TEXT | Encoding, formatting, regex, morse code, leet speak |
| 7 | COLOR | Color conversion, palettes, gradients |
| 8 | DATA | Base-N, UUID, barcode, password gen, calculators |
| 9 | ROBLOX | User/group intel, cookie login, asset download |
| 10 | SIM | Fake identities, wallets, terminals, simulations |
| 11 | NET | Port scanner, traceroute, DNS, WiFi scanner |
| 12 | DEV | Request builder, obfuscators, formatters |
| 13 | FILE | File type, hex dump, steganography, checksums |
| 14 | SETTINGS | Themes (100+), updates, proxy |

---

## all the tools

### discord operations
- Webhook Info, Token Decoder, Account Info, Server Info, Status Rotator, Bot Invite, Snowflake, Embed Builder, Webhook Spammer, Token Nuker, Onliner, Nitro Generator, Server Cloner, DM Logger, Nitro Snipe, Webhook Deployer

### osint & intelligence
- Whois Lookup, DNS Resolver, IP Info, Metadata Scanner, Username Checker, Breach Check, SSL Certificate, GeoIP Lookup, ASN Intel, Email Validate, Email Reputation, Stealer Check, Wayback Machine, Tech Stack, Blacklist Check, Email Format Gen, URL Extractor, OSINT Report, Phone Lookup, IP Grabber, GitHub Dorker

### security & utilities
- Obfuscator V3, Web Cloner, Cryptography, QR Generator, Hash Tool, Base64 Image, Ciphers, JWT Tools, CORS Tester, Entropy, Password Check, Timestamp, Security Headers, CSP Analyzer, Honeypot Detector, HTTP Status, Port Scanner, Traceroute, Tor Check, Link Tools, IP Pinger, System Info, Proxy Scraper, Proxy Checker, OTP Generator, Hex Dump, Hash Cracker, VirusTotal

### malware & builders

- **Discord RAT** -- full Discord C2 RAT with WebSocket Gateway client (.py/.exe). shell, screenshot, WiFi dump, clipboard, file download, webcam capture, audio recording, keylogger, browser data theft, UAC/AMSI bypass, persistence, stealth mode.

  connects via WebSocket Gateway (not REST polling). uses intents GUILDS + GUILD_MESSAGES + MESSAGE_CONTENT. webhook used for sending responses/files back to Discord. shows offline in Discord (normal -- no gateway status updates).

  **persistence** -- triple-method: registry Run key + startup folder shortcut + scheduled task. randomized filename from disguises list (csrss, svchost, RuntimeBroker, etc). skips if already persisted.

  **stealth** -- anti-VM (file artifacts, WMI manufacturer, BIOS serial), anti-debug (IsDebuggerPresent, sandbox resource checks), console hidden, randomized window title, sleep jitter, reconnect backoff with jitter.

  RAT commands (prefix + command):

  | Command | Description |
  |---------|-------------|
  | `info` | System info (user, PC, OS, IP) |
  | `sysinfo` | Detailed system info (RAM, disks) |
  | `shell <cmd>` | Run shell command |
  | `cd <path>` | Change directory |
  | `ls [path]` | List directory contents |
  | `screenshot` | Capture screen (PowerShell System.Drawing, sent as PNG) |
  | `clipboard` | Get clipboard content |
  | `setclip <txt>` | Set clipboard content |
  | `wifi` | Show saved WiFi passwords |
  | `processes` | List running processes |
  | `killproc <name>` | Kill process by name |
  | `download <file>` | Send file via webhook |
  | `webcam` | Capture webcam image (dshow/VFW) |
  | `audio [sec]` | Record audio 1-30s (winmm waveIn, default 5s) |
  | `keylog` | Start in-process keylogger (webhook exfil) |
  | `keylog_stop` | Stop keylogger and dump captured keystrokes |
  | `steal_browser` | Steal Chrome/Edge/Firefox Login Data, Cookies, History |
  | `uac` | Attempt UAC bypass (fodhelper registry debugger) |
  | `amsi` | Bypass AMSI for current session (AmsiUtils patch) |
  | `persist` | Install persistence (triple-method) |
  | `kill` | Terminate RAT |

  **builder options** -- webhook URL, bot token (for commands), channel ID, command prefix, persistence toggle, stealth mode, beacon interval, custom .ico icon, custom persistence filename, custom output directory, debug mode.

- **Token Grabber** -- build Discord token grabber .exe with browser data exfil
- **Keylogger Builder** -- live keylogger + builder with webhook exfil, persistence, stealth
- **Crypto Clipper** -- clipboard monitor & crypto address swapper with Discord webhook notifications
- **Recovery Tool** -- browser data extraction (passwords, cookies, history)
- **HWID Spoofer** -- spoof all HWID identifiers (MAC, UUID, ProductId, Hostname, BIOS, BaseBoard, Disk, Volume Serial, registry noise) with backup/restore and debug mode
- **SQL Scanner** -- SQL injection scanner
- **Doxxer Tool** -- dox tracker & creator
- **Email Bomber** -- bulk email sender via SMTP
- **DDoS Tool** -- layer 7 HTTP flood stress test
- **App Decrypter** -- decrypt/rebuild .exe .dll .so with live runtime decrypt
- **Offset Dumper** -- hex view + search + PE/ELF sections

### web & network tools
- Web Cloner, Site Viewer, Web Search, Webhook Tester, Webhook Delete, Link Bypass, Link Spoof, Link Tracker, Browser FP, WebRTC Leak, DNS over HTTPS, Subdomain Enum, Subnet Calculator, Curl Builder, URL Parser, User-Agent Gen, WAF Detector, Directory Brute, Calculator, Guns Viewbot

### text & encoding
- Text Transform, Slug Generator, Sort Lines, Markdown Preview, Diff Tool, CSV Viewer, JSON Formatter, SQL Formatter, Regex Tester, Word Counter, HTML Entity, URL Encode, Unicode Tool, Emoji Lookup, Text Stats, Text/Binary, Morse Code, Leet Speak, Reverse/Upside, Word Scrambler, Palindrome Check, Random Haiku

### color & design
- Color Converter, Gradient Generator, Contrast Checker, Color Palette, Image Colors, Random Color, ANSI Tester, Tints & Shades, Named Colors

### data & conversion
- Base-N Encoder, Base64 Decode, Roman Numerals, Number System, Percentage Calc, YAML/TOML, CSV Tools, JSON/XML, Receipt Generator, UUID Generator, Barcode Generator, Password Generator, Random Data, Duration Calc, Age Calculator, Unit Converter, Byte Converter, Interest Calc, BMI Calc, Prime & Factors, Date Diff

### roblox game suite
- User Intel, Group Intel, Name History, Username Check, Cookie Login, Asset Downloader, Inventory Viewer, Game Info, Link Builder, Username Styles, Gamertag Gen

### simulation & generators
- Identity Generator, Credit Card Gen, Crypto Wallets, Username Generator, Password Generator, Lorem Ipsum, Fake Nitro Code, Server Template, Fake Mail, Fake DDoS, Fake Wallet Miner, Social Botter, Fake PayPal OTP, Fake Account Gen, Fake Fortnite Check, Fake Exodus, Hacker Terminal, Ransomware Sim, Fake Bruteforcer, ASCII Art, Stealth Art, Creeper Text, Small Caps, Bubble Text, Mirror Text, Fake Crypto Wallet, Fake Money, Fake IP/MAC/Phone/Address/Company, Hacker Alias, Buzzword Gen, Emoji Flood

### network & DNS
- Port Scanner, Traceroute, DNS Resolver, DNS over HTTPS, Subdomain Enum, Subnet Calculator, Whois, IP Pinger, ASN Lookup, Blacklist Check, Port Lookup, Random Domain, Subnet List, WiFi Scanner

### developer tools
- Request Builder, Header Inspector, Cookie Inspector, JS Obfuscator, Lua Obfuscator, Lua Sandbox, Cron Builder, Cron Parser, Code Formatter, YAML/TOML, JSON Formatter, SQL Formatter, Code Minify, Case Converter, Semver Compare, UUID/Hash Gen, Bracket Matcher

### file & image tools
- File Type Detector, Image to Base64, Photo Metadata, Metadata Stripper, Hex Dump, Steganography, File Checksum, Binary Viewer, Dir Tree, File Search, Biggest Files, Path Info

### themes & settings
- 100+ themes (modern, dracula, monokai, nord, cyberpunk, synthwave, matrix, and 90+ more)
- auto-update via zip download (preserves settings)
- auto-proxy validation on boot (150+ sources, 200 threads, 0.8s timeout)
- check for updates manually
- view version and user info

---

## themes

100+ themes organized into two tiers:
- **Core themes**: modern, modern red, modern purple, blue, red, purple, green, yellow, rainbow
- **Extended themes**: dracula, monokai, nord, ocean, matrix, midnight, sunset, fire, forest, gold, cyberpunk, synthwave, terminal, high contrast, bubblegum, mint, violet, rust, steel, peacock, ember, aurora, lava, ice, candy, neon variants, blood, toxic, royal, sakura, ocean deep, solarized, gruvbox, tokyo night, catppuccin, rose pine, everforest, palenight, material ocean, onedark, github dark/light, and many more

each theme controls banner gradient, header color, number color, text color, subtitle color, and input color.

---

## file structure

```
Kev-tool/
  kevtool.py              # main app (14 tabs, 215+ tools)
  kevtool.bat             # windows launcher
  valid_proxies.txt       # working proxies (auto-refreshed on boot, 1hr freshness)
  .gitignore              # excludes cloned_*/, kevtool_obf.py, recovery_*/
  modules/
    config/               # settings.json + notes/
    version.txt           # version tracking
    requirements.txt      # python dependencies
    browser_utils.py      # shared browser kill/access/decrypt utils
    obfuscator.py         # Obfuscator V3 (multi-layer)
    lua_obfuscator.py     # lua obfuscation
    discord_ops.py        # discord operations (16 functions)
    hwid_spoofer.py       # HWID spoofer v2 (15 options)
    discord_rat.py        # RAT builder (.py/.exe) -- WebSocket Gateway, 21 commands
    token_grabber.py      # token grabber builder (.py/.exe)
    keylogger.py          # keylogger builder (.py/.exe)
    crypto_clipper.py     # clipboard swapper builder (.py/.exe)
    recovery_tool.py      # browser data extraction
    sql_scanner.py        # SQL injection scanner
    dox_tool.py           # dox creator/tracker
    email_bomber.py       # bulk email sender
    ddos_tool.py          # layer 7 HTTP flood
    app_decrypter.py      # decrypt/rebuild .exe .dll .so
    offset_dumper.py      # hex view + PE/ELF sections
    guns_viewbot.py       # honest HTTP flood viewbot
    wifi_scanner.py       # saved WiFi + passwords
    github_dorker.py      # GitHub secret dorker
    virus_total.py        # VT file/URL/hash scan
    webhook_deployer.py   # create/test/manage webhooks
    phone_lookup.py       # phone number OSINT
    ip_grabber.py         # IP grabber link builder
    ...                   # 100+ more modules
```

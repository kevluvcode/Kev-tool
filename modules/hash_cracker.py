"""Hash Cracker — Identify hash type + crack with wordlist."""

import hashlib
import string
import os


COMMON_ALIASES = {
    32: ['MD5', 'NTLM', 'MD4'],
    40: ['SHA1', 'RIPEMD-160'],
    56: ['SHA224'],
    64: ['SHA256', 'BLAKE2s-256'],
    96: ['SHA384'],
    128: ['SHA512', 'BLAKE2b-512'],
    16: ['CRC32'],
    8: [' Adler32'],
}

ALGO_MAP = {
    'MD5': hashlib.md5,
    'SHA1': hashlib.sha1,
    'SHA256': hashlib.sha256,
    'SHA224': hashlib.sha224,
    'SHA384': hashlib.sha384,
    'SHA512': hashlib.sha512,
    'MD4': lambda b: __import__('hashlib').md4(b),
}

BUILTIN_WORDS = [
    'password', '123456', '12345678', 'qwerty', 'abc123', 'monkey', 'master',
    'dragon', '111111', 'baseball', 'iloveyou', 'trustno1', 'sunshine',
    'princess', 'football', 'charlie', 'shadow', 'michael', 'letmein',
    'password1', 'admin', 'welcome', 'hello', 'passw0rd', 'starwars',
    'hello123', 'access', 'hello1', 'loveme', 'fuckyou', '1234567',
    'hunter2', 'batman', 'matrix', 'secret', 'summer', 'winter',
    'spring', 'autumn', 'orange', 'pepper', 'jennifer', 'jordan',
    'thomas', 'hunter', 'ranger', 'hockey', 'george', 'andrew',
    'joshua', 'computer', 'internet', 'cookie', 'coffee', 'donald',
]


def _hash_hex(algo, data):
    try:
        return hashlib.new(algo.lower(), data.encode()).hexdigest()
    except Exception:
        return None


def identify_hash(hash_str):
    h = hash_str.strip().lower()
    length = len(h)
    if not all(c in string.hexdigits for c in h):
        return ['Not a hex string'], length
    algos = COMMON_ALIASES.get(length, ['Unknown'])
    return algos, length


def crack_wordlist(hash_str, algo_name, wordlist_path, kevbin=None):
    h = hash_str.strip().lower()
    algo_upper = algo_name.upper()
    count = 0
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                word = line.strip()
                if not word:
                    continue
                count += 1
                test = _hash_hex(algo_upper, word)
                if test and test == h:
                    return word, count
                if kevbin and count % 50000 == 0:
                    kevbin.cprint(kevbin.t.dim, f"  [~] {count:,} words tested...")
    except FileNotFoundError:
        return None, -1
    return None, count


def crack_builtin(hash_str, algo_name):
    h = hash_str.strip().lower()
    algo_upper = algo_name.upper()
    for word in BUILTIN_WORDS:
        test = _hash_hex(algo_upper, word)
        if test and test == h:
            return word
    return None


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🔓', 'HASH CRACKER')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Identify hash type")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Crack with built-in list")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Crack with wordlist file")
        kevbin.cprint(kevbin.t.secondary, "  [4]  Brute-force all algos (short words)")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0':
            return

        if choice == '1':
            h = kevbin.input_choice("  Hash: ").strip()
            if not h:
                continue
            algos, length = identify_hash(h)
            kevbin.cprint(kevbin.t.accent, f"\n  Length: {length} chars")
            kevbin.cprint(kevbin.t.accent, f"  Possible: {', '.join(algos)}")
            kevbin.pause()

        elif choice == '2':
            h = kevbin.input_choice("  Hash: ").strip()
            if not h:
                continue
            algos, _ = identify_hash(h)
            kevbin.cprint(kevbin.t.dim, f"  Trying {len(BUILTIN_WORDS)} common passwords...")
            for algo in algos:
                result = crack_builtin(h, algo)
                if result:
                    kevbin.cprint(kevbin.t.success, f"\n  [✓] FOUND! Algorithm: {algo}")
                    kevbin.cprint(kevbin.t.success, f"  Password: {result}")
                    kevbin.pause()
                    break
            else:
                kevbin.cprint(kevbin.t.warning, "\n  [!] Not found in built-in list.")
                kevbin.pause()

        elif choice == '3':
            h = kevbin.input_choice("  Hash: ").strip()
            if not h:
                continue
            path = kevbin.input_choice("  Wordlist path: ").strip().strip('"').strip("'")
            if not path or not os.path.isfile(path):
                kevbin.cprint(kevbin.t.error, "  [X] File not found.")
                kevbin.pause()
                continue
            algos, _ = identify_hash(h)
            kevbin.cprint(kevbin.t.dim, f"  Testing against {len(algos)} algorithms...")
            for algo in algos:
                result, tested = crack_wordlist(h, algo, path, kevbin)
                if tested == -1:
                    kevbin.cprint(kevbin.t.error, f"  [X] Could not read wordlist.")
                    break
                if result:
                    kevbin.cprint(kevbin.t.success, f"\n  [✓] FOUND! Algorithm: {algo}")
                    kevbin.cprint(kevbin.t.success, f"  Password: {result}")
                    kevbin.cprint(kevbin.t.dim, f"  Tried {tested:,} words")
                    break
                kevbin.cprint(kevbin.t.dim, f"  [{algo}] not found after {tested:,} words")
            else:
                kevbin.cprint(kevbin.t.warning, "\n  [!] Exhausted all algorithms.")
            kevbin.pause()

        elif choice == '4':
            h = kevbin.input_choice("  Hash: ").strip()
            if not h:
                continue
            algos, _ = identify_hash(h)
            import itertools
            chars = string.ascii_lowercase + string.digits
            kevbin.cprint(kevbin.t.dim, "  Brute-forcing short words (1-4 chars)...")
            found = False
            for length in range(1, 5):
                count = 0
                for combo in itertools.product(chars, repeat=length):
                    word = ''.join(combo)
                    count += 1
                    for algo in algos:
                        test = _hash_hex(algo, word)
                        if test and test == h.lower():
                            kevbin.cprint(kevbin.t.success, f"\n  [✓] FOUND! Algorithm: {algo}")
                            kevbin.cprint(kevbin.t.success, f"  Password: {word}")
                            found = True
                            break
                    if found:
                        break
                    if count % 100000 == 0:
                        kevbin.cprint(kevbin.t.dim, f"  [{algo}] length {length}: {count:,} tried...")
                if found:
                    break
            if not found:
                kevbin.cprint(kevbin.t.warning, "\n  [!] Not found (max 4 chars).")
            kevbin.pause()

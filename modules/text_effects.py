import random

ZALGO_UP = ['\u0300', '\u0301', '\u0302', '\u0303', '\u0304', '\u0305', '\u0306', '\u0307', '\u0308', '\u0309', '\u030a', '\u030b', '\u030c', '\u030d', '\u030e', '\u030f', '\u0310', '\u0311', '\u0312', '\u0313', '\u0314', '\u0315', '\u0316', '\u0317', '\u0318', '\u0319', '\u031a', '\u031b', '\u031c', '\u031d', '\u031e', '\u031f', '\u0320', '\u0321', '\u0322', '\u0323', '\u0324', '\u0325', '\u0326', '\u0327', '\u0328', '\u0329', '\u032a', '\u032b', '\u032c', '\u032d', '\u032e', '\u032f', '\u0330', '\u0331', '\u0332', '\u0333', '\u0334', '\u0335', '\u0336', '\u0337', '\u0338', '\u0339', '\u033a', '\u033b', '\u033c', '\u033d', '\u033e', '\u033f', '\u0340', '\u0341', '\u0342', '\u0343', '\u0344', '\u0345', '\u0346', '\u0347', '\u0348', '\u0349', '\u034a', '\u034b', '\u034c', '\u034d', '\u034e', '\u034f', '\u0350', '\u0351', '\u0352', '\u0353', '\u0354', '\u0355', '\u0356', '\u0357', '\u0358', '\u0359', '\u035a', '\u035b', '\u035c', '\u035d', '\u035e', '\u035f', '\u0360', '\u0361', '\u0362', '\u0363', '\u0364', '\u0365', '\u0366', '\u0367', '\u0368', '\u0369', '\u036a', '\u036b', '\u036c', '\u036d', '\u036e', '\u036f']
ZALGO_DOWN = ['\u0316', '\u0317', '\u0318', '\u0319', '\u031a', '\u031b', '\u031c', '\u031d', '\u031e', '\u031f', '\u0320', '\u0321', '\u0322', '\u0323', '\u0324', '\u0325', '\u0326', '\u0327', '\u0328', '\u0329', '\u032a', '\u032b', '\u032c', '\u032d', '\u032e', '\u032f', '\u0330', '\u0331', '\u0332', '\u0333', '\u0334', '\u0335', '\u0336', '\u0337', '\u0338', '\u0339', '\u033a', '\u033b', '\u033c', '\u033d', '\u033e', '\u033f', '\u0340', '\u0341', '\u0342', '\u0343', '\u0344', '\u0345', '\u0346', '\u0347', '\u0348', '\u0349', '\u034a', '\u034b', '\u034c', '\u034d', '\u034e', '\u034f', '\u0350', '\u0351', '\u0352', '\u0353', '\u0354', '\u0355', '\u0356', '\u0357', '\u0358', '\u0359', '\u035a', '\u035b', '\u035c', '\u035d', '\u035e', '\u035f', '\u0360', '\u0361', '\u0362', '\u0363', '\u0364', '\u0365', '\u0366', '\u0367', '\u0368', '\u0369', '\u036a', '\u036b', '\u036c', '\u036d', '\u036e', '\u036f']
ZALGO_MID = ['\u035c', '\u035d', '\u035e', '\u035f', '\u0360', '\u0361', '\u0362']

SMALL_CAPS_MAP = str.maketrans({
    'a': '\u1d00', 'b': '\u1d01', 'c': '\u1d02', 'd': '\u1d03', 'e': '\u1d04', 'f': '\u1d05',
    'g': '\u1d06', 'h': '\u1d07', 'i': '\u1d08', 'j': '\u1d09', 'k': '\u1d0a', 'l': '\u1d0b',
    'm': '\u1d0c', 'n': '\u1d0d', 'o': '\u1d0e', 'p': '\u1d0f', 'q': '\u1d10', 'r': '\u1d11',
    's': '\u1d12', 't': '\u1d13', 'u': '\u1d14', 'v': '\u1d15', 'w': '\u1d16', 'x': '\u1d17',
    'y': '\u1d18', 'z': '\u1d19', 'A': '\u1d00', 'B': '\u1d01', 'C': '\u1d02', 'D': '\u1d03',
    'E': '\u1d04', 'F': '\u1d05', 'G': '\u1d06', 'H': '\u1d07', 'I': '\u1d08', 'J': '\u1d09',
    'K': '\u1d0a', 'L': '\u1d0b', 'M': '\u1d0c', 'N': '\u1d0d', 'O': '\u1d0e', 'P': '\u1d0f',
    'Q': '\u1d10', 'R': '\u1d11', 'S': '\u1d12', 'T': '\u1d13', 'U': '\u1d14', 'V': '\u1d15',
    'W': '\u1d16', 'X': '\u1d17', 'Y': '\u1d18', 'Z': '\u1d19', '0': '\u2070', '1': '\u00b9',
    '2': '\u2074', '3': '\u2075', '4': '\u2076', '5': '\u2077', '6': '\u2078', '7': '\u2079',
    '8': '\u207a', '9': '\u207b'
})

BUBBLE_MAP = str.maketrans({
    'a': '\u24d0', 'b': '\u24d1', 'c': '\u24d2', 'd': '\u24d3', 'e': '\u24d4', 'f': '\u24d5',
    'g': '\u24d6', 'h': '\u24d7', 'i': '\u24d8', 'j': '\u24d9', 'k': '\u24da', 'l': '\u24db',
    'm': '\u24dc', 'n': '\u24dd', 'o': '\u24de', 'p': '\u24df', 'q': '\u24e0', 'r': '\u24e1',
    's': '\u24e2', 't': '\u24e3', 'u': '\u24e4', 'v': '\u24e5', 'w': '\u24e6', 'x': '\u24e7',
    'y': '\u24e8', 'z': '\u24e9', 'A': '\u24b6', 'B': '\u24b7', 'C': '\u24b8', 'D': '\u24b9',
    'E': '\u24ba', 'F': '\u24bb', 'G': '\u24bc', 'H': '\u24bd', 'I': '\u24be', 'J': '\u24bf',
    'K': '\u24c0', 'L': '\u24c1', 'M': '\u24c2', 'N': '\u24c3', 'O': '\u24c4', 'P': '\u24c5',
    'Q': '\u24c6', 'R': '\u24c7', 'S': '\u24c8', 'T': '\u24c9', 'U': '\u24ca', 'V': '\u24cb',
    'W': '\u24cc', 'X': '\u24cd', 'Y': '\u24ce', 'Z': '\u24cf', '0': '\u24ea', '1': '\u2460',
    '2': '\u2461', '3': '\u2462', '4': '\u2463', '5': '\u2464', '6': '\u2465', '7': '\u2466',
    '8': '\u2467', '9': '\u2468'
})

MIRROR_MAP = str.maketrans({
    'a': '\u0250', 'b': 'q', 'c': '\u0254', 'd': 'p', 'e': '\u01dd', 'f': '\u025f',
    'g': '\u0183', 'h': '\u0265', 'i': '\u0131', 'j': '\u027e', 'k': '\u029e', 'l': 'l',
    'm': '\u026f', 'n': 'u', 'o': 'o', 'p': 'd', 'q': 'b', 'r': '\u0279', 's': 's',
    't': '\u0287', 'u': 'n', 'v': '\u028c', 'w': '\u028d', 'x': 'x', 'y': '\u028e',
    'z': 'z', 'A': '\u2c6f', 'B': '\u0182', 'C': '\u2183', 'D': '\u018e', 'E': '\u018e',
    'F': '\u2132', 'G': '\u2141', 'H': 'H', 'I': 'I', 'J': '\u017f', 'K': '\u22ca',
    'L': '\u2142', 'M': 'W', 'N': 'N', 'O': 'O', 'P': '\u0500', 'Q': '\u038c',
    'R': '\u1d1a', 'S': 'S', 'T': '\u22a5', 'U': '\u2229', 'V': '\u039b',
    'W': 'M', 'X': 'X', 'Y': '\u039e', 'Z': 'Z', '0': '0', '1': '\u0190',
    '2': '\u1d10', '3': '\u2189', '4': '\u2142', '5': '\u078e', '6': '9',
    '7': '\u3125', '8': '8', '9': '6', '.': '\u02d9', ',': "'", '?': '\u00bf',
    '!': '\u00a1', '"': ',,', "'": ',', '(': ')', ')': '(', '[': ']', ']': '[',
    '{': '}', '}': '{', '<': '>', '>': '<', '&': '\u214b', '_': '\u203e'
})

CREEPER_FACES = [
    "  \u2588\u2588  \u2588\u2588  ",
    "  \u2588\u2588  \u2588\u2588  ",
    "  \u2588\u2588  \u2588\u2588  ",
    "  \u2588\u2588\u2588\u2588\u2588\u2588  ",
    "  \u2588\u2588\u2588\u2588\u2588\u2588  ",
    "  \u2588\u2588\u2588\u2588\u2588\u2588  ",
    "    \u2588\u2588    ",
    "    \u2588\u2588    ",
    "  \u2588\u2588\u2588\u2588\u2588\u2588  ",
]

def zalgo(kevbin):
    kevbin.box.title("Zalgo Text Generator")
    text = kevbin.box.input("Enter text: ")
    if not text:
        return
    intensity = kevbin.box.input("Intensity 1-10 (default 5): ", default="5")
    try:
        intensity = max(1, min(10, int(intensity)))
    except:
        intensity = 5
    result = ""
    for char in text:
        result += char
        if char != ' ':
            for _ in range(intensity):
                result += random.choice(ZALGO_UP)
                result += random.choice(ZALGO_MID)
                result += random.choice(ZALGO_DOWN)
    kevbin.box.code(result)

def creeper(kevbin):
    kevbin.box.title("Creeper Text Generator")
    text = kevbin.box.input("Enter text: ")
    if not text:
        return
    lines = text.split('\n')
    result = []
    for line in lines:
        for face_line in CREEPER_FACES:
            result.append(face_line + "  " + line)
    kevbin.box.code("\n".join(result))

def smallcaps(kevbin):
    kevbin.box.title("Small Caps Generator")
    text = kevbin.box.input("Enter text: ")
    if not text:
        return
    result = text.translate(SMALL_CAPS_MAP)
    kevbin.box.code(result)

def bubble(kevbin):
    kevbin.box.title("Bubble Text Generator")
    text = kevbin.box.input("Enter text: ")
    if not text:
        return
    result = text.translate(BUBBLE_MAP)
    kevbin.box.code(result)

def mirror(kevbin):
    kevbin.box.title("Mirror/Flip Text Generator")
    text = kevbin.box.input("Enter text: ")
    if not text:
        return
    result = text.translate(MIRROR_MAP)[::-1]
    kevbin.box.code(result)
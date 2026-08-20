import re
import html
import urllib.parse
from collections import Counter

def _menu(kevbin, options, title):
    kevbin.clear()
    kevbin.section_header("🔤", title)
    for i, (key, desc) in enumerate(options.items(), 1):
        kevbin.cprint(kevbin.t.primary, f"  {i}. {key}")
        kevbin.cprint(kevbin.t.dim, f"     {desc}")
    kevbin.line()
    choice = kevbin.input_choice("Select option (number or name)")
    return choice

def transform(kevbin):
    options = {
        "upper": "Convert to UPPERCASE",
        "lower": "Convert to lowercase",
        "title": "Convert to Title Case",
        "swap": "Swap Case",
        "reverse": "Reverse String",
        "repeat": "Repeat String N times",
    }
    choice = _menu(kevbin, options, "Text Transform")
    
    kevbin.clear()
    kevbin.section_header("🔤", "Text Transform")
    text = kevbin.input_choice("Enter text to transform")
    if not text:
        return
    
    result = ""
    if choice in ("1", "upper"):
        result = text.upper()
    elif choice in ("2", "lower"):
        result = text.lower()
    elif choice in ("3", "title"):
        result = text.title()
    elif choice in ("4", "swap"):
        result = text.swapcase()
    elif choice in ("5", "reverse"):
        result = text[::-1]
    elif choice in ("6", "repeat"):
        n = kevbin.input_choice("Repeat count")
        try:
            result = text * int(n)
        except ValueError:
            result = "Invalid count"
    
    kevbin.box_top()
    kevbin.box_row("Result", result[:80] + ("..." if len(result) > 80 else ""))
    kevbin.box_bottom()
    kevbin.pause()

def slugify(kevbin):
    kevbin.clear()
    kevbin.section_header("🔗", "URL Slug Generator")
    text = kevbin.input_choice("Enter text to slugify")
    if not text:
        return
    
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    
    kevbin.box_top()
    kevbin.box_row("Original", text[:75])
    kevbin.box_row("Slug", slug[:75])
    kevbin.box_bottom()
    kevbin.pause()

def sort(kevbin):
    options = {
        "alpha": "Alphabetical (A-Z)",
        "alpha_desc": "Alphabetical (Z-A)",
        "numeric": "Numeric (0-9)",
        "numeric_desc": "Numeric (9-0)",
        "length": "By Length (short-first)",
        "length_desc": "By Length (long-first)",
    }
    choice = _menu(kevbin, options, "Sort Lines")
    
    kevbin.clear()
    kevbin.section_header("📋", "Sort Lines")
    kevbin.cprint(kevbin.t.dim, "Enter lines (empty line to finish):")
    lines = []
    while True:
        line = kevbin.input_choice("> ")
        if line == "":
            break
        lines.append(line)
    
    if not lines:
        return
    
    reverse = choice.endswith("_desc")
    key = None
    if choice.startswith("numeric"):
        key = lambda x: float(x) if x.replace('.','',1).lstrip('-').isdigit() else float('inf')
    elif choice.startswith("length"):
        key = len
    
    lines.sort(key=key, reverse=reverse)
    
    kevbin.box_top()
    for i, line in enumerate(lines[:20], 1):
        kevbin.box_row(f"{i:2}", line[:70])
    if len(lines) > 20:
        kevbin.box_row("...", f"({len(lines)} total lines)")
    kevbin.box_bottom()
    kevbin.pause()

def wordcount(kevbin):
    kevbin.clear()
    kevbin.section_header("📊", "Word Count")
    kevbin.cprint(kevbin.t.dim, "Enter text (empty line to finish):")
    lines = []
    while True:
        line = kevbin.input_choice("> ")
        if line == "":
            break
        lines.append(line)
    
    if not lines:
        return
    
    text = "\n".join(lines)
    words = text.split()
    chars = len(text)
    chars_no_space = len(text.replace(" ", "").replace("\n", ""))
    lines_count = len(lines)
    paragraphs = len([p for p in text.split("\n\n") if p.strip()])
    
    kevbin.box_top()
    kevbin.box_row("Characters", str(chars))
    kevbin.box_row("Chars (no space)", str(chars_no_space))
    kevbin.box_row("Words", str(len(words)))
    kevbin.box_row("Lines", str(lines_count))
    kevbin.box_row("Paragraphs", str(paragraphs))
    if words:
        kevbin.box_row("Avg word length", f"{sum(len(w) for w in words)/len(words):.1f}")
    kevbin.box_bottom()
    kevbin.pause()

def slugify2(kevbin):
    kevbin.clear()
    kevbin.section_header("🔗", "Advanced Slugify")
    text = kevbin.input_choice("Enter text")
    if not text:
        return
    
    separator = kevbin.input_choice("Separator [-]", default="-") or "-"
    max_len = kevbin.input_choice("Max length [0=unlimited]", default="0")
    try:
        max_len = int(max_len)
    except ValueError:
        max_len = 0
    
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', separator, slug)
    slug = slug.strip(separator)
    if max_len > 0:
        slug = slug[:max_len].rstrip(separator)
    
    kevbin.box_top()
    kevbin.box_row("Original", text[:75])
    kevbin.box_row("Slug", slug[:75])
    kevbin.box_bottom()
    kevbin.pause()

def html_entity(kevbin):
    options = {
        "encode": "Encode special chars to HTML entities",
        "decode": "Decode HTML entities to text",
    }
    choice = _menu(kevbin, options, "HTML Entities")
    
    kevbin.clear()
    kevbin.section_header("🔧", "HTML Entities")
    text = kevbin.input_choice("Enter text")
    if not text:
        return
    
    if choice in ("1", "encode"):
        result = html.escape(text)
        label = "Encoded"
    else:
        result = html.unescape(text)
        label = "Decoded"
    
    kevbin.box_top()
    kevbin.box_row("Original", text[:75])
    kevbin.box_row(label, result[:75])
    kevbin.box_bottom()
    kevbin.pause()

def url_encode(kevbin):
    options = {
        "encode": "URL encode",
        "decode": "URL decode",
    }
    choice = _menu(kevbin, options, "URL Encode/Decode")
    
    kevbin.clear()
    kevbin.section_header("🔗", "URL Encode/Decode")
    text = kevbin.input_choice("Enter text")
    if not text:
        return
    
    if choice in ("1", "encode"):
        result = urllib.parse.quote(text)
        label = "Encoded"
    else:
        try:
            result = urllib.parse.unquote(text)
        except Exception:
            result = "Invalid URL encoding"
        label = "Decoded"
    
    kevbin.box_top()
    kevbin.box_row("Original", text[:75])
    kevbin.box_row(label, result[:75])
    kevbin.box_bottom()
    kevbin.pause()

def stats(kevbin):
    kevbin.clear()
    kevbin.section_header("📈", "Readability Statistics")
    kevbin.cprint(kevbin.t.dim, "Enter text (empty line to finish):")
    lines = []
    while True:
        line = kevbin.input_choice("> ")
        if line == "":
            break
        lines.append(line)
    
    if not lines:
        return
    
    text = " ".join(lines)
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if s.strip()]
    syllables = sum(_count_syllables(w) for w in words)
    
    word_count = len(words)
    sentence_count = len(sentences) or 1
    syllable_count = syllables or 1
    
    flesch = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
    flesch = max(0, min(100, flesch))
    
    grade = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59
    grade = max(0, grade)
    
    kevbin.box_top()
    kevbin.box_row("Words", str(word_count))
    kevbin.box_row("Sentences", str(sentence_count))
    kevbin.box_row("Syllables (est.)", str(syllable_count))
    kevbin.box_row("Flesch Reading Ease", f"{flesch:.1f}/100")
    kevbin.box_row("Flesch-Kincaid Grade", f"{grade:.1f}")
    if flesch >= 90:
        level = "Very Easy (5th grade)"
    elif flesch >= 80:
        level = "Easy (6th grade)"
    elif flesch >= 70:
        level = "Fairly Easy (7th grade)"
    elif flesch >= 60:
        level = "Standard (8-9th grade)"
    elif flesch >= 50:
        level = "Fairly Difficult (10-12th grade)"
    elif flesch >= 30:
        level = "Difficult (College)"
    else:
        level = "Very Difficult (Graduate)"
    kevbin.box_row("Reading Level", level)
    kevbin.box_bottom()
    kevbin.pause()

def _count_syllables(word):
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    if word[0] in vowels:
        count += 1
    for i in range(1, len(word)):
        if word[i] in vowels and word[i-1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
        count += 1
    return max(1, count)

def run(kevbin):
    options = {
        "transform": "Case transforms, reverse, repeat",
        "slugify": "Basic URL-safe slug",
        "sort": "Sort lines alphabetically/numerically",
        "wordcount": "Count words, chars, lines",
        "slugify2": "Advanced slug with options",
        "html_entity": "Encode/decode HTML entities",
        "url_encode": "URL encode/decode",
        "stats": "Readability analysis",
    }
    while True:
        kevbin.clear()
        kevbin.section_header("🔤", "Text Tools")
        for i, (key, desc) in enumerate(options.items(), 1):
            kevbin.cprint(kevbin.t.primary, f"  {i}. {key}")
            kevbin.cprint(kevbin.t.dim, f"     {desc}")
        kevbin.cprint(kevbin.t.dim, "  0. Back")
        kevbin.line()
        choice = kevbin.input_choice("Select tool")
        if choice in ("0", "back", ""):
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                choice = list(options.keys())[idx]
        except ValueError:
            pass
        if choice in globals():
            globals()[choice](kevbin)
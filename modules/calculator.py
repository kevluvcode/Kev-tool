"""Calculator — Scientific calculator with history."""

import math
import random
import time
import datetime
import re


HISTORY = []
BUILTIN_FUNCS = {
    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
    'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
    'sqrt': math.sqrt, 'cbrt': lambda x: x ** (1 / 3),
    'log': math.log, 'log2': math.log2, 'log10': math.log10,
    'exp': math.exp, 'abs': abs, 'round': round,
    'ceil': math.ceil, 'floor': math.floor,
    'factorial': math.factorial, 'gamma': math.gamma,
    'radians': math.radians, 'degrees': math.degrees,
    'pow': pow,
}
BUILTIN_VARS = {
    'pi': math.pi, 'e': math.e, 'tau': math.tau,
    'phi': (1 + math.sqrt(5)) / 2,
    'inf': math.inf, 'nan': math.nan,
}


def _safe_eval(expr):
    expr = expr.replace('^', '**')
    expr = expr.replace('√', 'sqrt')
    expr = expr.replace('π', 'pi')
    expr = expr.replace('×', '*')
    expr = expr.replace('÷', '/')
    expr = expr.replace('−', '-')

    expr = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expr)

    namespace = {**BUILTIN_FUNCS, **BUILTIN_VARS, '__builtins__': {}}
    try:
        result = eval(expr, namespace)
        return result
    except Exception as e:
        return f"Error: {e}"


def _format_result(val):
    if isinstance(val, str):
        return val
    if isinstance(val, float):
        if val == int(val) and abs(val) < 1e15:
            return str(int(val))
        if abs(val) < 0.0001 or abs(val) > 1e12:
            return f"{val:.6e}"
        return f"{val:.10g}"
    return str(val)


def _history_add(expr, result):
    HISTORY.append((expr, _format_result(result)))
    if len(HISTORY) > 50:
        HISTORY.pop(0)


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🧮', 'SCIENTIFIC CALCULATOR')
        kevbin.cprint(kevbin.t.secondary, "  [1]  Calculator")
        kevbin.cprint(kevbin.t.secondary, "  [2]  Base converter")
        kevbin.cprint(kevbin.t.secondary, "  [3]  Random number generator")
        kevbin.cprint(kevbin.t.secondary, "  [4]  Date/time calculator")
        kevbin.cprint(kevbin.t.secondary, "  [5]  History")
        kevbin.cprint(kevbin.t.secondary, "  [6]  Constants reference")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()

        choice = kevbin.input_choice()
        if choice == '0':
            return

        if choice == '1':
            kevbin.cprint(kevbin.t.dim, "  Enter expressions (q=back, h=history)")
            kevbin.cprint(kevbin.t.dim, "  Functions: sin cos tan sqrt log log2 log10 exp abs factorial")
            kevbin.cprint(kevbin.t.dim, "  Constants: pi e tau phi\n")
            while True:
                expr = kevbin.input_choice("  = ").strip()
                if expr.lower() in ('q', 'quit', 'exit', 'back', ''):
                    break
                if expr.lower() == 'h':
                    if HISTORY:
                        for e, r in HISTORY[-10:]:
                            kevbin.cprint(kevbin.t.txt, f"    {e} = {r}")
                    else:
                        kevbin.cprint(kevbin.t.dim, "    (empty)")
                    continue
                result = _safe_eval(expr)
                formatted = _format_result(result)
                _history_add(expr, result)
                kevbin.cprint(kevbin.t.accent, f"  {formatted}")

        elif choice == '2':
            raw = kevbin.input_choice("  Number: ").strip()
            if not raw:
                continue
            try:
                if raw.startswith('0x'):
                    num = int(raw, 16)
                elif raw.startswith('0b'):
                    num = int(raw, 2)
                elif raw.startswith('0o'):
                    num = int(raw, 8)
                else:
                    num = int(raw)
            except ValueError:
                kevbin.cprint(kevbin.t.error, "  [X] Invalid number.")
                kevbin.pause()
                continue
            rows = [
                ("Decimal", str(num)),
                ("Binary", bin(num)[2:]),
                ("Octal", oct(num)[2:]),
                ("Hex", hex(num)[2:].upper()),
                ("Base36", _to_base(num, 36)),
                ("Base62", _to_base(num, 62)),
                ("Roman", _to_roman(num)),
                ("Words", _num_to_words(num)),
            ]
            kevbin.box_table(rows, title=f"Conversions for {num}")

        elif choice == '3':
            low = kevbin.input_choice("  Min [0]: ").strip() or '0'
            high = kevbin.input_choice("  Max [100]: ").strip() or '100'
            count = kevbin.input_choice("  Count [10]: ").strip() or '10'
            try:
                lo, hi, n = int(low), int(high), int(count)
                results = [random.randint(lo, hi) for _ in range(min(100, n))]
                kevbin.cprint(kevbin.t.accent, "\n  Results:")
                for i in range(0, len(results), 10):
                    chunk = results[i:i + 10]
                    kevbin.cprint(kevbin.t.txt, "    " + "  ".join(str(x) for x in chunk))
                if n > 1:
                    kevbin.cprint(kevbin.t.dim, f"\n  Sum: {sum(results)}  Avg: {sum(results)/len(results):.2f}")
            except ValueError:
                kevbin.cprint(kevbin.t.error, "  [X] Invalid numbers.")

        elif choice == '4':
            kevbin.cprint(kevbin.t.dim, "  Days between two dates")
            try:
                d1 = datetime.date.fromisoformat(kevbin.input_choice("  Start (YYYY-MM-DD): ").strip())
                d2 = datetime.date.fromisoformat(kevbin.input_choice("  End (YYYY-MM-DD): ").strip())
                delta = abs((d2 - d1).days)
                rows = [
                    ("Days", f"{delta:,}"),
                    ("Weeks", f"{delta / 7:.1f}"),
                    ("Months (est.)", f"{delta / 30.44:.1f}"),
                    ("Hours", f"{delta * 24:,}"),
                    ("Minutes", f"{delta * 1440:,}"),
                    ("Seconds", f"{delta * 86400:,}"),
                ]
                kevbin.box_table(rows, title="Duration")
            except ValueError:
                kevbin.cprint(kevbin.t.error, "  [X] Use YYYY-MM-DD format.")

        elif choice == '5':
            if HISTORY:
                kevbin.cprint(kevbin.t.accent, f"\n  History ({len(HISTORY)} entries):\n")
                for e, r in HISTORY[-20:]:
                    kevbin.cprint(kevbin.t.txt, f"    {e} = {r}")
            else:
                kevbin.cprint(kevbin.t.warning, "  [!] No history yet.")

        elif choice == '6':
            rows = [
                ("pi", f"{math.pi}"),
                ("e", f"{math.e}"),
                ("tau (2pi)", f"{math.tau}"),
                ("phi (golden)", f"{(1 + math.sqrt(5)) / 2}"),
                ("sqrt(2)", f"{math.sqrt(2)}"),
                ("sqrt(3)", f"{math.sqrt(3)}"),
                ("ln(2)", f"{math.log(2)}"),
                ("ln(10)", f"{math.log(10)}"),
                ("speed of light (m/s)", "299792458"),
                ("planck (J*s)", "6.626e-34"),
                ("avogadro", "6.022e23"),
            ]
            kevbin.box_table(rows, title="Math Constants")

        kevbin.pause()


def _to_base(num, base, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'):
    if num == 0:
        return '0'
    chars = []
    while num:
        chars.append(alphabet[num % base])
        num //= base
    return ''.join(reversed(chars))


def _to_roman(num):
    if num <= 0 or num > 3999:
        return '(out of range)'
    vals = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
            (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
            (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
    result = ''
    for v, s in vals:
        while num >= v:
            result += s
            num -= v
    return result


def _num_to_words(num):
    if num == 0:
        return 'zero'
    if num < 0:
        return 'negative ' + _num_to_words(-num)

    ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
            'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
            'seventeen', 'eighteen', 'nineteen']
    tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']

    if num < 20:
        return ones[num]
    if num < 100:
        return tens[num // 10] + ('' if num % 10 == 0 else '-' + ones[num % 10])
    if num < 1000:
        return ones[num // 100] + ' hundred' + ('' if num % 100 == 0 else ' and ' + _num_to_words(num % 100))

    for suffix, div in [('billion', 10**9), ('million', 10**6), ('thousand', 1000)]:
        if num >= div:
            return _num_to_words(num // div) + ' ' + suffix + ('' if num % div == 0 else ' ' + _num_to_words(num % div))

    return str(num)

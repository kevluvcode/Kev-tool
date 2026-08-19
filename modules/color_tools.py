import re
import colorsys
import math
from typing import List, Tuple, Optional

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360, s * 100, l * 100)


def _hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
    return (int(r * 255), int(g * 255), int(b * 255))


def _luminance(r: int, g: int, b: int) -> float:
    def channel(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _contrast_ratio(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    l1 = _luminance(*rgb1) + 0.05
    l2 = _luminance(*rgb2) + 0.05
    return max(l1, l2) / min(l1, l2)


def _wcag_rating(ratio: float) -> str:
    if ratio >= 7:
        return "AAA (Large & Normal)"
    elif ratio >= 4.5:
        return "AA (Normal) / AAA (Large)"
    elif ratio >= 3:
        return "AA (Large)"
    return "Fail"


def _get_color_input(kevbin, prompt: str, default: str = "") -> str:
    kevbin.box_print(f"[cyan]{prompt}[/cyan]")
    if default:
        kevbin.box_print(f"[dim]Default: {default}[/dim]")
    return kevbin.box_input("Enter color (HEX, RGB, or HSL): ").strip()


def _parse_color(color_str: str) -> Optional[Tuple[int, int, int]]:
    color_str = color_str.strip()
    
    hex_match = re.match(r'^#?([0-9a-fA-F]{3,8})$', color_str)
    if hex_match:
        hex_val = hex_match.group(1)
        if len(hex_val) in (3, 4):
            hex_val = ''.join(c * 2 for c in hex_val)
        if len(hex_val) == 6:
            return _hex_to_rgb(hex_val)
        elif len(hex_val) == 8:
            return _hex_to_rgb(hex_val[:6])
    
    rgb_match = re.match(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str, re.I)
    if rgb_match:
        return tuple(int(x) for x in rgb_match.groups())
    
    hsl_match = re.match(r'hsl\s*\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)', color_str, re.I)
    if hsl_match:
        h, s, l = map(int, hsl_match.groups())
        return _hsl_to_rgb(h, s, l)
    
    return None


def converter(kevbin):
    kevbin.box_title("Color Converter")
    kevbin.box_print("Convert between HEX, RGB, and HSL formats")
    
    while True:
        color_input = _get_color_input(kevbin, "Enter a color to convert (or 'q' to quit)")
        if color_input.lower() in ('q', 'quit', 'exit'):
            break
        
        rgb = _parse_color(color_input)
        if not rgb:
            kevbin.box_print("[red]Invalid color format. Use HEX (#ff0000), RGB (255,0,0), or HSL (0,100%,50%)[/red]")
            continue
        
        r, g, b = rgb
        h, s, l = _rgb_to_hsl(r, g, b)
        hex_color = _rgb_to_hex(r, g, b)
        
        rows = [
            ["Format", "Value"],
            ["HEX", hex_color.upper()],
            ["RGB", f"rgb({r}, {g}, {b})"],
            ["HSL", f"hsl({h:.0f}, {s:.0f}%, {l:.0f}%)"],
            ["Preview", f"[on {hex_color}]        [/on {hex_color}] {hex_color}"]
        ]
        kevbin.box_table(rows, title="Color Conversion")
        kevbin.box_print("")


def gradient(kevbin):
    kevbin.box_title("CSS Gradient Generator")
    kevbin.box_print("Generate linear/radial gradient CSS code")
    
    direction = kevbin.box_input("Direction (to right, to bottom, 45deg, etc.) [to right]: ").strip() or "to right"
    gradient_type = kevbin.box_input("Type (linear/radial) [linear]: ").strip().lower() or "linear"
    
    stops = []
    while True:
        color = kevbin.box_input(f"Color stop {len(stops)+1} (HEX/RGB/HSL) or empty to finish: ").strip()
        if not color:
            break
        rgb = _parse_color(color)
        if not rgb:
            kevbin.box_print("[red]Invalid color[/red]")
            continue
        position = kevbin.box_input(f"  Position % (0-100) [auto]: ").strip()
        stop_str = _rgb_to_hex(*rgb).upper()
        if position:
            stop_str += f" {position}%"
        stops.append(stop_str)
    
    if len(stops) < 2:
        kevbin.box_print("[yellow]Need at least 2 color stops[/yellow]")
        return
    
    if gradient_type == "radial":
        css = f"background: radial-gradient(circle, {', '.join(stops)});"
    else:
        css = f"background: linear-gradient({direction}, {', '.join(stops)});"
    
    kevbin.box_print("")
    kevbin.box_code(css, language="css")
    kevbin.box_print("")
    kevbin.box_print("[green]Copied to clipboard![/green]")


def contrast(kevbin):
    kevbin.box_title("WCAG Contrast Ratio Calculator")
    kevbin.box_print("Calculate contrast ratio between two colors")
    
    color1 = _get_color_input(kevbin, "Foreground color")
    rgb1 = _parse_color(color1)
    if not rgb1:
        kevbin.box_print("[red]Invalid foreground color[/red]")
        return
    
    color2 = _get_color_input(kevbin, "Background color")
    rgb2 = _parse_color(color2)
    if not rgb2:
        kevbin.box_print("[red]Invalid background color[/red]")
        return
    
    ratio = _contrast_ratio(rgb1, rgb2)
    rating = _wcag_rating(ratio)
    
    fg_hex = _rgb_to_hex(*rgb1)
    bg_hex = _rgb_to_hex(*rgb2)
    
    rows = [
        ["Property", "Value"],
        ["Foreground", f"[on {fg_hex}]  [/on {fg_hex}] {fg_hex.upper()}"],
        ["Background", f"[on {bg_hex}]  [/on {bg_hex}] {bg_hex.upper()}"],
        ["Contrast Ratio", f"{ratio:.2f}:1"],
        ["WCAG Rating", rating],
        ["", ""],
        ["AA Normal Text", "✓" if ratio >= 4.5 else "✗"],
        ["AA Large Text", "✓" if ratio >= 3 else "✗"],
        ["AAA Normal Text", "✓" if ratio >= 7 else "✗"],
        ["AAA Large Text", "✓" if ratio >= 4.5 else "✗"],
    ]
    kevbin.box_table(rows, title="Contrast Analysis")


def palette(kevbin):
    kevbin.box_title("Color Palette Generator")
    kevbin.box_print("Generate harmonious color palettes from a base color")
    
    base_input = _get_color_input(kevbin, "Enter base color")
    base_rgb = _parse_color(base_input)
    if not base_rgb:
        kevbin.box_print("[red]Invalid base color[/red]")
        return
    
    r, g, b = base_rgb
    h, s, l = _rgb_to_hsl(r, g, b)
    
    palette_types = {
        "1": ("Monochromatic", [(h, s, l + i * 15) for i in range(-2, 3)]),
        "2": ("Analogous", [(h + i * 30, s, l) for i in range(-2, 3)]),
        "3": ("Complementary", [(h, s, l), ((h + 180) % 360, s, l)]),
        "4": ("Triadic", [(h, s, l), ((h + 120) % 360, s, l), ((h + 240) % 360, s, l)]),
        "5": ("Tetradic", [(h, s, l), ((h + 90) % 360, s, l), ((h + 180) % 360, s, l), ((h + 270) % 360, s, l)]),
        "6": ("Split Complementary", [(h, s, l), ((h + 150) % 360, s, l), ((h + 210) % 360, s, l)]),
    }
    
    kevbin.box_print("\nPalette types:")
    for k, (name, _) in palette_types.items():
        kevbin.box_print(f"  {k}. {name}")
    
    choice = kevbin.box_input("Select palette type [1]: ").strip() or "1"
    name, colors_hsl = palette_types.get(choice, palette_types["1"])
    
    rows = [["#", "HEX", "RGB", "HSL", "Preview"]]
    for i, (ph, ps, pl) in enumerate(colors_hsl, 1):
        pr, pg, pb = _hsl_to_rgb(ph % 360, max(0, min(100, ps)), max(0, min(100, pl)))
        phex = _rgb_to_hex(pr, pg, pb)
        rows.append([str(i), phex.upper(), f"rgb({pr},{pg},{pb})", f"hsl({ph:.0f},{ps:.0f}%,{pl:.0f}%)", f"[on {phex}]    [/on {phex}]"])
    
    kevbin.box_table(rows, title=f"{name} Palette")


def image_colors(kevbin):
    kevbin.box_title("Image Color Extractor")
    
    if not HAS_PILLOW:
        kevbin.box_print("[red]Pillow not installed. Run: pip install pillow[/red]")
        return
    
    path = kevbin.box_input("Image file path: ").strip().strip('"')
    if not path:
        return
    
    try:
        img = Image.open(path)
        img = img.convert('RGB')
        
        kevbin.box_print(f"Image: {img.size[0]}x{img.size[1]}, Mode: {img.mode}")
        
        num_colors = int(kevbin.box_input("Number of dominant colors [5]: ").strip() or "5")
        
        small = img.resize((150, 150))
        colors = small.getcolors(150 * 150)
        
        if not colors:
            kevbin.box_print("[yellow]Could not extract colors[/yellow]")
            return
        
        colors.sort(key=lambda x: x[0], reverse=True)
        dominant = colors[:num_colors]
        
        total = sum(c[0] for c in dominant)
        
        rows = [["#", "HEX", "RGB", "Percentage", "Preview"]]
        for i, (count, (r, g, b)) in enumerate(dominant, 1):
            hex_color = _rgb_to_hex(r, g, b)
            pct = (count / total) * 100
            rows.append([str(i), hex_color.upper(), f"rgb({r},{g},{b})", f"{pct:.1f}%", f"[on {hex_color}]    [/on {hex_color}]"])
        
        kevbin.box_table(rows, title="Dominant Colors")
        
        palette_hex = [_rgb_to_hex(*c[1]).upper() for c in dominant]
        kevbin.box_print(f"\nPalette: {', '.join(palette_hex)}")
        
    except FileNotFoundError:
        kevbin.box_print("[red]File not found[/red]")
    except Exception as e:
        kevbin.box_print(f"[red]Error: {e}[/red]")


def run(kevbin):
    kevbin.box_title("Color Tools")
    kevbin.box_print("Select a tool:")
    kevbin.box_print("  1. Color Converter (HEX/RGB/HSL)")
    kevbin.box_print("  2. CSS Gradient Generator")
    kevbin.box_print("  3. WCAG Contrast Calculator")
    kevbin.box_print("  4. Color Palette Generator")
    kevbin.box_print("  5. Image Color Extractor")
    
    choice = kevbin.box_input("Choice [1]: ").strip() or "1"
    
    tools = {
        "1": converter,
        "2": gradient,
        "3": contrast,
        "4": palette,
        "5": image_colors,
    }
    
    tool = tools.get(choice)
    if tool:
        tool(kevbin)
    else:
        kevbin.box_print("[red]Invalid choice[/red]")
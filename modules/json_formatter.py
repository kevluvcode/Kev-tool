import json
import xml.etree.ElementTree as ET

def run(kevbin):
    kevbin.clear()
    kevbin.section_header("📋", "JSON Formatter")
    kevbin.cprint(kevbin.t.dim, "Enter JSON (empty line to finish):")
    
    lines = []
    while True:
        line = kevbin.input_choice("> ")
        if line == "":
            break
        lines.append(line)
    
    if not lines:
        return
    
    text = "\n".join(lines)
    
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        kevbin.cprint(kevbin.t.error, f"Invalid JSON: {e}")
        kevbin.pause()
        return
    
    pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
    
    kevbin.box_top()
    kevbin.box_row("Status", "Valid JSON ✓")
    kevbin.box_mid()
    for line in pretty.split('\n'):
        kevbin.box_row("", line[:78])
    kevbin.box_bottom()
    kevbin.pause()

def xml(kevbin):
    kevbin.clear()
    kevbin.section_header("🔄", "JSON to XML")
    kevbin.cprint(kevbin.t.dim, "Enter JSON (empty line to finish):")
    
    lines = []
    while True:
        line = kevbin.input_choice("> ")
        if line == "":
            break
        lines.append(line)
    
    if not lines:
        return
    
    text = "\n".join(lines)
    
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        kevbin.cprint(kevbin.t.error, f"Invalid JSON: {e}")
        kevbin.pause()
        return
    
    root = ET.Element("root")
    _json_to_xml(parsed, root)
    
    xml_str = ET.tostring(root, encoding='unicode', method='xml')
    xml_str = _pretty_xml(xml_str)
    
    kevbin.box_top()
    kevbin.box_row("Status", "Converted to XML ✓")
    kevbin.box_mid()
    for line in xml_str.split('\n'):
        kevbin.box_row("", line[:78])
    kevbin.box_bottom()
    kevbin.pause()

def _json_to_xml(obj, parent):
    if isinstance(obj, dict):
        for key, value in obj.items():
            key = _sanitize_key(key)
            child = ET.SubElement(parent, key)
            _json_to_xml(value, child)
    elif isinstance(obj, list):
        for item in obj:
            child = ET.SubElement(parent, "item")
            _json_to_xml(item, child)
    else:
        parent.text = str(obj)

def _sanitize_key(key):
    key = str(key)
    key = key.replace(' ', '_').replace('-', '_')
    key = ''.join(c for c in key if c.isalnum() or c == '_')
    if key and key[0].isdigit():
        key = '_' + key
    return key or 'item'

def _pretty_xml(xml_str):
    import re
    lines = []
    indent = 0
    for line in xml_str.split('><'):
        line = line.strip()
        if line.startswith('</'):
            indent -= 1
        lines.append('  ' * indent + line)
        if not line.startswith('</') and not line.endswith('/>'):
            indent += 1
    return '\n'.join(lines).replace('><', '>\n<')
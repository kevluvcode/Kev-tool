with open(r'C:\Users\Kids\Documents\Default Project\Kev-tool\modules\markdown_tools.py', 'r', encoding='utf-8') as f:
    c = f.read()

old = """def _escape_html(text):
    return (text
        .replace('&', '&')
        .replace('<', '<')
        .replace('>', '>')
        .replace('"', '"')
        .replace("'", "'''"))"""

new = """def _escape_html(text):
    return (text
        .replace("&", "&")
        .replace("<", "<")
        .replace(">", ">")
        .replace('"', '"')
        .replace("'", "&apos;"))"""

c = c.replace(old, new)

with open(r'C:\Users\Kids\Documents\Default Project\Kev-tool\modules\markdown_tools.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('done')
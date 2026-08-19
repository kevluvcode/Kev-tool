import re

def run(kevbin):
    kevbin.clear()
    kevbin.section_header("📝", "Markdown to HTML")
    kevbin.cprint(kevbin.t.dim, "Enter Markdown (empty line to finish):")
    
    lines = []
    while True:
        line = kevbin.input_choice("> ")
        if line == "":
            break
        lines.append(line)
    
    if not lines:
        return
    
    md = "\n".join(lines)
    html = _markdown_to_html(md)
    
    kevbin.box_top()
    kevbin.box_row("HTML Output", html[:80])
    kevbin.box_mid()
    for hline in html.split('\n'):
        kevbin.box_row("", hline[:78])
    kevbin.box_bottom()
    kevbin.pause()

def _markdown_to_html(md):
    lines = md.split('\n')
    html_lines = []
    in_code = False
    in_ul = False
    in_ol = False
    code_buffer = []
    
    for line in lines:
        stripped = line.rstrip()
        
        if stripped.startswith('```'):
            if not in_code:
                in_code = True
                code_buffer = []
                lang = stripped[3:].strip()
                html_lines.append(f'<pre><code class="language-{lang}">')
            else:
                in_code = False
                code_text = '\n'.join(code_buffer)
                html_lines.append(_escape_html(code_text))
                html_lines.append('</code></pre>')
            continue
        
        if in_code:
            code_buffer.append(stripped)
            continue
        
        if stripped.startswith('```'):
            in_code = not in_code
            if in_code:
                html_lines.append('<pre><code>')
            else:
                html_lines.append('</code></pre>')
            continue
        
        heading_match = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2)
            html_lines.append(f'<h{level}>{_inline(content)}</h{level}>')
            continue
        
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_ul:
                if in_ol:
                    html_lines.append('</ol>')
                    in_ol = False
                html_lines.append('<ul>')
                in_ul = True
            content = stripped[2:]
            html_lines.append(f'  <li>{_inline(content)}</li>')
            continue
        
        ol_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if ol_match:
            if not in_ol:
                if in_ul:
                    html_lines.append('</ul>')
                    in_ul = False
                html_lines.append('<ol>')
                in_ol = True
            content = ol_match.group(2)
            html_lines.append(f'  <li>{_inline(content)}</li>')
            continue
        
        if in_ul:
            html_lines.append('</ul>')
            in_ul = False
        if in_ol:
            html_lines.append('</ol>')
            in_ol = False
        
        if stripped == '---' or stripped == '***' or stripped == '___':
            html_lines.append('<hr>')
            continue
        
        if stripped.startswith('> '):
            content = stripped[2:]
            html_lines.append(f'<blockquote>{_inline(content)}</blockquote>')
            continue
        
        if stripped.strip() == '':
            html_lines.append('<br>')
            continue
        
        html_lines.append(f'<p>{_inline(stripped)}</p>')
    
    if in_ul:
        html_lines.append('</ul>')
    if in_ol:
        html_lines.append('</ol>')
    if in_code:
        code_text = '\n'.join(code_buffer)
        html_lines.append(_escape_html(code_text))
        html_lines.append('</code></pre>')
    
    return '\n'.join(html_lines)

def _inline(text):
    text = _escape_html(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
    return text

def _escape_html(text):
    t = text.replace("&", "&")
    t = t.replace("<", "<")
    t = t.replace(">", ">")
    t = t.replace('"', '"')
    t = t.replace("'", "'")
    return t
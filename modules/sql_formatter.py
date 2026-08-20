import re

KEYWORDS = {
    'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER',
    'ON', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN', 'LIKE', 'IS', 'NULL',
    'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'INTERSECT',
    'EXCEPT', 'DISTINCT', 'AS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
    'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'TABLE',
    'DROP', 'ALTER', 'ADD', 'COLUMN', 'INDEX', 'PRIMARY', 'KEY', 'FOREIGN',
    'REFERENCES', 'CONSTRAINT', 'DEFAULT', 'UNIQUE', 'CHECK', 'AUTO_INCREMENT',
    'BEGIN', 'COMMIT', 'ROLLBACK', 'TRANSACTION', 'TRUNCATE',
}

def run(kevbin):
    kevbin.clear()
    kevbin.section_header("🗄️", "SQL Formatter")
    kevbin.cprint(kevbin.t.dim, "Enter SQL (empty line to finish):")
    
    lines = []
    while True:
        line = kevbin.input_choice("> ")
        if line == "":
            break
        lines.append(line)
    
    if not lines:
        return
    
    sql = " ".join(lines)
    formatted = _format_sql(sql)
    
    kevbin.box_top()
    kevbin.box_row("Formatted SQL", "")
    kevbin.box_mid()
    for line in formatted.split('\n'):
        kevbin.box_row("", line[:78])
    kevbin.box_bottom()
    kevbin.pause()

def _format_sql(sql):
    sql = re.sub(r'\s+', ' ', sql.strip())
    
    tokens = _tokenize(sql)
    output = []
    indent = 0
    in_paren = 0
    
    for token in tokens:
        upper = token.upper()
        
        if upper in ('SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING',
                     'LIMIT', 'OFFSET', 'UNION', 'INTERSECT', 'EXCEPT'):
            if output and not output[-1].endswith('\n'):
                output.append('\n')
            output.append('  ' * indent + token)
            if upper in ('SELECT', 'FROM', 'WHERE'):
                indent += 1
        elif upper in ('INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN',
                       'LEFT OUTER JOIN', 'RIGHT OUTER JOIN', 'FULL OUTER JOIN'):
            output.append('\n' + '  ' * indent + token)
        elif upper == 'ON':
            output.append('\n' + '  ' * (indent + 1) + token)
        elif upper == 'AND' and in_paren == 0:
            output.append('\n' + '  ' * indent + token)
        elif upper == 'OR' and in_paren == 0:
            output.append('\n' + '  ' * indent + token)
        elif token == '(':
            in_paren += 1
            output.append(token)
        elif token == ')':
            in_paren = max(0, in_paren - 1)
            output.append(token)
        elif token == ',':
            output.append(token + ' ')
        else:
            if output and output[-1] not in (' ', '\n', '(', '(', '') and not output[-1].endswith('\n'):
                output.append(' ')
            output.append(token)
    
    return ''.join(output).strip()

def _tokenize(sql):
    tokens = []
    i = 0
    while i < len(sql):
        if sql[i].isspace():
            i += 1
            continue
        
        if sql[i] in '(),;':
            tokens.append(sql[i])
            i += 1
            continue
        
        if sql[i] == "'" or sql[i] == '"':
            quote = sql[i]
            j = i + 1
            while j < len(sql) and sql[j] != quote:
                if sql[j] == '\\' and j + 1 < len(sql):
                    j += 2
                else:
                    j += 1
            tokens.append(sql[i:j+1])
            i = j + 1
            continue
        
        if sql[i] == '-' and i + 1 < len(sql) and sql[i+1] == '-':
            j = i + 2
            while j < len(sql) and sql[j] != '\n':
                j += 1
            tokens.append(sql[i:j])
            i = j
            continue
        
        match = re.match(r'[A-Za-z_][A-Za-z0-9_]*', sql[i:])
        if match:
            word = match.group(0)
            j = i + len(word)
            if j < len(sql) and sql[j] == '.' and j+1 < len(sql) and sql[j+1].isalnum():
                while j < len(sql) and (sql[j].isalnum() or sql[j] in '._'):
                    j += 1
            tokens.append(sql[i:j])
            i = j
            continue
        
        match = re.match(r'\d+\.?\d*', sql[i:])
        if match:
            tokens.append(match.group(0))
            i += len(match.group(0))
            continue
        
        tokens.append(sql[i])
        i += 1
    
    return tokens
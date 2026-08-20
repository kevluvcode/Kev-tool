def run(kevbin):
    kevbin.clear()
    kevbin.section_header("🔀", "Diff Tool")
    kevbin.cprint(kevbin.t.dim, "Enter first text (empty line to finish):")
    
    text1_lines = []
    while True:
        line = kevbin.input_choice("A> ")
        if line == "":
            break
        text1_lines.append(line)
    
    if not text1_lines:
        return
    
    kevbin.cprint(kevbin.t.dim, "Enter second text (empty line to finish):")
    text2_lines = []
    while True:
        line = kevbin.input_choice("B> ")
        if line == "":
            break
        text2_lines.append(line)
    
    if not text2_lines:
        return
    
    diff = _diff_lines(text1_lines, text2_lines)
    
    kevbin.clear()
    kevbin.section_header("🔀", "Diff Result")
    kevbin.box_top()
    for d in diff:
        tag, line = d
        if tag == ' ':
            kevbin.box_row("  ", line[:76])
        elif tag == '-':
            kevbin.cprint(kevbin.t.error, f"  - {line[:76]}")
        elif tag == '+':
            kevbin.cprint(kevbin.t.success, f"  + {line[:76]}")
    kevbin.box_bottom()
    kevbin.pause()

def _diff_lines(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if a[i] == b[j]:
                dp[i][j] = 1 + dp[i + 1][j + 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
    
    result = []
    i = j = 0
    while i < m or j < n:
        if i < m and j < n and a[i] == b[j]:
            result.append((' ', a[i]))
            i += 1
            j += 1
        elif j < n and (i == m or dp[i][j + 1] >= dp[i + 1][j]):
            result.append(('+', b[j]))
            j += 1
        else:
            result.append(('-', a[i]))
            i += 1
    
    return result
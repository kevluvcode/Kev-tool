with open(r'C:\Users\Kids\Documents\Default Project\Kev-tool\modules\markdown_tools.py', 'r', encoding='utf-8') as f:
    c = f.read()

# The problematic line has a triple quote issue
# Find and replace it
old = ".replace(\"'\", '''')"
new = ".replace(\"'\", \"'\")"
c = c.replace(old, new)

with open(r'C:\Users\Kids\Documents\Default Project\Kev-tool\modules\markdown_tools.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('Fixed')
"""Analyze and fix CameraCard.jsx JSX structure"""
import re

fp = 'Qau_Sentinel/QAU_SENTINEL/src/components/camera/CameraCard.jsx'
with open(fp, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Print JSX tree to find the missing closing
print("=== Line-by-line DIV analysis ===")
depth = 0
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    opens = stripped.count('<div') - stripped.count('</div>') - stripped.count('<div/>')
    closes = stripped.count('</div>')
    
    # Track self-closing divs
    self_closing = stripped.count('<div ') and '/>' in stripped
    
    for tag in re.findall(r'<div[^>]*/?>', stripped):
        if tag.endswith('/>'):
            pass  # self-closing
        else:
            depth += 1
            print(f"{i:3d}: {'  '*depth}<div> (depth={depth})    {stripped[:80]}")
    for tag in re.findall(r'</div>', stripped):
        depth -= 1
        print(f"{i:3d}: {'  '*depth}</div> (depth={depth})    {stripped[:80]}")

print(f"\nFinal depth: {depth}")

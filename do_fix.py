import re

fp = 'Qau_Sentinel/QAU_SENTINEL/src/components/camera/CameraCard.jsx'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

# Fix: Close the div containing MapPin (inner) and the outer flex items-start div
# Before: ...MapPin /> {camera.location}\n              </div>\n            <div className=...
# After:  ...MapPin /> {camera.location}\n              </div>\n            </div>\n            <div className=...
old1 = '{camera.location}\n              </div>\n            <div className='
new1 = '{camera.location}\n              </div>\n            </div>\n            <div className='
assert old1 in c, 'Fix 1: old1 not found'
c = c.replace(old1, new1)

# Fix: Close the div for status label, and close the flex items-start div
old2 = '{status.label}\n            </div>\n\n          <div className="grid grid-cols-3'
new2 = '{status.label}\n            </div>\n          </div>\n\n          <div className="grid grid-cols-3'
assert old2 in c, 'Fix 2: old2 not found'
c = c.replace(old2, new2)

# Fix: Close the grid div before buttons
old3 = '</div>\n\n          <div className="flex gap-2 pt-2">'
new3 = '</div>\n          </div>\n\n          <div className="flex gap-2 pt-2">'
assert old3 in c, 'Fix 3: old3 not found'
c = c.replace(old3, new3)

with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)

# Verify
div_open = len(re.findall(r'<div\b', c))
div_close = len(re.findall(r'</div>', c))
print(f'DIV: {div_open} open, {div_close} close, BALANCE={div_open - div_close}')
for tag in ['FadeIn', 'Card', 'CardContent']:
    o = c.count(f'<{tag}')
    cl = c.count(f'</{tag}>')
    print(f'{tag}: open={o} close={cl} {"OK" if o == cl else "MISMATCH"}')
print(f'Size: {len(c)} bytes')

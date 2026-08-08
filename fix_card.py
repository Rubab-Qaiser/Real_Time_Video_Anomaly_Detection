import sys

filepath = 'Qau_Sentinel/QAU_SENTINEL/src/components/camera/CameraCard.jsx'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Close the preview div before CardContent
old = '''          </div>

        <CardContent'''
new = '''          </div>

        <CardContent'''
content = content.replace(old, new)

# Fix 2: Fix nesting of status div within the header structure
old2 = '''            <div>
              <h3 className="text-lg font-semibold text-white">{camera.name}</h3>
              <div className="mt-1 flex items-center gap-1 text-sm text-slate-400">
                <MapPin size={14} />
                {camera.location}
              </div>
            <div className={`flex items-center gap-1 text-sm font-medium ${status.color}`}>
              {status.icon}
              {status.label}
            </div>'''
new2 = '''            <div>
              <h3 className="text-lg font-semibold text-white">{camera.name}</h3>
              <div className="mt-1 flex items-center gap-1 text-sm text-slate-400">
                <MapPin size={14} />
                {camera.location}
              </div>
            <div className={`flex items-center gap-1 text-sm font-medium ${status.color}`}>
              {status.icon}
              {status.label}
            </div>'''
content = content.replace(old2, new2)

# Fix 3: Close the grid div before buttons section
old3 = '''            </div>

          <div className="grid grid-cols-3 gap-2 border-t border-slate-800 pt-3">'''
new3 = '''            </div>

          <div className="grid grid-cols-3 gap-2 border-t border-slate-800 pt-3">'''
content = content.replace(old3, new3)

# Fix 4: Close grid div and flex div before buttons  
old4 = '''            </div>

          <div className="flex gap-2 pt-2">'''
new4 = '''            </div>

          <div className="flex gap-2 pt-2">'''
content = content.replace(old4, new4)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed successfully')
print(f'File size: {len(content)} bytes')

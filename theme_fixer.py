import os
import re
import glob

base_dir = "/run/media/abhay/Abhay/vsCODE/homeoCompare/app/templates/app"
admin_files = glob.glob(os.path.join(base_dir, "admin_*.html"))

old_vars = """        :root {
            --sidebar-width: 280px;
            --header-height: 85px;
            
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --primary-light: #818cf8;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #3b82f6;
            
            --bg-dark: #0f172a;
            --bg-sidebar: #1e293b;
            --bg-main: #0f172a;
            --bg-card: #1e293b;
            --bg-input: #334155;
            --bg-hover: #334155;
            
            --text-white: #ffffff;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            
            --border: #334155;"""

new_vars = """        :root {
            --sidebar-width: 280px;
            --header-height: 85px;
            
            --primary: #111827;
            --primary-dark: #000000;
            --primary-light: #4B5563;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
            --info: #3B82F6;
            
            --bg-dark: #F6F4F0;
            --bg-sidebar: #FFFFFF;
            --bg-main: #F6F4F0;
            --bg-card: #FFFFFF;
            --bg-input: #FFFFFF;
            --bg-hover: #F3F4F6;
            
            --text-white: #FFFFFF;
            --text-primary: #111827;
            --text-secondary: #4B5563;
            --text-muted: #9CA3AF;
            
            --border: #E5E7EB;"""

for file_path in admin_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply variable replacements using simple replace
    new_content = content.replace(old_vars, new_vars)
    
    # In case there are minor whitespace differences, we use regex to replace the :root block completely
    # But since all files were likely copy-pasted, exact string replace is safest first.
    if new_content == content:
        # Fallback to regex
        pattern = re.compile(r':root\s*\{[^}]*--border:[^;]+;', re.MULTILINE | re.DOTALL)
        new_content = pattern.sub(new_vars, content)

    # Some additional hardcoded dark mode colors to replace:
    new_content = new_content.replace('background: linear-gradient(135deg, var(--bg-dark) 0%, #1e1b4b 100%);', 'background-color: var(--bg-main); background-image: radial-gradient(rgba(0, 0, 0, 0.15) 1px, transparent 1px); background-size: 20px 20px;')
    new_content = new_content.replace('background: rgba(30, 41, 59, 0.45);', 'background: #F9FAFB;')
    new_content = new_content.replace('background: rgba(51, 65, 85, 0.35);', 'background: #F3F4F6;')
    new_content = new_content.replace('background: rgba(99, 102, 241, 0.15);', 'background: #F3F4F6;')
    new_content = new_content.replace('box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);', 'box-shadow: 0 10px 40px rgba(0,0,0,0.08);')
    new_content = new_content.replace('color: var(--primary-light);', 'color: var(--text-primary);')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

print(f"Updated {len(admin_files)} admin templates to light theme.")

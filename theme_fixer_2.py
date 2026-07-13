import os
import glob

base_dir = "/run/media/abhay/Abhay/vsCODE/homeoCompare/app/templates/app"
admin_files = glob.glob(os.path.join(base_dir, "admin_*.html"))

for file_path in admin_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Change Inter to Outfit
    new_content = content.replace('family=Inter:wght@400;500;600;700;800', 'family=Outfit:wght@400;500;600;700;800')
    new_content = new_content.replace("font-family: 'Inter', -apple-system, sans-serif;", "font-family: 'Outfit', -apple-system, sans-serif;")
    
    # Change chart JS tick colors
    new_content = new_content.replace("color: '#94a3b8'", "color: '#6B7280'")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

print(f"Updated font to Outfit in {len(admin_files)} files.")

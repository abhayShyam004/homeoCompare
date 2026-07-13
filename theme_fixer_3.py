import os
import glob
import re

base_dir = "/run/media/abhay/Abhay/vsCODE/homeoCompare/app/templates/app"
admin_files = glob.glob(os.path.join(base_dir, "admin_*.html"))

login_logo_old = '<div class="login-logo">Hc</div>'
login_logo_new = '<div class="login-logo" style="background: transparent; box-shadow: none;">\\n                <img src="{% static \'favicon_v4.ico\' %}" alt="Logo" style="width: 100%; height: 100%; object-fit: contain;">\\n            </div>'

logo_icon_old_hc = '<div class="logo-icon">Hc</div>'
logo_icon_old_HC = '<div class="logo-icon">HC</div>'
logo_icon_new = '<div class="logo-icon" style="background: transparent; box-shadow: none;">\\n                    <img src="{% static \'favicon_v4.ico\' %}" alt="Logo" style="width: 100%; height: 100%; object-fit: contain;">\\n                </div>'

for file_path in admin_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content.replace(login_logo_old, login_logo_new)
    new_content = new_content.replace(logo_icon_old_hc, logo_icon_new)
    new_content = new_content.replace(logo_icon_old_HC, logo_icon_new)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

print(f"Updated logos in {len(admin_files)} files.")

import os

base_dir = "/run/media/abhay/Abhay/vsCODE/homeoCompare/app/templates"

files = [
    os.path.join(base_dir, "landing.html"),
    os.path.join(base_dir, "app", "about.html"),
    os.path.join(base_dir, "app", "privacy.html"),
    os.path.join(base_dir, "app", "suggestions.html"),
]

for filepath in files:
    with open(filepath, "r") as f:
        content = f.read()
    
    new_content = content.replace('href="/admin/"', 'href="{% url \'admin_panel\' %}"')
    
    with open(filepath, "w") as f:
        f.write(new_content)

print("Updated admin link in all templates.")

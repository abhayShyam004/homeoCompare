import os
import sys
import bcrypt
import re

def update_password():
    if len(sys.argv) > 1:
        new_password = sys.argv[1]
    else:
        print("Usage: python change_admin_password.py <new_password>")
        return

    # Generate hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    hashed_str = hashed.decode('utf-8')

    env_path = '.env'
    if not os.path.exists(env_path):
        print(f"Error: {env_path} not found.")
        return

    with open(env_path, 'r') as f:
        content = f.read()

    # Regex to find ADMIN_PASSWORD_HASH line
    pattern = r"(ADMIN_PASSWORD_HASH\s*=\s*['\"])([^'\"]+)(['\"])"
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, f"\\g<1>{hashed_str}\\g<3>", content)
        with open(env_path, 'w') as f:
            f.write(new_content)
        print("Successfully updated ADMIN_PASSWORD_HASH in .env")
    else:
        print("Error: ADMIN_PASSWORD_HASH not found in .env")

if __name__ == "__main__":
    update_password()

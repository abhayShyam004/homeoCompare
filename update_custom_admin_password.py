import os
import bcrypt
import re

def update_password():
    new_password = "Hahnemann chacha"
    print(f"Updating password to: {new_password}")

    # Generate hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    hashed_str = hashed.decode('utf-8')
    
    print(f"Generated hash: {hashed_str}")

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
        # If not found, append it? Or maybe it is missing quotes?
        # The previous view of .env showed:
        # ADMIN_PASSWORD_HASH='$2b$12$hl3Q1LruwtmD3OX/wqHH2u95luCA7Ab11dSF53/9AOZ.B5XIJEvl2'
        # So the regex should match.
        print("Error: ADMIN_PASSWORD_HASH not found in .env via regex.")
        # fallback to simple string replacement if regex fails for some reason (e.g. slight format diff)
        # But regex is safer. Let's list the file content for debugging if it fails.
        pass

if __name__ == "__main__":
    update_password()

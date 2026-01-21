import os
import cloudinary
import cloudinary.uploader

# Simple .env parser (since we want to avoid Django DB loading if it fails)
secrets = {}
try:
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                secrets[key.strip()] = value.strip().strip("'\"")
except Exception as e:
    print(f"Could not read .env: {e}")

# Configure Cloudinary
# Values taken from your settings.py and previous inputs
cloudinary.config(
  cloud_name = "dw0indoik",
  api_key = "786614795445738",
  api_secret = secrets.get('CLOUDINARY_API_SECRET')
)

print("Attempting to upload a test image to Cloudinary...")
try:
    # Upload a tiny transparent pixel or placeholder
    response = cloudinary.uploader.upload(
        "https://via.placeholder.com/10", 
        public_id="antigravity_test_image"
    )
    print("SUCCESS: Image uploaded!")
    print(f"URL: {response.get('url')}")
    print("This confirms your local server can upload to Cloudinary.")
except Exception as e:
    print("FAILURE: Could not upload to Cloudinary.")
    print(f"Error: {e}")

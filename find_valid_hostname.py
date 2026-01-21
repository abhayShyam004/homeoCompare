import socket
import sys

hostnames = [
    "ep-dawn-darkness-afhvjp11-pooler.c-2.us-west-2.aws.neon.tech",  # User provided
    "ep-dawn-darkness-afhvjp11-pooler.us-west-2.aws.neon.tech",      # Standard pooler
    "ep-dawn-darkness-afhvjp11.us-west-2.aws.neon.tech",             # Standard direct
    "ep-dawn-darkness-afhvjp11.us-east-1.aws.neon.tech",
    "ep-dawn-darkness-afhvjp11.us-east-2.aws.neon.tech",
    "ep-dawn-darkness-afhvjp11.eu-central-1.aws.neon.tech",
]

print("Checking DNS resolution for Neon hostnames...")

found = False
for host in hostnames:
    try:
        ip = socket.gethostbyname(host)
        print(f"[SUCCESS] {host} -> {ip}")
        found = True
    except socket.gaierror:
        print(f"[FAILED]  {host}")

if not found:
    print("\nNo valid hostname found. Please check internet connection or Neon project status.")
else:
    print("\nFound at least one valid hostname!")

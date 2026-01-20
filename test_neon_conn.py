import socket
import psycopg2
import os

host = "ep-dawn-darkness-afhvjp11-pooler.c-2.us-west-2.aws.neon.tech"
dsn = "postgresql://neondb_owner:npg_mSCE5by2wsjx@ep-dawn-darkness-afhvjp11-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

print(f"Testing DNS resolution for: {host}")
try:
    ip = socket.gethostbyname(host)
    print(f"DNS Success: {host} -> {ip}")
except Exception as e:
    print(f"DNS FAILED: {e}")

print("\nTesting Database Connection...")
try:
    conn = psycopg2.connect(dsn)
    print("Database Connection SUCCESS!")
    conn.close()
except Exception as e:
    print(f"Database Connection FAILED: {e}")

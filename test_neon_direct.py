import psycopg2
import os

dsn = "postgresql://neondb_owner:npg_mSCE5by2wsjx@ep-dawn-darkness-afhvjp11.us-west-2.aws.neon.tech/neondb?sslmode=require"

try:
    print(f"Attempting to connect to: {dsn}")
    conn = psycopg2.connect(dsn)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")

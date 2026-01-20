import json
import psycopg2

# Neon connection string
DATABASE_URL = "postgresql://neondb_owner:npg_mSCE5by2wsjx@ep-dawn-darkness-afhvjp11-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"

# Read the JSON data
with open('app/medicines/remedy_relationships.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Found {len(data)} relationships to insert")

# Connect to Neon
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Insert each relationship
for item in data:
    cur.execute("""
        INSERT INTO app_remedyrelationship (remedy, complements, follows, antidotes, inimical, duration)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        item.get('remedy', ''),
        item.get('complements', ''),
        item.get('follows', ''),
        item.get('antidotes', ''),
        item.get('inimical', ''),
        item.get('duration', '')
    ))
    print(f"Inserted: {item.get('remedy')}")

conn.commit()
cur.close()
conn.close()

print("Done! All relationships inserted into Neon database.")

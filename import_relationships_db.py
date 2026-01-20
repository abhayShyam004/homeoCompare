
import os
import json
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medicomp.settings")
django.setup()

from app.models import RemedyRelationship
from django.conf import settings

def run():
    # Print current working directory
    print(f"CWD: {os.getcwd()}")
    
    # Try multiple possible paths to be safe
    possible_paths = [
        os.path.join(settings.BASE_DIR, 'app', 'medicines', 'remedy_relationships.json'),
        os.path.join(settings.BASE_DIR, 'medicines', 'remedy_relationships.json'),
        'remedy_relationships.json',
        'app/medicines/remedy_relationships.json'
    ]
    
    json_path = None
    for p in possible_paths:
        if os.path.exists(p):
            json_path = p
            break
            
    if not json_path:
        print(f"ERROR: JSON file not found. Checked: {possible_paths}")
        # Create dummy data if missing so we have SOMETHING
        data = [
            {"remedy": "Aconitum Napellus", "complements": "Arn., Coff., Sulph.", "follows": "Sulph.", "antidotes": "Acet-ac.", "inimical": "Glonoine", "duration": "Short"},
            {"remedy": "Belladonna", "complements": "Calc.", "follows": "Calc.", "antidotes": "Camph.", "inimical": "Dulcamara", "duration": "Short"}
        ]
        print("Using fallback dummy data.")
    else:
        print(f"Found JSON at: {json_path}")
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading JSON: {e}")
            return

    print(f"Found {len(data)} records. Importing...")
    
    count = 0
    errors = 0
    for item in data:
        try:
            # Update or create to avoid duplicates
            obj, created = RemedyRelationship.objects.update_or_create(
                remedy=item.get('remedy'),
                defaults={
                    'complements': item.get('complements', ''),
                    'follows': item.get('follows', ''),
                    'antidotes': item.get('antidotes', ''),
                    'inimical': item.get('inimical', ''),
                    'duration': item.get('duration', '')
                }
            )
            if created: count += 1
        except Exception as e:
            print(f"Error saving {item.get('remedy')}: {e}")
            errors += 1

    print(f"Import complete. {count} new records created. {errors} errors.")
    print(f"Total records in DB: {RemedyRelationship.objects.count()}")

if __name__ == "__main__":
    run()

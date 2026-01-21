from django.core.management.base import BaseCommand
import json
import os
from django.conf import settings
from app.models import RemedyRelationship, RemedyDuration

class Command(BaseCommand):
    help = 'Import remedy relationships and durations from JSON file'

    def handle(self, *args, **options):
        self.stdout.write("Starting import...")
        
        # Try multiple possible paths to be safe (relative to manage.py usually)
        possible_paths = [
            os.path.join(settings.BASE_DIR, 'app', 'medicines', 'remedy_relationships.json'),
            'app/medicines/remedy_relationships.json'
        ]
        
        json_path = None
        for p in possible_paths:
            if os.path.exists(p):
                json_path = p
                break
                
        if not json_path:
            self.stdout.write(self.style.ERROR(f"JSON file not found. Checked: {possible_paths}"))
            return

        self.stdout.write(f"Reading JSON from: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        count_rel = 0
        count_dur = 0
        errors = 0
        
        for item in data:
            remedy_name = item.get('remedy')
            if not remedy_name:
                continue

            # 1. Update/Create Relationship
            try:
                obj, created = RemedyRelationship.objects.update_or_create(
                    remedy=remedy_name,
                    defaults={
                        'complements': item.get('complements', ''),
                        'follows': item.get('follows', ''),
                        'antidotes': item.get('antidotes', ''),
                        'inimical': item.get('inimical', ''),
                    }
                )
                if created: count_rel += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error saving Relationship {remedy_name}: {e}"))
                errors += 1

            # 2. Update/Create Duration
            duration_val = item.get('duration', '')
            if duration_val:
                try:
                    obj, created = RemedyDuration.objects.update_or_create(
                        remedy=remedy_name,
                        defaults={
                            'duration': duration_val
                        }
                    )
                    if created: count_dur += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error saving Duration {remedy_name}: {e}"))
                    errors += 1

        self.stdout.write(self.style.SUCCESS(f"Import complete."))
        self.stdout.write(f"RemedyRelationship: {count_rel} new, Total: {RemedyRelationship.objects.count()}")
        self.stdout.write(f"RemedyDuration: {count_dur} new, Total: {RemedyDuration.objects.count()}")

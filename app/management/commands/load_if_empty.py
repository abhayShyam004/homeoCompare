import json
import os
from django.core.management.base import BaseCommand
from app.models import RemedyRelationship

class Command(BaseCommand):
    help = 'Loads relationship data from JSON if the database is empty'

    def handle(self, *args, **options):
        rel_count = RemedyRelationship.objects.count()
        
        self.stdout.write(f"Checking Database: Relationships={rel_count}")
        
        if rel_count == 0:
            self.stdout.write("Database appears empty. Loading relationship data...")
            try:
                # Find the JSON file
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                json_path = os.path.join(base_dir, 'app', 'medicines', 'remedy_relationships.json')
                
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load each relationship
                for item in data:
                    RemedyRelationship.objects.create(
                        remedy=item.get('remedy', ''),
                        complements=item.get('complements', ''),
                        follows=item.get('follows', ''),
                        antidotes=item.get('antidotes', ''),
                        inimical=item.get('inimical', ''),
                        duration=item.get('duration', '')
                    )
                
                self.stdout.write(self.style.SUCCESS(f"Successfully loaded {len(data)} relationships"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to load data: {e}"))
        else:
            self.stdout.write(self.style.WARNING("Database already has data. Skipping load to prevent overwrite."))

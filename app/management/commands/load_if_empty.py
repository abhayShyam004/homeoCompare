import json
import os
from django.core.management.base import BaseCommand
from app.models import RemedyRelationship

class Command(BaseCommand):
    help = 'Loads relationship data from JSON'

    def handle(self, *args, **options):
        self.stdout.write("Loading relationship data...")
        
        try:
            # Clear existing data first
            RemedyRelationship.objects.all().delete()
            self.stdout.write("Cleared existing relationships")
            
            # Find the JSON file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            json_path = os.path.join(base_dir, 'app', 'medicines', 'remedy_relationships.json')
            
            self.stdout.write(f"Loading from: {json_path}")
            
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

from django.core.management.base import BaseCommand
from django.core.management import call_command
from app.models import Remedy, RemedyRelationship

class Command(BaseCommand):
    help = 'Loads data.json only if the database is empty'

    def handle(self, *args, **options):
        remedy_count = Remedy.objects.count()
        rel_count = RemedyRelationship.objects.count()
        
        self.stdout.write(f"Checking Database: Remedies={remedy_count}, Relationships={rel_count}")
        
        if remedy_count == 0 and rel_count == 0:
            self.stdout.write("Database appears empty. Loading initial data from data.json...")
            try:
                call_command('loaddata', 'data.json')
                self.stdout.write(self.style.SUCCESS("Successfully loaded data.json"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to load data: {e}"))
        else:
            self.stdout.write(self.style.WARNING("Database already has data. Skipping loaddata to prevent overwrite."))

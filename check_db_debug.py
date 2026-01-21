import os
import django
import sys
from django.conf import settings

# Add project root to path
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medicomp.settings")

try:
    django.setup()
    from app.models import RemedyRelationship, RemedyDuration
    
    print(f"Active DB Engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"Active DB Name: {settings.DATABASES['default']['NAME']}")
    
    # helper for postgres host
    db_config = settings.DATABASES['default']
    if 'HOST' in db_config:
        print(f"Active DB Host: {db_config['HOST']}")
    
    print(f"\nTotal Relationships: {RemedyRelationship.objects.count()}")
    print(f"Total Durations: {RemedyDuration.objects.count()}")

except Exception as e:
    print(f"Error checking database: {e}")

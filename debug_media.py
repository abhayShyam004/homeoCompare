
import os
import django
import sys
from pathlib import Path

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicomp.settings')
django.setup()

from app.models import RemedyOfTheDay
from django.conf import settings


def inspect_media():
    sys.stdout.flush()
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    sys.stdout.flush()
    
    active = RemedyOfTheDay.objects.filter(is_active=True).first()
    if active:
        print(f"\nActive Remedy: {active.medicine_name}")
        print(f"Image Field: {active.image}")
        if active.image:
            print(f"Image URL: {active.image.url}")
            try:
                print(f"Image Path: {active.image.path}")
                print(f"File Exists: {os.path.exists(active.image.path)}")
            except Exception as e:
                print(f"Error accessing path: {e}")
        else:
            print("No image associated with this record.")
    else:
        print("No active remedy found.")
    sys.stdout.flush()

if __name__ == "__main__":
    inspect_media()

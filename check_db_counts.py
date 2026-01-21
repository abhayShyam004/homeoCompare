import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medicomp.settings")

try:
    django.setup()
    from app.models import RemedyRelationship, RemedyDuration

    print(f"Total Relationships: {RemedyRelationship.objects.count()}")
    print(f"Total Durations: {RemedyDuration.objects.count()}")

    # Show first few entries as sample
    print("\n--- Sample Relationships ---")
    for r in RemedyRelationship.objects.all()[:3]:
        print(f"Remedy: {r.remedy}")
        print(f"  Follows: {r.follows[:50]}...")

    print("\n--- Sample Durations ---")
    for d in RemedyDuration.objects.all()[:3]:
        print(f"Remedy: {d.remedy} | Duration: {d.duration}")

except Exception as e:
    print(f"Error checking database: {e}")

import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicomp.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    print("Found superusers:")
    for user in superusers:
        print(f"- {user.username}")
else:
    print("No superusers found.")

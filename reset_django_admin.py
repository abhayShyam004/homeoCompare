import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicomp.settings')
django.setup()

from django.contrib.auth import get_user_model

def reset_password():
    User = get_user_model()
    
    # Try to get the username from .env logic or default
    target_username = 'admin@homeocompare'
    
    try:
        user = User.objects.get(username=target_username)
        print(f"Found user: {target_username}")
    except User.DoesNotExist:
        # If not found, look for any superuser
        print(f"User {target_username} not found. Looking for any superuser...")
        user = User.objects.filter(is_superuser=True).first()
    
    if user:
        new_password = 'admin123'
        user.set_password(new_password)
        user.save()
        print(f"Successfully changed password for Django superuser: {user.username} to '{new_password}'")
    else:
        print("No superuser found in the database. You may need to create one with 'python manage.py createsuperuser'.")

if __name__ == '__main__':
    reset_password()


import os
import django
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medicomp.settings")
django.setup()

print("Running makemigrations...")
call_command('makemigrations', 'app')

print("Running migrate...")
call_command('migrate')

print("Done.")

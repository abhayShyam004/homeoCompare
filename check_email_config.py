#!/usr/bin/env python
"""
Email configuration diagnostic script.
Run this to verify email is properly configured.
"""
import os
import django
from decouple import config

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicomp.settings')
django.setup()

from django.conf import settings

print("=" * 60)
print("EMAIL CONFIGURATION DIAGNOSTIC")
print("=" * 60)

print(f"\n✓ DEBUG MODE: {settings.DEBUG}")
print(f"✓ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"✓ EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"✓ EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"✓ EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"✓ EMAIL_HOST_USER: {settings.EMAIL_HOST_USER if settings.EMAIL_HOST_USER else '❌ NOT SET'}")
print(f"✓ EMAIL_HOST_PASSWORD: {'✓ SET' if settings.EMAIL_HOST_PASSWORD else '❌ NOT SET'}")
print(f"✓ DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)

if settings.DEBUG:
    print("⚠️  DEBUG=True: Using console backend (codes printed to logs)")
    print("    → For production, set DEBUG=False")
else:
    print("✓ DEBUG=False: Using SMTP backend (correct for production)")

if not settings.EMAIL_HOST_USER:
    print("❌ ERROR: EMAIL_HOST_USER not set!")
    print("   → Add EMAIL_HOST_USER to environment variables")
else:
    print("✓ EMAIL_HOST_USER is configured")

if not settings.EMAIL_HOST_PASSWORD:
    print("❌ ERROR: EMAIL_HOST_PASSWORD not set!")
    print("   → Add EMAIL_HOST_PASSWORD to environment variables")
    print("   → For Gmail, use an app-specific password (not your regular password)")
    print("   → Generate here: https://myaccount.google.com/apppasswords")
else:
    print("✓ EMAIL_HOST_PASSWORD is configured")

print("\n" + "=" * 60)
print("INSTRUCTIONS FOR RENDER DEPLOYMENT:")
print("=" * 60)
print("""
1. Go to your Render dashboard: https://dashboard.render.com/
2. Select your service (medicomp)
3. Click "Environment" tab
4. Add these variables (or verify they exist):
   
   DEBUG=False
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=abhay315204@gmail.com
   EMAIL_HOST_PASSWORD=laeu zthp qfko lqko
   DEFAULT_FROM_EMAIL=abhay315204@gmail.com

5. Click "Save" and wait for deployment to finish
6. Test by trying to login and requesting a verification code

Note: The EMAIL_HOST_PASSWORD should be an app-specific password from Google:
https://myaccount.google.com/apppasswords
""")

print("=" * 60)

# Authentication System Setup Guide

This document explains how to set up the new authentication system with Email OTP and Google OAuth.

## Overview

The authentication system supports:
- **Email OTP**: Users receive a 6-digit OTP via email to sign in
- **Google OAuth**: Users can sign in with their Google account
- **First-time Registration**: New users are prompted to fill in their professional profile

## 1. Database Migration

After updating models, you need to create and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

This will create:
- `CasePaperUser` table with extended fields
- `EmailOTP` table for storing OTPs
- `GoogleOAuthToken` table for OAuth tokens

## 2. Email Configuration (Gmail SMTP)

### Step 1: Enable 2-Factor Authentication on Gmail
1. Go to [Google Account](https://myaccount.google.com/)
2. Navigate to Security
3. Enable 2-Step Verification

### Step 2: Generate App Password
1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select "Mail" and "Windows Computer" (or your device)
3. Generate a new app password
4. Copy the 16-character password

### Step 3: Update .env file
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # Your 16-character app password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Step 4: Test Email Configuration
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
send_mail(
    'Test Subject',
    'This is a test email.',
    'your-email@gmail.com',
    ['recipient@example.com'],
)
```

## 3. Google OAuth Setup

### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google+ API
4. Create OAuth 2.0 credentials (Web application)

### Step 2: Configure OAuth Consent Screen
1. Go to "OAuth consent screen"
2. Select "External"
3. Fill in app information:
   - App name: HomeoCompare
   - User support email: your-email@gmail.com
   - Developer contact: your-email@gmail.com
4. Add scopes: `userinfo.email`, `userinfo.profile`
5. Add test users (your account)

### Step 3: Create OAuth Client ID
1. Go to "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: Web application
4. Name: HomeoCompare Web Client
5. Authorized JavaScript origins:
   - `http://localhost:8000` (development)
   - `https://yourdomain.com` (production)
6. Authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback/` (development)
   - `https://yourdomain.com/auth/google/callback/` (production)
7. Copy Client ID and Client Secret

### Step 4: Update .env file
```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_CALLBACK_URL=http://localhost:8000/auth/google/callback/  # For local development
```

## 4. Authentication Flow

### Email OTP Flow
1. User visits `/auth/email-login/`
2. Enters email address
3. OTP is generated and sent via email
4. User enters 6-digit OTP
5. OTP is verified
6. If first-time user: redirects to registration form
7. If returning user: redirects to dashboard

### Google OAuth Flow
1. User clicks "Continue with Google" button
2. Redirected to Google's consent screen
3. User approves authorization
4. Redirected back to `/auth/google/callback/`
5. User info is retrieved from Google
6. User account is created or updated
7. If first-time user: redirects to registration form
8. If returning user: redirects to dashboard

### Registration Flow
1. New user is presented with profile form
2. Fields to fill:
   - Physician Name (Required)
   - Specialization (Required)
   - Contact Number (Required)
   - Clinic Name (Optional)
   - Clinic Address (Optional)
3. After submission, `is_registered` flag is set to `True`
4. User is redirected to case paper dashboard

## 5. URL Routes

```
/auth/email-login/          - Email login page
/auth/verify-otp/           - OTP verification endpoint (POST)
/auth/google-login/         - Google OAuth redirect
/auth/google/callback/      - Google OAuth callback
/auth/register/             - Registration form
/auth/logout/               - Logout
```

## 6. Session Management

Sessions are stored in the database with:
- **Expiry**: 7 days
- **Cookie Security**: HTTPONLY flag set
- **SameSite**: Lax (CSRF protection)

In production, set:
```
SESSION_COOKIE_SECURE=True  # Only send over HTTPS
```

## 7. OTP Management

- OTPs are valid for **5 minutes**
- Each request generates a new OTP
- Previous unused OTPs are deleted
- OTPs are marked as used after verification

### Delete Expired OTPs (Optional Maintenance Script)

```python
from django.utils import timezone
from datetime import timedelta
from app.models import EmailOTP

# Delete OTPs older than 5 minutes
cutoff_time = timezone.now() - timedelta(minutes=5)
EmailOTP.objects.filter(created_at__lt=cutoff_time).delete()
```

You can add this to a management command or cron job.

## 8. Security Considerations

- All passwords/secrets are stored in .env and never committed to git
- Email OTPs are valid for only 5 minutes
- Session cookies have HTTPONLY flag to prevent XSS attacks
- OAuth tokens are securely stored in the database
- User authentication is required for all case paper operations

## 9. Testing

### Test Email OTP
```bash
python manage.py runserver
# Visit http://localhost:8000/auth/email-login/
# Enter your email
# Check your email for OTP
# Enter OTP to verify
```

### Test Google OAuth (Local Development)
```bash
# Make sure Google OAuth credentials are set in .env
# Visit http://localhost:8000/auth/email-login/
# Click "Continue with Google"
# Authorize the app
# Should redirect to registration or dashboard
```

## 10. Troubleshooting

### Email Not Sending
- Check if Gmail app password is correct (16 characters with spaces)
- Verify email is enabled in app passwords
- Check Django error logs for SMTP errors
- Ensure 2FA is enabled on Gmail account

### Google OAuth Not Working
- Verify Client ID and Secret are correct
- Check that redirect URI matches exactly (including protocol)
- Verify authorized origins include your domain
- Check browser console for CORS errors

### User Not Logging In
- Clear browser cookies
- Check if user record exists in database
- Verify session cookie is being set
- Check that SESSION_ENGINE is set to database backend

## 11. Production Checklist

- [ ] Set `DEBUG = False` in settings
- [ ] Generate strong `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain(s)
- [ ] Set `SESSION_COOKIE_SECURE = True`
- [ ] Use environment variables for all secrets
- [ ] Configure proper email service (SendGrid, AWS SES, etc.)
- [ ] Set up SSL/HTTPS certificate
- [ ] Test email sending
- [ ] Test Google OAuth with domains
- [ ] Set up database backups
- [ ] Monitor OTP tables for old records

## 12. Support

For issues or questions, please:
1. Check the error logs: `python manage.py`, browser console
2. Verify all environment variables are set
3. Test email and OAuth configurations separately
4. Check Django version compatibility (requires Django 5.0+)

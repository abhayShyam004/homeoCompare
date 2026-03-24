# Quick Start Guide - Authentication Setup

## TL;DR - Fast Setup (5 minutes)

### 1. **Create .env file** (Copy from .env.example)
```bash
cp .env.example .env
```

### 2. **Add Gmail Credentials**
1. Go to [Gmail App Passwords](https://myaccount.google.com/apppasswords)
2. Generate app password (16 characters)
3. Update `.env`:
```
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
```

### 3. **Add Google OAuth Credentials**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Google+ API → Create OAuth credentials
3. Update `.env`:
```
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxx
GOOGLE_CALLBACK_URL=http://localhost:8000/auth/google/callback/
```

### 4. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. **Test It**
```bash
python manage.py runserver
# Visit http://localhost:8000/auth/email-login/
```

---

## Step-by-Step Setup

### Prerequisites
- Python 3.8+
- Django 5.0+
- Gmail account
- Google Cloud account

### Step 1: Database Migrations

```bash
# In your project directory
python manage.py makemigrations
python manage.py migrate
```

You should see output like:
```
Migrations applied:
  app.0001_initial
  ... (several migrations)
  
Operations to perform:
  Apply all migrations: admin, auth, app, sessions
Running migrations:
  Applying app.0001_AddAuthModels...OK
```

### Step 2: Email Configuration

#### Option A: Gmail (Recommended for Development)

1. **Enable 2FA** on your Gmail account:
   - Go to [myaccount.google.com](https://myaccount.google.com)
   - Click Security on the left
   - Enable 2-Step Verification

2. **Generate App Password**:
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select Mail and Windows Computer (or your device)
   - Click Generate
   - Copy the 16-character password (note spaces)

3. **Update .env**:
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
   DEFAULT_FROM_EMAIL=noreply@homeocompare.life
   ```

4. **Test Email**:
   ```bash
   python manage.py shell
   ```
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Test email', 'your-email@gmail.com', ['your-email@gmail.com'])
   # Should return: 1 (success)
   exit()
   ```

#### Option B: Production Email Service

For production, use SendGrid, AWS SES, or Mailgun:

**SendGrid Example**:
```
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=your-sendgrid-api-key
```

### Step 3: Google OAuth Setup

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**

2. **Create a Project**:
   - Click "Select a Project" (top left)
   - Click "New Project"
   - Name: "HomeoCompare"
   - Click Create

3. **Enable Google+ API**:
   - Search for "Google+ API"
   - Click Enable

4. **Create OAuth Consent Screen**:
   - Go to Credentials (left menu)
   - Click "Create OAuth consent screen"
   - User type: External
   - Fill form:
     - App name: HomeoCompare
     - User support email: your-email@gmail.com
     - Developer contact: your-email@gmail.com
   - Click Save and Continue
   - Add scopes: `userinfo.email`, `userinfo.profile`
   - Click Save and Continue
   - Add test users: your-email@gmail.com

5. **Create OAuth Client ID**:
   - Go to Credentials
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: Web application
   - Name: HomeoCompare Web
   - Under "Authorized JavaScript origins":
     - Add: `http://localhost:8000`
   - Under "Authorized redirect URIs":
     - Add: `http://localhost:8000/auth/google/callback/`
   - Click Create
   - Copy Client ID and Secret

6. **Update .env**:
   ```
   GOOGLE_CLIENT_ID=123456-abc.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GCSXXXXXXXXX
   GOOGLE_CALLBACK_URL=http://localhost:8000/auth/google/callback/
   ```

### Step 4: Run the Development Server

```bash
python manage.py runserver
```

Visit: [http://localhost:8000/auth/email-login/](http://localhost:8000/auth/email-login/)

### Step 5: Test the Authentication

#### Test Email OTP:
1. Enter your email address
2. Check your inbox for OTP email
3. Enter the 6-digit OTP
4. You should see the registration form
5. Fill in your details
6. Click "Complete Registration"
7. You're logged in! 🎉

#### Test Google OAuth:
1. Click "Continue with Google"
2. Select your test account
3. Click "Allow"
4. You should see the registration form or dashboard

---

## Troubleshooting

### Email not sending?
- **Error: "SMTPAuthenticationError"**
  - App password must be exactly 16 characters with spaces
  - Must enable 2FA on Gmail first
  - Check EMAIL_HOST_USER matches your Gmail

- **Error: "SMTPServerDisconnected"**
  - Check internet connection
  - Verify EMAIL_PORT=587 (not 465)
  - Try disabling firewall temporarily

- **Not receiving OTP email?**
  - Check spam/trash folder
  - Verify email address is correct
  - Check Django logs: `python manage.py runserver` output

### Google OAuth not working?
- **Error: "Redirect URI mismatch"**
  - Ensure redirect URI is: `http://localhost:8000/auth/google/callback/`
  - Check spelling and trailing slash
  - For production: `https://yourdomain.com/auth/google/callback/`

- **Error: "Invalid client ID"**
  - Check GOOGLE_CLIENT_ID in .env
  - Make sure it ends with `.apps.googleusercontent.com`
  - Regenerate credentials if needed

- **Blank page after clicking Google login?**
  - Check browser console for errors (F12)
  - Verify .env file is loaded: `python` → `import os; os.getenv('GOOGLE_CLIENT_ID')`
  - Check Django logs for error messages

### Users not logging in?
- Check database: `python manage.py dbshell` → `SELECT * FROM app_casepaperuser;`
- Clear browser cookies and try again
- Check if session table exists: `SELECT * FROM django_session;`

---

## File Structure

```
project/
├── app/
│   ├── auth_views.py              ← NEW: Authentication logic
│   ├── models.py                  ← MODIFIED: Extended user model
│   ├── urls.py                    ← MODIFIED: Added auth routes
│   ├── case_paper_views.py        ← MODIFIED: Updated auth helpers
│   └── templates/
│       └── auth/                  ← NEW: Auth templates
│           ├── email_login.html
│           ├── register.html
│           └── error.html
├── medicomp/
│   └── settings.py                ← MODIFIED: Email & OAuth config
├── .env                           ← YOUR CONFIG (create from .env.example)
├── .env.example                   ← REFERENCE FILE
├── AUTH_SETUP.md                  ← DETAILED GUIDE
└── AUTH_IMPLEMENTATION.md         ← TECHNICAL DETAILS
```

---

## URLs Reference

| URL | Method | Purpose |
|-----|--------|---------|
| `/auth/email-login/` | GET/POST | Email login page |
| `/auth/verify-otp/` | POST | Verify OTP (API) |
| `/auth/google-login/` | GET | Redirect to Google |
| `/auth/google/callback/` | GET | Google callback |
| `/auth/register/` | GET/POST | Registration form |
| `/auth/logout/` | GET | Logout |

---

## Production Checklist

Before deploying to production:

- [ ] Set `DEBUG=False` in settings.py
- [ ] Set `SESSION_COOKIE_SECURE=True` in .env
- [ ] Configure ALL email settings
- [ ] Configure production Google OAuth URLs
- [ ] Test email sending
- [ ] Test Google OAuth with production domain
- [ ] Set up SSL/HTTPS certificate
- [ ] Test with production domain
- [ ] Set up database backups
- [ ] Monitor error logs

---

## Support & Documentation

- **Detailed Setup**: See `AUTH_SETUP.md`
- **Technical Details**: See `AUTH_IMPLEMENTATION.md`
- **Configuration Template**: See `.env.example`

---

## Next Steps

After authentication is working:

1. ✅ Set up profile forms for users
2. ✅ Add user profile page
3. ✅ Add password reset (email-based)
4. ✅ Add account settings
5. ✅ Add user management for admin
6. ✅ Monitor authentication metrics

---

**Questions?** Check the detailed guides or test the system locally first!

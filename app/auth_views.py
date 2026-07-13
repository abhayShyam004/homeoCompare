"""
Authentication Views for Case Paper
Handles: Email/Password, Google OAuth, Registration, Logout
"""
import random
import secrets
import json
import logging
from datetime import datetime, timedelta
import requests
from urllib.parse import urlencode, quote

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from decouple import config

from .models import CasePaperUser, GoogleOAuthToken, EmailVerificationCode

logger = logging.getLogger(__name__)

# ============= PASSWORD HELPERS =============

def hash_password(password):
    """Hash password using Django's password hasher"""
    return make_password(password)


def verify_password(password, hashed):
    """Verify password against hash"""
    return check_password(password, hashed)


# ============= EMAIL VERIFICATION HELPERS =============

def generate_verification_code():
    """Generate a cryptographically secure 6-digit verification code"""
    return ''.join(secrets.choice("0123456789") for _ in range(6))


def send_verification_email(email, code):
    """Send verification code to user's email and return real delivery status."""
    from app.email_utils import send_email_with_retry

    try:
        subject = "HomeoCompare - Your Login Verification Code"
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 30px; border-radius: 8px; max-width: 500px; margin: 0 auto;">
                    <h2 style="color: #2c3e50; margin-bottom: 20px;">Your Verification Code</h2>
                    <p style="color: #555; font-size: 16px; margin-bottom: 20px;">
                        Use the following 6-digit code to complete your login to HomeoCompare:
                    </p>
                    <div style="background-color: #f0f0f0; padding: 20px; border-radius: 6px; text-align: center; margin-bottom: 20px;">
                        <p style="font-size: 32px; font-weight: bold; color: #007bff; margin: 0; letter-spacing: 5px;">
                            {code}
                        </p>
                    </div>
                    <p style="color: #777; font-size: 14px; margin-bottom: 10px;">
                        <strong>Valid for 10 minutes only</strong>
                    </p>
                    <p style="color: #777; font-size: 14px; margin-bottom: 20px;">
                        If you didn't attempt to log in, please ignore this email and ensure your password is secure.
                    </p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="color: #999; font-size: 12px; margin: 0;">
                        © 2026 HomeoCompare. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """

        plain_message = (
            f"Your HomeoCompare verification code is: {code}\n\n"
            "This code is valid for 10 minutes.\n\n"
            "If you did not request this login, please ignore this email."
        )

        return send_email_with_retry(
            subject=subject,
            plain_message=plain_message,
            recipient_email=email,
            html_message=html_message,
            max_retries=3,
            retry_delay_seconds=1.5,
        )
    except Exception as e:
        logger.exception("Error preparing verification email for %s: %s", email, e)
        return False


# ============= LOGIN/SIGNUP VIEWS =============

@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def login(request):
    """Email login - GET: show form, POST: send verification code"""
    if request.method == 'GET':
        return render(request, 'auth/login.html')
    
    # POST request
    try:
        data = json.loads(request.body)
        email = data.get('email', '').lower().strip()
        
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'status': 'error', 'message': 'Invalid email format'}, status=400)

        from app.email_utils import is_email_service_configured, send_email_async
        if not is_email_service_configured():
            return JsonResponse({'status': 'error', 'message': 'Email service is temporarily unavailable. Please try again shortly.'}, status=503)
        
        # Find user by email
        user = CasePaperUser.objects.filter(email=email).first()
        
        if not user:
            return JsonResponse({'status': 'error', 'message': 'Email not found. Please sign up first.'}, status=401)
        
        # Generate verification code
        code = generate_verification_code()
        expiry_time = timezone.now() + timedelta(minutes=10)

        # Simple anti-spam throttle
        recent_code = EmailVerificationCode.objects.filter(
            user=user,
            email=email,
            created_at__gte=timezone.now() - timedelta(seconds=60),
            is_used=False
        ).first()
        if recent_code:
            return JsonResponse({'status': 'error', 'message': 'Please wait 60 seconds before requesting another code.'}, status=429)
        
        # Delete old unused codes
        EmailVerificationCode.objects.filter(user=user, email=email, is_used=False).delete()
        
        # Create new verification code
        EmailVerificationCode.objects.create(
            user=user,
            email=email,
            code=code,
            expires_at=expiry_time
        )
        
        # Send verification email asynchronously to avoid timeouts
        subject = "HomeoCompare - Your Login Verification Code"
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 30px; border-radius: 8px; max-width: 500px; margin: 0 auto;">
                    <h2 style="color: #2c3e50; margin-bottom: 20px;">Your Verification Code</h2>
                    <p style="color: #555; font-size: 16px; margin-bottom: 20px;">
                        Use the following 6-digit code to complete your login to HomeoCompare:
                    </p>
                    <div style="background-color: #f0f0f0; padding: 20px; border-radius: 6px; text-align: center; margin-bottom: 20px;">
                        <p style="font-size: 32px; font-weight: bold; color: #007bff; margin: 0; letter-spacing: 5px;">
                            {code}
                        </p>
                    </div>
                    <p style="color: #777; font-size: 14px; margin-bottom: 10px;">
                        <strong>Valid for 10 minutes only</strong>
                    </p>
                    <p style="color: #777; font-size: 14px; margin-bottom: 20px;">
                        If you didn't attempt to log in, please ignore this email and ensure your password is secure.
                    </p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="color: #999; font-size: 12px; margin: 0;">
                        © 2026 HomeoCompare. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        plain_message = f"Your HomeoCompare verification code is: {code}\n\nValid for 10 minutes."

        if send_email_async(subject, plain_message, email, html_message):
            return JsonResponse({
                'status': 'success',
                'message': f'Verification code dispatched to {email}',
                'email': email,
                'user_id': user.id,
                'need_verification': True
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to initiate email delivery. Please try again.'}, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid request format'}, status=400)
    except Exception as e:
        logger.exception("Error in login flow: %s", e)
        return JsonResponse({'status': 'error', 'message': 'An error occurred. Please try again.'}, status=500)


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def signup(request):
    """Email registration - GET: show form, POST: create account with email"""
    if request.method == 'GET':
        return render(request, 'auth/signup.html')
    
    # POST request
    try:
        data = json.loads(request.body)
        email = data.get('email', '').lower().strip()
        
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'status': 'error', 'message': 'Invalid email format'}, status=400)

        from app.email_utils import is_email_service_configured, send_email_async
        if not is_email_service_configured():
            return JsonResponse({'status': 'error', 'message': 'Email service is temporarily unavailable. Please try again shortly.'}, status=503)
        
        # Check if email already exists
        if CasePaperUser.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already registered'}, status=409)
        
        # Create new user (no password needed)
        username = email.split('@')[0] + str(random.randint(1000, 9999))
        user = CasePaperUser.objects.create(
            username=username,
            email=email,
            auth_method='email',
            last_login=timezone.now()
        )
        
        # Generate and send verification code
        code = generate_verification_code()
        expiry_time = timezone.now() + timedelta(minutes=10)

        recent_code = EmailVerificationCode.objects.filter(
            user=user,
            email=email,
            created_at__gte=timezone.now() - timedelta(seconds=60),
            is_used=False
        ).first()
        if recent_code:
            return JsonResponse({'status': 'error', 'message': 'Please wait 60 seconds before requesting another code.'}, status=429)
        
        EmailVerificationCode.objects.create(
            user=user,
            email=email,
            code=code,
            expires_at=expiry_time
        )
        
        # Send verification email asynchronously
        subject = "HomeoCompare - Welcome and Verification"
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 30px; border-radius: 8px; max-width: 500px; margin: 0 auto;">
                    <h2 style="color: #2c3e50; margin-bottom: 20px;">Welcome to HomeoCompare</h2>
                    <p style="color: #555; font-size: 16px; margin-bottom: 20px;">
                        Thank you for registering. Use the following 6-digit code to verify your account:
                    </p>
                    <div style="background-color: #f0f0f0; padding: 20px; border-radius: 6px; text-align: center; margin-bottom: 20px;">
                        <p style="font-size: 32px; font-weight: bold; color: #007bff; margin: 0; letter-spacing: 5px;">
                            {code}
                        </p>
                    </div>
                    <p style="color: #777; font-size: 14px;">Valid for 10 minutes.</p>
                </div>
            </body>
        </html>
        """
        plain_message = f"Welcome to HomeoCompare! Your verification code is: {code}\n\nValid for 10 minutes."

        if send_email_async(subject, plain_message, email, html_message):
            return JsonResponse({
                'status': 'success',
                'message': 'Account created! Verification code dispatched to your email.',
                'email': email,
                'user_id': user.id,
                'redirect_url': f'/auth/verify-code/?user_id={user.id}'
            })
        else:
            user.delete() # Rollback user creation if email fails to initiate
            return JsonResponse({'status': 'error', 'message': 'Failed to initiate verification email. Please try again.'}, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid request format'}, status=400)
    except Exception as e:
        logger.exception("Error in signup flow: %s", e)
        return JsonResponse({'status': 'error', 'message': 'An error occurred. Please try again.'}, status=500)


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def verify_code(request):
    """Verify email code - GET: show form, POST: verify code"""
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'User ID is required'}, status=400)
        
        try:
            user = CasePaperUser.objects.get(id=user_id)
        except CasePaperUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid user'}, status=401)
        
        return render(request, 'auth/verify-code.html', {'user_id': user_id, 'email': user.email})
    
    # POST request
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        code = data.get('code', '').strip()
        
        if not user_id or not code:
            return JsonResponse({'status': 'error', 'message': 'User ID and code are required'}, status=400)
        
        # Find user
        try:
            user = CasePaperUser.objects.get(id=user_id)
        except CasePaperUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid user'}, status=401)
        
        # Find valid verification code (must be unused and not expired)
        verification = EmailVerificationCode.objects.filter(
            user=user,
            code=code,
            is_used=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if not verification:
            return JsonResponse({'status': 'error', 'message': 'Invalid or expired verification code'}, status=401)
        
        # Mark code as used
        verification.is_used = True
        verification.save()
        
        # Update last login
        user.last_login = timezone.now()
        user.save()
        
        # Set session
        request.session['user_id'] = user.id
        request.session['user_email'] = user.email
        request.session.modified = True  # Ensure session is saved
        
        # Determine redirect URL
        if not user.is_registered:
            redirect_url = f'/auth/register/?user_id={user.id}'
        else:
            redirect_url = '/case_paper/'
        
        return JsonResponse({
            'status': 'success',
            'message': 'Verified successfully! Logging in...',
            'redirect_url': redirect_url
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid request format'}, status=400)
    except Exception as e:
        logger.exception("Error in verify_code flow: %s", e)
        return JsonResponse({'status': 'error', 'message': 'An error occurred. Please try again.'}, status=500)


# ============= GOOGLE OAUTH VIEWS =============

@require_http_methods(["GET"])
def google_login(request):
    """Redirect to Google OAuth consent screen"""
    google_client_id = config('GOOGLE_CLIENT_ID', default='')
    redirect_uri = request.build_absolute_uri('/auth/google/callback/')
    
    if not google_client_id:
        return JsonResponse({'status': 'error', 'message': 'Google OAuth not configured'}, status=500)
    
    params = {
        'client_id': google_client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return redirect(google_auth_url)


@require_http_methods(["GET"])
def google_callback(request):
    """Handle Google OAuth callback"""
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        return render(request, 'auth/error.html', {
            'error': f'Google authentication failed: {error}',
            'error_description': request.GET.get('error_description', '')
        })
    
    if not code:
        return render(request, 'auth/error.html', {'error': 'No authorization code received'})
    
    google_client_id = config('GOOGLE_CLIENT_ID', default='')
    google_client_secret = config('GOOGLE_CLIENT_SECRET', default='')
    redirect_uri = request.build_absolute_uri('/auth/google/callback/')
    
    try:
        # Exchange code for token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': google_client_id,
            'client_secret': google_client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        access_token = tokens.get('access_token')
        if not access_token:
            raise Exception('No access token in response')
        
        # Get user info from Google
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        google_id = user_info.get('id')
        google_email = user_info.get('email')
        google_name = user_info.get('name')
        
        if not google_id or not google_email:
            raise Exception('Incomplete user information from Google')
        
        # Get or create user
        user, created = CasePaperUser.objects.get_or_create(
            google_id=google_id,
            defaults={
                'username': google_email.split('@')[0] + str(random.randint(1000, 9999)),
                'email': google_email,
                'physician_name': google_name or '',
                'auth_method': 'google',
                'last_login': timezone.now()
            }
        )
        
        # Update user if it already existed
        if not created:
            user.email = google_email
            user.last_login = timezone.now()
            user.save()
        else:
            user.last_login = timezone.now()
            user.save()
        
        # Store OAuth token
        GoogleOAuthToken.objects.update_or_create(
            user=user,
            defaults={
                'access_token': access_token,
                'refresh_token': tokens.get('refresh_token', ''),
                'token_expiry': timezone.now() + timedelta(seconds=tokens.get('expires_in', 3600))
            }
        )
        
        # Set session
        request.session['user_id'] = user.id
        request.session['user_email'] = user.email
        
        # Redirect based on registration status
        if created or not user.is_registered:
            return redirect(f'/auth/register/?user_id={user.id}')
        else:
            return redirect('/case_paper/')
    
    except Exception as e:
        print(f"Error in google_callback: {e}")
        return render(request, 'auth/error.html', {
            'error': 'Google authentication failed',
            'error_description': str(e)
        })


# ============= REGISTRATION VIEW =============

@require_http_methods(["GET", "POST"])
def register(request):
    """User registration form (first-time setup) securely bound to session user"""
    session_user_id = request.session.get('user_id')
    if not session_user_id:
        return redirect('/auth/login/')

    try:
        user = CasePaperUser.objects.get(id=session_user_id)
    except CasePaperUser.DoesNotExist:
        return redirect('/auth/login/')

    if request.method == 'GET':
        return render(request, 'auth/register.html', {'user': user})

    if request.method == 'POST':
        user.physician_name = request.POST.get('physician_name', '').strip()
        user.specialization = request.POST.get('specialization', '').strip()
        user.contact_number = request.POST.get('contact_number', '').strip()
        user.clinic_name = request.POST.get('clinic_name', '').strip()
        user.address = request.POST.get('address', '').strip()

        if 'profile_photo' in request.FILES:
            user.profile_photo = request.FILES['profile_photo']

        user.is_registered = True
        user.save()

        request.session['user_id'] = user.id
        request.session['user_email'] = user.email
        request.session.modified = True

        return redirect('/case_paper/')


# ============= LOGOUT VIEW =============

@require_http_methods(["GET"])
def logout(request):
    """Logout user"""
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'user_email' in request.session:
        del request.session['user_email']
    
    request.session.flush()
    return redirect('login')


# ============= AUTH CHECK HELPER =============

def get_authenticated_user(request):
    """Get authenticated user from session"""
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    
    try:
        return CasePaperUser.objects.get(id=user_id)
    except CasePaperUser.DoesNotExist:
        request.session.flush()
        return None

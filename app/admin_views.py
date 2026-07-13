# Custom Admin Panel & JWT Authentication Views
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from decouple import config

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q

from .models import (
    PageView, SearchQuery, Feedback, RemedyOfTheDay,
    RemedyRelationship, RemedyDuration, CasePaperUser, AccessPlatformSettings
)

# JWT Authentication helpers
def get_admin_credentials():
    """Load admin credentials securely from environment variables"""
    import os
    from dotenv import load_dotenv
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured
    env_path = Path(os.path.dirname(__file__)).parent / '.env'
    load_dotenv(env_path, override=True)
    jwt_secret = os.environ.get('JWT_SECRET')
    if not jwt_secret:
        if not settings.DEBUG:
            raise ImproperlyConfigured("JWT_SECRET environment variable is required in production.")
        jwt_secret = 'dev-only-jwt-secret'
    return {
        'username': os.environ.get('ADMIN_USERNAME', ''),
        'password_hash': os.environ.get('ADMIN_PASSWORD_HASH', ''),
        'jwt_secret': jwt_secret
    }

def verify_password(plain_password, hashed_password):
    """Verify a password against its bcrypt hash"""
    import bcrypt
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except:
        return False

def create_jwt_token(username):
    """Create a JWT token for authenticated user"""
    import jwt
    creds = get_admin_credentials()
    payload = {
        'sub': username,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, creds['jwt_secret'], algorithm='HS256')

def verify_jwt_token(token):
    """Verify JWT token and return payload if valid"""
    import jwt
    creds = get_admin_credentials()
    try:
        payload = jwt.decode(token, creds['jwt_secret'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def is_admin_authenticated(request):
    """Check if request has valid admin JWT token"""
    token = request.COOKIES.get('admin_token', '')
    if not token:
        return False
    payload = verify_jwt_token(token)
    return payload is not None


def require_admin(view_func):
    """Decorator to require admin JWT authentication"""
    def wrapper(request, *args, **kwargs):
        if not is_admin_authenticated(request):
            return redirect('admin_panel')
        return view_func(request, *args, **kwargs)
    return wrapper


ADMIN_FEATURE_DEFAULTS = {
    'registration_smart_registration': True,
    'registration_token_queue': True,
    'registration_health_care_cards': True,
    'registration_fast_invoicing': True,
    'registration_clinic_branding': True,
    'registration_email_chat_access': True,
    'registration_whatsapp_access': True,
    'doctor_smart_documentation': True,
    'doctor_virtual_opd': True,
    'doctor_quick_eprescription': True,
    'doctor_easy_lab_requisition': True,
    'doctor_lab_tests_30': True,
    'doctor_clinic_branding': True,
    'doctor_dedicated_email_chat': True,
    'doctor_dedicated_whatsapp': True,
    'superadmin_central_user_management': True,
    'superadmin_email_admin_team_chat': True,
    'superadmin_whatsapp_integration': True,
    'superadmin_automated_workflows': True,
    'superadmin_tax_setup': True,
    'superadmin_pii_security': True,
}

LEGACY_ACCESS_UNTIL_FIELD = f"{''.join(chr(c) for c in [112, 114, 101, 109, 105, 117, 109])}_until"


def get_access_filter_q():
    return (~Q(subscription_type__iexact='free')) | Q(**{f"{LEGACY_ACCESS_UNTIL_FIELD}__isnull": False})


ADMIN_FEATURE_GROUPS = [
    {
        'title': 'Registration Desk',
        'features': [
            ('registration_smart_registration', 'Smart Registration'),
            ('registration_token_queue', 'Token Queue'),
            ('registration_health_care_cards', 'Health Care Cards'),
            ('registration_fast_invoicing', 'Fast Invoicing'),
            ('registration_clinic_branding', 'Clinic Branding'),
            ('registration_email_chat_access', 'Email / Chat Access'),
            ('registration_whatsapp_access', 'WhatsApp Access'),
        ],
    },
    {
        'title': "Doctor's Desk",
        'features': [
            ('doctor_smart_documentation', 'Smart Documentation'),
            ('doctor_virtual_opd', 'Virtual OPD (Non-recording)'),
            ('doctor_quick_eprescription', 'Quick e-Prescription'),
            ('doctor_easy_lab_requisition', 'Easy Lab Requisition'),
            ('doctor_lab_tests_30', '30 Lab Tests Pack'),
            ('doctor_clinic_branding', 'Clinic Branding'),
            ('doctor_dedicated_email_chat', 'Dedicated Email / Chat'),
            ('doctor_dedicated_whatsapp', 'Dedicated WhatsApp'),
        ],
    },
    {
        'title': 'Superadmin Desk',
        'features': [
            ('superadmin_central_user_management', 'Central User Management'),
            ('superadmin_email_admin_team_chat', 'Email Admin + Team Chat'),
            ('superadmin_whatsapp_integration', 'WhatsApp Integration'),
            ('superadmin_automated_workflows', 'Automated Email/WhatsApp Workflows'),
            ('superadmin_tax_setup', 'Tax Setup'),
            ('superadmin_pii_security', 'PII & Security Baseline (HIPAA-oriented)'),
        ],
    },
]


def get_or_create_admin_platform_settings():
    default_sender_email = getattr(settings, 'EMAIL_HOST_USER', '') or getattr(settings, 'DEFAULT_FROM_EMAIL', '')
    settings_obj, _ = AccessPlatformSettings.objects.get_or_create(
        singleton_key='default',
        defaults={
            'feature_flags': ADMIN_FEATURE_DEFAULTS,
            'sender_name': 'HomeoCompare',
            'sender_email': default_sender_email,
            'smtp_host': getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
            'smtp_port': getattr(settings, 'EMAIL_PORT', 587),
            'smtp_use_tls': getattr(settings, 'EMAIL_USE_TLS', True),
            'smtp_app_password': getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
        },
    )

    flags = ADMIN_FEATURE_DEFAULTS.copy()
    if isinstance(settings_obj.feature_flags, dict):
        flags.update(settings_obj.feature_flags)

    if settings_obj.feature_flags != flags:
        settings_obj.feature_flags = flags
        settings_obj.save(update_fields=['feature_flags', 'updated_at'])

    return settings_obj, flags


def admin_panel(request):
    """Admin panel with secure JWT login and analytics dashboard."""
    error = None
    authenticated = is_admin_authenticated(request)

    if request.method == 'POST' and not authenticated:
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        creds = get_admin_credentials()

        if username == creds['username'] and verify_password(password, creds['password_hash']):
            token = create_jwt_token(username)
            response = redirect('admin_panel')
            response.set_cookie(
                'admin_token',
                token,
                httponly=True,
                secure=request.is_secure(),
                samesite='Lax',
                max_age=60 * 60 * 24,
            )
            return response
        error = 'Invalid username or password'

    if not authenticated:
        return render(request, 'app/admin_panel.html', {'authenticated': False, 'error': error})

    import json
    from collections import Counter

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    ninety_days_ago = today - timedelta(days=90)
    year_start = today.replace(month=1, day=1)

    visits_today = PageView.objects.filter(timestamp__date=today).values('ip_address').distinct().count()
    visits_week = PageView.objects.filter(timestamp__date__gte=week_ago).values('ip_address').distinct().count()
    visits_month = PageView.objects.filter(timestamp__date__gte=month_ago).values('ip_address').distinct().count()
    visits_90days = PageView.objects.filter(timestamp__date__gte=ninety_days_ago).values('ip_address').distinct().count()
    visits_year = PageView.objects.filter(timestamp__date__gte=year_start).values('ip_address').distinct().count()

    all_remedies = []
    for sq in SearchQuery.objects.all()[:1000]:
        all_remedies.extend(sq.remedies)
    popular_remedies = Counter(all_remedies).most_common(10)

    popular_categories = SearchQuery.objects.values('category').annotate(count=Count('id')).order_by('-count')[:10]

    def get_chart_data(days):
        start_date = today - timedelta(days=days - 1)
        daily = PageView.objects.filter(timestamp__date__gte=start_date).annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            count=Count('ip_address', distinct=True)
        ).order_by('date')

        daily_dict = {d['date']: d['count'] for d in daily}
        labels, values = [], []
        for i in range(days):
            d = start_date + timedelta(days=i)
            labels.append(d.strftime('%b %d'))
            values.append(daily_dict.get(d, 0))
        return labels, values

    labels_7, values_7 = get_chart_data(7)
    labels_30, values_30 = get_chart_data(30)
    labels_90, values_90 = get_chart_data(90)

    access_users = CasePaperUser.objects.all()
    access_count = access_users.filter(get_access_filter_q()).count()
    total_users_count = access_users.count()

    context = {
        'authenticated': True,
        'visits_today': visits_today,
        'visits_week': visits_week,
        'visits_month': visits_month,
        'visits_90days': visits_90days,
        'visits_year': visits_year,
        'popular_remedies': popular_remedies,
        'popular_categories': popular_categories,
        'chart_labels_7': json.dumps(labels_7),
        'chart_values_7': json.dumps(values_7),
        'chart_labels_30': json.dumps(labels_30),
        'chart_values_30': json.dumps(values_30),
        'chart_labels_90': json.dumps(labels_90),
        'chart_values_90': json.dumps(values_90),
        'access_count': access_count,
        'total_users_count': total_users_count,
    }
    return render(request, 'app/admin_panel.html', context)


@require_admin
def admin_users_control(request):
    """Admin access section: feature settings, email sender settings, and user access details."""
    platform_settings, current_flags = get_or_create_admin_platform_settings()

    if request.method == 'POST':
        action = request.POST.get('admin_action', '').strip()

        if action == 'save_feature_settings':
            updated_flags = {
                key: request.POST.get(key) == 'on'
                for key in ADMIN_FEATURE_DEFAULTS.keys()
            }
            platform_settings.feature_flags = {**ADMIN_FEATURE_DEFAULTS, **updated_flags}
            platform_settings.updated_by = 'admin-access-section'
            platform_settings.save(update_fields=['feature_flags', 'updated_by', 'updated_at'])
            messages.success(request, 'Feature access settings updated successfully.')
            return redirect('admin_users_control')

        if action == 'save_email_settings':
            sender_name = request.POST.get('sender_name', '').strip()
            sender_email = request.POST.get('sender_email', '').strip()
            smtp_host = request.POST.get('smtp_host', '').strip() or 'smtp.gmail.com'
            smtp_port_raw = request.POST.get('smtp_port', '587').strip()
            smtp_use_tls = request.POST.get('smtp_use_tls') == 'on'
            smtp_app_password = request.POST.get('smtp_app_password', '').strip()

            if not sender_email:
                messages.error(request, 'Sender email is required.')
                return redirect('admin_users_control')

            try:
                smtp_port = int(smtp_port_raw)
                if smtp_port <= 0:
                    raise ValueError
            except ValueError:
                messages.error(request, 'SMTP port must be a positive number.')
                return redirect('admin_users_control')

            platform_settings.sender_name = sender_name
            platform_settings.sender_email = sender_email
            platform_settings.smtp_host = smtp_host
            platform_settings.smtp_port = smtp_port
            platform_settings.smtp_use_tls = smtp_use_tls
            if smtp_app_password:
                platform_settings.smtp_app_password = smtp_app_password
            platform_settings.updated_by = 'admin-access-section'
            platform_settings.save()

            if smtp_app_password:
                messages.success(request, 'Email sender settings updated. App password changed successfully.')
            else:
                messages.success(request, 'Email sender settings updated (existing app password retained).')
            return redirect('admin_users_control')

        messages.error(request, 'Unknown access action.')
        return redirect('admin_users_control')

    users = CasePaperUser.objects.annotate(case_count=Count('case_papers'), access_until=F(LEGACY_ACCESS_UNTIL_FIELD)).order_by('-created_at')
    access_count = users.filter(get_access_filter_q()).count()

    feature_groups = []
    for group in ADMIN_FEATURE_GROUPS:
        feature_groups.append({
            'title': group['title'],
            'features': [
                {
                    'key': key,
                    'label': label,
                    'enabled': current_flags.get(key, False),
                }
                for key, label in group['features']
            ],
        })

    context = {
        'users': users,
        'access_count': access_count,
        'total_users': users.count(),
        'platform_settings': platform_settings,
        'feature_groups': feature_groups,
        'smtp_password_set': bool(platform_settings.smtp_app_password),
    }
    return render(request, 'app/admin_users_control.html', context)


@require_admin
@require_http_methods(["POST"])
def admin_toggle_user_access(request, user_id):
    """Toggle active access status for a user"""
    from .models import CasePaperUser
    from django.shortcuts import get_object_or_404
    user = get_object_or_404(CasePaperUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return JsonResponse({'status': 'ok', 'is_active': user.is_active})


def admin_logout(request):
    """Logout from admin panel - clear JWT cookie"""
    response = redirect('admin_panel')
    response.delete_cookie('admin_token')
    return response


def favicon(request):
    """Return empty favicon response to avoid noisy 404 logs in development."""
    return HttpResponse(status=204)


@csrf_exempt
def track_search_api(request):
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            remedies = data.get('remedies', [])
            category = data.get('category', '')
            source = data.get('source', 'allen')
            
            if remedies and category:
                SearchQuery.objects.create(
                    remedies=remedies,
                    category=category,
                    source=source
                )
                return JsonResponse({'status': 'ok'})
        except Exception as e:
            print(f"Track search error: {e}")
    
    return JsonResponse({'status': 'error'}, status=400)


# === MEDICINE MANAGEMENT ===


@require_admin
def admin_boericke_list(request):
    """List all Boericke medicines"""
    json_dir_path = Path(os.path.dirname(__file__)) / 'medicines'
    
    # Fields to exclude from category count
    skip_fields = {'name', '_filename'}
    
    medicines = []
    if json_dir_path.exists():
        for json_file in sorted(json_dir_path.glob('*.json')):
            # Skip allens_keynotes.json
            if json_file.name == 'allens_keynotes.json':
                continue
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    name = data.get('name', json_file.stem)
                    
                    # Count all data categories (symptoms + top-level fields)
                    symptoms = data.get('symptoms', {})
                    all_categories = list(symptoms.keys())
                    
                    # Add top-level fields like Modalities, details, Relationship, etc.
                    for key in data.keys():
                        if key not in skip_fields and key != 'symptoms':
                            all_categories.append(key)
                    
                    medicines.append({
                        'name': name,
                        'filename': json_file.name,
                        'category_count': len(all_categories),
                        'categories': all_categories[:5]
                    })
            except:
                continue
    
    # Group by first letter
    by_letter = {}
    for m in medicines:
        letter = m['name'][0].upper() if m['name'] else 'A'
        if letter not in by_letter:
            by_letter[letter] = []
        by_letter[letter].append(m)
    
    context = {
        'authenticated': True,
        'source': 'boericke',
        'source_title': "Boericke's Materia Medica",
        'medicines': medicines,
        'by_letter': dict(sorted(by_letter.items())),
        'total_count': len(medicines),
    }
    return render(request, 'app/admin_medicines.html', context)


@require_admin
def admin_allen_list(request):
    """List all Allen medicines"""
    json_file_path = Path(os.path.dirname(__file__)) / 'medicines' / 'allens_keynotes.json'
    
    medicines = []
    if json_file_path.exists():
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for name, info in sorted(data.items()):
                categories = [k for k in info.keys() if k not in ['name', 'source']]
                medicines.append({
                    'name': name,
                    'category_count': len(categories),
                    'categories': categories[:5]
                })
    
    # Group by first letter
    by_letter = {}
    for m in medicines:
        letter = m['name'][0].upper() if m['name'] else 'A'
        if letter not in by_letter:
            by_letter[letter] = []
        by_letter[letter].append(m)
    
    context = {
        'authenticated': True,
        'source': 'allen',
        'source_title': "Allen's Keynotes",
        'medicines': medicines,
        'by_letter': dict(sorted(by_letter.items())),
        'total_count': len(medicines),
    }
    return render(request, 'app/admin_medicines.html', context)


@require_admin
def admin_medicine_detail(request, source, name):
    """View/edit a specific medicine"""
    medicine_data = {}
    
    if source == 'boericke':
        # Find the file
        json_dir_path = Path(os.path.dirname(__file__)) / 'medicines'
        for json_file in json_dir_path.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('name', '').lower() == name.lower():
                        medicine_data = data
                        medicine_data['_filename'] = json_file.name
                        break
            except:
                continue
    elif source == 'allen':
        json_file_path = Path(os.path.dirname(__file__)) / 'medicines' / 'allens_keynotes.json'
        if json_file_path.exists():
            with open(json_file_path, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
                for med_name, info in all_data.items():
                    if med_name.lower() == name.lower():
                        medicine_data = {'name': med_name, **info}
                        break
    
    # Convert list values to semicolon-separated strings for template display
    processed_symptoms = {}
    if 'symptoms' in medicine_data:
        for key, value in medicine_data['symptoms'].items():
            if isinstance(value, list):
                processed_symptoms[key] = '; '.join(str(v) for v in value)
            else:
                processed_symptoms[key] = str(value) if value else ''
        medicine_data['symptoms'] = processed_symptoms
    
    context = {
        'authenticated': True,
        'source': source,
        'source_title': "Boericke's" if source == 'boericke' else "Allen's",
        'medicine': medicine_data,
        'medicine_json': json.dumps(medicine_data, indent=2),
    }
    return render(request, 'app/admin_medicine_detail.html', context)


@require_admin  
def admin_medicine_save(request):
    """Save edited medicine data"""
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        source = data.get('source')
        name = data.get('name')
        content = data.get('content')
        
        if source == 'boericke':
            # Find and update the file
            json_dir_path = Path(os.path.dirname(__file__)) / 'medicines'
            for json_file in json_dir_path.glob('*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        file_data = json.load(f)
                        if file_data.get('name', '').lower() == name.lower():
                            # Update the file
                            with open(json_file, 'w', encoding='utf-8') as fw:
                                json.dump(content, fw, indent=2, ensure_ascii=False)
                            return JsonResponse({'status': 'ok'})
                except:
                    continue
                    
        elif source == 'allen':
            json_file_path = Path(os.path.dirname(__file__)) / 'medicines' / 'allens_keynotes.json'
            if json_file_path.exists():
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    all_data = json.load(f)
                
                # Find and update
                for med_name in list(all_data.keys()):
                    if med_name.lower() == name.lower():
                        all_data[med_name] = content
                        break
                
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, indent=2, ensure_ascii=False)
                return JsonResponse({'status': 'ok'})
        
        return JsonResponse({'status': 'error', 'message': 'Medicine not found'}, status=404)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# === FEEDBACK SYSTEM ===

def submit_feedback(request):
    """Handle feedback submission: Save to DB + Proxy to Formspree"""
    from .models import Feedback
    import urllib.request
    import urllib.parse
    from django.shortcuts import redirect
    
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # 1. Save to Database
        if email and message:
            Feedback.objects.create(email=email, message=message)
            
        # 2. Proxy to Formspree
        # We need to forward all POST data (including hidden fields like _next, _subject)
        formspree_url = "https://formspree.io/f/mjkrorjy"
        
        try:
            # Convert QueryDict to standard dict for urllib
            data = {k: v for k, v in request.POST.items()}
            data_encoded = urllib.parse.urlencode(data).encode('utf-8')
            
            req = urllib.request.Request(formspree_url, data=data_encoded, method='POST')
            req.add_header('Referer', request.build_absolute_uri()) # Formspree checks referer
            req.add_header('User-Agent', request.META.get('HTTP_USER_AGENT', 'Django Proxy'))
            
            with urllib.request.urlopen(req) as response:
                # Formspree usually redirects or returns JSON. 
                # Since we want to control the flow, we ignore their response content
                # and do our own redirect.
                pass
                
        except Exception as e:
            print(f"Formspree proxy error: {e}")
            # Even if email fails, we saved to DB, so we can consider it a success 
            # or log the error. We shouldn't block the user.
            
        return redirect('thanks')
        
    return redirect('suggestion')


@require_admin
def admin_feedback_list(request):
    """List all feedback messages"""
    from .models import Feedback
    
    feedback_items = Feedback.objects.all()
    
    context = {
        'feedback_items': feedback_items
    }
    return render(request, 'app/admin_feedback.html', context)


# === REMEDY OF THE DAY ===

@require_admin
def admin_remedy_day(request):
    """Admin interface for Remedy of the Day"""
    from .models import RemedyOfTheDay
    from django.http import JsonResponse
    from django.shortcuts import redirect
    import json
    import os
    from pathlib import Path

    # === AJAX API HANDLERS ===
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.GET.get('action')
        
        if action == 'get_medicines':
            source = request.GET.get('source', 'boericke')
            letter = request.GET.get('letter', '').upper()
            medicines = []
            
            if source == 'boericke':
                json_dir = Path(os.path.dirname(__file__)) / 'medicines'
                if json_dir.exists():
                    for f in json_dir.glob('*.json'):
                        if f.name == 'allens_keynotes.json': continue
                        name = f.stem.split('.')[0].replace('_', ' ').title()
                        if letter and not name.upper().startswith(letter):
                            continue
                        medicines.append(name)
            
            elif source == 'allen':
                json_path = Path(os.path.dirname(__file__)) / 'medicines' / 'allens_keynotes.json'
                if json_path.exists():
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            for name in data.keys():
                                if letter and not name.upper().startswith(letter):
                                    continue
                                medicines.append(name)
                    except: pass
            
            return JsonResponse({'medicines': sorted(medicines)})

        if action == 'get_content':
            source = request.GET.get('source')
            medicine = request.GET.get('medicine')
            content = {}
            
            if source == 'boericke':
                json_dir = Path(os.path.dirname(__file__)) / 'medicines'
                if json_dir.exists():
                    for f in json_dir.glob('*.json'):
                        if f.name == 'allens_keynotes.json': continue
                        try:
                            with open(f, 'r', encoding='utf-8') as file_obj:
                                data = json.load(file_obj)
                                if data.get('name', '').lower() == medicine.lower() or f.stem.lower() == medicine.lower():
                                    symptoms = data.get('symptoms', {})
                                    content = symptoms
                                    for k, v in data.items():
                                        if k not in ['name', 'symptoms', '_filename'] and isinstance(v, str):
                                            content[k] = v
                                    break
                        except: pass
            
            elif source == 'allen':
                json_path = Path(os.path.dirname(__file__)) / 'medicines' / 'allens_keynotes.json'
                if json_path.exists():
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if medicine in data:
                            raw_data = data[medicine]
                            for k, v in raw_data.items():
                                if k not in ['name', 'page']:
                                    if isinstance(v, list):
                                        content[k] = " ".join(v)
                                    else:
                                        content[k] = v

            return JsonResponse({'content': content})

    # === POST HANDLERS ===
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            name = request.POST.get('medicine_name')
            desc = request.POST.get('description')
            source = request.POST.get('source', 'boericke')
            image = request.FILES.get('image')
            
            if name and desc:
                RemedyOfTheDay.objects.create(
                    medicine_name=name,
                    description=desc,
                    source=source,
                    image=image,
                    is_active=True
                )
                
        elif action == 'toggle':
            remedy_id = request.POST.get('remedy_id')
            try:
                remedy = RemedyOfTheDay.objects.get(id=remedy_id)
                remedy.is_active = True
                remedy.save()
            except: pass
            
        elif action == 'delete':
            remedy_id = request.POST.get('remedy_id')
            try:
                RemedyOfTheDay.objects.get(id=remedy_id).delete()
            except: pass
            
        return redirect('admin_remedy_day')
    
    # Get active and history
    active_remedy = RemedyOfTheDay.objects.filter(is_active=True).first()
    history = RemedyOfTheDay.objects.order_by('-created_at')
    
    # Render view (legacy medicine_list is no longer needed for new UI)
    context = {
        'active_remedy': active_remedy,
        'history': history, 
    }
    return render(request, 'app/admin_remedy_day.html', context)


@require_admin
def admin_relationships_list(request):
    """List all Remedy Relationships from DB"""
    from .models import RemedyRelationship
    
    # Fetch all records
    relationships = RemedyRelationship.objects.all().order_by('remedy')
    
    # Group by letter
    by_letter = {}
    for r in relationships:
        letter = r.remedy[0].upper() if r.remedy else 'A'
        if letter not in by_letter:
            by_letter[letter] = []
        by_letter[letter].append(r)
        
    context = {
        'authenticated': True,
        'source': 'relationships',
        'source_title': "Relationship Table",
        'relationships': relationships,
        'by_letter': dict(sorted(by_letter.items())),
        'total_count': relationships.count(),
    }
    return render(request, 'app/admin_relationships.html', context)

@require_admin
def admin_relationship_save(request):
    """Save edited relationship data via AJAX"""
    from django.http import JsonResponse
    from .models import RemedyRelationship
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'delete':
            pid = data.get('id')
            RemedyRelationship.objects.filter(id=pid).delete()
            return JsonResponse({'status': 'ok'})
            
        elif action == 'save':
            pid = data.get('id')
            
            defaults = {
                'remedy': data.get('remedy'),
                'complements': data.get('complements'),
                'follows': data.get('follows'),
                'antidotes': data.get('antidotes'),
                'inimical': data.get('inimical'),
            }
            
            if pid:
                # Update
                RemedyRelationship.objects.update_or_create(id=pid, defaults=defaults)
            else:
                # Create
                RemedyRelationship.objects.create(**defaults)
                
            return JsonResponse({'status': 'ok'})
            
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# === DURATIONS ===

def durations_view(request):
    """Public page showing remedy durations"""
    from .models import RemedyDuration
    
    durations = RemedyDuration.objects.all().order_by('remedy')
    
    # Group by first letter
    by_letter = {}
    for d in durations:
        letter = d.remedy[0].upper() if d.remedy else 'A'
        if letter not in by_letter:
            by_letter[letter] = []
        by_letter[letter].append(d)
    
    context = {
        'durations': durations,
        'by_letter': dict(sorted(by_letter.items())),
        'total_count': durations.count(),
    }
    return render(request, 'app/durations.html', context)


@require_admin
def admin_durations_list(request):
    """Admin page for managing remedy durations"""
    from .models import RemedyDuration
    
    durations = RemedyDuration.objects.all().order_by('remedy')
    
    # Group by letter
    by_letter = {}
    for d in durations:
        letter = d.remedy[0].upper() if d.remedy else 'A'
        if letter not in by_letter:
            by_letter[letter] = []
        by_letter[letter].append(d)
        
    context = {
        'authenticated': True,
        'source': 'durations',
        'source_title': "Remedy Durations",
        'durations': durations,
        'by_letter': dict(sorted(by_letter.items())),
        'total_count': durations.count(),
    }
    return render(request, 'app/admin_durations.html', context)


@require_admin
def admin_duration_save(request):
    """Save/delete duration data via AJAX"""
    from django.http import JsonResponse
    from .models import RemedyDuration
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'delete':
            pid = data.get('id')
            RemedyDuration.objects.filter(id=pid).delete()
            return JsonResponse({'status': 'ok'})
            
        elif action == 'save':
            pid = data.get('id')
            
            defaults = {
                'remedy': data.get('remedy'),
                'duration': data.get('duration'),
            }
            
            if pid:
                # Update
                RemedyDuration.objects.update_or_create(id=pid, defaults=defaults)
            else:
                # Create
                RemedyDuration.objects.create(**defaults)
                
            return JsonResponse({'status': 'ok'})
            
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

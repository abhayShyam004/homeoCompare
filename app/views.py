import json
from django.shortcuts import render
from pathlib import Path
import os
from django.conf import settings
from django.http import HttpResponse
import re
import ast


def split_text_to_bullets(text):
    """
    Split Allen's keynotes text into bullet points.
    Handles:
    1. Lists already provided as JSON arrays
    2. String representations of Python lists (e.g., "['item1', 'item2']")
    3. Plain text with multiple sentences separated by periods, semicolons, or newlines
    """
    # If it's already a list, clean and return it
    if isinstance(text, list):
        return [str(item).strip() for item in text if item and str(item).strip()]
    
    # If not a string, return as-is
    if not isinstance(text, str):
        return text
    
    # Strip whitespace
    text = text.strip()
    if not text:
        return text
    
    # Try to parse string representation of Python list (e.g., "['item1', 'item2']")
    if text.startswith('[') and text.endswith(']'):
        try:
            parsed_list = ast.literal_eval(text)
            if isinstance(parsed_list, list):
                return [str(item).strip() for item in parsed_list if item and str(item).strip()]
        except (ValueError, SyntaxError):
            # If parsing fails, continue to text splitting below
            pass
    
    # Split by semicolons first, then by periods followed by uppercase
    final_bullets = []
    
    # Split by semicolons
    parts = [p.strip() for p in text.split(';')]
    
    # Further split parts that contain periods followed by capitals
    for part in parts:
        if '.' in part:
            # Split on periods followed by uppercase letters
            sub_parts = re.split(r'(?<=[.])\s+(?=[A-Z])', part)
            final_bullets.extend([p.strip() for p in sub_parts if p.strip()])
        else:
            if part.strip():
                final_bullets.append(part.strip())
    
    # Capitalize first letter of each bullet if not already done
    final_bullets = [b[0].upper() + b[1:] if b and b[0].isalpha() else b for b in final_bullets]
    
    # Return as array so template recognizes it as list
    return final_bullets if final_bullets else text


def process_allen_remedy_data(data):
    """
    Preprocess all Allen's Keynotes remedy data by applying split_text_to_bullets()
    to all relevant fields. This ensures frontend JavaScript gets processed lists.
    """
    # Fields in Allen's Keynotes that should be converted to bullet points
    bullet_fields = [
        'constitution', 'mental generals', 'physical generals', 'head', 'eyes',
        'vision', 'ears', 'hearing', 'nose', 'face', 'mouth', 'teeth', 'throat',
        'appetite', 'stomach', 'stool', 'abdomen', 'urinary system',
        'gastro-intestinal system', 'upper limbs', 'lower limbs', 'limbs in general',
        'sleep', 'injuries', 'female reproductive system', 'male reproductive system',
        'respiratory system', 'cardio-vascular system', 'neck', 'back', 'extremities',
        'nervous system', 'skin', 'fever', 'modalities', 'relation'
    ]
    
    processed_data = {}
    
    for remedy_name, remedy_info in data.items():
        processed_remedy = dict(remedy_info)  # Shallow copy
        
        # Process each bullet field
        for field in bullet_fields:
            if field in processed_remedy:
                processed_remedy[field] = split_text_to_bullets(processed_remedy[field])
        
        processed_data[remedy_name] = processed_remedy
    
    return processed_data


def remedy_compare(request):
    try:
        # Path to directory containing multiple JSON files
        json_dir_path = Path(os.path.join(
            os.path.dirname(__file__), 'medicines'))

        # Check if directory exists
        if not json_dir_path.exists():
            return HttpResponse("Medicines directory not found", status=404)

        # Load data from all JSON files
        data = {}
        for json_file in json_dir_path.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as file:
                    medicine_data = json.load(file)
                    # Skip if not a dictionary (e.g. relationship data which is a list)
                    if not isinstance(medicine_data, dict):
                        continue
                        
                    medicine_name = medicine_data.get('name', json_file.stem)
                    data[medicine_name] = medicine_data
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                print(f"Error loading {json_file}: {str(e)}")
                continue

        # Extract medicine names
        remedy_names = list(data.keys())

        # Initialize context with default values
        context = {
            'remedy_names': remedy_names,
            'symptoms': {},
            'selected_remedies': [],  # Fixed typo from 'selected_remedies' to match template
            'selected_symptom': '',
            'symptom_options': {
                'description': False,
                'mind': False,
                'head': False,
                'eyes': False,
                'ears': False,
                'nose': False,
                'mouth': False,
                'throat': False,
                'stomach': False,
                'abdomen': False,
                'rectum': False,
                'urinary': False,
                'male': False,
                'female': False,
                'respiratory': False,
                'back': False,
                'extremities': False,
                'sleep': False,
                'fever': False,
                'skin': False,
                'modalities': False,
                'relationship': False,
                'compare': False,
                'dose': False
            }
        }

        if request.method == 'POST':
            selected_remedies = [
                request.POST.get('remedy1'),
                request.POST.get('remedy2'),
                request.POST.get('remedy3'),
                request.POST.get('remedy4')
            ]
            selected_remedies = [r for r in selected_remedies if r]
            # Fixed to match template
            context['selected_remedies'] = selected_remedies

            selected_symptom = request.POST.get('symptom', '').lower()
            context['selected_symptom'] = selected_symptom

            if selected_symptom in context['symptom_options']:
                context['symptom_options'][selected_symptom] = True

            symptoms = {}
            for name in selected_remedies:
                if name in data:
                    symptom_data = data[name].get('symptoms', {})
                    symptoms[name] = {
                        'description': data[name].get('details', ''),
                        'mind': '; '.join(symptom_data.get('Mind', [])) if symptom_data.get('Mind') else '',
                        'head': '; '.join(symptom_data.get('Head', [])) if symptom_data.get('Head') else '',
                        'eyes': '; '.join(symptom_data.get('Eyes', [])) if symptom_data.get('Eyes') else '',
                        'ears': '; '.join(symptom_data.get('Ears', [])) if symptom_data.get('Ears') else '',
                        'nose': '; '.join(symptom_data.get('Nose', [])) if symptom_data.get('Nose') else '',
                        'mouth': '; '.join(symptom_data.get('Mouth', [])) if symptom_data.get('Mouth') else '',
                        'throat': '; '.join(symptom_data.get('Throat', [])) if symptom_data.get('Throat') else '',
                        'stomach': '; '.join(symptom_data.get('Stomach', [])) if symptom_data.get('Stomach') else '',
                        'abdomen': '; '.join(symptom_data.get('Abdomen', [])) if symptom_data.get('Abdomen') else '',
                        'rectum': '; '.join(symptom_data.get('Rectum', [])) if symptom_data.get('Rectum') else '',
                        'urinary': '; '.join(symptom_data.get('Urine', [])) if symptom_data.get('Urine') else '',
                        'male': '; '.join(symptom_data.get('Male', [])) if symptom_data.get('Male') else '',
                        'female': '; '.join(symptom_data.get('Female', [])) if symptom_data.get('Female') else '',
                        'respiratory': '; '.join(symptom_data.get('Respiratory', [])) if symptom_data.get('Respiratory') else '',
                        'back': '; '.join(symptom_data.get('Back', [])) if symptom_data.get('Back') else '',
                        'extremities': '; '.join(symptom_data.get('Extremities', [])) if symptom_data.get('Extremities') else '',
                        'sleep': '; '.join(symptom_data.get('Sleep', [])) if symptom_data.get('Sleep') else '',
                        'fever': '; '.join(symptom_data.get('Fever', [])) if symptom_data.get('Fever') else '',
                        'skin': '; '.join(symptom_data.get('Skin', [])) if symptom_data.get('Skin') else '',
                        'modalities': '; '.join(data[name].get('Modalities', [])) if data[name].get('Modalities') else '',
                        'relationship': data[name].get('Relationship', ''),
                        'compare': '',
                        'dose': data[name].get('dosage', '')
                    }
            context['symptoms'] = symptoms
            
            # Track search
            from .models import SearchQuery
            try:
                SearchQuery.objects.create(
                    remedies=selected_remedies,
                    category=selected_symptom,
                    source='boericke'
                )
            except: pass

        # Track page view
        from .models import PageView
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            PageView.objects.create(page='boericke', ip_address=ip, user_agent=request.META.get('HTTP_USER_AGENT', '')[:500])
        except: pass

        return render(request, 'app/base.html', context)

    except Exception as e:
        print(f"Error in remedy_compare: {str(e)}")
        return HttpResponse("An error occurred", status=500)


def allen_compare(request):
    # json_file_path = Path(settings.BASE_DIR, 'medicines',
    #                       'allens_keynotes.json')

    json_file_path = Path(os.path.dirname(__file__)) / \
        'medicines' / 'allens_keynotes.json'
    print(f"Looking for JSON at: {json_file_path}")

    if not json_file_path.exists():
        raise FileNotFoundError(f"JSON file not found at: {json_file_path}")

    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    remedy_names = list(data.keys())
    
    # Preprocess all remedy data to apply bullet point splitting
    processed_data = process_allen_remedy_data(data)

    context = {
        'remedy_names': remedy_names,
        'remedy_data': processed_data,  # Pass processed data with bullet points
        'symptoms': {},
        'selected_remedies': [],
        'selected_symptom': '',
        'symptom_options': {
            'constitution': False,
            'mental_generals': False,
            'physical_generals': False,
            'head': False,
            'eyes': False,
            'vision': False,
            'ears': False,
            'hearing': False,
            'nose': False,
            'face': False,
            'mouth': False,
            'teeth': False,
            'throat': False,
            'appetite': False,
            'stomach': False,
            'stool': False,
            'abdomen': False,
            'urinary_system': False,
            'gastro_intestinal_system': False,
            'upper_limbs': False,
            'lower_limbs': False,
            'limbs_in_general': False,
            'sleep': False,
            'injuries': False,
            'female_reproductive_system': False,
            'male_reproductive_system': False,
            'respiratory_system': False,
            'cardio_vascular_system': False,
            'neck': False,
            'back': False,
            'extremities': False,
            'nervous_system': False,
            'skin': False,
            'fever': False,
            'modalities': False,
            'relation': False
        }
    }

    if request.method == 'POST':
        selected_remedies = [
            request.POST.get('remedy1'),
            request.POST.get('remedy2'),
            request.POST.get('remedy3'),
            request.POST.get('remedy4')
        ]
        selected_remedies = [r for r in selected_remedies if r]
        context['selected_remedies'] = selected_remedies

        context['remedy1'] = request.POST.get('remedy1', '')
        context['remedy2'] = request.POST.get('remedy2', '')
        context['remedy3'] = request.POST.get('remedy3', '')
        context['remedy4'] = request.POST.get('remedy4', '')
        context['raw_symptom'] = request.POST.get('symptom', '')

        selected_symptom = request.POST.get(
            'symptom', '').lower().replace(' ', '_')
        context['selected_symptom'] = selected_symptom

        if selected_symptom in context['symptom_options']:
            context['symptom_options'][selected_symptom] = True

        symptoms = {}
        for name in selected_remedies:
            if name in data:
                remedy_info = data[name]
                symptoms[name] = {
                    'constitution': split_text_to_bullets(remedy_info.get('constitution', '')),
                    'mental_generals': split_text_to_bullets(remedy_info.get('mental generals', '')),
                    'physical_generals': split_text_to_bullets(remedy_info.get('physical generals', '')),
                    'head': split_text_to_bullets(remedy_info.get('head', '')),
                    'eyes': split_text_to_bullets(remedy_info.get('eyes', '')),
                    'vision': split_text_to_bullets(remedy_info.get('vision', '')),
                    'ears': split_text_to_bullets(remedy_info.get('ears', '')),
                    'hearing': split_text_to_bullets(remedy_info.get('hearing', '')),
                    'nose': split_text_to_bullets(remedy_info.get('nose', '')),
                    'face': split_text_to_bullets(remedy_info.get('face', '')),
                    'mouth': split_text_to_bullets(remedy_info.get('mouth', '')),
                    'teeth': split_text_to_bullets(remedy_info.get('teeth', '')),
                    'throat': split_text_to_bullets(remedy_info.get('throat', '')),
                    'appetite': split_text_to_bullets(remedy_info.get('appetite', '')),
                    'stomach': split_text_to_bullets(remedy_info.get('stomach', '')),
                    'stool': split_text_to_bullets(remedy_info.get('stool', '')),
                    'abdomen': split_text_to_bullets(remedy_info.get('abdomen', '')),
                    'urinary_system': split_text_to_bullets(remedy_info.get('urinary system', '')),
                    'gastro_intestinal_system': split_text_to_bullets(remedy_info.get('gastro-intestinal system', '')),
                    'upper_limbs': split_text_to_bullets(remedy_info.get('upper limbs', '')),
                    'lower_limbs': split_text_to_bullets(remedy_info.get('lower limbs', '')),
                    'limbs_in_general': split_text_to_bullets(remedy_info.get('limbs in general', '')),
                    'sleep': split_text_to_bullets(remedy_info.get('sleep', '')),
                    'injuries': split_text_to_bullets(remedy_info.get('injuries', '')),
                    'female_reproductive_system': split_text_to_bullets(remedy_info.get('female reproductive system', '')),
                    'male_reproductive_system': split_text_to_bullets(remedy_info.get('male reproductive system', '')),
                    'respiratory_system': split_text_to_bullets(remedy_info.get('respiratory system', '')),
                    'cardio_vascular_system': split_text_to_bullets(remedy_info.get('cardio-vascular system', '')),
                    'neck': split_text_to_bullets(remedy_info.get('neck', '')),
                    'back': split_text_to_bullets(remedy_info.get('back', '')),
                    'extremities': split_text_to_bullets(remedy_info.get('extremities', '')),
                    'nervous_system': split_text_to_bullets(remedy_info.get('nervous system', '')),
                    'skin': split_text_to_bullets(remedy_info.get('skin', '')),
                    'fever': split_text_to_bullets(remedy_info.get('fever', '')),
                    'modalities': split_text_to_bullets(remedy_info.get('modalities', '')),
                    'relation': split_text_to_bullets(remedy_info.get('relation', ''))
                }
        context['symptoms'] = symptoms

    # Track page view
    from .models import PageView
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        PageView.objects.create(page='allen', ip_address=ip, user_agent=request.META.get('HTTP_USER_AGENT', '')[:500])
    except: pass

    return render(request, 'app/allen.html', context)


def home(request):
    # Track page view
    from .models import PageView
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        PageView.objects.create(page='home', ip_address=ip, user_agent=request.META.get('HTTP_USER_AGENT', '')[:500])
    except: pass
    # Get Remedy of the Day
    from .models import RemedyOfTheDay
    remedy_of_day = RemedyOfTheDay.objects.filter(is_active=True).first()
    
    return render(request, 'landing.html', {'remedy_of_day': remedy_of_day})


def about(request):
    return render(request, 'app/about.html')


def saved_remedies(request):
    # Track page view
    from .models import PageView
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        PageView.objects.create(page='saved_remedies', ip_address=ip, user_agent=request.META.get('HTTP_USER_AGENT', '')[:500])
    except: pass
    return render(request, 'app/saved_remedies.html')


def relationships_view(request):
    from .models import RemedyRelationship
    
    # Query database instead of reading JSON
    relationships = RemedyRelationship.objects.all().order_by('remedy')
    
    # Convert queryset to list of dicts for the grouping logic
    data = []
    for r in relationships:
        data.append({
            'remedy': r.remedy,
            'complements': r.complements,
            'follows': r.follows,
            'antidotes': r.antidotes,
            'inimical': r.inimical
        })

    # Group data alphabetically for the view (simulating multiple tables)
    sorted_data = sorted(data, key=lambda x: x['remedy'])
    groups = {
        'A-C': [],
        'D-K': [],
        'L-P': [],
        'R-S': [],
        'T-Z': []
    }
    
    for item in sorted_data:
        first_char = item['remedy'][0].upper()
        if first_char <= 'C': groups['A-C'].append(item)
        elif first_char <= 'K': groups['D-K'].append(item)
        elif first_char <= 'P': groups['L-P'].append(item)
        elif first_char <= 'S': groups['R-S'].append(item)
        else: groups['T-Z'].append(item)
        
    # Filter out empty groups
    active_groups = {k: v for k, v in groups.items() if v}
    
    return render(request, 'app/relationships.html', {'grouped_relationships': active_groups})


def suggestion(request):
    return render(request, 'app/suggestions.html')


def thanks(request):
    return render(request, 'app/thanks.html')


def privacy(request):
    return render(request, 'app/privacy.html')


def remedy_history(request, remedy_id=None):
    from .models import RemedyOfTheDay, PageView
    
    # Track page view
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        PageView.objects.create(page='remedy_history', ip_address=ip, user_agent=request.META.get('HTTP_USER_AGENT', '')[:500])
    except: pass

    # Get all remedies ordered by newest first
    history_list = RemedyOfTheDay.objects.all().order_by('-created_at')
    
    selected_remedy = None
    if remedy_id:
        selected_remedy = history_list.filter(id=remedy_id).first()
    
    # If no specific ID or not found, show the latest active one, or just the first in list
    if not selected_remedy:
        selected_remedy = history_list.filter(is_active=True).first()
        if not selected_remedy and history_list.exists():
            selected_remedy = history_list.first()
            
    context = {
        'history_list': history_list,
        'selected_remedy': selected_remedy
    }
    return render(request, 'app/remedy_history.html', context)


# === ADMIN PANEL ===

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime
from .models import PageView, SearchQuery

# JWT Authentication helpers
def get_admin_credentials():
    """Load admin credentials from .env file"""
    import os
    from dotenv import load_dotenv
    env_path = Path(os.path.dirname(__file__)).parent / '.env'
    load_dotenv(env_path, override=True)
    return {
        'username': os.environ.get('ADMIN_USERNAME', ''),
        'password_hash': os.environ.get('ADMIN_PASSWORD_HASH', ''),
        'jwt_secret': os.environ.get('JWT_SECRET', 'fallback-secret-change-this')
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


def track_page_view(request, page_name):
    """Track a page view"""
    try:
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        PageView.objects.create(
            page=page_name,
            ip_address=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
    except Exception as e:
        print(f"Error tracking page view: {e}")


def track_search(remedies, category, source='boericke'):
    """Track a search query"""
    try:
        SearchQuery.objects.create(
            remedies=remedies,
            category=category,
            source=source
        )
    except Exception as e:
        print(f"Error tracking search: {e}")


def admin_panel(request):
    """Admin panel with secure JWT login and analytics dashboard"""
    error = None
    
    # Check if already logged in via JWT cookie
    authenticated = is_admin_authenticated(request)
    
    # Handle login
    if request.method == 'POST' and not authenticated:
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        creds = get_admin_credentials()
        
        # Verify credentials
        if username == creds['username'] and verify_password(password, creds['password_hash']):
            # Create JWT token
            token = create_jwt_token(username)
            
            # Post-login redirect to avoid form resubmission and ensure cookie is set
            from django.shortcuts import redirect
            response = redirect('admin_panel')
            response.set_cookie(
                'admin_token',
                token,
                httponly=True,
                secure=request.is_secure(),
                samesite='Lax',  # Changed to Lax to be more permissive with navigation
                max_age=60 * 60 * 24  # 24 hours
            )
            return response
            
        else:
            error = 'Invalid username or password'
    
    # If not authenticated, show login form
    if not authenticated:
        return render(request, 'app/admin_panel.html', {'authenticated': False, 'error': error})
    
    import json
    from collections import Counter
    
    # Get time periods
    now = timezone.now()
    today = now.date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    ninety_days_ago = today - timedelta(days=90)
    year_start = today.replace(month=1, day=1)
    
    # Visitor stats (unique visitors by IP)
    visits_today = PageView.objects.filter(timestamp__date=today).values('ip_address').distinct().count()
    visits_week = PageView.objects.filter(timestamp__date__gte=week_ago).values('ip_address').distinct().count()
    visits_month = PageView.objects.filter(timestamp__date__gte=month_ago).values('ip_address').distinct().count()
    visits_90days = PageView.objects.filter(timestamp__date__gte=ninety_days_ago).values('ip_address').distinct().count()
    visits_year = PageView.objects.filter(timestamp__date__gte=year_start).values('ip_address').distinct().count()
    
    # Popular remedies
    all_remedies = []
    for sq in SearchQuery.objects.all()[:1000]:
        all_remedies.extend(sq.remedies)
    popular_remedies = Counter(all_remedies).most_common(10)
    
    # Popular categories
    popular_categories = SearchQuery.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Chart data for 7 days
    def get_chart_data(days):
        start_date = today - timedelta(days=days-1)
        daily = PageView.objects.filter(
            timestamp__date__gte=start_date
        ).annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            count=Count('ip_address', distinct=True)
        ).order_by('date')
        
        # Create dict for easy lookup
        daily_dict = {d['date']: d['count'] for d in daily}
        
        # Fill in all days
        labels = []
        values = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            labels.append(d.strftime('%b %d'))
            values.append(daily_dict.get(d, 0))
        
        return labels, values
    
    labels_7, values_7 = get_chart_data(7)
    labels_30, values_30 = get_chart_data(30)
    labels_90, values_90 = get_chart_data(90)
    
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
    }
    
    return render(request, 'app/admin_panel.html', context)


def admin_logout(request):
    """Logout from admin panel - clear JWT cookie"""
    from django.shortcuts import redirect
    response = redirect('admin_panel')
    response.delete_cookie('admin_token')
    return response


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


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

def require_admin(view_func):
    """Decorator to require admin JWT authentication"""
    def wrapper(request, *args, **kwargs):
        if not is_admin_authenticated(request):
            from django.shortcuts import redirect
            return redirect('admin_panel')
        return view_func(request, *args, **kwargs)
    return wrapper


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

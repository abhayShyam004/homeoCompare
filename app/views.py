import json
from django.shortcuts import render
from pathlib import Path
import os
from django.conf import settings
from django.http import HttpResponse


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

    context = {
        'remedy_names': remedy_names,
        'remedy_data': data,  # Pass the full data for client-side use
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
                    'constitution': remedy_info.get('constitution', ''),
                    'mental_generals': remedy_info.get('mental generals', ''),
                    'physical_generals': remedy_info.get('physical generals', ''),
                    'head': remedy_info.get('head', ''),
                    'eyes': remedy_info.get('eyes', ''),
                    'vision': remedy_info.get('vision', ''),
                    'ears': remedy_info.get('ears', ''),
                    'hearing': remedy_info.get('hearing', ''),
                    'nose': remedy_info.get('nose', ''),
                    'face': remedy_info.get('face', ''),
                    'mouth': remedy_info.get('mouth', ''),
                    'teeth': remedy_info.get('teeth', ''),
                    'throat': remedy_info.get('throat', ''),
                    'appetite': remedy_info.get('appetite', ''),
                    'stomach': remedy_info.get('stomach', ''),
                    'stool': remedy_info.get('stool', ''),
                    'abdomen': remedy_info.get('abdomen', ''),
                    'urinary_system': remedy_info.get('urinary system', ''),
                    'gastro_intestinal_system': remedy_info.get('gastro-intestinal system', ''),
                    'upper_limbs': remedy_info.get('upper limbs', ''),
                    'lower_limbs': remedy_info.get('lower limbs', ''),
                    'limbs_in_general': remedy_info.get('limbs in general', ''),
                    'sleep': remedy_info.get('sleep', ''),
                    'injuries': remedy_info.get('injuries', ''),
                    'female_reproductive_system': remedy_info.get('female reproductive system', ''),
                    'male_reproductive_system': remedy_info.get('male reproductive system', ''),
                    'respiratory_system': remedy_info.get('respiratory system', ''),
                    'cardio_vascular_system': remedy_info.get('cardio-vascular system', ''),
                    'neck': remedy_info.get('neck', ''),
                    'back': remedy_info.get('back', ''),
                    'extremities': remedy_info.get('extremities', ''),
                    'nervous_system': remedy_info.get('nervous system', ''),
                    'skin': remedy_info.get('skin', ''),
                    'fever': remedy_info.get('fever', ''),
                    'modalities': remedy_info.get('modalities', ''),
                    'relation': remedy_info.get('relation', '')
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
    return render(request, 'landing.html')


def about(request):
    return render(request, 'app/about.html')


def suggestion(request):
    return render(request, 'app/suggestions.html')


def thanks(request):
    return render(request, 'app/thanks.html')


def privacy(request):
    return render(request, 'app/privacy.html')


# === ADMIN PANEL ===

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from .models import PageView, SearchQuery

ADMIN_PASSWORD = 'admin@homeocompare'


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
    """Admin panel with login and analytics dashboard"""
    error = None
    
    # Check if already logged in
    is_authenticated = request.session.get('admin_authenticated', False)
    
    # Handle login
    if request.method == 'POST' and not is_authenticated:
        password = request.POST.get('password', '')
        if password == ADMIN_PASSWORD:
            request.session['admin_authenticated'] = True
            is_authenticated = True
        else:
            error = 'Invalid password'
    
    # If not authenticated, show login form
    if not is_authenticated:
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
    
    # Visitor stats (total page views, not individual pages)
    visits_today = PageView.objects.filter(timestamp__date=today).count()
    visits_week = PageView.objects.filter(timestamp__date__gte=week_ago).count()
    visits_month = PageView.objects.filter(timestamp__date__gte=month_ago).count()
    visits_90days = PageView.objects.filter(timestamp__date__gte=ninety_days_ago).count()
    visits_year = PageView.objects.filter(timestamp__date__gte=year_start).count()
    
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
            count=Count('id')
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
    """Logout from admin panel"""
    request.session['admin_authenticated'] = False
    from django.shortcuts import redirect
    return redirect('admin_panel')


def track_search_api(request):
    """API endpoint for tracking searches from JavaScript"""
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    import json
    
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

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from pathlib import Path
import os
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime
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
    if not remedy_of_day:
        remedy_of_day = RemedyOfTheDay.objects.order_by('-created_at').first()
    
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
        'history': history_list,
        'history_list': history_list,
        'selected_remedy': selected_remedy
    }
    return render(request, 'app/remedy_history.html', context)


# === ADMIN PANEL ===

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime
from .models import PageView, SearchQuery, CasePaperUser, AccessPlatformSettings



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



# Re-export custom admin panel views for backwards compatibility with URLs
from .admin_views import *

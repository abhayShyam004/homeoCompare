# Case Paper Views - Premium Feature
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.conf import settings
from datetime import datetime
import json
from django.utils import timezone
from .models import CasePaper, CasePaperUser

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None


def get_ist_now():
    """Return India Standard Time datetime for dashboard status."""
    try:
        if ZoneInfo is not None:
            return datetime.now(ZoneInfo('Asia/Kolkata'))
    except Exception:
        pass

    try:
        import pytz
        return datetime.now(pytz.timezone('Asia/Kolkata'))
    except Exception:
        return timezone.localtime(timezone.now())


# ============= AUTHENTICATION HELPERS =============

def get_case_paper_user(request):
    """Get the current case paper user from session, or None if not logged in"""
    # Check both new auth system (user_id) and old system (case_paper_user_id)
    user_id = request.session.get('user_id') or request.session.get('case_paper_user_id')
    if user_id:
        try:
            return CasePaperUser.objects.get(id=user_id)
        except CasePaperUser.DoesNotExist:
            # Clear invalid session
            if 'user_id' in request.session:
                del request.session['user_id']
            if 'case_paper_user_id' in request.session:
                del request.session['case_paper_user_id']
    return None


def require_case_paper_login(view_func):
    """Decorator to require case paper login"""
    def wrapper(request, *args, **kwargs):
        user = get_case_paper_user(request)
        if not user:
            return redirect('login')  # Redirect to new auth system
        return view_func(request, *args, **kwargs)
    return wrapper


# ============= HELPER FUNCTIONS =============

def _save_form_data_to_case(request, case):
    """Extract form POST data and save to case paper sections"""
    post_data = request.POST
    
    # Section 1: Preliminary Data
    case.preliminary = {
        'physician_name': post_data.get('physician_name', ''),
        'consultation_date': post_data.get('consultation_date', ''),
        'consultation_time': post_data.get('consultation_time', ''),
        'patient_name': post_data.get('patient_name', ''),
        'age': post_data.get('age', ''),
        'sex': post_data.get('sex', ''),
        'occupation': post_data.get('occupation', ''),
        'contact_number': post_data.get('contact_number', ''),
        'email': post_data.get('email', ''),
        'address': post_data.get('address', ''),
        'remarks': post_data.get('preliminary_remarks', ''),
    }
    
    # Section 4: History
    case.history = {
        'hpi': post_data.get('hpi', ''),
        'past_medical_history': post_data.get('past_medical_history', ''),
        'family_history': post_data.get('family_history', ''),
    }
    
    # Section 5: Generals
    case.generals = {
        'appetite': post_data.get('appetite', ''),
        'thirst': post_data.get('thirst', ''),
        'digestion': post_data.get('digestion', ''),
        'mental_state': post_data.get('mental_state', ''),
        'build_complexion': post_data.get('build_complexion', ''),
        'sleep_pattern': post_data.get('sleep_pattern', ''),
    }
    
    # Section 6: Examination
    case.clinical = {
        'bp': post_data.get('bp', ''),
        'pulse': post_data.get('pulse', ''),
        'temperature': post_data.get('temperature', ''),
        'physical_examination': post_data.get('physical_examination', ''),
        'investigations': post_data.get('investigations', ''),
    }
    
    # Section 7: Diagnosis
    case.analysis = {
        'provisional_diagnosis': post_data.get('provisional_diagnosis', ''),
        'miasmatic': post_data.get('miasmatic', ''),
        'rubrics': post_data.get('rubrics', ''),
        'differential_medicines': post_data.get('differential_medicines', ''),
    }
    
    # Section 8: Prescription
    case.prescription = {
        'remedy_potency': post_data.get('remedy_potency', ''),
        'dosage': post_data.get('dosage', ''),
        'duration': post_data.get('duration', ''),
        'lifestyle_advice': post_data.get('lifestyle_advice', ''),
    }
    
    # Section 10: Summary
    case.notes = post_data.get('executive_summary', '')


def case_paper_login(request):
    """Legacy login - redirects to new email login"""
    return redirect('login')


def case_paper_logout(request):
    """Logout: Clear session"""
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'case_paper_user_id' in request.session:
        del request.session['case_paper_user_id']
    if 'user_email' in request.session:
        del request.session['user_email']
    request.session.modified = True
    return redirect('login')


# ============= CASE PAPER VIEWS =============

@require_case_paper_login
def case_paper_dashboard(request):
    """Dashboard: List all case papers with search and filter for logged-in user"""
    user = get_case_paper_user(request)
    
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    # Filter cases by current user only
    cases = CasePaper.objects.filter(user=user)
    
    if search_query:
        cases = cases.filter(
            Q(case_id__icontains=search_query) |
            Q(preliminary__patient_name__icontains=search_query)
        )
    
    if status_filter in ['draft', 'complete']:
        cases = cases.filter(status=status_filter)
    
    context = {
        'cases': cases,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_count': CasePaper.objects.filter(user=user).count(),
        'draft_count': CasePaper.objects.filter(user=user, status='draft').count(),
        'complete_count': CasePaper.objects.filter(user=user, status='complete').count(),
        'page_title': 'Dashboard',
        'last_sync': get_ist_now().strftime('%Y-%m-%d %H:%M:%S IST'),
        'user': user,
    }
    
    return render(request, 'case_paper/dashboard.html', context)


@require_case_paper_login
def case_paper_cases(request):
    user = get_case_paper_user(request)
    search_query = request.GET.get('search', '').strip()
    cases = CasePaper.objects.filter(user=user)
    if search_query:
        cases = cases.filter(
            Q(case_id__icontains=search_query) |
            Q(preliminary__patient_name__icontains=search_query) |
            Q(status__icontains=search_query)
        )
    context = {
        'user': user,
        'cases': cases,
        'page_title': 'Cases',
        'search_query': search_query,
        'total_count': CasePaper.objects.filter(user=user).count(),
        'draft_count': CasePaper.objects.filter(user=user, status='draft').count(),
        'complete_count': CasePaper.objects.filter(user=user, status='complete').count(),
        'last_sync': get_ist_now().strftime('%Y-%m-%d %H:%M:%S IST'),
    }
    return render(request, 'case_paper/cases.html', context)


@require_case_paper_login
def case_paper_patients(request):
    user = get_case_paper_user(request)
    search_query = request.GET.get('search', '').strip()
    cases = CasePaper.objects.filter(user=user)
    # Build patient details: name, age, sex, contact, total_cases
    patient_map = {}
    for case in cases:
        prelim = case.preliminary if isinstance(case.preliminary, dict) else {}
        name = prelim.get('patient_name', 'Unknown')
        if not name:
            name = 'Unknown'
        if name not in patient_map:
            patient_map[name] = {
                'name': name,
                'age': prelim.get('age', ''),
                'sex': prelim.get('sex', ''),
                'contact': prelim.get('contact_number', ''),
                'total_cases': 1,
            }
        else:
            patient_map[name]['total_cases'] += 1
    patients = list(patient_map.values())
    if search_query:
        patients = [p for p in patients if search_query.lower() in p['name'].lower()]
    context = {
        'user': user,
        'patients': patients,
        'page_title': 'Patients',
        'search_query': search_query,
        'total_patients': len(patients),
        'total_cases': cases.count(),
        'draft_count': cases.filter(status='draft').count(),
        'last_sync': get_ist_now().strftime('%Y-%m-%d %H:%M:%S IST'),
    }
    return render(request, 'case_paper/patients.html', context)


@require_case_paper_login
def case_paper_calendar(request):
    user = get_case_paper_user(request)
    context = {
        'user': user,
        'page_title': 'Calendar',
        'last_sync': get_ist_now().strftime('%Y-%m-%d %H:%M:%S IST'),
    }
    return render(request, 'case_paper/calendar.html', context)


@require_case_paper_login
def case_paper_settings(request):
    user = get_case_paper_user(request)
    context = {
        'user': user,
        'page_title': 'Settings',
        'last_sync': get_ist_now().strftime('%Y-%m-%d %H:%M:%S IST'),
    }
    return render(request, 'case_paper/settings.html', context)


@require_case_paper_login
def case_paper_new(request):
    """Create new case paper for logged-in user"""
    user = get_case_paper_user(request)
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        action = request.POST.get('action', 'save_draft')
        
        # Create new case for current user
        case = CasePaper(user=user)
        
        # Save form data to case paper sections
        _save_form_data_to_case(request, case)
        
        # Set status based on action
        if action == 'mark_complete':
            case.status = 'complete'
        else:
            case.status = 'draft'
        
        case.save()
        
        # Redirect to case dashboard
        return redirect('case_paper_dashboard')
    
    # GET request - show form
    context = {
        'mode': 'new',
        'case': None,
        'user': user,
        'page_title': 'New Case Paper',
    }
    return render(request, 'case_paper/form.html', context)


@require_case_paper_login
def case_paper_form(request, case_id=None):
    """Edit existing case paper for logged-in user"""
    user = get_case_paper_user(request)
    case = None
    mode = 'new'
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        action = request.POST.get('action', 'save_draft')
        
        # Get or create case
        if case_id:
            case = get_object_or_404(CasePaper, case_id=case_id)
            # Ensure user owns this case
            if case.user != user:
                return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
        else:
            case = CasePaper(user=user)
        
        # Save form data to case paper sections
        _save_form_data_to_case(request, case)
        
        # Set status based on action
        if action == 'mark_complete':
            case.status = 'complete'
        else:
            case.status = 'draft'
        
        case.save()
        
        # Redirect to case dashboard
        return redirect('case_paper_dashboard')
    
    # GET request - show form
    if case_id:
        case = get_object_or_404(CasePaper, case_id=case_id)
        # Ensure user owns this case
        if case.user != user:
            return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
        mode = 'edit'
    
    context = {
        'mode': mode,
        'case': case,
        'case_id': case_id,
        'user': user,
        'page_title': 'Edit Case Paper' if mode == 'edit' else 'New Case Paper',
    }
    
    return render(request, 'case_paper/form.html', context)


@require_case_paper_login
def case_paper_view(request, case_id):
    """View case paper (read-only mode) for logged-in user"""
    user = get_case_paper_user(request)
    case = get_object_or_404(CasePaper, case_id=case_id)
    
    # Ensure user owns this case
    if case.user != user:
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    context = {
        'case': case,
        'mode': 'view',
        'user': user,
        'page_title': 'View Case Paper',
    }
    
    return render(request, 'case_paper/view.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def case_paper_save(request):
    """AJAX endpoint to save/update case paper (user-specific)"""
    try:
        # Check authentication
        user = get_case_paper_user(request)
        if not user:
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
        
        data = json.loads(request.body)
        case_id = data.get('case_id')
        section = data.get('section')  # Which section is being saved
        content = data.get('content', {})
        status = data.get('status', 'draft')
        
        # Get or create case
        if case_id:
            case = CasePaper.objects.get(case_id=case_id)
            # Verify user owns this case
            if case.user != user:
                return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
        else:
            # Create new case for current user
            case = CasePaper(user=user)
        
        # Update the appropriate section
        section_mapping = {
            'preliminary': 'preliminary',
            'chief_complaints': 'chief_complaints',
            'associated_complaints': 'associated_complaints',
            'history': 'history',
            'generals': 'generals',
            'clinical': 'clinical',
            'analysis': 'analysis',
            'prescription': 'prescription',
            'followup': 'followup',
            'notes': 'notes',
        }
        
        if section in section_mapping:
            field_name = section_mapping[section]
            setattr(case, field_name, content)
        
        case.status = status
        case.save()
        
        return JsonResponse({
            'status': 'ok',
            'case_id': case.case_id,
            'message': f'{section} saved successfully'
        })
    
    except CasePaper.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Case not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def case_paper_full_save(request):
    """AJAX endpoint to save entire case paper at once (user-specific)"""
    try:
        # Check authentication
        user = get_case_paper_user(request)
        if not user:
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
        
        data = json.loads(request.body)
        case_id = data.get('case_id')
        
        # Get or create case
        if case_id:
            case = CasePaper.objects.get(case_id=case_id)
            # Verify user owns this case
            if case.user != user:
                return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
        else:
            case = CasePaper(user=user)
        
        # Update all sections
        case.preliminary = data.get('preliminary', {})
        case.chief_complaints = data.get('chief_complaints', [])
        case.associated_complaints = data.get('associated_complaints', [])
        case.history = data.get('history', {})
        case.generals = data.get('generals', {})
        case.clinical = data.get('clinical', {})
        case.analysis = data.get('analysis', {})
        case.prescription = data.get('prescription', {})
        case.followup = data.get('followup', [])
        case.notes = data.get('notes', '')
        case.status = data.get('status', 'draft')
        case.save()
        
        return JsonResponse({
            'status': 'ok',
            'case_id': case.case_id,
            'message': 'Case saved successfully'
        })
    
    except CasePaper.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Case not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def case_paper_delete(request):
    """AJAX endpoint to delete case paper (user-specific)"""
    try:
        # Check authentication
        user = get_case_paper_user(request)
        if not user:
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
        
        data = json.loads(request.body)
        case_id = data.get('case_id')
        
        case = CasePaper.objects.get(case_id=case_id)
        # Verify user owns this case
        if case.user != user:
            return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
        
        case.delete()
        
        return JsonResponse({'status': 'ok', 'message': 'Case deleted successfully'})
    
    except CasePaper.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Case not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def case_paper_get_data(request, case_id):
    """Get case paper data as JSON (for AJAX loading, user-specific)"""
    try:
        # Check authentication
        user = get_case_paper_user(request)
        if not user:
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
        
        case = CasePaper.objects.get(case_id=case_id)
        # Verify user owns this case
        if case.user != user:
            return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
        
        data = {
            'case_id': case.case_id,
            'status': case.status,
            'created_at': case.created_at.isoformat(),
            'updated_at': case.updated_at.isoformat(),
            'preliminary': case.preliminary,
            'chief_complaints': case.chief_complaints,
            'associated_complaints': case.associated_complaints,
            'history': case.history,
            'generals': case.generals,
            'clinical': case.clinical,
            'analysis': case.analysis,
            'prescription': case.prescription,
            'followup': case.followup,
            'notes': case.notes,
        }
        
        return JsonResponse(data)
    
    except CasePaper.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Case not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

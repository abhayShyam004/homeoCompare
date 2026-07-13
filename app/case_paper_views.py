# Case Paper Core Views (Case Taking Form, CRUD, AJAX APIs, PDF Export)
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import json

from .models import CasePaper, CasePaperUser
from .case_paper_helpers import *
from .clinic_management_views import *


def _save_form_data_to_case(request, case):
    """Extract form POST data and save to case paper sections (20 sections)"""
    post_data = request.POST
    
    # Section 1: Preliminary Data (Patient Profile)
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
        'marital_status': post_data.get('marital_status', ''),
        'religion': post_data.get('religion', ''),
        'socioeconomic_status': post_data.get('socioeconomic_status', ''),
    }
    
    # Section 2: Chief Complaints (CC) - Handled as a list of dicts in JS usually, 
    # but here we'll capture from flattened fields or structured JSON if available.
    # For a standard form submission, we'll try to reconstruct or use a single blob if complex.
    # Logic for dynamic rows (reconstructing from lists):
    cc_names = post_data.getlist('cc_name[]')
    cc_durations = post_data.getlist('cc_duration[]')
    cc_locations = post_data.getlist('cc_location[]')
    cc_sensations = post_data.getlist('cc_sensation[]')
    cc_modalities = post_data.getlist('cc_modality[]')
    cc_concomitants = post_data.getlist('cc_concomitant[]')
    cc_intensities = post_data.getlist('cc_intensity[]')
    
    case.chief_complaints = []
    for i in range(len(cc_names)):
        if cc_names[i]:
            case.chief_complaints.append({
                'name': cc_names[i],
                'duration': cc_durations[i] if i < len(cc_durations) else '',
                'location': cc_locations[i] if i < len(cc_locations) else '',
                'sensation': cc_sensations[i] if i < len(cc_sensations) else '',
                'modality': cc_modalities[i] if i < len(cc_modalities) else '',
                'concomitant': cc_concomitants[i] if i < len(cc_concomitants) else '',
                'intensity': cc_intensities[i] if i < len(cc_intensities) else '',
            })

    # Section 3: Associated Complaints
    ac_names = post_data.getlist('ac_name[]')
    ac_chars = post_data.getlist('ac_char[]')
    case.associated_complaints = []
    for i in range(len(ac_names)):
        if ac_names[i]:
            case.associated_complaints.append({
                'name': ac_names[i],
                'characteristics': ac_chars[i] if i < len(ac_chars) else '',
            })
    
    # Section 4: History of Presenting Illness (HPI)
    case.history = {
        'hpi': {
            'onset': post_data.get('hpi_onset', ''),
            'duration': post_data.get('hpi_duration', ''),
            'progress': post_data.get('hpi_progress', ''),
            'causative_factors': post_data.get('hpi_causative', ''),
            'sequence': post_data.get('hpi_sequence', ''),
            'previous_treatments': post_data.get('hpi_treatments', ''),
        },
        # Section 5: Past History
        'past_history': {
            'illnesses': post_data.get('past_illnesses', ''),
            'hospitalizations': post_data.get('past_hospitalizations', ''),
            'surgeries': post_data.get('past_surgeries', ''),
            'trauma': post_data.get('past_trauma', ''),
            'drug_history': post_data.get('past_drugs', ''),
        },
        # Section 6: Family History
        'family_history': {
            'diabetes': post_data.get('fam_diabetes', ''),
            'hypertension': post_data.get('fam_hypertension', ''),
            'tuberculosis': post_data.get('fam_tb', ''),
            'cancer': post_data.get('fam_cancer', ''),
            'mental_illness': post_data.get('fam_mental', ''),
            'hereditary': post_data.get('fam_hereditary', ''),
        }
    }
    
    # Sections 7, 8, 9: Generals
    case.generals = {
        # Section 7: Personal History
        'personal': {
            'appetite': post_data.get('pers_appetite', ''),
            'thirst': post_data.get('pers_thirst', ''),
            'cravings': post_data.get('pers_cravings', ''),
            'bowel': post_data.get('pers_bowel', ''),
            'urine': post_data.get('pers_urine', ''),
            'perspiration': post_data.get('pers_perspiration', ''),
            'sleep': post_data.get('pers_sleep', ''),
            'thermals': post_data.get('pers_thermals', ''),
            'addictions': post_data.get('pers_addictions', ''),
        },
        # Section 8: Mental Generals
        'mental': {
            'nature': post_data.get('ment_nature', ''),
            'fears': post_data.get('ment_fears', ''),
            'anxiety': post_data.get('ment_anxiety', ''),
            'anger': post_data.get('ment_anger', ''),
            'memory': post_data.get('ment_memory', ''),
            'triggers': post_data.get('ment_triggers', ''),
            'social': post_data.get('ment_social', ''),
        },
        # Section 9: Physical Generals
        'physical': {
            'thermal_reaction': post_data.get('phys_thermal', ''),
            'food_desires': post_data.get('phys_food', ''),
            'modalities': post_data.get('phys_modalities', ''),
            'energy': post_data.get('phys_energy', ''),
        }
    }
    
    # Sections 10, 11: Clinical
    case.clinical = {
        # Section 10: Examination Findings
        'examination': {
            'general': post_data.get('exam_general', ''),
            'systemic': post_data.get('exam_systemic', ''),
            'local': post_data.get('exam_local', ''),
        },
        # Section 11: Investigations
        'investigations': {
            'blood': post_data.get('inv_blood', ''),
            'imaging': post_data.get('inv_imaging', ''),
            'other': post_data.get('inv_other', ''),
        }
    }
    
    # Sections 12-16: Analysis
    case.analysis = {
        # Section 12: Diagnosis
        'diagnosis': {
            'probable': post_data.get('diag_probable', ''),
            'final': post_data.get('diag_final', ''),
        },
        # Section 13: Totality of Symptoms
        'totality': post_data.get('anal_totality', ''),
        # Section 14: Rubrics
        'rubrics': post_data.get('anal_rubrics', ''),
        # Section 15: Repertorial Result
        'repertorial_result': post_data.get('anal_repertorial', ''),
        # Section 16: Analysis & Evaluation
        'miasmatic': post_data.get('anal_miasmatic', ''),
        'differentiation': post_data.get('anal_differentiation', ''),
        'keynotes': post_data.get('anal_keynotes', ''),
    }
    
    # Sections 17, 18: Prescription & Advice
    case.prescription = {
        # Section 17: Prescription
        'final_remedy': post_data.get('presc_remedy', ''),
        'potency': post_data.get('presc_potency', ''),
        'dose': post_data.get('presc_dose', ''),
        'repetition': post_data.get('presc_repetition', ''),
        'mode': post_data.get('presc_mode', ''),
        # Section 18: Advice
        'advice': {
            'diet': post_data.get('adv_diet', ''),
            'restrictions': post_data.get('adv_restrictions', ''),
            'instructions': post_data.get('adv_instructions', ''),
        }
    }
    
    # Section 19: Follow-Up
    fu_dates = post_data.getlist('fu_date[]')
    fu_changes = post_data.getlist('fu_changes[]')
    fu_generals = post_data.getlist('fu_generals[]')
    fu_new_symp = post_data.getlist('fu_new_symptoms[]')
    fu_feeling = post_data.getlist('fu_feeling[]')
    fu_assessment = post_data.getlist('fu_assessment[]')
    fu_presc = post_data.getlist('fu_presc[]')
    fu_next = post_data.getlist('fu_next[]')
    
    case.followup = []
    for i in range(len(fu_dates)):
        if fu_dates[i]:
            case.followup.append({
                'date': fu_dates[i],
                'changes': fu_changes[i] if i < len(fu_changes) else '',
                'generals': fu_generals[i] if i < len(fu_generals) else '',
                'new_symptoms': fu_new_symp[i] if i < len(fu_new_symp) else '',
                'overall_feeling': fu_feeling[i] if i < len(fu_feeling) else '',
                'assessment': fu_assessment[i] if i < len(fu_assessment) else '',
                'prescription': fu_presc[i] if i < len(fu_presc) else '',
                'next_followup': fu_next[i] if i < len(fu_next) else '',
            })
    
    # Section 20: Case Summary
    case.notes = {
        'summary': post_data.get('sum_summary', ''),
        'logic': post_data.get('sum_logic', ''),
        'learning': post_data.get('sum_learning', ''),
    }



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
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'status': 'success', 'case_id': str(case.case_id)})
        
        # Redirect to case dashboard
        return redirect('case_paper_dashboard')
    
    # GET request - show form
    context = {
        'mode': 'new',
        'case': {
            'preliminary': {
                'patient_name': request.GET.get('patient_name', ''),
                'physician_name': user.physician_name
            }
        },
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
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'status': 'success', 'case_id': str(case.case_id)})
        
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


@require_http_methods(["POST"])
def case_paper_delete(request):
    """Delete case paper (handles both AJAX and Form POST)"""
    try:
        # Check authentication
        user = get_case_paper_user(request)
        if not user:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Content-Type', ''):
                return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
            return redirect('login')
        
        case_id = None
        
        # Try to get case_id from JSON body
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                case_id = data.get('case_id')
            except json.JSONDecodeError:
                pass
        
        # Try to get case_id from POST data if not in JSON
        if not case_id:
            case_id = request.POST.get('case_id')
            
        if not case_id:
            return JsonResponse({'status': 'error', 'message': 'Case ID required'}, status=400)
            
        case = CasePaper.objects.get(case_id=case_id)
        
        # Verify user owns this case
        if case.user != user:
            return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
        
        case.delete()
        
        # Check if it was a standard form submission
        if request.POST.get('case_id'):
            messages.success(request, 'Case paper deleted successfully.')
            return redirect('case_paper_dashboard')
            
        return JsonResponse({'status': 'ok', 'message': 'Case deleted successfully'})
    
    except CasePaper.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Case not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


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


@require_http_methods(["GET"])
def remedy_search(request):
    """API for searching remedies from Allen's Keynotes"""
    query = request.GET.get('q', '').upper().strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    import json
    import os
    from django.conf import settings
    
    try:
        json_path = os.path.join(settings.BASE_DIR, 'app', 'allens_keynotes.json')
        if not os.path.exists(json_path):
            return JsonResponse({'error': 'Remedy database not found'}, status=404)
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = []
        for name, details in data.items():
            if query in name.upper():
                results.append({
                    'name': name,
                    'summary': details.get('description', '')[:120] + '...' if len(details.get('description', '')) > 120 else details.get('description', ''),
                    'family': details.get('family', '')
                })
                if len(results) >= 15: break
                
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_case_paper_login
def case_paper_pdf(request, case_id):
    """View for generating and downloading a PDF version of the case paper"""
    from .pdf_utils import render_to_pdf
    user = get_case_paper_user(request)
    case = get_object_or_404(CasePaper, case_id=case_id, user=user)
    
    context = {
        'case': case,
        'user': user,
        'is_pdf': True,
        'page_title': f"Case_{case_id}"
    }
    
    pdf_content = render_to_pdf('case_paper/view.html', context)
    if pdf_content:
        response = HttpResponse(pdf_content, content_type='application/pdf')
        filename = f"HC_Record_{case_id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    return HttpResponse("Failed to generate PDF. Clinical record is still available for printing via browser.", status=500)

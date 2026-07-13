# Clinic Management Views (Dashboard, Patients, Appointments, Doctor Desk)
import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Max, Sum
from django.utils import timezone
from django.contrib import messages

from .models import (
    CasePaper,
    CasePaperUser,
    AgendaEvent,
    PatientProfile,
    Appointment,
    QuickInvoice,
    SpecialtyTemplate,
    VirtualOPDSession,
    EPrescription,
    LabRequisition,
    PublicBookingRequest,
)
from .case_paper_helpers import (
    get_ist_now,
    get_effective_feature_flags,
    get_or_create_workspace_settings,
    get_case_paper_user,
    require_case_paper_login,
)
from .whatsapp_utils import send_booking_confirmation_message

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
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    
    # Base queryset for current user
    cases = CasePaper.objects.filter(user=user)
    
    # Apply filters to the main list
    if search_query:
        cases = cases.filter(
            Q(case_id__icontains=search_query) |
            Q(preliminary__patient_name__icontains=search_query)
        )
    
    if status_filter in ['draft', 'complete']:
        cases = cases.filter(status=status_filter)
        
    if date_from:
        cases = cases.filter(created_at__date__gte=date_from)
        
    if date_to:
        cases = cases.filter(created_at__date__lte=date_to)
    
    # Calculate counts based on the filtered queryset or user base
    # Usually dashboard stats show overall totals, but here we'll keep them consistent with user
    total_count_base = CasePaper.objects.filter(user=user)
    
    # Calculate Analytics for "Practice Snapshot"
    from datetime import timedelta
    fourteen_days_ago = timezone.now() - timedelta(days=14)
    recent_cases = total_count_base.filter(created_at__gte=fourteen_days_ago)
    
    # 1. Volume Trend (last 14 days)
    volume_trend = []
    for i in range(14):
        d = (timezone.now() - timedelta(days=i)).date()
        count = recent_cases.filter(created_at__date=d).count()
        volume_trend.append({'date': d.strftime('%d %b'), 'count': count})
    volume_trend.reverse()
    
    # 2. Demographics (Sex)
    sex_dist = {'M': 0, 'F': 0, 'O': 0}
    for c in total_count_base:
        s = c.preliminary.get('sex', 'O')
        if s in sex_dist: sex_dist[s] += 1
        else: sex_dist['O'] += 1
    
    # 3. Demographics (Age Groups)
    age_dist = {'Child': 0, 'Adult': 0, 'Senior': 0}
    for c in total_count_base:
        try:
            a = int(c.preliminary.get('age', 0))
            if a < 18: age_dist['Child'] += 1
            elif a < 60: age_dist['Adult'] += 1
            else: age_dist['Senior'] += 1
        except: pass

    context = {
        'cases': cases,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_count': total_count_base.count(),
        'draft_count': total_count_base.filter(status='draft').count(),
        'complete_count': total_count_base.filter(status='complete').count(),
        'page_title': 'Dashboard',
        'last_sync': get_ist_now().strftime('%Y-%m-%d %H:%M:%S IST'),
        'user': user,
        'analytics': {
            'volume_trend': volume_trend,
            'sex_dist': sex_dist,
            'age_dist': age_dist
        }
    }
    
    return render(request, 'case_paper/dashboard.html', context)


@require_case_paper_login
def case_paper_cases(request):
    user = get_case_paper_user(request)
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    cases = CasePaper.objects.filter(user=user)
    
    if search_query:
        cases = cases.filter(
            Q(case_id__icontains=search_query) |
            Q(preliminary__patient_name__icontains=search_query) |
            Q(status__icontains=search_query)
        )
    
    if status_filter in ['draft', 'complete']:
        cases = cases.filter(status=status_filter)
        
    if date_from:
        cases = cases.filter(created_at__date__gte=date_from)
        
    if date_to:
        cases = cases.filter(created_at__date__lte=date_to)

    context = {
        'user': user,
        'cases': cases,
        'page_title': 'Cases',
        'search_query': search_query,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_count': CasePaper.objects.filter(user=user).count(),
        'draft_count': CasePaper.objects.filter(user=user, status='draft').count(),
        'complete_count': CasePaper.objects.filter(user=user, status='complete').count(),
        'last_sync': get_ist_now().strftime('%Y-%m-%d %H:%M:%S IST'),
    }
    return render(request, 'case_paper/cases.html', context)


@require_case_paper_login
def case_paper_patients(request, section='registration'):
    from decimal import Decimal, InvalidOperation
    from datetime import date

    user = get_case_paper_user(request)
    search_query = request.GET.get('search', '').strip()
    today = timezone.localdate()

    section_route_names = {
        'registration': 'case_paper_patients_registration',
        'queue': 'case_paper_patients_queue',
        'directory': 'case_paper_patients_directory',
        'billing': 'case_paper_patients_billing',
    }
    if section not in section_route_names:
        section = 'registration'

    def redirect_to_section(target_section=None):
        route_name = section_route_names.get(target_section or section, 'case_paper_patients')
        return redirect(route_name)

    feature_flags = get_effective_feature_flags()
    workspace = get_or_create_workspace_settings(user)
    registration_enabled = workspace.registration_desk_enabled and feature_flags.get('registration_smart_registration', True)
    queue_enabled = feature_flags.get('registration_token_queue', True)
    invoicing_enabled = feature_flags.get('registration_fast_invoicing', True)
    communication_enabled = feature_flags.get('registration_email_chat_access', True)
    whatsapp_enabled = feature_flags.get('registration_whatsapp_access', True)
    branding_enabled = feature_flags.get('registration_clinic_branding', True)

    action_section_map = {
        'register_patient': 'registration',
        'create_appointment': 'queue',
        'update_queue_status': 'queue',
        'create_invoice': 'billing',
    }

    if request.method == 'POST':
        desk_action = request.POST.get('desk_action', '').strip()
        action_section = action_section_map.get(desk_action, section)

        if desk_action == 'register_patient':
            if not registration_enabled:
                messages.error(request, 'Registration Desk is currently disabled by settings.')
                return redirect_to_section(action_section)

            full_name = request.POST.get('full_name', '').strip()
            age_raw = request.POST.get('age', '').strip()
            sex = request.POST.get('sex', 'O').strip().upper()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            whatsapp_number = request.POST.get('whatsapp_number', '').strip()
            address = request.POST.get('address', '').strip()
            allergies = request.POST.get('allergies', '').strip()
            notes = request.POST.get('notes', '').strip()

            age = None
            if age_raw:
                try:
                    age = int(age_raw)
                    if age < 0:
                        raise ValueError
                except ValueError:
                    messages.error(request, 'Age must be a valid positive number.')
                    return redirect_to_section(action_section)

            if not full_name:
                messages.error(request, 'Patient full name is required.')
                return redirect_to_section(action_section)

            if sex not in dict(PatientProfile.SEX_CHOICES):
                sex = 'O'

            patient = PatientProfile.objects.create(
                user=user,
                full_name=full_name,
                age=age,
                sex=sex,
                phone=phone,
                email=email,
                whatsapp_number=whatsapp_number,
                address=address,
                allergies=allergies,
                notes=notes,
            )
            messages.success(request, f'Patient registered successfully: {patient.full_name} ({patient.patient_code})')
            return redirect_to_section(action_section)

        if desk_action == 'create_appointment':
            if not queue_enabled:
                messages.error(request, 'Token queue is currently disabled by settings.')
                return redirect_to_section(action_section)

            patient_id = request.POST.get('patient_id', '').strip()
            appointment_date_raw = request.POST.get('appointment_date', '').strip()
            appointment_time_raw = request.POST.get('appointment_time', '').strip()
            visit_type = request.POST.get('visit_type', 'opd').strip().lower()
            chief_complaint = request.POST.get('chief_complaint', '').strip()

            patient = PatientProfile.objects.filter(id=patient_id, user=user).first()
            if not patient:
                messages.error(request, 'Please select a valid patient for appointment.')
                return redirect_to_section(action_section)

            if visit_type not in dict(Appointment.VISIT_TYPE_CHOICES):
                visit_type = 'opd'

            try:
                appointment_date = date.fromisoformat(appointment_date_raw)
            except ValueError:
                messages.error(request, 'Please provide a valid appointment date.')
                return redirect_to_section(action_section)

            appointment_time = None
            if appointment_time_raw:
                try:
                    appointment_time = datetime.strptime(appointment_time_raw, '%H:%M').time()
                except ValueError:
                    messages.error(request, 'Please provide a valid appointment time.')
                    return redirect_to_section(action_section)

            max_token = Appointment.objects.filter(user=user, appointment_date=appointment_date).aggregate(
                value=Max('token_number')
            )['value'] or 0
            token_number = max_token + 1

            appointment = Appointment.objects.create(
                user=user,
                patient=patient,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                visit_type=visit_type,
                token_number=token_number,
                chief_complaint=chief_complaint,
            )
            messages.success(request, f'Appointment created. Token #{appointment.token_number} assigned.')
            return redirect_to_section(action_section)

        if desk_action == 'update_queue_status':
            if not queue_enabled:
                messages.error(request, 'Queue status updates are currently disabled.')
                return redirect_to_section(action_section)

            appointment_id = request.POST.get('appointment_id', '').strip()
            new_status = request.POST.get('queue_status', '').strip().lower()

            appointment = Appointment.objects.filter(id=appointment_id, user=user).select_related('patient').first()
            if not appointment:
                messages.error(request, 'Appointment not found.')
                return redirect_to_section(action_section)

            if new_status not in dict(Appointment.STATUS_CHOICES):
                messages.error(request, 'Invalid queue status selected.')
                return redirect_to_section(action_section)

            appointment.status = new_status
            if new_status == 'checked_in' and not appointment.checked_in_at:
                appointment.checked_in_at = timezone.now()
            if new_status == 'completed' and not appointment.completed_at:
                appointment.completed_at = timezone.now()
            appointment.save()
            messages.success(request, f'Token #{appointment.token_number} updated to {appointment.get_status_display()}.')
            return redirect_to_section(action_section)

        if desk_action == 'create_invoice':
            if not invoicing_enabled:
                messages.error(request, 'Fast invoicing is currently disabled by settings.')
                return redirect_to_section(action_section)

            patient_id = request.POST.get('invoice_patient_id', '').strip()
            appointment_id = request.POST.get('invoice_appointment_id', '').strip()
            amount_raw = request.POST.get('invoice_amount', '').strip()
            tax_percent_raw = request.POST.get('invoice_tax_percent', '').strip() or '0'
            discount_raw = request.POST.get('invoice_discount', '').strip() or '0'
            payment_status = request.POST.get('invoice_payment_status', 'unpaid').strip().lower()
            payment_mode = request.POST.get('invoice_payment_mode', 'cash').strip().lower()
            notes = request.POST.get('invoice_notes', '').strip()

            patient = PatientProfile.objects.filter(id=patient_id, user=user).first()
            if not patient:
                messages.error(request, 'Please select a valid patient for invoicing.')
                return redirect_to_section(action_section)

            appointment = None
            if appointment_id:
                appointment = Appointment.objects.filter(id=appointment_id, user=user, patient=patient).first()

            if payment_status not in dict(QuickInvoice.PAYMENT_STATUS_CHOICES):
                payment_status = 'unpaid'
            if payment_mode not in dict(QuickInvoice.PAYMENT_MODE_CHOICES):
                payment_mode = 'cash'

            try:
                amount = Decimal(amount_raw)
                tax_percent = Decimal(tax_percent_raw)
                discount = Decimal(discount_raw)
                if amount < 0 or tax_percent < 0 or discount < 0:
                    raise InvalidOperation
            except (InvalidOperation, ValueError):
                messages.error(request, 'Invoice values must be valid positive numbers.')
                return redirect_to_section(action_section)

            invoice = QuickInvoice.objects.create(
                user=user,
                patient=patient,
                appointment=appointment,
                amount=amount,
                tax_percent=tax_percent,
                discount=discount,
                payment_status=payment_status,
                payment_mode=payment_mode,
                notes=notes,
            )

            if appointment and payment_status == 'paid' and appointment.status != 'completed':
                appointment.status = 'completed'
                appointment.completed_at = appointment.completed_at or timezone.now()
                appointment.save()

            messages.success(request, f'Invoice {invoice.invoice_number} created successfully.')
            return redirect_to_section(action_section)

    patients_qs = PatientProfile.objects.filter(user=user)
    if search_query:
        patients_qs = patients_qs.filter(
            Q(full_name__icontains=search_query)
            | Q(patient_code__icontains=search_query)
            | Q(phone__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(whatsapp_number__icontains=search_query)
        )

    patients = patients_qs.order_by('-updated_at')
    today_queue = Appointment.objects.filter(user=user, appointment_date=today).select_related('patient').order_by('token_number', 'appointment_time')
    upcoming_appointments = Appointment.objects.filter(user=user, appointment_date__gte=today).select_related('patient').order_by('appointment_date', 'token_number', 'appointment_time')[:20]
    recent_invoices = QuickInvoice.objects.filter(user=user).select_related('patient', 'appointment').order_by('-created_at')[:25]

    queue_live = today_queue.exclude(status__in=['completed', 'cancelled'])

    month_revenue = QuickInvoice.objects.filter(
        user=user,
        payment_status='paid',
        created_at__year=today.year,
        created_at__month=today.month,
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    section_meta = {
        'registration': ('Smart Registration', 'Create and manage patient profiles with health-card readiness.'),
        'queue': ('Token Queue', 'Run OPD flow with token generation and real-time status updates.'),
        'directory': ('Patient Directory', 'Search and access patient communication and quick case links.'),
        'billing': ('Fast Invoicing', 'Generate invoices and monitor payment records quickly.'),
    }
    section_title, section_subtitle = section_meta.get(section, section_meta['registration'])

    context = {
        'user': user,
        'page_title': 'Patients',
        'search_query': search_query,
        'patients': patients,
        'today_queue': today_queue,
        'queue_live_count': queue_live.count(),
        'upcoming_appointments': upcoming_appointments,
        'recent_invoices': recent_invoices,
        'visit_type_choices': Appointment.VISIT_TYPE_CHOICES,
        'queue_status_choices': Appointment.STATUS_CHOICES,
        'invoice_status_choices': QuickInvoice.PAYMENT_STATUS_CHOICES,
        'invoice_mode_choices': QuickInvoice.PAYMENT_MODE_CHOICES,
        'total_patients': PatientProfile.objects.filter(user=user).count(),
        'appointments_today': today_queue.count(),
        'month_revenue': month_revenue,
        'registration_enabled': registration_enabled,
        'queue_enabled': queue_enabled,
        'invoicing_enabled': invoicing_enabled,
        'communication_enabled': communication_enabled,
        'whatsapp_enabled': whatsapp_enabled,
        'branding_enabled': branding_enabled,
        'workspace': workspace,
        'active_section': section,
        'section_title': section_title,
        'section_subtitle': section_subtitle,
        'last_sync': get_ist_now().strftime('%Y-%m-%d %H:%M:%S IST'),
    }
    return render(request, 'case_paper/patients.html', context)


@require_case_paper_login
def case_paper_calendar(request):
    import calendar
    from datetime import date, timedelta

    user = get_case_paper_user(request)
    category_map = dict(AgendaEvent.CATEGORY_CHOICES)

    # Get requested month and year (supports GET and form POST)
    month_input = request.GET.get('month') or request.POST.get('month') or timezone.now().month
    year_input = request.GET.get('year') or request.POST.get('year') or timezone.now().year

    try:
        month = int(month_input)
        year = int(year_input)
    except (ValueError, TypeError):
        month = timezone.now().month
        year = timezone.now().year

    if month < 1 or month > 12:
        month = timezone.now().month

    # Handle agenda create/update/delete
    if request.method == 'POST':
        agenda_action = request.POST.get('agenda_action', 'create').strip().lower()
        agenda_id = request.POST.get('agenda_id', '').strip()

        if agenda_action == 'delete':
            if not agenda_id:
                messages.error(request, 'Agenda ID is missing.')
            else:
                agenda = AgendaEvent.objects.filter(id=agenda_id, user=user).first()
                if not agenda:
                    messages.error(request, 'Agenda item not found.')
                else:
                    agenda.delete()
                    messages.success(request, 'Agenda item deleted successfully.')
            return redirect(f"{request.path}?month={month}&year={year}")

        agenda_title = request.POST.get('agenda_title', '').strip()
        agenda_subtitle = request.POST.get('agenda_subtitle', '').strip()
        agenda_description = request.POST.get('agenda_description', '').strip()
        agenda_location = request.POST.get('agenda_location', '').strip()
        agenda_category = request.POST.get('agenda_category', 'reminder').strip().lower()
        agenda_date_str = request.POST.get('agenda_date', '').strip()
        agenda_time_str = request.POST.get('agenda_time', '').strip()

        if agenda_category not in category_map:
            agenda_category = 'reminder'

        if not agenda_title or not agenda_date_str:
            messages.error(request, 'Agenda title and date are required.')
            return redirect(f"{request.path}?month={month}&year={year}")

        try:
            agenda_date = date.fromisoformat(agenda_date_str)
            agenda_time = None
            if agenda_time_str:
                agenda_time = datetime.strptime(agenda_time_str, '%H:%M').time()

            if agenda_action == 'update':
                agenda = AgendaEvent.objects.filter(id=agenda_id, user=user).first()
                if not agenda:
                    messages.error(request, 'Agenda item not found for update.')
                else:
                    agenda.title = agenda_title
                    agenda.subtitle = agenda_subtitle
                    agenda.description = agenda_description
                    agenda.location = agenda_location
                    agenda.category = agenda_category
                    agenda.date = agenda_date
                    agenda.time = agenda_time
                    agenda.save()
                    messages.success(request, 'Agenda item updated successfully.')
            else:
                AgendaEvent.objects.create(
                    user=user,
                    title=agenda_title,
                    subtitle=agenda_subtitle,
                    description=agenda_description,
                    location=agenda_location,
                    category=agenda_category,
                    date=agenda_date,
                    time=agenda_time,
                )
                messages.success(request, 'Agenda item added successfully.')
        except ValueError:
            messages.error(request, 'Please enter valid date/time values.')

        return redirect(f"{request.path}?month={month}&year={year}")

    # Calculate navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    month_label = f"{calendar.month_name[month]} {year}"

    # Get calendar grid
    cal = calendar.Calendar(firstweekday=0)  # Monday start
    month_days = cal.monthdays2calendar(year, month)

    # Fetch user data
    cases = list(CasePaper.objects.filter(user=user))
    month_agenda_events = list(
        AgendaEvent.objects.filter(user=user, date__year=year, date__month=month).order_by('date', 'time', 'created_at')
    )

    # Build lookup maps for fast day rendering
    created_by_date = {}
    followups_by_date = {}

    for case in cases:
        created_date = case.created_at.date()
        created_by_date.setdefault(created_date, []).append(case)

        if isinstance(case.followup, list):
            for fu in case.followup:
                fu_date_str = fu.get('next_followup', '')
                try:
                    if fu_date_str:
                        fu_date = date.fromisoformat(fu_date_str)
                        followups_by_date.setdefault(fu_date, []).append((case, fu))
                except (ValueError, TypeError):
                    continue

    agenda_by_date = {}
    for agenda in month_agenda_events:
        agenda_by_date.setdefault(agenda.date, []).append(agenda)

    calendar_weeks = []
    today = date.today()

    for week in month_days:
        week_data = []
        for day_num, _weekday in week:
            day_events = []
            if day_num != 0:
                current_date = date(year, month, day_num)

                for case in created_by_date.get(current_date, []):
                    day_events.append({
                        'case_id': case.case_id,
                        'title': case.preliminary.get('patient_name', 'Unknown'),
                        'subtitle': 'New Case',
                        'type': 'new',
                        'time': '',
                        'time_display': '',
                        'sort_order': 2,
                    })

                for case, _fu in followups_by_date.get(current_date, []):
                    day_events.append({
                        'case_id': case.case_id,
                        'title': case.preliminary.get('patient_name', 'Unknown'),
                        'subtitle': 'Follow-up',
                        'type': 'followup',
                        'time': '',
                        'time_display': '',
                        'sort_order': 2,
                    })

                for agenda in agenda_by_date.get(current_date, []):
                    time_24h = agenda.time.strftime('%H:%M') if agenda.time else ''
                    day_events.append({
                        'case_id': None,
                        'agenda_id': agenda.id,
                        'title': agenda.title,
                        'subtitle': agenda.subtitle or agenda.location or 'Agenda',
                        'description': agenda.description,
                        'location': agenda.location,
                        'category': agenda.category,
                        'category_label': category_map.get(agenda.category, 'Reminder'),
                        'date_iso': agenda.date.isoformat(),
                        'type': 'agenda',
                        'time': time_24h,
                        'time_display': agenda.time.strftime('%I:%M %p') if agenda.time else '',
                        'sort_order': 0 if agenda.time else 1,
                    })

                day_events.sort(key=lambda x: (x.get('sort_order', 9), x.get('time', ''), x.get('title', '')))

            week_data.append({
                'day': day_num if day_num != 0 else '',
                'is_current_month': day_num != 0,
                'is_today': day_num != 0 and date(year, month, day_num) == today,
                'events': day_events,
            })
        calendar_weeks.append(week_data)

    # Upcoming events: next 30 days (follow-ups + custom agenda)
    upcoming_events = []
    max_date = today + timedelta(days=30)

    for fu_date, items in followups_by_date.items():
        if today <= fu_date <= max_date:
            for case, _fu in items:
                upcoming_events.append({
                    'date': fu_date,
                    'title': case.preliminary.get('patient_name', 'Unknown Patient'),
                    'subtitle': 'Scheduled Follow-up',
                    'case_id': case.case_id,
                    'type': 'followup',
                    'time': '',
                    'time_display': '',
                })

    agenda_range = AgendaEvent.objects.filter(user=user, date__gte=today, date__lte=max_date).order_by('date', 'time', 'created_at')
    for agenda in agenda_range:
        upcoming_events.append({
            'date': agenda.date,
            'title': agenda.title,
            'subtitle': agenda.subtitle or agenda.location or 'Agenda',
            'description': agenda.description,
            'location': agenda.location,
            'category': agenda.category,
            'category_label': category_map.get(agenda.category, 'Reminder'),
            'date_iso': agenda.date.isoformat(),
            'case_id': None,
            'agenda_id': agenda.id,
            'type': 'agenda',
            'time': agenda.time.strftime('%H:%M') if agenda.time else '',
            'time_display': agenda.time.strftime('%I:%M %p') if agenda.time else '',
        })

    upcoming_events.sort(key=lambda x: (x['date'], x.get('time', ''), x['title']))

    context = {
        'user': user,
        'page_title': 'Calendar',
        'calendar_weeks': calendar_weeks,
        'month_label': month_label,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'upcoming_events': upcoming_events,
        'agenda_categories': AgendaEvent.CATEGORY_CHOICES,
        'current_month': month,
        'current_year': year,
        'last_sync': get_ist_now().strftime('%Y-%m-%d %H:%M:%S IST'),
    }
    return render(request, 'case_paper/calendar.html', context)


@require_case_paper_login
def case_paper_doctor_desk(request, section='documentation'):
    from datetime import date

    user = get_case_paper_user(request)
    workspace = get_or_create_workspace_settings(user)
    feature_flags = get_effective_feature_flags()

    section_route_names = {
        'documentation': 'case_paper_doctor_desk_templates',
        'virtual': 'case_paper_doctor_desk_virtual',
        'eprescription': 'case_paper_doctor_desk_eprescriptions',
        'lab': 'case_paper_doctor_desk_lab',
        'requests': 'case_paper_doctor_desk_requests',
    }
    if section not in section_route_names:
        section = 'documentation'

    def redirect_to_section(target_section=None):
        route_name = section_route_names.get(target_section or section, 'case_paper_doctor_desk')
        return redirect(route_name)

    doctor_enabled = workspace.doctor_desk_enabled and feature_flags.get('doctor_smart_documentation', True)
    if not doctor_enabled:
        messages.error(request, "Doctor Desk is disabled from settings.")
        return redirect('case_paper_settings')

    if request.method == 'POST':
        desk_action = request.POST.get('doctor_action', '').strip()

        if desk_action == 'save_template':
            if not feature_flags.get('doctor_smart_documentation', True):
                messages.error(request, 'Smart Documentation is disabled by admin settings.')
                return redirect_to_section()

            template_id = request.POST.get('template_id', '').strip()
            name = request.POST.get('template_name', '').strip()
            specialty = request.POST.get('template_specialty', '').strip() or 'General Practice'
            notes_template = request.POST.get('notes_template', '').strip()
            diagnosis_template = request.POST.get('diagnosis_template', '').strip()
            plan_template = request.POST.get('plan_template', '').strip()
            is_default = request.POST.get('template_is_default') == 'on'

            if not name:
                messages.error(request, 'Template name is required.')
                return redirect_to_section()

            if is_default:
                SpecialtyTemplate.objects.filter(user=user, is_default=True).update(is_default=False)

            if template_id:
                template = SpecialtyTemplate.objects.filter(id=template_id, user=user).first()
                if not template:
                    messages.error(request, 'Template not found.')
                else:
                    template.name = name
                    template.specialty = specialty
                    template.notes_template = notes_template
                    template.diagnosis_template = diagnosis_template
                    template.plan_template = plan_template
                    template.is_default = is_default
                    template.save()
                    messages.success(request, 'Documentation template updated.')
            else:
                SpecialtyTemplate.objects.create(
                    user=user,
                    name=name,
                    specialty=specialty,
                    notes_template=notes_template,
                    diagnosis_template=diagnosis_template,
                    plan_template=plan_template,
                    is_default=is_default,
                )
                messages.success(request, 'Documentation template created.')
            return redirect_to_section()

        if desk_action == 'create_virtual_session':
            if not feature_flags.get('doctor_virtual_opd', True):
                messages.error(request, 'Virtual OPD is disabled by admin settings.')
                return redirect_to_section()

            patient_id = request.POST.get('virtual_patient_id', '').strip()
            session_date_str = request.POST.get('virtual_date', '').strip()
            session_time_str = request.POST.get('virtual_time', '').strip()
            platform = request.POST.get('virtual_platform', '').strip() or 'Google Meet'
            meeting_link = request.POST.get('meeting_link', '').strip()
            chief_concern = request.POST.get('chief_concern', '').strip()
            clinical_notes = request.POST.get('virtual_notes', '').strip()

            patient = PatientProfile.objects.filter(id=patient_id, user=user).first()
            if not patient:
                messages.error(request, 'Please select a valid patient for virtual OPD.')
                return redirect_to_section()

            try:
                session_date = date.fromisoformat(session_date_str)
            except ValueError:
                messages.error(request, 'Please provide a valid session date.')
                return redirect_to_section()

            session_time = None
            if session_time_str:
                try:
                    session_time = datetime.strptime(session_time_str, '%H:%M').time()
                except ValueError:
                    messages.error(request, 'Please provide a valid session time.')
                    return redirect_to_section()

            VirtualOPDSession.objects.create(
                user=user,
                patient=patient,
                session_date=session_date,
                session_time=session_time,
                platform=platform,
                meeting_link=meeting_link,
                chief_concern=chief_concern,
                clinical_notes=clinical_notes,
            )
            messages.success(request, 'Virtual OPD session scheduled.')
            return redirect_to_section()

        if desk_action == 'update_virtual_status':
            session_id = request.POST.get('virtual_session_id', '').strip()
            new_status = request.POST.get('virtual_status', '').strip()
            session = VirtualOPDSession.objects.filter(id=session_id, user=user).first()

            if not session:
                messages.error(request, 'Virtual session not found.')
                return redirect_to_section()

            if new_status not in dict(VirtualOPDSession.STATUS_CHOICES):
                messages.error(request, 'Invalid virtual OPD status.')
                return redirect_to_section()

            session.status = new_status
            session.save(update_fields=['status'])
            messages.success(request, 'Virtual OPD status updated.')
            return redirect_to_section()

        if desk_action == 'create_eprescription':
            if not feature_flags.get('doctor_quick_eprescription', True):
                messages.error(request, 'Quick e-Prescription is disabled by admin settings.')
                return redirect_to_section()

            patient_id = request.POST.get('rx_patient_id', '').strip()
            appointment_id = request.POST.get('rx_appointment_id', '').strip()
            medicines_raw = request.POST.get('rx_medicines', '').strip()
            instructions = request.POST.get('rx_instructions', '').strip()
            followup_date_raw = request.POST.get('rx_followup_date', '').strip()
            share_email = request.POST.get('rx_share_email') == 'on'
            share_whatsapp = request.POST.get('rx_share_whatsapp') == 'on'

            patient = PatientProfile.objects.filter(id=patient_id, user=user).first()
            if not patient:
                messages.error(request, 'Please select a valid patient for e-prescription.')
                return redirect_to_section()

            appointment = None
            if appointment_id:
                appointment = Appointment.objects.filter(id=appointment_id, user=user, patient=patient).first()

            medicines = [line.strip() for line in medicines_raw.splitlines() if line.strip()]
            if not medicines:
                messages.error(request, 'Please add at least one medicine line.')
                return redirect_to_section()

            followup_date = None
            if followup_date_raw:
                try:
                    followup_date = date.fromisoformat(followup_date_raw)
                except ValueError:
                    messages.error(request, 'Invalid follow-up date in e-prescription.')
                    return redirect_to_section()

            EPrescription.objects.create(
                user=user,
                patient=patient,
                appointment=appointment,
                medicines=medicines,
                instructions=instructions,
                followup_date=followup_date,
                shared_via_email=share_email,
                shared_via_whatsapp=share_whatsapp,
            )
            messages.success(request, 'e-Prescription saved successfully.')
            return redirect_to_section()

        if desk_action == 'create_lab_requisition':
            if not feature_flags.get('doctor_easy_lab_requisition', True):
                messages.error(request, 'Lab requisition is disabled by admin settings.')
                return redirect_to_section()

            patient_id = request.POST.get('lab_patient_id', '').strip()
            appointment_id = request.POST.get('lab_appointment_id', '').strip()
            tests = request.POST.getlist('lab_tests')
            notes = request.POST.get('lab_notes', '').strip()

            patient = PatientProfile.objects.filter(id=patient_id, user=user).first()
            if not patient:
                messages.error(request, 'Please select a valid patient for lab requisition.')
                return redirect_to_section()

            appointment = None
            if appointment_id:
                appointment = Appointment.objects.filter(id=appointment_id, user=user, patient=patient).first()

            cleaned_tests = [t for t in tests if t]
            if not cleaned_tests:
                messages.error(request, 'Please select at least one lab test.')
                return redirect_to_section()

            LabRequisition.objects.create(
                user=user,
                patient=patient,
                appointment=appointment,
                tests=cleaned_tests,
                notes=notes,
            )
            messages.success(request, 'Lab requisition created successfully.')
            return redirect_to_section()

    patients = PatientProfile.objects.filter(user=user).order_by('-updated_at')
    appointments = Appointment.objects.filter(user=user).select_related('patient').order_by('-appointment_date', '-token_number')[:100]
    templates = SpecialtyTemplate.objects.filter(user=user).order_by('-is_default', '-updated_at')
    virtual_sessions = VirtualOPDSession.objects.filter(user=user).select_related('patient').order_by('-session_date', '-session_time')[:40]
    eprescriptions = EPrescription.objects.filter(user=user).select_related('patient', 'appointment').order_by('-created_at')[:40]
    lab_requisitions = LabRequisition.objects.filter(user=user).select_related('patient', 'appointment').order_by('-created_at')[:40]
    booking_requests = PublicBookingRequest.objects.filter(user=user).order_by('-created_at')[:40]

    lab_tests_catalog = [
        'CBC', 'ESR', 'CRP', 'LFT', 'KFT', 'RBS', 'FBS', 'PPBS', 'HbA1c', 'Lipid Profile',
        'TSH', 'T3', 'T4', 'Vitamin D', 'Vitamin B12', 'Urine Routine', 'Urine Culture',
        'Stool Routine', 'Dengue NS1', 'Malaria Parasite', 'Typhidot', 'Widal', 'HIV', 'HBsAg',
        'HCV', 'Serum Calcium', 'Uric Acid', 'ECG', 'Chest X-Ray', 'USG Abdomen'
    ]

    section_meta = {
        'documentation': ('Smart Documentation', 'Build and manage specialty templates for rapid clinical notes.'),
        'virtual': ('Virtual OPD', 'Schedule and track virtual consultations with structured status flow.'),
        'eprescription': ('Quick ePrescription', 'Generate and review digital prescription records.'),
        'lab': ('Lab Requisition', 'Create and monitor diagnostic test requisitions.'),
        'requests': ('Booking Requests', 'Review incoming public clinic booking requests.'),
    }
    section_title, section_subtitle = section_meta.get(section, section_meta['documentation'])

    context = {
        'user': user,
        'page_title': 'Doctor Desk',
        'patients': patients,
        'appointments': appointments,
        'templates': templates,
        'virtual_sessions': virtual_sessions,
        'eprescriptions': eprescriptions,
        'lab_requisitions': lab_requisitions,
        'booking_requests': booking_requests,
        'lab_tests_catalog': lab_tests_catalog,
        'virtual_status_choices': VirtualOPDSession.STATUS_CHOICES,
        'workspace': workspace,
        'feature_flags': feature_flags,
        'active_section': section,
        'section_title': section_title,
        'section_subtitle': section_subtitle,
        'last_sync': get_ist_now().strftime('%Y-%m-%d %H:%M:%S IST'),
    }
    return render(request, 'case_paper/doctor_desk.html', context)


@require_case_paper_login
def case_paper_settings(request, section='profile'):
    user = get_case_paper_user(request)
    settings_saved = False
    settings_error = None

    section_route_names = {
        'profile': 'case_paper_settings_profile',
        'workspace': 'case_paper_settings_workspace',
        'account': 'case_paper_settings_account',
    }
    if section not in section_route_names:
        section = 'profile'

    feature_flags = get_effective_feature_flags()
    workspace = get_or_create_workspace_settings(user)

    if request.method == 'POST':
        action = request.POST.get('settings_action', 'profile').strip().lower()
        action_section = 'workspace' if action == 'workspace' else 'profile'
        section = action_section

        try:
            if action == 'workspace':
                workspace.registration_desk_enabled = request.POST.get('registration_desk_enabled') == 'on'
                workspace.doctor_desk_enabled = request.POST.get('doctor_desk_enabled') == 'on'
                workspace.superadmin_tools_visible = request.POST.get('superadmin_tools_visible') == 'on'

                workspace.public_profile_enabled = request.POST.get('public_profile_enabled') == 'on'
                workspace.allow_public_booking_requests = request.POST.get('allow_public_booking_requests') == 'on'
                workspace.show_phone_public = request.POST.get('show_phone_public') == 'on'
                workspace.show_email_public = request.POST.get('show_email_public') == 'on'
                workspace.whatsapp_notifications_enabled = request.POST.get('whatsapp_notifications_enabled') == 'on'
                workspace.email_notifications_enabled = request.POST.get('email_notifications_enabled') == 'on'
                workspace.whatsapp_doctor_consent = request.POST.get('whatsapp_doctor_consent') == 'on'
                workspace.whatsapp_sender_number = request.POST.get('whatsapp_sender_number', '').strip()
                workspace.whatsapp_business_phone_number_id = request.POST.get('whatsapp_business_phone_number_id', '').strip()

                slug_input = request.POST.get('public_slug', '').strip().lower()
                if slug_input:
                    slug_value = slugify(slug_input)
                    if not slug_value:
                        settings_error = 'Public slug must contain letters or numbers.'
                    else:
                        conflict = UserWorkspaceSettings.objects.filter(public_slug=slug_value).exclude(user=user).exists()
                        if conflict:
                            settings_error = 'Public slug already in use. Please choose another.'
                        else:
                            workspace.public_slug = slug_value

                if not settings_error:
                    workspace.save()
                    settings_saved = True

            else:
                user.physician_name = request.POST.get('physician_name', '').strip()
                user.specialization = request.POST.get('specialization', '').strip()
                user.clinic_name = request.POST.get('clinic_name', '').strip()
                user.contact_number = request.POST.get('contact_number', '').strip()
                user.email = request.POST.get('email', '').strip()
                user.address = request.POST.get('address', '').strip()
                user.save()
                settings_saved = True

        except Exception as e:
            settings_error = str(e)

    # Get case counts for sidebar
    total_cases = CasePaper.objects.filter(user=user).count()
    completed_cases = CasePaper.objects.filter(user=user, status='complete').count()
    draft_cases = CasePaper.objects.filter(user=user, status='draft').count()

    clinic_base_url = (getattr(settings, 'PUBLIC_CLINIC_BASE_URL', '') or '').strip().rstrip('/')
    if clinic_base_url:
        public_url = f"{clinic_base_url}/{workspace.public_slug}/"
    else:
        try:
            public_url = request.build_absolute_uri(f"/clinic/{workspace.public_slug}/")
        except Exception:
            public_url = f"/clinic/{workspace.public_slug}/"

    section_meta = {
        'profile': ('Profile Settings', 'Manage clinic identity, practitioner details, and contact information.'),
        'workspace': ('Workspace Controls', 'Configure module visibility, notifications, and public profile behavior.'),
        'account': ('Account & Access', 'Review account identity and module readiness snapshot.'),
    }
    section_title, section_subtitle = section_meta.get(section, section_meta['profile'])

    context = {
        'user': user,
        'workspace': workspace,
        'feature_flags': feature_flags,
        'public_url': public_url,
        'page_title': 'Settings',
        'last_sync': get_ist_now().strftime('%Y-%m-%d %H:%M:%S IST'),
        'total_cases': total_cases,
        'completed_cases': completed_cases,
        'draft_cases': draft_cases,
        'settings_saved': settings_saved,
        'settings_error': settings_error,
        'active_section': section,
        'section_title': section_title,
        'section_subtitle': section_subtitle,
    }
    return render(request, 'case_paper/settings.html', context)



def public_clinic_page(request, public_slug):
    workspace = UserWorkspaceSettings.objects.select_related('user').filter(public_slug=public_slug).first()
    if not workspace or not workspace.public_profile_enabled:
        return render(request, 'case_paper/public_clinic.html', {'not_found': True}, status=404)

    clinic_user = workspace.user

    if request.method == 'POST':
        if not workspace.allow_public_booking_requests:
            messages.error(request, 'Public booking is not enabled for this clinic.')
            return redirect('public_clinic_profile', public_slug=public_slug)

        patient_name = request.POST.get('patient_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        requested_date_raw = request.POST.get('requested_date', '').strip()
        concern = request.POST.get('concern', '').strip()

        if not patient_name or not phone:
            messages.error(request, 'Patient name and phone are required for booking request.')
            return redirect('public_clinic_profile', public_slug=public_slug)

        requested_date = None
        if requested_date_raw:
            try:
                requested_date = datetime.strptime(requested_date_raw, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Please provide a valid preferred date.')
                return redirect('public_clinic_profile', public_slug=public_slug)

        booking_request = PublicBookingRequest.objects.create(
            user=clinic_user,
            patient_name=patient_name,
            phone=phone,
            requested_date=requested_date,
            concern=concern,
        )

        whatsapp_sent, whatsapp_note = send_booking_confirmation_message(
            workspace=workspace,
            booking_request=booking_request,
            doctor=clinic_user,
        )

        if whatsapp_sent:
            messages.success(request, 'Booking request sent and WhatsApp confirmation delivered successfully.')
        else:
            if workspace.whatsapp_notifications_enabled and workspace.whatsapp_doctor_consent:
                messages.warning(request, f'Booking request sent. WhatsApp delivery skipped: {whatsapp_note}')
            else:
                messages.success(request, 'Booking request sent to clinic successfully.')

        return redirect('public_clinic_profile', public_slug=public_slug)

    recent_templates = SpecialtyTemplate.objects.filter(user=clinic_user).order_by('-is_default', '-updated_at')[:6]

    context = {
        'not_found': False,
        'clinic_user': clinic_user,
        'workspace': workspace,
        'recent_templates': recent_templates,
    }
    return render(request, 'case_paper/public_clinic.html', context)



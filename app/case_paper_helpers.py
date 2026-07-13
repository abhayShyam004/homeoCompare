from django.shortcuts import redirect
from django.utils import timezone
from django.utils.text import slugify
from datetime import datetime
from .models import (
    CasePaperUser,
    AccessPlatformSettings,
    UserWorkspaceSettings,
)

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


def get_default_feature_flags():
    return {
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


def get_effective_feature_flags():
    defaults = get_default_feature_flags()
    settings_obj = AccessPlatformSettings.objects.filter(singleton_key='default').first()
    if settings_obj and isinstance(settings_obj.feature_flags, dict):
        defaults.update(settings_obj.feature_flags)
    return defaults


def _build_unique_public_slug(seed, exclude_user_id=None):
    base = slugify((seed or '').strip())[:90].strip('-')
    if not base:
        base = 'clinic'

    candidate = base
    counter = 2

    while UserWorkspaceSettings.objects.filter(public_slug=candidate).exclude(user_id=exclude_user_id).exists():
        suffix = f"-{counter}"
        candidate = f"{base[:max(1, 120 - len(suffix))]}{suffix}"
        counter += 1

    return candidate


def get_or_create_workspace_settings(user):
    slug_seed = (user.clinic_name or user.physician_name or user.username or '').strip()
    if not slug_seed:
        slug_seed = user.username

    workspace, _ = UserWorkspaceSettings.objects.get_or_create(
        user=user,
        defaults={
            'public_slug': _build_unique_public_slug(slug_seed),
            'registration_desk_enabled': True,
            'doctor_desk_enabled': True,
            'superadmin_tools_visible': False,
            'public_profile_enabled': False,
            'allow_public_booking_requests': False,
            'show_phone_public': False,
            'show_email_public': False,
            'whatsapp_notifications_enabled': True,
            'email_notifications_enabled': True,
            'whatsapp_doctor_consent': False,
            'whatsapp_sender_number': '',
            'whatsapp_business_phone_number_id': '',
        },
    )

    if not workspace.public_slug:
        workspace.public_slug = _build_unique_public_slug(slug_seed, exclude_user_id=user.id)
        workspace.save(update_fields=['public_slug', 'updated_at'])

    return workspace


def get_case_paper_user(request):
    """Get the current case paper user from session, or None if not logged in"""
    user_id = request.session.get('user_id') or request.session.get('case_paper_user_id')
    if user_id:
        try:
            return CasePaperUser.objects.get(id=user_id)
        except CasePaperUser.DoesNotExist:
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
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

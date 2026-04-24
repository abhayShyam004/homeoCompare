"""WhatsApp utilities for clinic messaging (Meta WhatsApp Cloud API)."""

import logging
import re
from typing import Tuple

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _normalize_phone_number(raw_phone: str) -> str:
    """Convert input phone into WhatsApp API-friendly numeric E.164 (without '+')."""
    raw_phone = (raw_phone or '').strip()
    if not raw_phone:
        return ''

    starts_with_plus = raw_phone.startswith('+')
    digits = re.sub(r'\D', '', raw_phone)
    if not digits:
        return ''

    if digits.startswith('00'):
        digits = digits[2:]

    if starts_with_plus:
        return digits

    default_cc = str(getattr(settings, 'WHATSAPP_DEFAULT_COUNTRY_CODE', '91')).strip().lstrip('+')

    # If number looks local, prepend default country code.
    if len(digits) <= 10 and default_cc:
        return f"{default_cc}{digits}"

    return digits


def _build_booking_message(doctor, booking_request) -> str:
    doctor_name = (
        getattr(doctor, 'physician_name', '')
        or getattr(doctor, 'clinic_name', '')
        or getattr(doctor, 'username', '')
        or 'the clinic'
    )
    date_text = booking_request.requested_date.strftime('%d %b %Y') if booking_request.requested_date else 'Not specified'

    return (
        f"Hi {booking_request.patient_name}, your booking request with {doctor_name} has been received. "
        f"Preferred date: {date_text}. "
        "The clinic will contact you shortly to confirm the slot."
    )


def _dispatch_whatsapp_message(phone_number_id: str, access_token: str, payload: dict) -> Tuple[bool, str]:
    api_version = getattr(settings, 'WHATSAPP_META_API_VERSION', 'v20.0')
    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
    except requests.RequestException as exc:
        logger.warning('WhatsApp API request failed: %s', exc)
        return False, 'network error while contacting WhatsApp API'

    if response.status_code in (200, 201):
        return True, 'sent'

    try:
        data = response.json()
        error_message = data.get('error', {}).get('message') or data
    except Exception:
        error_message = response.text[:300]

    logger.warning('WhatsApp API error (%s): %s', response.status_code, error_message)
    return False, f"API error {response.status_code}: {error_message}"


def send_booking_confirmation_message(workspace, booking_request, doctor) -> Tuple[bool, str]:
    """
    Send booking confirmation message over WhatsApp.

    Returns: (success, note)
    """
    if not getattr(workspace, 'whatsapp_notifications_enabled', False):
        return False, 'notifications disabled by doctor settings'

    if not getattr(workspace, 'whatsapp_doctor_consent', False):
        return False, 'doctor consent not enabled'

    phone_number_id = (getattr(workspace, 'whatsapp_business_phone_number_id', '') or '').strip()
    if not phone_number_id:
        return False, 'doctor WhatsApp phone number ID is missing'

    access_token = (getattr(settings, 'WHATSAPP_META_ACCESS_TOKEN', '') or '').strip()
    if not access_token:
        return False, 'server WhatsApp API token is not configured'

    recipient = _normalize_phone_number(getattr(booking_request, 'phone', ''))
    if not recipient:
        return False, 'patient phone number is invalid'

    doctor_name = (
        getattr(doctor, 'physician_name', '')
        or getattr(doctor, 'clinic_name', '')
        or getattr(doctor, 'username', '')
        or 'Clinic'
    )
    date_text = booking_request.requested_date.strftime('%d %b %Y') if booking_request.requested_date else 'Not specified'

    template_name = (getattr(settings, 'WHATSAPP_BOOKING_TEMPLATE_NAME', '') or '').strip()
    language_code = (getattr(settings, 'WHATSAPP_TEMPLATE_LANGUAGE', 'en') or 'en').strip()

    if template_name:
        template_payload = {
            'messaging_product': 'whatsapp',
            'to': recipient,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': language_code},
                'components': [
                    {
                        'type': 'body',
                        'parameters': [
                            {'type': 'text', 'text': (booking_request.patient_name or 'Patient')[:60]},
                            {'type': 'text', 'text': doctor_name[:60]},
                            {'type': 'text', 'text': date_text[:60]},
                        ],
                    }
                ],
            },
        }
        sent, note = _dispatch_whatsapp_message(phone_number_id, access_token, template_payload)
        if sent:
            return True, note

        fallback_enabled = bool(getattr(settings, 'WHATSAPP_ALLOW_TEXT_FALLBACK', True))
        if not fallback_enabled:
            return False, note

    text_payload = {
        'messaging_product': 'whatsapp',
        'to': recipient,
        'type': 'text',
        'text': {
            'preview_url': False,
            'body': _build_booking_message(doctor, booking_request),
        },
    }

    return _dispatch_whatsapp_message(phone_number_id, access_token, text_payload)

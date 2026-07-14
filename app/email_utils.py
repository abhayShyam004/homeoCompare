"""
Email utilities for production-safe delivery.

Includes:
- SMTP configuration checks
- Retry-based synchronous send confirmation
- Optional background-thread helper
"""
import threading
import time
import logging
from smtplib import SMTPException

from django.core.mail import send_mail, get_connection
from django.conf import settings

logger = logging.getLogger(__name__)

_email_threads = []


def _get_runtime_email_config():
    """Return effective email config, allowing admin overrides from AccessPlatformSettings."""
    cfg = {
        'backend': getattr(settings, 'EMAIL_BACKEND', ''),
        'host': getattr(settings, 'EMAIL_HOST', ''),
        'port': getattr(settings, 'EMAIL_PORT', None),
        'use_tls': getattr(settings, 'EMAIL_USE_TLS', True),
        'user': getattr(settings, 'EMAIL_HOST_USER', ''),
        'password': getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
        'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', ''),
        'timeout': getattr(settings, 'EMAIL_TIMEOUT', 30),
    }

    try:
        from .models import AccessPlatformSettings

        runtime = AccessPlatformSettings.objects.filter(singleton_key='default').first()
        if runtime:
            if runtime.sender_email:
                cfg['user'] = runtime.sender_email
                cfg['from_email'] = runtime.sender_email
            if runtime.smtp_host:
                cfg['host'] = runtime.smtp_host
            if runtime.smtp_port:
                cfg['port'] = runtime.smtp_port
            cfg['use_tls'] = runtime.smtp_use_tls
            if runtime.smtp_app_password:
                cfg['password'] = runtime.smtp_app_password
    except Exception as exc:
        logger.warning("Failed to load runtime email overrides: %s", exc)

    return cfg


def is_email_service_configured():
    """Return True when required email settings are present."""
    cfg = _get_runtime_email_config()

    if cfg['backend'] == 'django.core.mail.backends.console.EmailBackend':
        return True

    required_values = {
        'EMAIL_HOST': cfg['host'],
        'EMAIL_HOST_USER': cfg['user'],
        'EMAIL_HOST_PASSWORD': cfg['password'],
        'EMAIL_PORT': cfg['port'],
    }

    missing = [key for key, value in required_values.items() if not value]
    if missing:
        logger.error("Email configuration incomplete. Missing: %s", ", ".join(missing))
        return False

    return True


def send_email_with_retry(subject, plain_message, recipient_email, html_message=None, max_retries=1, retry_delay_seconds=1.5):
    """
    Send an email synchronously with retry logic.

    Returns True only when SMTP confirms a message was queued.
    """
    if not is_email_service_configured():
        logger.error("Email service is not configured correctly")
        return False

    cfg = _get_runtime_email_config()
    from_email = cfg.get('from_email', '')
    if not from_email:
        logger.error("No DEFAULT_FROM_EMAIL or EMAIL_HOST_USER configured")
        return False

    connection = None
    if cfg['backend'] != 'django.core.mail.backends.console.EmailBackend':
        connection = get_connection(
            backend=cfg['backend'],
            host=cfg['host'],
            port=cfg['port'],
            username=cfg['user'],
            password=cfg['password'],
            use_tls=cfg['use_tls'],
            timeout=cfg.get('timeout', 5),
            fail_silently=False,
        )

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            result = send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False,
                connection=connection,
            )
            if result == 1:
                logger.info("Verification email sent to %s on attempt %s", recipient_email, attempt)
                return True

            last_error = RuntimeError(f"Unexpected send_mail result={result}")
            logger.warning("Email send returned result=%s for %s on attempt %s", result, recipient_email, attempt)
        except (SMTPException, TimeoutError, OSError, Exception) as exc:
            last_error = exc
            logger.warning("Email send failed for %s on attempt %s: %s", recipient_email, attempt, exc)

        if attempt < max_retries:
            time.sleep(retry_delay_seconds)

    logger.error("Failed to send email to %s after %s attempts: %s", recipient_email, max_retries, last_error)
    return False

def _send_via_resend_api(subject, plain_message, recipient_email, html_message, api_key, from_email):
    """Send email via Resend HTTP API to bypass SMTP port blocking."""
    import urllib.request
    import urllib.error
    import json
    
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "from": from_email,
        "to": [recipient_email],
        "subject": subject,
        "text": plain_message,
    }
    if html_message:
        data["html"] = html_message

    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status in (200, 201):
                logger.info("Email sent successfully via Resend API to %s", recipient_email)
                return True
            else:
                logger.warning("Resend API returned status %s", response.status)
                return False
    except urllib.error.URLError as e:
        logger.error("Failed to send email via Resend API: %s", e)
        return False

def send_email_async(subject, message, recipient_email, html_message=None):
    """
    Send email synchronously with retry logic.
    (Kept the function name `send_email_async` for compatibility but removed threading
    to prevent daemon thread death in production WSGI environments like Gunicorn).
    """
    import os
    resend_key = os.environ.get('RESEND_API_KEY')
    
    if resend_key:
        cfg = _get_runtime_email_config()
        # Resend requires a verified domain, or defaults to onboarding@resend.dev for testing to your own email
        from_email = cfg.get('from_email', '') or 'onboarding@resend.dev'
        
        logger.info("Starting email delivery via Resend HTTPS API to %s", recipient_email)
        return _send_via_resend_api(
            subject=subject, 
            plain_message=message, 
            recipient_email=recipient_email, 
            html_message=html_message, 
            api_key=resend_key,
            from_email=from_email
        )

    if not is_email_service_configured():
        logger.error("Email service not configured. Will not send to %s", recipient_email)
        return False
    
    logger.info("Starting synchronous email delivery to %s", recipient_email)
    return send_email_with_retry(
        subject=subject,
        plain_message=message,
        recipient_email=recipient_email,
        html_message=html_message,
    )

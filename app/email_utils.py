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

from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

_email_threads = []


def is_email_service_configured():
    """
    Return True when required email settings are present.
    """
    backend = getattr(settings, 'EMAIL_BACKEND', '')
    if backend == 'django.core.mail.backends.console.EmailBackend':
        return True

    host = getattr(settings, 'EMAIL_HOST', '')
    user = getattr(settings, 'EMAIL_HOST_USER', '')
    password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    port = getattr(settings, 'EMAIL_PORT', None)
    return bool(host and user and password and port)


def send_email_with_retry(subject, plain_message, recipient_email, html_message=None, max_retries=3, retry_delay_seconds=1.5):
    """
    Send an email synchronously with retry logic.

    Returns True only when SMTP confirms a message was queued.
    """
    if not is_email_service_configured():
        logger.error("Email service is not configured correctly")
        return False

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', '')
    if not from_email:
        logger.error("No DEFAULT_FROM_EMAIL or EMAIL_HOST_USER configured")
        return False

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


def send_email_async(subject, message, recipient_email, html_message=None):
    """
    Send email asynchronously in a background thread.
    
    Returns immediately without waiting for email to send.
    Email is sent in background - request completes before SMTP handshake.
    
    Args:
        subject: Email subject
        message: Plain text message
        recipient_email: Recipient email address
        html_message: HTML version of message (optional)
    
    Returns:
        True if thread started successfully, False if failed to start
    """
    
    def send_email_thread():
        send_email_with_retry(
            subject=subject,
            plain_message=message,
            recipient_email=recipient_email,
            html_message=html_message,
        )

    try:
        thread = threading.Thread(target=send_email_thread, daemon=False, name=f"email-{recipient_email}")
        thread.start()
        _email_threads.append(thread)
        _email_threads[:] = [t for t in _email_threads if t.is_alive()]
        return True
    except Exception as exc:
        logger.error("Error starting email thread: %s", exc)
        return False

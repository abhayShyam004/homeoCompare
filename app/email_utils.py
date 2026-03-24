"""
Asynchronous email utilities
Sends emails in background threads to prevent blocking request handlers
"""
import threading
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_email_async(subject, message, recipient_email, html_message=None):
    """
    Send email asynchronously in a background thread.
    
    This prevents blocking the request handler and causing worker timeouts.
    
    Args:
        subject: Email subject
        message: Plain text message
        recipient_email: Recipient email address
        html_message: HTML version of message (optional)
    
    Returns:
        True if thread started successfully, False otherwise
    """
    def send_email_thread():
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient_email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"✓ Verification email sent to {recipient_email}")
        except Exception as e:
            logger.error(f"✗ Error sending email to {recipient_email}: {str(e)}")
    
    try:
        # Start email sending in background thread
        thread = threading.Thread(target=send_email_thread, daemon=True)
        thread.start()
        return True
    except Exception as e:
        logger.error(f"✗ Error starting email thread: {str(e)}")
        return False

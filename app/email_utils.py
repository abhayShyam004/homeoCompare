"""
Asynchronous email utilities
Sends emails in background threads to prevent blocking request handlers
"""
import threading
from django.core.mail import send_mail
from django.conf import settings
import logging
import sys

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
            print(f"📧 [EMAIL THREAD] Starting async email send to {recipient_email}", file=sys.stderr)
            print(f"📧 [EMAIL THREAD] Backend: {settings.EMAIL_BACKEND}", file=sys.stderr)
            print(f"📧 [EMAIL THREAD] Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}", file=sys.stderr)
            print(f"📧 [EMAIL THREAD] User: {settings.EMAIL_HOST_USER}", file=sys.stderr)
            
            result = send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            print(f"✅ [EMAIL SUCCESS] Email sent to {recipient_email} (result={result})", file=sys.stderr)
            logger.info(f"✓ Verification email sent to {recipient_email}")
            
        except Exception as e:
            print(f"❌ [EMAIL ERROR] Failed to send email to {recipient_email}: {str(e)}", file=sys.stderr)
            logger.error(f"✗ Error sending email to {recipient_email}: {str(e)}")
    
    try:
        print(f"🔄 [EMAIL THREAD] Creating background thread for {recipient_email}", file=sys.stderr)
        # Start email sending in background thread
        thread = threading.Thread(target=send_email_thread, daemon=True)
        thread.start()
        print(f"🔄 [EMAIL THREAD] Thread started successfully", file=sys.stderr)
        return True
    except Exception as e:
        print(f"❌ [EMAIL THREAD ERROR] Failed to start email thread: {str(e)}", file=sys.stderr)
        logger.error(f"✗ Error starting email thread: {str(e)}")
        return False

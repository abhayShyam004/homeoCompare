"""
Asynchronous email utilities
Sends emails in background threads to prevent blocking request handlers
"""
import threading
import time
from django.core.mail import send_mail
from django.conf import settings
import logging
import sys

logger = logging.getLogger(__name__)

# Keep track of email threads to prevent premature termination
_email_threads = []


def send_email_async(subject, message, recipient_email, html_message=None):
    """
    Send email asynchronously in a background thread.
    
    This prevents blocking the request handler and causing worker timeouts.
    Uses non-daemon threads with timeout to ensure email is sent.
    
    Args:
        subject: Email subject
        message: Plain text message
        recipient_email: Recipient email address
        html_message: HTML version of message (optional)
    
    Returns:
        True if email sent successfully, False if failed
    """
    email_sent = {'success': False, 'error': None}
    
    def send_email_thread():
        try:
            print(f"📧 [EMAIL] Starting email send to {recipient_email}", file=sys.stderr)
            print(f"📧 [EMAIL] Backend: {settings.EMAIL_BACKEND}", file=sys.stderr)
            print(f"📧 [EMAIL] Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}", file=sys.stderr)
            
            result = send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            print(f"✅ [EMAIL SUCCESS] Email sent to {recipient_email}", file=sys.stderr)
            logger.info(f"✓ Verification email sent to {recipient_email}")
            email_sent['success'] = True
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ [EMAIL ERROR] Failed to send to {recipient_email}: {error_msg}", file=sys.stderr)
            logger.error(f"✗ Error sending email: {error_msg}")
            email_sent['error'] = error_msg
    
    try:
        print(f"🔄 [EMAIL] Creating thread for {recipient_email}", file=sys.stderr)
        
        # Use non-daemon thread so it completes even after request ends
        thread = threading.Thread(target=send_email_thread, daemon=False, name=f"email-{recipient_email}")
        thread.start()
        
        # Store thread reference to prevent garbage collection
        _email_threads.append(thread)
        
        # Wait up to 10 seconds for email to send
        # This is long enough for SMTP to complete but short enough to not block
        thread.join(timeout=10)
        
        if thread.is_alive():
            print(f"⚠️  [EMAIL WARNING] Thread still running after 10s timeout for {recipient_email}", file=sys.stderr)
        
        # Clean up old threads
        _email_threads[:] = [t for t in _email_threads if t.is_alive()]
        
        return email_sent['success']
        
    except Exception as e:
        print(f"❌ [EMAIL THREAD ERROR] Failed to start thread: {str(e)}", file=sys.stderr)
        logger.error(f"✗ Error starting email thread: {str(e)}")
        return False

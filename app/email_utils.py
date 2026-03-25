"""
Asynchronous email utilities
Sends emails in background threads to prevent blocking request handlers
"""
import threading
from django.core.mail import send_mail, get_connection, EmailMessage
from django.conf import settings
import logging
import sys

logger = logging.getLogger(__name__)

# Keep track of email threads to prevent premature termination
_email_threads = []


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
        try:
            print(f"📧 [EMAIL] Starting email send to {recipient_email}", file=sys.stderr)
            print(f"📧 [EMAIL] Backend: {settings.EMAIL_BACKEND}", file=sys.stderr)
            print(f"📧 [EMAIL] Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}", file=sys.stderr)
            
            # Use connection with custom timeout
            connection = get_connection(
                backend=settings.EMAIL_BACKEND,
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
                timeout=getattr(settings, 'EMAIL_TIMEOUT', 30),
            )
            
            email = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient_email],
                connection=connection,
            )
            if html_message:
                email.attach_alternative(html_message, "text/html")
            
            email.send()
            
            print(f"✅ [EMAIL SUCCESS] Email sent to {recipient_email}", file=sys.stderr)
            logger.info(f"✓ Verification email sent to {recipient_email}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ [EMAIL ERROR] Failed to send to {recipient_email}: {error_msg}", file=sys.stderr)
            logger.error(f"✗ Error sending email: {error_msg}")
    
    try:
        print(f"🔄 [EMAIL] Starting background thread for {recipient_email}", file=sys.stderr)
        
        # Use non-daemon thread so it completes even after request ends
        thread = threading.Thread(target=send_email_thread, daemon=False, name=f"email-{recipient_email}")
        thread.start()
        
        # Store thread reference to prevent garbage collection
        _email_threads.append(thread)
        
        # Clean up completed threads periodically
        _email_threads[:] = [t for t in _email_threads if t.is_alive()]
        
        print(f"✓ [EMAIL] Thread started - returning immediately (no wait)", file=sys.stderr)
        
        # IMPORTANT: Return immediately without waiting
        # The thread will continue in background even after request completes
        return True
        
    except Exception as e:
        print(f"❌ [EMAIL THREAD ERROR] Failed to start thread: {str(e)}", file=sys.stderr)
        logger.error(f"✗ Error starting email thread: {str(e)}")
        return False

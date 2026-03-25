"""
Email configuration test view - Use this to diagnose email issues
"""
import json
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
import sys


@require_http_methods(["GET"])
def test_email_config(request):
    """Test endpoint to check email configuration"""
    
    try:
        config_info = {
            "debug": settings.DEBUG,
            "email_backend": settings.EMAIL_BACKEND,
            "email_host": settings.EMAIL_HOST,
            "email_port": settings.EMAIL_PORT,
            "email_use_tls": settings.EMAIL_USE_TLS,
            "email_host_user": settings.EMAIL_HOST_USER if settings.EMAIL_HOST_USER else "NOT SET ❌",
            "email_host_password": "SET ✓" if settings.EMAIL_HOST_PASSWORD else "NOT SET ❌",
            "default_from_email": settings.DEFAULT_FROM_EMAIL,
        }
        
        # Determine status
        if settings.DEBUG:
            status = "⚠️ DEBUG=True (using console backend)"
        elif settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            status = "❌ Using CONSOLE backend in production!"
        elif not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            status = "❌ Email credentials NOT set"
        else:
            status = "✅ Email configured correctly"
        
        message = f"""
        EMAIL CONFIGURATION DIAGNOSTIC
        
        Status: {status}
        
        Settings:
        - DEBUG: {config_info['debug']}
        - EMAIL_BACKEND: {config_info['email_backend']}
        - EMAIL_HOST: {config_info['email_host']}
        - EMAIL_PORT: {config_info['email_port']}
        - EMAIL_USE_TLS: {config_info['email_use_tls']}
        - EMAIL_HOST_USER: {config_info['email_host_user']}
        - EMAIL_HOST_PASSWORD: {config_info['email_host_password']}
        - DEFAULT_FROM_EMAIL: {config_info['default_from_email']}
        
        If email credentials show "NOT SET", add these to Render environment variables:
        - DEBUG=False
        - EMAIL_HOST=smtp.gmail.com
        - EMAIL_PORT=587
        - EMAIL_USE_TLS=True
        - EMAIL_HOST_USER=abhay315204@gmail.com
        - EMAIL_HOST_PASSWORD=your-app-password
        """
        
        print(message, file=sys.stderr)
        
        return JsonResponse({
            "status": "ok",
            "message": message,
            "config": config_info
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e)
        }, status=500)

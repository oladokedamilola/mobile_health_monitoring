from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

def email_verification_required(view_func):
    """
    Decorator for function-based views that checks if user has verified their email.
    Admin/superuser are exempt from this check.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Allow access for admin/superuser
            if request.user.is_superuser or request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            # Check if email is verified
            if not getattr(request.user, 'is_email_verified', False):
                messages.warning(
                    request, 
                    'Please verify your email address to access this page.'
                )
                return redirect('accounts:email_verification_required')  # Create this view
                
        return view_func(request, *args, **kwargs)
    return _wrapped_view
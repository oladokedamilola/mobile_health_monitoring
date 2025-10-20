# accounts/utils.py
import secrets
from datetime import timedelta, datetime
from django.utils import timezone
from django.core.mail import send_mail, BadHeaderError
from django.urls import reverse
from django.conf import settings
from .models import CustomUser, PasswordResetToken, PasswordResetAttempt

User = CustomUser

# ================================
# 🔑 Email Verification Handling
# ================================

def generate_email_token() -> str:
    """Generate a secure token for email verification."""
    return secrets.token_urlsafe(32)

def send_verification_email(user: User, request) -> bool:
    """
    Send an email verification link to the user's email.
    Returns True if successful, False otherwise.
    """
    print(f"🔍 DEBUG: Starting send_verification_email for {user.email}")
    
    if user.is_email_verified:
        print(f"ℹ️ User {user.email} is already verified")
        return False

    # Check rate limiting
    if not user.can_resend_verification():
        print(f"⏳ User {user.email} is rate limited until {user.verification_rate_limit_expiry}")
        return False

    # Generate secure token and expiry
    token = generate_email_token()
    expiry = timezone.now() + timedelta(hours=24)
    print(f"🔍 DEBUG: Generated token: {token}")

    # Save token to DB
    user.email_verification_token = token
    user.email_verification_expiry = expiry
    user.save(update_fields=["email_verification_token", "email_verification_expiry"])
    print(f"🔍 DEBUG: Token saved to database")

    # Build verification URL
    verification_url = request.build_absolute_uri(
        reverse("accounts:verify_email", kwargs={"token": token})
    )
    print(f"🔍 DEBUG: Verification URL: {verification_url}")

    subject = "✅ Verify Your Email - Auralis Health"
    message = f"""
Hi {user.get_full_name() or user.email},

Welcome to Auralis Health! Please verify your email address by clicking the link below:

{verification_url}

This verification link will expire in 24 hours.

If you did not sign up for an account, please ignore this email.

Thanks,
The Auralis Health Team
"""

    try:
        print(f"🔍 DEBUG: Attempting to send email via send_mail...")
        print(f"🔍 DEBUG: From: {settings.DEFAULT_FROM_EMAIL}")
        print(f"🔍 DEBUG: To: {user.email}")
        print(f"🔍 DEBUG: Subject: {subject}")
        
        sent_count = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        print(f"🔍 DEBUG: send_mail returned: {sent_count}")
        
        if sent_count == 1:
            # Track the verification request
            user.mark_verification_sent()
            print(f"✅ Verification email sent to {user.email}")
            return True
        else:
            print(f"⚠️ send_mail returned 0 for {user.email}")
            return False
            
    except BadHeaderError as e:
        print(f"⚠️ Invalid header when sending verification email to {user.email}: {str(e)}")
        return False
    except Exception as e:
        print(f"⚠️ Could not send verification email to {user.email}: {str(e)}")
        print(f"🔍 DEBUG: Exception type: {type(e).__name__}")
        import traceback
        print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        return False

def verify_email_token(token: str) -> bool:
    """
    Verify the email verification token.
    Returns True if successful, False otherwise.
    """
    try:
        user = User.objects.get(email_verification_token=token)
    except User.DoesNotExist:
        print(f"❌ Invalid verification token")
        return False
    except User.MultipleObjectsReturned:
        print(f"❌ Multiple users found with same verification token")
        return False
    except Exception as e:
        print(f"⚠️ Error fetching user in verify_email_token: {str(e)}")
        return False

    try:
        # Check expiry
        if user.email_verification_expiry and timezone.now() <= user.email_verification_expiry:
            user.is_email_verified = True
            user.email_verification_token = None
            user.email_verification_expiry = None
            user.verification_sent_count = 0  # Reset rate limiting counter
            user.verification_rate_limit_expiry = None
            user.save(update_fields=[
                "is_email_verified", 
                "email_verification_token", 
                "email_verification_expiry",
                "verification_sent_count",
                "verification_rate_limit_expiry"
            ])
            print(f"✅ Email verified successfully for {user.email}")
            return True
        else:
            print(f"❌ Verification token expired for {user.email}")
            # Clean up expired token
            user.email_verification_token = None
            user.email_verification_expiry = None
            user.save(update_fields=["email_verification_token", "email_verification_expiry"])
            return False
    except Exception as e:
        print(f"⚠️ Error updating user in verify_email_token: {str(e)}")
        return False

# ===================================
# 🔑 Password Reset Handling
# ===================================
def generate_password_reset_token():
    """Generates a random secure token."""
    return secrets.token_urlsafe(32)

def send_password_reset_email(user, request=None):
    """Send password reset email with reset link."""
    try:
        # Check for recent attempts using the model method
        recent_attempts = PasswordResetAttempt.recent_attempts(user, minutes=30)
        if recent_attempts >= 5:
            print(f"⏳ Too many password reset attempts for {user.email}")
            return False

        # Generate and save token
        token = generate_password_reset_token()
        
        # Invalidate any existing tokens for this user
        PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
        
        # Create new token
        PasswordResetToken.objects.create(user=user, token=token)
        
        # Record the attempt
        client_ip = get_client_ip(request) if request else None
        PasswordResetAttempt.objects.create(user=user, ip_address=client_ip)
        
        # Build reset URL
        if request:
            reset_url = request.build_absolute_uri(
                reverse("accounts:password_reset_confirm", kwargs={"token": token})
            )
        else:
            # fallback: construct with domain if request not passed
            domain = getattr(settings, "DOMAIN", "http://localhost:8000")
            reset_url = f"{domain}{reverse('accounts:password_reset_confirm', kwargs={'token': token})}"

        subject = "🔑 Reset Your Password - Auralis Health"
        message = f"""
Hi {user.get_full_name() or user.email},

You requested to reset your password for your Auralis Health account. 
Click the link below to set a new password:

{reset_url}

This password reset link will expire in 1 hour.

If you did not request this password reset, please ignore this email. 
Your account remains secure.

Thanks,  
The Auralis Health Team
"""

        sent_count = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        if sent_count == 1:
            print(f"✅ Password reset email sent to {user.email}")
            return True
        else:
            print(f"⚠️ Password reset email failed to send for {user.email}")
            return False
            
    except Exception as e:
        print(f"⚠️ Error in send_password_reset_email: {str(e)}")
        return False

def verify_password_reset_token(token: str):
    """
    Verify if a password reset token is valid and not expired.
    Returns the token object if valid, None otherwise.
    """
    try:
        reset_token = PasswordResetToken.objects.get(token=token, used=False)
        
        if reset_token.is_expired():
            print(f"❌ Password reset token expired for user {reset_token.user.email}")
            # Mark as used to clean up
            reset_token.used = True
            reset_token.save(update_fields=['used'])
            return None
            
        return reset_token
        
    except PasswordResetToken.DoesNotExist:
        print(f"❌ Invalid or used password reset token")
        return None
    except Exception as e:
        print(f"⚠️ Error verifying password reset token: {str(e)}")
        return None

def cleanup_expired_tokens():
    """Clean up expired password reset tokens."""
    try:
        expired_tokens = PasswordResetToken.objects.filter(
            created_at__lt=timezone.now() - timedelta(hours=1)
        )
        count = expired_tokens.count()
        expired_tokens.delete()
        print(f"🧹 Cleaned up {count} expired password reset tokens")
        return count
    except Exception as e:
        print(f"⚠️ Error cleaning up expired tokens: {str(e)}")
        return 0

# ===================================
# ⏰ Time-based greeting
# ===================================
def time_sensitive_greeting(user):
    """Return a greeting based on the current time of day."""
    try:
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        name = user.first_name or user.username
        return f"{greeting}, {name}!"
    except Exception as e:
        print(f"⚠️ Error generating greeting for {user.email}: {str(e)}")
        return f"Hello, {user.username}!"

# ===================================
# 🔧 Utility Functions
# ===================================
def get_client_ip(request):
    """Get client IP address for rate limiting"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
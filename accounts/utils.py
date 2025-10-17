# accounts/utils.py
import secrets
import random
from datetime import timedelta, datetime
from django.utils import timezone
from django.core.mail import send_mail, BadHeaderError
from django.urls import reverse
from django.conf import settings
from .models import CustomUser, PasswordResetToken

User = CustomUser

# ================================
# 🔑 Token generation and handling
# ================================

def generate_email_token() -> str:
    """Generate a 6-digit numeric token for email verification."""
    return f"{random.randint(100000, 999999)}"

def generate_verification_method() -> str:
    """Randomly choose whether to send a clickable link or just a token."""
    return random.choice(["link", "token"])

def send_verification_email(user: User, request, method: str = None) -> str | None:
    """
    Send an email verification to the user's email.
    """
    if user.is_email_verified:
        return None  # Already verified

    # Check rate limiting
    if not user.can_resend_verification():
        print(f"⏳ User {user.email} is rate limited until {user.verification_rate_limit_expiry}")
        return None

    # Use the same method if session already has one
    if not method:
        method = request.session.get("email_verification_method")

    # If still not set, randomly choose
    if method not in ["link", "token"]:
        method = generate_verification_method()

    # Generate token and expiry
    token = generate_email_token()
    expiry = timezone.now() + timedelta(hours=24)

    # Save token to DB
    user.email_verification_token = token
    user.email_verification_expiry = expiry
    user.save(update_fields=["email_verification_token", "email_verification_expiry"])

    subject = "✅ Verify Your Email - Auralis Health"

    if method == "link":
        verification_url = request.build_absolute_uri(
            reverse("accounts:verify_email") + f"?token={token}&email={user.email}"
        )
        message = f"""
Hi {user.get_full_name() or user.email},

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you did not sign up for an account, please ignore this email.

Thanks,
Auralis Health Team
"""
    else:  # token method
        message = f"""
Hi {user.get_full_name() or user.email},

Use the following token to verify your email: {token}

This token will expire in 24 hours.

If you did not sign up for an account, please ignore this email.

Thanks,
Auralis Health Team
"""

    try:
        sent_count = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        if sent_count == 1:
            # Track request
            request.session["email_verification_method"] = method
            user.mark_verification_sent()
            return method
        else:
            print(f"⚠️ send_mail returned 0 for {user.email}")
            return None
    except BadHeaderError:
        print(f"⚠️ Invalid header when sending to {user.email}")
        return None
    except Exception as e:
        print(f"⚠️ Could not send verification email to {user.email}: {str(e)}")
        return None

def verify_email_token(token: str, email: str) -> bool:
    """
    Verify the token for a given email. Returns True if successful.
    """
    try:
        user = User.objects.get(email=email, email_verification_token=token)
    except User.DoesNotExist:
        return False
    except Exception as e:
        print(f"⚠️ Error fetching user in verify_email_token: {str(e)}")
        return False

    try:
        # Check expiry
        if user.email_verification_expiry and timezone.now() <= user.email_verification_expiry:
            user.is_email_verified = True
            user.email_verification_token = ""
            user.email_verification_expiry = None
            user.save(update_fields=["is_email_verified", "email_verification_token", "email_verification_expiry"])
            return True
    except Exception as e:
        print(f"⚠️ Error updating user in verify_email_token: {str(e)}")

    return False

# ===================================
# 🔑 Password reset token handling
# ===================================
def generate_password_reset_token():
    """Generates a random secure token."""
    return secrets.token_urlsafe(32)

def send_password_reset_email(user, token, request=None):
    """Send password reset email with proper absolute URL."""
    try:
        if request:
            reset_url = request.build_absolute_uri(
                reverse("accounts:password_reset_confirm", args=[token])
            )
        else:
            # fallback: construct with domain if request not passed
            domain = getattr(settings, "DOMAIN", "http://localhost:8000")
            reset_url = f"{domain}{reverse('accounts:password_reset_confirm', args=[token])}"

        subject = "🔑 Reset Your Password - Auralis Health"
        message = f"""
Hi {user.get_full_name() or user.email},

You requested to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 1 hour.

If you did not request this, you can ignore this email.

Thanks,  
Auralis Health Team
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"⚠️ Error in send_password_reset_email: {str(e)}")
        return False

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
    
    
    
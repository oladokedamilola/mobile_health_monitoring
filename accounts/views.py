# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .forms import RegisterForm, LoginForm, ProfileForm, PasswordResetRequestForm, PasswordResetForm
from .services.user_service import UserService
from monitoring.models import HealthRecord, ActivityRecord
from analytics.models import Anomaly, HealthSummary
from .models import DoctorVerification, PasswordResetToken, PasswordResetAttempt
from .forms import DoctorVerificationForm
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta
from django.http import JsonResponse
from django.conf import settings
from .models import CustomUser
from .utils import send_verification_email, verify_email_token, send_password_reset_email, verify_password_reset_token, get_client_ip
from .decorators import email_verification_required

User = get_user_model()

# Initialize service
user_service = UserService()

# ------------------------------------------------------
# 🧍‍♂️ Register View (with role selection)
# ------------------------------------------------------
@csrf_exempt
def register_view(request, role=None):
    """Handles user registration using UserService, with optional preselected role."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    # Normalize role value
    allowed_roles = ['patient', 'doctor', 'admin']
    role = role.lower() if role else None
    if role and role not in allowed_roles:
        messages.error(request, "Invalid role selection.")
        return redirect('accounts:register')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            selected_role = role or data.get('role', 'patient')
            try:
                user = user_service.register(
                    username=data['username'],
                    email=data['email'],
                    password=data['password1'],
                    role=selected_role,
                )
                # Send verification email after registration
                if user:
                    if send_verification_email(user, request):
                        messages.success(
                            request, 
                            "Registration successful! Please check your email to verify your account."
                        )
                    else:
                        messages.warning(
                            request,
                            "Registration successful, but we couldn't send the verification email. "
                            "You can request a new verification link from your profile."
                        )
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f"Registration failed: {e}")
    else:
        # Prefill role if passed via URL
        initial_data = {'role': role} if role else {}
        form = RegisterForm(initial=initial_data)

    return render(request, 'accounts/register.html', {
        'form': form,
        'selected_role': role,  
    })

# ----------------------------
# ✉ Email Verification
# ----------------------------
@login_required
def verify_email_notice(request):
    """
    Email verification page - only shows verification link status
    """
    try:
        user = request.user

        if user.is_email_verified:
            messages.success(request, "✅ Your email is already verified.")
            return redirect("accounts:dashboard")

        # Check hard cooldown
        if user.verification_rate_limit_expiry and user.verification_rate_limit_expiry > timezone.now():
            remaining = (user.verification_rate_limit_expiry - timezone.now()).total_seconds()
            if remaining > 60:
                return render(request, "accounts/verification_cooldown.html", {"user": user})

        # Send initial verification email if not already sent
        if not user.email_verification_token:
            if not send_verification_email(user, request):
                messages.error(request, "⚠️ Could not send verification email. Please try again later.")
                return redirect("accounts:dashboard")

        # Handle RESEND
        if request.method == "POST" and "resend" in request.POST:
            if not user.can_resend_verification():
                return render(request, "accounts/verification_cooldown.html", {"user": user})
            
            if send_verification_email(user, request):
                messages.success(request, "📧 A new verification link has been sent to your email.")
                if settings.DEBUG:
                    # Show debug link in development - UPDATED to match new URL pattern
                    debug_link = request.build_absolute_uri(
                        reverse("accounts:verify_email", kwargs={"token": user.email_verification_token})
                    )
                    messages.info(request, f"[DEV] Verification Link: {debug_link}")
            else:
                return render(request, "accounts/verification_cooldown.html", {"user": user})

        # Generate verification link for display - UPDATED to match new URL pattern
        verification_link = None
        if user.email_verification_token:
            verification_link = request.build_absolute_uri(
                reverse("accounts:verify_email", kwargs={"token": user.email_verification_token})
            )

        # Soft cooldown (frontend timer)
        countdown_seconds = 60
        if user.verification_rate_limit_expiry and user.verification_rate_limit_expiry > timezone.now():
            remaining = (user.verification_rate_limit_expiry - timezone.now()).total_seconds()
            countdown_seconds = int(min(remaining, 60))

        return render(request, "accounts/verify_email.html", {
            "user": user,
            "verification_link": verification_link,
            "countdown_seconds": countdown_seconds,
            "show_resend": True,
        })

    except Exception as e:
        print(f"⚠️ Exception in verify_email_notice: {str(e)}")
        messages.error(request, f"⚠️ An unexpected error occurred: {str(e)}")
        return redirect("accounts:dashboard")

def verify_email(request, token=None):
    """
    Verify the user email via direct verification link
    UPDATED: Now uses URL parameter instead of query string
    """
    # Support both URL pattern (token in URL) and legacy query string
    if not token:
        token = request.GET.get("token")
    
    if not token:
        messages.error(request, "❌ Invalid verification link.")
        return redirect("accounts:login")

    # UPDATED: Only pass token to the function (no email needed)
    if verify_email_token(token):
        messages.success(request, "✅ Your email has been verified successfully!")
    else:
        messages.error(request, "❌ Verification failed or link has expired.")

    return redirect("accounts:login")

# ----------------------------
# 🔄 Password Reset Views
# ----------------------------
RESET_LIMIT = 3
RESET_WINDOW_MINUTES = 30

def password_reset_request(request):
    """Request password reset (step 1)."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].lower()
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Don't reveal whether email exists
                messages.success(
                    request,
                    "✅ If an account exists with that email, we've sent a password reset link. Please check your inbox."
                )
                return redirect("accounts:login")
            
            # Rate limiting
            attempts = PasswordResetAttempt.recent_attempts(user, minutes=RESET_WINDOW_MINUTES)
            if attempts >= RESET_LIMIT:
                messages.error(
                    request,
                    f"⚠️ Maximum {RESET_LIMIT} reset attempts allowed in {RESET_WINDOW_MINUTES} minutes. Please try again later."
                )
                return redirect("accounts:password_reset_request")
            
            # Log attempt
            PasswordResetAttempt.objects.create(user=user, ip_address=get_client_ip(request))
            
            # Send password reset email
            if send_password_reset_email(user, request):
                messages.success(
                    request,
                    "✅ If an account exists with that email, we've sent a password reset link. Please check your inbox."
                )
            else:
                messages.error(
                    request,
                    "⚠️ Failed to send reset email. Please try again later."
                )
            return redirect("accounts:login")
    else:
        form = PasswordResetRequestForm()
    
    return render(request, "accounts/password_reset_request.html", {"form": form})

def password_reset_confirm(request, token):
    """Reset password using token (step 2)."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    # Verify the reset token
    reset_token = verify_password_reset_token(token)
    
    if not reset_token:
        messages.error(request, "❌ This reset link is invalid or has expired.")
        return redirect("accounts:password_reset_request")
    
    if request.method == "POST":
        form = PasswordResetForm(reset_token.user, request.POST)
        if form.is_valid():
            form.save()
            reset_token.used = True
            reset_token.save()
            messages.success(request, "✅ Password reset successful. You can now log in.")
            return redirect("accounts:login")
    else:
        form = PasswordResetForm(reset_token.user)
    
    return render(request, "accounts/password_reset_confirm.html", {
        "form": form,
        "token": token
    })

# ------------------------------------------------------
# 🏠 Dashboard Redirect View
# ------------------------------------------------------
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@login_required
def dashboard_redirect(request):
    """
    Smart dashboard redirect with comprehensive verification logic
    and role-based routing for Auralis Health platform.
    """
    user = request.user
    
    # Log dashboard access for monitoring
    logger.info(f"Dashboard access attempt by user: {user.username} (Role: {user.role}, Superuser: {user.is_superuser}, Staff: {user.is_staff})")
    
    try:
        # 🔐 Check email verification (admin users are exempt)
        if not _is_user_email_verified(user):
            logger.warning(f"User {user.username} attempted dashboard access without email verification")
            messages.warning(
                request,
                "Please verify your email address to access the dashboard."
            )
            return redirect("accounts:verify_email_notice")
        
        # 🛡️ ADMIN ROUTING - Check superuser/staff status FIRST (most important)
        if user.is_superuser or user.is_staff:
            # Ensure superusers/staff have admin role set
            if user.role != "admin":
                user.role = "admin"
                user.save()
                logger.info(f"Updated superuser/staff {user.username} role to 'admin'")
            
            logger.info(f"Admin dashboard access: {user.username} (superuser/staff)")
            return redirect('admin_dashboard')
        
        # Check admin role for non-superuser admin users
        elif user.role == "admin":
            logger.info(f"Admin dashboard access: {user.username} (role=admin)")
            return redirect('admin_dashboard')
        
        # 🩺 DOCTOR ROUTING with comprehensive verification
        elif user.role == "doctor":
            return _handle_doctor_redirect(request, user)
        
        # 👤 PATIENT ROUTING (default)
        else:
            # Ensure patient role is set correctly for non-admin, non-doctor users
            if user.role not in ["patient", "admin", "doctor"]:
                user.role = "patient"
                user.save()
                logger.warning(f"User {user.username} had invalid role '{user.role}', set to 'patient'")
            
            logger.info(f"Patient dashboard access: {user.username}")
            return redirect("patient_dashboard")
            
    except Exception as e:
        # Comprehensive error handling
        logger.error(f"Dashboard redirect error for user {user.username}: {str(e)}", exc_info=True)
        messages.error(
            request, 
            f"We encountered an issue redirecting you to your dashboard. Please try again. Error: {str(e)}"
        )
        # Fallback to profile page which should always be accessible
        return redirect("accounts:profile")

def _is_user_email_verified(user):
    """
    Check if user's email is verified.
    Admin users (superuser, staff, or role=admin) are exempt from email verification.
    """
    # Admin users are exempt from email verification
    if user.is_superuser or user.is_staff or user.role == "admin":
        return True
    
    # For non-admin users, check email verification status
    return user.is_email_verified

def _handle_doctor_redirect(request, user):
    """
    Handle doctor-specific verification and routing logic
    """
    from .models import DoctorVerification
    
    try:
        verification = DoctorVerification.objects.filter(user=user).first()
        
        # Case 1: No verification record exists
        if not verification:
            logger.warning(f"Doctor {user.username} has no verification record, redirecting to verification")
            messages.info(
                request,
                "Please complete your doctor verification to access the dashboard."
            )
            return redirect("accounts:doctor_verification")
        
        # Case 2: Verification is pending
        if verification.status == "pending":
            # Check if verification is stuck (older than 7 days)
            if verification.submitted_at and (timezone.now() - verification.submitted_at).days > 7:
                messages.warning(
                    request,
                    "Your verification has been pending for over a week. "
                    "Please contact support if this continues."
                )
            else:
                messages.info(
                    request,
                    "Your verification is under review. We'll notify you once it's complete."
                )
            return redirect("accounts:verification_status")
        
        # Case 3: Verification was rejected
        if verification.status == "rejected":
            rejection_reason = verification.remarks or "Please review and resubmit your details."
            messages.error(
                request,
                f"Verification rejected: {rejection_reason} "
                "Please update your information and resubmit."
            )
            return redirect("accounts:doctor_verification")
        
        # Case 4: Verification is approved but is_verified flag not set
        if verification.status == "approved" and not user.is_verified:
            user.is_verified = True  # This is only for doctors
            user.save()
            logger.info(f"Auto-updated is_verified for doctor {user.username}")
        
        # Case 5: Successfully verified doctor
        if verification.status == "approved":
            logger.info(f"Verified doctor dashboard access: {user.username}")
            # Add welcome message for first-time access after verification
            if not getattr(user, '_verification_accessed', False):
                messages.success(
                    request,
                    "Welcome to your doctor dashboard! You can now monitor patient data."
                )
                user._verification_accessed = True
            
            return redirect("doctor_dashboard")
        
        # Fallback for unexpected verification states
        logger.error(f"Unexpected verification state for doctor {user.username}: {verification.status}")
        messages.error(
            request,
            "There's an issue with your verification status. Please contact support."
        )
        return redirect("accounts:verification_status")
        
    except Exception as e:
        logger.error(f"Doctor verification error for {user.username}: {str(e)}", exc_info=True)
        messages.error(
            request,
            "We encountered an issue verifying your doctor status. Please try again or contact support."
        )
        return redirect("accounts:verification_status")

# Health check endpoint for monitoring
@login_required
def dashboard_health_check(request):
    """
    Health check endpoint to verify user can access their appropriate dashboard
    """
    from django.http import JsonResponse
    
    user = request.user
    health_data = {
        'user': user.username,
        'role': user.role,
        'is_authenticated': user.is_authenticated,
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'has_profile': hasattr(user, 'profile_picture') and bool(user.profile_picture),
    }
    
    # Only include is_verified for doctors
    if user.role == "doctor":
        health_data['is_verified'] = user.is_verified
        from .models import DoctorVerification
        verification = DoctorVerification.objects.filter(user=user).first()
        health_data.update({
            'verification_status': verification.status if verification else 'none',
            'verification_id': verification.id if verification else None,
        })
    
    return JsonResponse(health_data)

# ------------------------------------------------------
# 📧 Email Verification Required Decorator
# ------------------------------------------------------
def email_verification_required(view_func):
    """
    Decorator to ensure user has verified their email before accessing a view.
    Admin users are exempt from this requirement.
    """
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        
        # Skip check for anonymous users (they'll be redirected by login_required)
        if not user.is_authenticated:
            return view_func(request, *args, **kwargs)
        
        # Admin users are exempt from email verification
        if _is_user_email_verified(user):
            return view_func(request, *args, **kwargs)
        
        # Non-admin users without email verification
        logger.warning(f"User {user.username} attempted to access {request.path} without email verification")
        messages.warning(
            request,
            "Please verify your email address to access this page."
        )
        return redirect("accounts:verify_email_notice")
    
    return _wrapped_view


# ------------------------------------------------------
# 🎯 Usage Example for Other Views
# ------------------------------------------------------
# You can now use the decorator on other views that require email verification:
# 
# @login_required
# @email_verification_required
# def some_protected_view(request):
#     # This view will only be accessible to users with verified emails
#     # (admin users are automatically granted access)
#     return render(request, 'some_template.html')




# ------------------------------------------------------
# 🔐 Login View
# ------------------------------------------------------
@csrf_exempt
def login_view(request):
    """Handles user authentication with verification checks."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Get the authenticated user from the form's clean method
            user = form.cleaned_data.get('user')
            username_or_email = form.cleaned_data.get('username_or_email')
            
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")

                # 🔒 Check email verification for non-admin users
                if not _is_user_email_verified(user):
                    logger.warning(f"User {user.username} logged in without email verification")
                    messages.warning(
                        request,
                        "Please verify your email address to access all features."
                    )
                    return redirect("accounts:verify_email_notice")

                # Route based on user role
                if user.role == "admin" or user.is_superuser or user.is_staff:
                    return redirect("admin_dashboard")
                elif user.role == "doctor":
                    from .models import DoctorVerification
                    verification = DoctorVerification.objects.filter(user=user).first()

                    if not verification:
                        return redirect("accounts:doctor_verification")
                    elif verification.status == "pending":
                        return redirect("accounts:verification_status")
                    elif verification.status == "rejected":
                        messages.error(request, "Your verification was rejected. Please resubmit your details.")
                        return redirect("accounts:doctor_verification")
                    else:
                        return redirect("doctor_dashboard")
                else:
                    return redirect("patient_dashboard")

            else:
                # This shouldn't happen due to form validation, but just in case
                messages.error(request, "Invalid username/email or password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})



# ------------------------------------------------------
# 🚪 Logout View
# ------------------------------------------------------
@login_required
def logout_view(request):
    """Logs out the user."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')


# ===============================================================
# 👤 PATIENT DASHBOARD
# ===============================================================
@login_required
def patient_dashboard(request):
    if request.user.role != "patient":
        return redirect("accounts:dashboard")

    user = request.user

    recent_health = HealthRecord.objects.filter(user=user).order_by("-timestamp")[:5]
    recent_activity = ActivityRecord.objects.filter(user=user).order_by("-timestamp")[:5]
    recent_anomalies = Anomaly.objects.filter(user=user).order_by("-detected_at")[:5]
    recent_summaries = HealthSummary.objects.filter(user=user).order_by("-created_at")[:3]

    total_records = HealthRecord.objects.filter(user=user).count()
    total_anomalies = Anomaly.objects.filter(user=user).count()
    critical_anomalies = Anomaly.objects.filter(user=user, severity__in=["high", "critical"]).count()

    context = {
        "user": user,
        "recent_health": recent_health,
        "recent_activity": recent_activity,
        "recent_anomalies": recent_anomalies,
        "recent_summaries": recent_summaries,
        "total_records": total_records,
        "total_anomalies": total_anomalies,
        "critical_anomalies": critical_anomalies,
    }
    return render(request, "dashboard/patient_dashboard.html", context)


@login_required
def verification_status(request):
    if request.user.role != "doctor":
        return redirect("accounts:dashboard")

    try:
        verification = DoctorVerification.objects.get(user=request.user)
    except DoctorVerification.DoesNotExist:
        return redirect("accounts:doctor_verification")

    return render(request, "accounts/verification_status.html", {"verification": verification})


@login_required
def doctor_verification(request):
    if request.user.role != "doctor":
        return redirect("accounts:dashboard")

    # Check if already verified
    try:
        verification = DoctorVerification.objects.get(user=request.user)
    except DoctorVerification.DoesNotExist:
        verification = None

    if verification and verification.status == "approved":
        return redirect("doctor_dashboard")

    if request.method == "POST":
        form = DoctorVerificationForm(request.POST, request.FILES, instance=verification)
        if form.is_valid():
            verify = form.save(commit=False)
            verify.user = request.user
            verify.status = "pending"
            verify.submitted_at = timezone.now()
            verify.save()
            messages.success(request, "Verification submitted successfully. Await admin approval.")
            return redirect("accounts:verification_status")
    else:
        form = DoctorVerificationForm(instance=verification)

    return render(request, "accounts/doctor_verification.html", {"form": form})



# ===============================================================
# 🩺 DOCTOR DASHBOARD
# ===============================================================
@login_required
def doctor_dashboard(request):
    if request.user.role != "doctor":
        return redirect("accounts:dashboard")

    # ✅ Check verification
    from .models import DoctorVerification
    verification = DoctorVerification.objects.filter(user=request.user).first()
    if not verification:
        return redirect("accounts:doctor_verification")
    if verification.status == "pending":
        return redirect("accounts:verification_status")
    if verification.status == "rejected":
        messages.error(request, "Your verification was rejected. Please resubmit your details.")
        return redirect("accounts:doctor_verification")

    # Get all patients (for now, assume all users with role=patient)
    patients = (
        request.user.__class__.objects.filter(role="patient")
        .prefetch_related("health_records", "anomalies", "health_summaries")
    )

    total_patients = patients.count()
    total_records = HealthRecord.objects.filter(user__role="patient").count()
    total_anomalies = Anomaly.objects.filter(user__role="patient").count()
    critical_anomalies = Anomaly.objects.filter(
        user__role="patient", severity__in=["high", "critical"]
    ).count()

    recent_anomalies = Anomaly.objects.select_related("user").order_by("-detected_at")[:5]
    recent_summaries = HealthSummary.objects.select_related("user").order_by("-created_at")[:5]

    context = {
        "patients": patients,
        "total_patients": total_patients,
        "total_records": total_records,
        "total_anomalies": total_anomalies,
        "critical_anomalies": critical_anomalies,
        "recent_anomalies": recent_anomalies,
        "recent_summaries": recent_summaries,
    }

    return render(request, "dashboard/doctor_dashboard.html", context)



#===============================================================
# 🛠️ ADMIN DASHBOARD & ADMIN VIEWS
#  =============================================================
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

# accounts/views.py
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Clean Admin Dashboard Overview for Auralis Health"""
    
    # Essential Statistics Only
    total_users = CustomUser.objects.count()
    total_patients = CustomUser.objects.filter(role='patient').count()
    total_doctors = CustomUser.objects.filter(role='doctor').count()
    verified_doctors = CustomUser.objects.filter(role='doctor', is_verified=True).count()
    
    # Recent activity
    day_ago = timezone.now() - timedelta(hours=24)
    recent_records = HealthRecord.objects.filter(timestamp__gte=day_ago).count()
    recent_anomalies = Anomaly.objects.filter(detected_at__gte=day_ago).count()
    critical_anomalies = Anomaly.objects.filter(severity__in=['high', 'critical']).count()
    
    # Quick stats for cards
    week_ago = timezone.now() - timedelta(days=7)
    recent_users = CustomUser.objects.filter(date_joined__gte=week_ago).count()
    
    context = {
        'total_users': total_users,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'verified_doctors': verified_doctors,
        'recent_users': recent_users,
        'recent_records': recent_records,
        'recent_anomalies': recent_anomalies,
        'critical_anomalies': critical_anomalies,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

# Additional Admin Reporting Views
@login_required
@user_passes_test(is_admin)
def admin_user_management(request):
    """Detailed User Management Page"""
    users = CustomUser.objects.all().order_by('-date_joined')
    patients = CustomUser.objects.filter(role='patient')
    doctors = CustomUser.objects.filter(role='doctor')
    
    # Calculate recent users (last 7 days)
    from django.utils import timezone
    from datetime import timedelta
    week_ago = timezone.now() - timedelta(days=7)
    recent_users_count = CustomUser.objects.filter(date_joined__gte=week_ago).count()
    
    context = {
        'users': users,
        'patients': patients,
        'doctors': doctors,
        'recent_users_count': recent_users_count,
    }
    return render(request, 'admin/admin_user_management.html', context)

@login_required
@user_passes_test(is_admin)
def admin_health_reports(request):
    """Detailed Health Data Reports"""
    health_records = HealthRecord.objects.all().order_by('-timestamp')[:100]
    anomalies = Anomaly.objects.all().order_by('-detected_at')[:50]
    summaries = HealthSummary.objects.all().order_by('-created_at')[:20]
    
    # Calculate critical anomalies count from the sliced list
    critical_anomalies_count = sum(1 for anomaly in anomalies if anomaly.severity in ['critical', 'high'])
    
    context = {
        'health_records': health_records,
        'anomalies': anomalies,
        'summaries': summaries,
        'critical_anomalies_count': critical_anomalies_count,
    }
    return render(request, 'admin/admin_health_reports.html', context)

@login_required
@user_passes_test(is_admin)
def admin_doctor_verification(request):
    """Doctor Verification Management"""
    pending_doctors = CustomUser.objects.filter(role='doctor', is_verified=False)
    verified_doctors = CustomUser.objects.filter(role='doctor', is_verified=True)
    
    context = {
        'pending_doctors': pending_doctors,
        'verified_doctors': verified_doctors,
    }
    return render(request, 'admin/admin_doctor_verification.html', context)

@login_required
@user_passes_test(is_admin)
def admin_system_analytics(request):
    """System Analytics and Metrics with Real Data"""
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Avg, Q
    
    # Calculate time ranges
    now = timezone.now()
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # User Analytics
    total_users = CustomUser.objects.count()
    new_users_today = CustomUser.objects.filter(date_joined__gte=day_ago).count()
    new_users_week = CustomUser.objects.filter(date_joined__gte=week_ago).count()
    active_users_today = CustomUser.objects.filter(last_login__gte=day_ago).count()
    
    # Role Distribution
    role_distribution = CustomUser.objects.values('role').annotate(count=Count('id'))
    
    # Health Data Analytics
    total_health_records = HealthRecord.objects.count()
    health_records_today = HealthRecord.objects.filter(timestamp__gte=day_ago).count()
    health_records_week = HealthRecord.objects.filter(timestamp__gte=week_ago).count()
    
    # Anomaly Analytics
    total_anomalies = Anomaly.objects.count()
    critical_anomalies = Anomaly.objects.filter(severity__in=['critical', 'high']).count()
    anomalies_today = Anomaly.objects.filter(detected_at__gte=day_ago).count()
    
    # Activity Analytics
    total_activities = ActivityRecord.objects.count()
    activities_today = ActivityRecord.objects.filter(timestamp__gte=day_ago).count()
    
    # Doctor Verification Analytics
    total_doctors = CustomUser.objects.filter(role='doctor').count()
    verified_doctors = CustomUser.objects.filter(role='doctor', is_verified=True).count()
    pending_doctors = CustomUser.objects.filter(role='doctor', is_verified=False).count()
    
    # Health Metrics Averages
    avg_heart_rate = HealthRecord.objects.aggregate(avg=Avg('heart_rate'))['avg'] or 0
    avg_respiratory_rate = HealthRecord.objects.aggregate(avg=Avg('respiratory_rate'))['avg'] or 0
    
    # Recent Activity (last hour for "active sessions" simulation)
    hour_ago = now - timedelta(hours=1)
    recent_activity = HealthRecord.objects.filter(timestamp__gte=hour_ago).count()
    
    # Growth Rates
    users_last_week = CustomUser.objects.filter(
        date_joined__gte=week_ago - timedelta(days=7),
        date_joined__lt=week_ago
    ).count()
    user_growth_rate = ((new_users_week - users_last_week) / users_last_week * 100) if users_last_week > 0 else 0
    
    # System Health Indicators (simulated but based on real data)
    system_status = "Operational"
    error_rate = (critical_anomalies / total_anomalies * 100) if total_anomalies > 0 else 0
    
    context = {
        # User Analytics
        'total_users': total_users,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'active_users_today': active_users_today,
        'user_growth_rate': user_growth_rate,
        'role_distribution': role_distribution,
        
        # Health Data Analytics
        'total_health_records': total_health_records,
        'health_records_today': health_records_today,
        'health_records_week': health_records_week,
        'avg_heart_rate': avg_heart_rate,
        'avg_respiratory_rate': avg_respiratory_rate,
        
        # Anomaly Analytics
        'total_anomalies': total_anomalies,
        'critical_anomalies': critical_anomalies,
        'anomalies_today': anomalies_today,
        'error_rate': error_rate,
        
        # Activity Analytics
        'total_activities': total_activities,
        'activities_today': activities_today,
        'recent_activity': recent_activity,
        
        # Doctor Analytics
        'total_doctors': total_doctors,
        'verified_doctors': verified_doctors,
        'pending_doctors': pending_doctors,
        
        # System Health
        'system_status': system_status,
        
        # Time ranges for display
        'now': now,
        'day_ago': day_ago,
        'week_ago': week_ago,
        'month_ago': month_ago,
    }
    
    return render(request, 'admin/admin_system_analytics.html', context)


# ------------------------------------------------------
# 👤 Profile View
# ------------------------------------------------------
@login_required
@email_verification_required
def profile_view(request):
    """Display and update user profile."""
    user = request.user
    form = ProfileForm(instance=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {
        'form': form,
    })


# ------------------------------------------------------
# 🔁 Password Reset View (Optional)
# ------------------------------------------------------
@csrf_exempt
def password_reset_view(request):
    """Handles password reset request."""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user_service.send_password_reset(email)
            messages.success(request, "Password reset email sent.")
            return redirect('accounts:login')
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, 'accounts/password_reset.html')


# ------------------------------------------------------
# ✅ Email Verification View
# ------------------------------------------------------
def verify_view(request):
    """Handles post-registration email verification."""
    return render(request, 'accounts/verify.html')

# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import RegisterForm, LoginForm, ProfileForm
from .services.user_service import UserService
from django.contrib.auth.decorators import login_required
from monitoring.models import HealthRecord, ActivityRecord
from analytics.models import Anomaly, HealthSummary
from .models import DoctorVerification
from .forms import DoctorVerificationForm
from django.utils import timezone

# Initialize service
user_service = UserService()

# ------------------------------------------------------
# 🧍‍♂️ Register View (with role selection)
# ------------------------------------------------------
@csrf_exempt
def register_view(request, role=None):
    """Handles user registration using UserService, with optional preselected role."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    # Normalize role value
    allowed_roles = ['patient', 'practitioner']
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
                messages.success(request, "Registration successful! Please log in.")
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

# ------------------------------------------------------
# 🏠 Dashboard Redirect View
# ------------------------------------------------------
@login_required
def dashboard_redirect(request):
    """Redirects user to their role-based dashboard with verification logic"""
    user = request.user

    # Doctor verification check
    if user.role == "doctor":
        from .models import DoctorVerification
        verification = DoctorVerification.objects.filter(user=user).first()

        if not verification:
            return redirect("accounts:doctor_verification")

        if verification.status == "pending":
            return redirect("accounts:verification_status")

        if verification.status == "rejected":
            messages.error(request, "Your verification was rejected. Please resubmit your details.")
            return redirect("accounts:doctor_verification")

        # Approved doctor
        return redirect("dashboard:doctor_dashboard")

    # Default (patient)
    return redirect("dashboard:patient_dashboard")


# ------------------------------------------------------
# 🔐 Login View
# ------------------------------------------------------
@csrf_exempt
def login_view(request):
    """Handles user authentication with verification checks."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")

                # 🔒 After login, check if doctor verification is required
                if user.role == "doctor":
                    from .models import DoctorVerification
                    verification = DoctorVerification.objects.filter(user=user).first()

                    if not verification:
                        return redirect("accounts:doctor_verification")

                    if verification.status == "pending":
                        return redirect("accounts:verification_status")

                    if verification.status == "rejected":
                        messages.error(request, "Your verification was rejected. Please resubmit your details.")
                        return redirect("accounts:doctor_verification")

                    # Approved doctor
                    return redirect("dashboard:doctor_dashboard")

                # Normal patient user
                return redirect("dashboard:patient_dashboard")

            else:
                messages.error(request, "Invalid email or password.")
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
        return redirect("dashboard:dashboard_redirect")

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
        return redirect("dashboard:dashboard_redirect")

    try:
        verification = DoctorVerification.objects.get(user=request.user)
    except DoctorVerification.DoesNotExist:
        return redirect("accounts:doctor_verification")

    return render(request, "accounts/verification_status.html", {"verification": verification})


@login_required
def doctor_verification(request):
    if request.user.role != "doctor":
        return redirect("dashboard:dashboard_redirect")

    # Check if already verified
    try:
        verification = DoctorVerification.objects.get(user=request.user)
    except DoctorVerification.DoesNotExist:
        verification = None

    if verification and verification.status == "approved":
        return redirect("dashboard:doctor_dashboard")

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
        return redirect("dashboard:dashboard_redirect")

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


# ------------------------------------------------------
# 👤 Profile View
# ------------------------------------------------------
@login_required
def profile_view(request):
    """Display and update user profile."""
    user = request.user
    form = ProfileForm(instance=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')

    # Optional: Fetch recent health summary (if integrated)
    recent_summary = {
        'last_heart_rate': None,
        'last_resp_rate': None,
        'last_activity': None
    }

    return render(request, 'accounts/profile.html', {
        'form': form,
        'recent_summary': recent_summary
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

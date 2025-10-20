# monitoring/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import HealthRecord, ActivityRecord
import random
from accounts.decorators import email_verification_required

# ==========================================================
# 🩺 DASHBOARD VIEW
# ==========================================================
@login_required
@email_verification_required
def dashboard(request):
    """
    Main dashboard showing recent health and activity metrics.
    Aggregates last readings from all modules.
    """
    latest_health = HealthRecord.objects.filter(user=request.user).order_by('-timestamp').first()
    latest_activity = ActivityRecord.objects.filter(user=request.user).order_by('-timestamp').first()

    context = {
        "latest_heart_rate": getattr(latest_health, 'heart_rate', None),
        "latest_resp_rate": getattr(latest_health, 'respiratory_rate', None),
        "latest_spo2": getattr(latest_health, 'spo2', None),
        "latest_activity": getattr(latest_activity, 'activity_type', "Idle"),
        "latest_intensity": getattr(latest_activity, 'intensity', None),
    }
    return render(request, "monitoring/dashboard.html", context)


# ==========================================================
# 💓 HEART RATE MONITOR
# ==========================================================
@login_required
@email_verification_required
def heart_monitor(request):
    """Page to capture or simulate heart rate."""
    return render(request, "monitoring/heart_monitor.html")


@login_required
def heart_data_api(request):
    """
    Simulates heart rate readings.
    Later: integrate camera-based pulse estimation or sensor API.
    """
    bpm = random.randint(60, 100)
    HealthRecord.objects.create(user=request.user, heart_rate=bpm)
    return JsonResponse({"heart_rate": bpm})


# ==========================================================
# 🌬 RESPIRATORY RATE MONITOR
# ==========================================================
@login_required
@email_verification_required
def respiration_monitor(request):
    """Page to measure or simulate respiratory rate."""
    return render(request, "monitoring/respiration_monitor.html")


@login_required
def respiration_data_api(request):
    """
    Simulates respiratory rate (breaths per minute).
    Replace with microphone or chest movement detection later.
    """
    breaths = random.randint(10, 20)
    HealthRecord.objects.create(user=request.user, respiratory_rate=breaths)
    return JsonResponse({"respiratory_rate": breaths})


# ==========================================================
# 🚶 ACTIVITY MONITOR
# ==========================================================
@login_required
@email_verification_required
def activity_monitor(request):
    """Page to simulate or detect physical activity via accelerometer."""
    return render(request, "monitoring/activity_monitor.html")


@login_required
def activity_data_api(request):
    """
    Simulates activity type and intensity.
    Later: replace with accelerometer-based classification.
    """
    activities = ["Idle", "Walking", "Running"]
    activity_type = random.choice(activities)
    intensity = random.uniform(0.2, 1.0)
    ActivityRecord.objects.create(user=request.user, activity_type=activity_type, intensity=intensity)
    return JsonResponse({"activity_type": activity_type, "intensity": round(intensity, 2)})


# ==========================================================
# ⚡ LIVE COMBINED MONITOR
# ==========================================================
@login_required
@email_verification_required
def live_monitoring(request):
    """Displays unified live readings for heart, respiration, and activity."""
    return render(request, "monitoring/live_monitoring.html")


@login_required
def live_data_api(request):
    """
    Simulated unified API endpoint for real-time dashboard.
    Returns mock live sensor data every few seconds.
    """
    data = {
        "heart_rate": random.randint(60, 100),
        "resp_rate": random.randint(12, 22),
        "activity": random.choice(["Resting", "Walking", "Running"]),
    }
    return JsonResponse(data)


# ==========================================================
# 🗂 LOGS VIEW
# ==========================================================
@login_required
@email_verification_required
def logs(request):
    """Displays all recorded logs with optional date filters."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    health_logs = HealthRecord.objects.filter(user=request.user)
    if start_date:
        health_logs = health_logs.filter(timestamp__date__gte=start_date)
    if end_date:
        health_logs = health_logs.filter(timestamp__date__lte=end_date)

    health_logs = health_logs.order_by('-timestamp')

    context = {"logs": health_logs}
    return render(request, "monitoring/logs.html", context)


# # ==========================================================
# # 📊 ANALYTICS VIEW
# # ==========================================================
# @login_required
# def analytics(request):
#     """Renders charts and insights from historical data."""
#     recent_logs = HealthRecord.objects.filter(user=request.user).order_by('-timestamp')[:50]

#     heart_data = [log.heart_rate for log in recent_logs if log.heart_rate is not None]
#     resp_data = [log.respiratory_rate for log in recent_logs if log.respiratory_rate is not None]
#     timestamps = [log.timestamp.strftime("%Y-%m-%d %H:%M") for log in recent_logs]

#     context = {
#         "heart_data": heart_data[::-1],  # reverse for chronological order
#         "resp_data": resp_data[::-1],
#         "timestamps": timestamps[::-1],
#     }
#     return render(request, "monitoring/analytics.html", context)


# ==========================================================
# 🫁 SPO2 MONITOR
# ==========================================================
@login_required
@email_verification_required
def spo2_monitor(request):
    """Page for SpO₂ monitoring."""
    return render(request, "monitoring/spo2_monitor.html")

@login_required
def spo2_data_api(request):
    """Simulates SpO₂ (oxygen saturation) reading."""
    spo2 = random.randint(92, 100)
    status = "Normal" if spo2 >= 95 else "Low"
    HealthRecord.objects.create(user=request.user, spo2=spo2)
    return JsonResponse({"spo2": spo2, "status": status})


# ==========================================================
# 🌙 SLEEP MONITOR
# ==========================================================
@login_required
@email_verification_required
def sleep_monitor(request):
    """Displays sleep tracker page."""
    return render(request, "monitoring/sleep_monitor.html")

@login_required
def sleep_data_api(request):
    """Simulates sleep duration and quality."""
    duration = round(random.uniform(5.0, 8.5), 1)
    quality = random.choice(["Excellent", "Good", "Fair", "Poor"])
    return JsonResponse({"duration": duration, "quality": quality})

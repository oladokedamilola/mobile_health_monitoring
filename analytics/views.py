from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import HealthSummary, Anomaly
from .services.services import AnalyticsService


@login_required
def anomalies_view(request):
    """
    Displays a list of abnormal readings (flagged anomalies).
    """
    anomalies = Anomaly.objects.filter(user=request.user).order_by('-detected_at')
    context = {"anomalies": anomalies}
    return render(request, "analytics/anomalies.html", context)


@login_required
def progress_view(request):
    """
    Displays the user's monthly health progress using AnalyticsService trends.
    """
    trends = AnalyticsService.get_trends(request.user)

    # The service should return structured data, e.g.:
    # {
    #   "labels": [...],
    #   "heart_rate_data": [...],
    #   "resp_rate_data": [...],
    #   "summary": { "avg_heart_rate": 72, "avg_resp_rate": 18, "active_days": 25, "anomalies_count": 3 }
    # }

    if not trends:
        context = {"error": "No health data available for progress tracking."}
        return render(request, "analytics/progress.html", context)

    context = {
        "chart_labels": trends.get("labels", []),
        "heart_rate_data": trends.get("heart_rate_data", []),
        "resp_rate_data": trends.get("resp_rate_data", []),
        "avg_heart_rate": trends["summary"].get("avg_heart_rate"),
        "avg_resp_rate": trends["summary"].get("avg_resp_rate"),
        "active_days": trends["summary"].get("active_days"),
        "anomalies_count": trends["summary"].get("anomalies_count"),
    }

    return render(request, "analytics/progress.html", context)


@login_required
def report_view(request):
    """
    Generates and displays a printable health report summary for the user.
    """
    # Use the service to generate or fetch the latest summary
    summary = AnalyticsService.generate_summary(request.user)
    if not summary:
        context = {"error": "No health data found to generate report."}
        return render(request, "analytics/report.html", context)

    # Fetch trends for charts
    trends = AnalyticsService.get_trends(request.user)

    context = {
        "user": request.user,
        "generated_on": timezone.now(),
        "avg_heart_rate": getattr(summary, "avg_heart_rate", None),
        "avg_resp_rate": getattr(summary, "avg_resp_rate", None),
        "active_days": getattr(summary, "active_days", None),
        "anomalies_count": getattr(summary, "anomalies_count", None),
        "chart_labels": trends.get("labels", []),
        "heart_rate_data": trends.get("heart_rate_data", []),
        "resp_rate_data": trends.get("resp_rate_data", []),
    }

    return render(request, "analytics/report.html", context)

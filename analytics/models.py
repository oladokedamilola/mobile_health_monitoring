# analytics/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class HealthSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="health_summaries")
    average_heart_rate = models.FloatField(default=0.0)
    average_respiratory_rate = models.FloatField(default=0.0)
    activity_level = models.CharField(max_length=50, blank=True)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - Summary ({self.period_start.date()} to {self.period_end.date()})"


from django.conf import settings


class Anomaly(models.Model):
    """Stores flagged abnormal readings detected from health data."""

    PARAMETER_CHOICES = [
        ("heart_rate", "Heart Rate"),
        ("respiratory_rate", "Respiratory Rate"),
        ("spo2", "Oxygen Saturation"),
        ("activity", "Activity Level"),
        ("sleep", "Sleep Pattern"),
    ]

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("moderate", "Moderate"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="anomalies")
    parameter = models.CharField(max_length=50, choices=PARAMETER_CHOICES)
    value = models.FloatField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="low")
    remark = models.TextField(blank=True, null=True)
    detected_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-detected_at"]
        verbose_name_plural = "Anomalies"

    def __str__(self):
        return f"{self.user.username} - {self.parameter} ({self.severity})"

    def is_critical(self):
        return self.severity in ["high", "critical"]

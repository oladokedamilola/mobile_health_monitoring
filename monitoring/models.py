# monitoring/models.py
from django.db import models
from django.conf import settings

class HealthRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="health_records")
    heart_rate = models.FloatField(null=True, blank=True)          # beats per minute estimate
    respiratory_rate = models.FloatField(null=True, blank=True)    # breaths per minute
    spo2 = models.FloatField(null=True, blank=True)                # optional
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"]),
        ]

class ActivityRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_records")
    activity_type = models.CharField(max_length=32)  # e.g., idle, walking, running
    intensity = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"]),
        ]

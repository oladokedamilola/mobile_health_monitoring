# sync/models.py
from django.db import models
from django.conf import settings

class SyncLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sync_logs")
    payload = models.JSONField()
    status_choices = (("pending", "pending"), ("synced", "synced"), ("failed", "failed"))
    status = models.CharField(max_length=16, choices=status_choices, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["created_at"]),
        ]


class OfflineRecord(models.Model):
    """Temporarily stores data created offline before sync."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="offline_records")
    data_type = models.CharField(max_length=50)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    synced = models.BooleanField(default=False)
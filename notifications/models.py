# notifications/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Info'),
        ('alert', 'Alert'),
        ('reminder', 'Reminder'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type.upper()} - {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])



class AlertThreshold(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alert_threshold')
    max_heart_rate = models.IntegerField(default=120)
    max_respiratory_rate = models.IntegerField(default=25)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Thresholds"

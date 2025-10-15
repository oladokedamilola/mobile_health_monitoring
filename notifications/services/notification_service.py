# notifications/services/notification_service.py
from django.utils import timezone
from ..models import Notification
from analytics.services.services import AnalyticsService
from django.core.mail import send_mail
from django.conf import settings

class NotificationService:
    @staticmethod
    def create_notification(user, title, message, notif_type="info"):
        """Create an in-app notification."""
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notif_type,
        )
        return notification

    @staticmethod
    def alert_if_threshold_exceeded(user, threshold_heart_rate=120):
        """Trigger alert if heart rate exceeds threshold."""
        latest_summary = AnalyticsService.generate_summary(user)
        if latest_summary and latest_summary.average_heart_rate > threshold_heart_rate:
            msg = f"Your average heart rate ({latest_summary.average_heart_rate} bpm) exceeds {threshold_heart_rate} bpm."
            NotificationService.create_notification(
                user=user,
                title="High Heart Rate Alert",
                message=msg,
                notif_type="alert",
            )
            return True
        return False

    @staticmethod
    def send_email_notification(user, subject, message):
        """Send an optional email notification."""
        if not user.email:
            return
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )


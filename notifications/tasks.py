# notifications/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from celery import shared_task
from django.contrib.auth import get_user_model
from .services.notification_service import NotificationService

@shared_task
def send_email_notification(subject, message, recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=None,  # use DEFAULT_FROM_EMAIL
        recipient_list=recipient_list,
        fail_silently=False,
    )
    return True


User = get_user_model()

@shared_task
def check_user_health_alerts():
    """Periodic task to trigger alerts for all users."""
    for user in User.objects.all():
        NotificationService.alert_if_threshold_exceeded(user)

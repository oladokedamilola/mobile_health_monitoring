# notifications/repositories.py
from .models import Notification

class NotificationRepository:
    def create(self, user, title, message, level="info"):
        return Notification.objects.create(user=user, title=title, message=message, level=level)

    def get_unread(self, user):
        return Notification.objects.filter(user=user, is_read=False)

    def mark_read(self, notification_id):
        notif = Notification.objects.filter(id=notification_id).first()
        if notif:
            notif.is_read = True
            notif.save()
        return notif

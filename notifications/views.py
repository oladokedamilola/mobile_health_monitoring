from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from .services.notification_service import NotificationService
from accounts.decorators import email_verification_required


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
            notif.mark_as_read()
            return Response({'detail': 'Marked as read.'})
        except Notification.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Notification

@login_required
@email_verification_required
def notifications_view(request):
    """Render the notifications dashboard."""
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    unread_count = notifications.filter(is_read=False).count()
    return render(request, "notifications/notifications.html", {
        "notifications": notifications,
        "unread_count": unread_count,
    })

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/notifications/"""
        qs = Notification.objects.filter(user=request.user).order_by("-created_at")
        serializer = NotificationSerializer(qs, many=True)
        return Response(serializer.data)

    def mark_all_read(self, request):
        """POST /api/notifications/mark-read/"""
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"message": "All notifications marked as read"}, status=status.HTTP_200_OK)

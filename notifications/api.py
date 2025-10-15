from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer
from .services.notification_service import NotificationService

class NotificationViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    service = NotificationService()

    def list(self, request):
        notifs = self.service.get_unread_notifications(user=request.user)
        serializer = NotificationSerializer(notifs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notif = self.service.mark_notification_as_read(notification_id=pk)
        if not notif:
            return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "marked"}, status=status.HTTP_200_OK)

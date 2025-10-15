from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import SyncLogSerializer
from .services.sync_service import SyncService

class SyncViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    service = SyncService()

    @action(detail=False, methods=["post"])
    def queue(self, request):
        """
        Endpoint for PWA to queue payloads for later sync.
        Example body: {"payload": {"health": {...}}}
        """
        payload = request.data.get('payload')
        if not payload:
            return Response({"detail": "payload required"}, status=status.HTTP_400_BAD_REQUEST)
        log = self.service.queue_payload(user=request.user, payload=payload)
        serializer = SyncLogSerializer(log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        logs = self.service.repo.get_pending_logs(user=request.user)
        serializer = SyncLogSerializer(logs, many=True)
        return Response(serializer.data)

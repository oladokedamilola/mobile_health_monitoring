from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SyncLog, OfflineRecord
from .serializers import SyncLogSerializer, OfflineRecordSerializer

class SyncViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/sync/"""
        logs = SyncLog.objects.filter(user=request.user).order_by("-created_at")[:20]
        serializer = SyncLogSerializer(logs, many=True)
        return Response(serializer.data)

    def sync_now(self, request):
        """POST /api/sync/now/ → simulate manual sync"""
        records = OfflineRecord.objects.filter(user=request.user, synced=False)
        count = records.count()
        records.update(synced=True)
        SyncLog.objects.create(user=request.user, status="success", message=f"Synced {count} offline records")
        return Response({"message": f"Successfully synced {count} records"}, status=status.HTTP_200_OK)

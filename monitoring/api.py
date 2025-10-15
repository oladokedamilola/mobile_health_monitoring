from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import HealthRecordSerializer, ActivityRecordSerializer
from .services.services import HealthService

class MonitoringViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    service = HealthService()

    def list(self, request):
        # returns recent health records for authenticated user
        records = self.service.health_repo.get_recent(user=request.user, limit=50)
        serializer = HealthRecordSerializer(records, many=True)
        return Response(serializer.data)

    def create(self, request):
        # expects JSON with e.g. {"heart_rate": 72.5, "respiratory_rate": 16}
        data = request.data
        hr = data.get('heart_rate')
        rr = data.get('respiratory_rate')
        rec = self.service.health_repo.save_record(user=request.user, heart_rate=hr, respiratory_rate=rr)
        serializer = HealthRecordSerializer(rec)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def activity(self, request):
        payload = request.data
        activity_type = payload.get('activity_type')
        intensity = payload.get('intensity')
        act = self.service.record_activity(user=request.user, activity_type=activity_type, intensity=intensity)
        serializer = ActivityRecordSerializer(act)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

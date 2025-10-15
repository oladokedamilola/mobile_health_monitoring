from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import HealthSummarySerializer
from .services.services import AnalyticsService
from .models import HealthSummary, Anomaly


class AnalyticsAPIViewSet(viewsets.ViewSet):
    """
    API Endpoints for analytics summary and trends
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/analytics/summary/"""
        summaries = HealthSummary.objects.filter(user=request.user)
        serializer = HealthSummarySerializer(summaries, many=True)
        return Response(serializer.data)

    def create(self, request):
        """POST /api/analytics/summary/ → generate new summary"""
        summary = AnalyticsService.generate_summary(request.user)
        if not summary:
            return Response({"detail": "No records to summarize."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = HealthSummarySerializer(summary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def trends(self, request):
        """GET /api/analytics/trends/"""
        data = AnalyticsService.get_trends(request.user)
        serializer = HealthSummarySerializer(data, many=True)
        return Response(serializer.data)


class AnomalyAPIViewSet(viewsets.ViewSet):
    """
    API for fetching and managing anomaly data
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/analytics/anomalies/"""
        anomalies = Anomaly.objects.filter(user=request.user).order_by('-timestamp')
        data = [
            {
                "metric": a.metric,
                "value": a.value,
                "threshold": a.threshold,
                "severity": a.severity,
                "timestamp": a.timestamp,
            }
            for a in anomalies
        ]
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """GET /api/analytics/anomalies/<id>/"""
        try:
            anomaly = Anomaly.objects.get(pk=pk, user=request.user)
            data = {
                "metric": anomaly.metric,
                "value": anomaly.value,
                "threshold": anomaly.threshold,
                "severity": anomaly.severity,
                "timestamp": anomaly.timestamp,
                "notes": anomaly.notes,
            }
            return Response(data)
        except Anomaly.DoesNotExist:
            return Response({"detail": "Anomaly not found"}, status=status.HTTP_404_NOT_FOUND)


class ProgressAPIViewSet(viewsets.ViewSet):
    """
    API for fetching monthly health progress analytics
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/analytics/progress/"""
        progress_data = AnalyticsService.get_monthly_progress(request.user)
        return Response(progress_data, status=status.HTTP_200_OK)


class ReportAPIViewSet(viewsets.ViewSet):
    """
    API for generating and fetching printable reports
    """
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        """GET /api/analytics/report/<month>/"""
        report_data = AnalyticsService.get_monthly_report(request.user, month=pk)
        if not report_data:
            return Response({"detail": "No data found for the selected month."}, status=status.HTTP_404_NOT_FOUND)
        return Response(report_data)

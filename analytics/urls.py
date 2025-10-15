from django.urls import path
from . import views
from .api_views import (
    AnalyticsAPIViewSet,
    AnomalyAPIViewSet,
    ProgressAPIViewSet,
    ReportAPIViewSet,
)

app_name = "analytics"

# ==========================================================
# 🔌 API ENDPOINTS (DRF)
# ==========================================================
analytics_list = AnalyticsAPIViewSet.as_view({'get': 'list', 'post': 'create'})
analytics_trends = AnalyticsAPIViewSet.as_view({'get': 'trends'})
anomaly_list = AnomalyAPIViewSet.as_view({'get': 'list'})
anomaly_detail = AnomalyAPIViewSet.as_view({'get': 'retrieve'})
progress_list = ProgressAPIViewSet.as_view({'get': 'list'})
report_detail = ReportAPIViewSet.as_view({'get': 'retrieve'})

urlpatterns = [
    # ==========================================================
    # 📊 FRONTEND VIEWS (HTML Templates)
    # ==========================================================
    path("anomalies/", views.anomalies_view, name="anomalies"),
    path("progress/", views.progress_view, name="progress"),
    path("report/", views.report_view, name="report"),

    # ==========================================================
    # 🔌 API ENDPOINTS (DRF)
    # ==========================================================
    path("api/summary/", analytics_list, name="api_summary"),
    path("api/trends/", analytics_trends, name="api_trends"),
    path("api/anomalies/", anomaly_list, name="api_anomalies"),
    path("api/anomalies/<int:pk>/", anomaly_detail, name="api_anomaly_detail"),
    path("api/progress/", progress_list, name="api_progress"),
    path("api/report/<str:pk>/", report_detail, name="api_report"),
]

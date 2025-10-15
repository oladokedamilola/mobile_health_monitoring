from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from monitoring.api import MonitoringViewSet
from sync.api import SyncViewSet
from notifications.api import NotificationViewSet
from core.views import home_view  
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import patient_dashboard, doctor_dashboard

router = routers.DefaultRouter()
router.register(r'monitoring', MonitoringViewSet, basename='monitoring')
router.register(r'sync', SyncViewSet, basename='sync')
router.register(r'notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),

    # App URLs
    path("monitoring/", include("monitoring.urls")),
    path("accounts/", include("accounts.urls")),
    path("analytics/", include("analytics.urls")),
    path("sync/", include("sync.urls")),
    path("notifications/", include("notifications.urls")),
    path("dashboard/patient/", patient_dashboard, name="patient_dashboard"),
    path("dashboard/doctor/", doctor_dashboard, name="doctor_dashboard"),
    ]


if settings.DEBUG:
    from django.conf import settings
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
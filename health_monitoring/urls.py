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
from accounts.views import ( patient_dashboard, doctor_dashboard, admin_dashboard,
                            admin_user_management, admin_health_reports, 
                            admin_doctor_verification, admin_system_analytics )

router = routers.DefaultRouter()
router.register(r'monitoring', MonitoringViewSet, basename='monitoring')
router.register(r'sync', SyncViewSet, basename='sync')
router.register(r'notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
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
    path('dashboard/admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    
    
    
    path('admin/users/', admin_user_management, name='admin_user_management'),
    path('admin/health-reports/', admin_health_reports, name='admin_health_reports'),
    path('admin/doctor-verification/', admin_doctor_verification, name='admin_doctor_verification'),
    path('admin/analytics/', admin_system_analytics, name='admin_system_analytics'),
    
    
    path('admin/', admin.site.urls),

    ]


if settings.DEBUG:
    from django.conf import settings
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
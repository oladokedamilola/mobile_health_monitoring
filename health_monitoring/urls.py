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

# Import error views from core
from core.views import (bad_request, unauthorized, forbidden, not_found, 
                       method_not_allowed, request_timeout, payload_too_large,
                       too_many_requests, server_error, bad_gateway, 
                       service_unavailable, gateway_timeout)

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

# Django built-in error handlers (400, 403, 404, 500)
handler400 = 'core.views.bad_request'
handler403 = 'core.views.forbidden'
handler404 = 'core.views.not_found'
handler500 = 'core.views.server_error'

# For other error codes, we'll create custom URL patterns
# These will be caught when DEBUG = False and the specific errors occur
urlpatterns += [
    path('error/400/', bad_request, name='error_400'),
    path('error/401/', unauthorized, name='error_401'),
    path('error/403/', forbidden, name='error_403'),
    path('error/404/', not_found, name='error_404'),
    path('error/405/', method_not_allowed, name='error_405'),
    path('error/408/', request_timeout, name='error_408'),
    path('error/413/', payload_too_large, name='error_413'),
    path('error/429/', too_many_requests, name='error_429'),
    path('error/500/', server_error, name='error_500'),
    path('error/502/', bad_gateway, name='error_502'),
    path('error/503/', service_unavailable, name='error_503'),
    path('error/504/', gateway_timeout, name='error_504'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
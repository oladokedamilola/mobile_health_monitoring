from django.urls import path
from .views import NotificationViewSet

notification_list = NotificationViewSet.as_view({'get': 'list', 'post': 'create'})
notification_read = NotificationViewSet.as_view({'post': 'mark_read'})

app_name = 'notifications'

urlpatterns = [
    path('', notification_list, name='notification-list'),
    path('<int:pk>/read/', notification_read, name='notification-mark-read'),
]

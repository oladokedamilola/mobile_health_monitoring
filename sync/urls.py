from django.urls import path
from . import views
from .api_views import SyncViewSet

app_name = "sync"

sync_list = SyncViewSet.as_view({'get': 'list'})
sync_now = SyncViewSet.as_view({'post': 'sync_now'})

urlpatterns = [
    path("", views.sync_view, name="sync"),
    path("api/", sync_list, name="api_sync"),
    path("api/now/", sync_now, name="api_sync_now"),
]

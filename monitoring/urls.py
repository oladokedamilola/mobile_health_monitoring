# monitoring/urls.py
from django.urls import path
from . import views

app_name = "monitoring"

urlpatterns = [
    # ==========================================================
    # 🩺 CORE DASHBOARD & ANALYTICS
    # ==========================================================
    path("logs/", views.logs, name="logs"),
    
    # ==========================================================
    # ⚡ LIVE MONITORING (general + API)
    # ==========================================================
    path("live/", views.live_monitoring, name="live_monitoring"),
    path("api/live/", views.live_data_api, name="live_data_api"),

    # ==========================================================
    # 💓 INDIVIDUAL MONITORING MODULES
    # ==========================================================
    path("heart/", views.heart_monitor, name="heart_monitor"),
    path("respiration/", views.respiration_monitor, name="respiration_monitor"),
    path("activity/", views.activity_monitor, name="activity_monitor"),
    
    # Optional modules — add when implemented in views
    path("spo2/", views.spo2_monitor, name="spo2_monitor"),
    path("sleep/", views.sleep_monitor, name="sleep_monitor"),

    # ==========================================================
    # 🔌 SIMULATION / SENSOR APIs
    # ==========================================================
    path("api/heart/", views.heart_data_api, name="heart_data_api"),
    path("api/respiration/", views.respiration_data_api, name="respiration_data_api"),
    path("api/activity/", views.activity_data_api, name="activity_data_api"),
    
    # Optional simulated APIs — add when implemented
    path("api/spo2/", views.spo2_data_api, name="spo2_data_api"),
    path("api/sleep/", views.sleep_data_api, name="sleep_data_api"),
]

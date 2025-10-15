from django.contrib import admin
from .models import HealthRecord, ActivityRecord


# ============================
# 📈 Health Record Admin
# ============================
@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    """Admin configuration for health measurement data."""

    list_display = (
        "user",
        "heart_rate",
        "respiratory_rate",
        "spo2",
        "timestamp",
    )
    list_filter = ("timestamp",)
    search_fields = ("user__username", "user__email")
    ordering = ("-timestamp",)
    readonly_fields = ("timestamp",)
    list_per_page = 25

    fieldsets = (
        ("User Information", {"fields": ("user",)}),
        (
            "Health Metrics",
            {"fields": ("heart_rate", "respiratory_rate", "spo2")},
        ),
        ("Timestamp", {"fields": ("timestamp",)}),
    )


# ============================
# 🏃 Activity Record Admin
# ============================
@admin.register(ActivityRecord)
class ActivityRecordAdmin(admin.ModelAdmin):
    """Admin configuration for daily activity tracking."""

    list_display = (
        "user",
        "activity_type",
        "intensity",
        "timestamp",
    )
    list_filter = ("activity_type", "timestamp")
    search_fields = ("user__username", "user__email", "activity_type")
    ordering = ("-timestamp",)
    readonly_fields = ("timestamp",)
    list_per_page = 25

    fieldsets = (
        ("User Information", {"fields": ("user",)}),
        (
            "Activity Details",
            {"fields": ("activity_type", "intensity")},
        ),
        ("Timestamp", {"fields": ("timestamp",)}),
    )


# ============================
# ⚙️ Admin Branding
# ============================
admin.site.site_header = "Auralis Health Monitoring Administration"
admin.site.site_title = "Auralis Health Monitoring"
admin.site.index_title = "Monitor User Health and Activity Data"

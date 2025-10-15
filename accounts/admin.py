from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DoctorVerification
from monitoring.models import HealthRecord, ActivityRecord
from analytics.models import Anomaly, HealthSummary


# ================================
# 🔹 Inline Admins
# ================================

class HealthRecordInline(admin.TabularInline):
    model = HealthRecord
    extra = 0
    readonly_fields = ("timestamp",)
    fields = ("heart_rate", "respiratory_rate", "spo2", "timestamp")
    show_change_link = True
    can_delete = False
    verbose_name_plural = "Health Records"


class ActivityRecordInline(admin.TabularInline):
    model = ActivityRecord
    extra = 0
    readonly_fields = ("timestamp",)
    fields = ("activity_type", "intensity", "timestamp")
    show_change_link = True
    can_delete = False
    verbose_name_plural = "Activity Records"


class AnomalyInline(admin.TabularInline):
    model = Anomaly
    extra = 0
    readonly_fields = ("parameter", "value", "severity", "remark", "detected_at")
    show_change_link = True
    can_delete = False
    verbose_name_plural = "Detected Anomalies"


class HealthSummaryInline(admin.TabularInline):
    model = HealthSummary
    extra = 0
    readonly_fields = (
        "average_heart_rate",
        "average_respiratory_rate",
        "activity_level",
        "period_start",
        "period_end",
        "created_at",
    )
    show_change_link = True
    can_delete = False
    verbose_name_plural = "Health Summaries"


# ================================
# 👤 Custom User Admin
# ================================

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Customized admin panel for users with inlines."""

    list_display = ("username", "email", "role", "is_verified", "is_active", "date_joined")
    list_filter = ("role", "is_verified", "is_staff", "is_superuser")
    search_fields = ("username", "email", "phone")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login")

    fieldsets = (
        ("Login Info", {"fields": ("username", "email", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                    "date_of_birth",
                    "location",
                    "bio",
                    "profile_picture",
                )
            },
        ),
        ("Role & Verification", {"fields": ("role", "is_verified")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    inlines = [HealthRecordInline, ActivityRecordInline, AnomalyInline, HealthSummaryInline]


# ================================
# 🩺 Doctor Verification Admin
# ================================

@admin.register(DoctorVerification)
class DoctorVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "license_number", "status", "submitted_at", "reviewed_at")
    list_filter = ("status", "submitted_at", "reviewed_at")
    search_fields = ("user__username", "full_name", "license_number", "hospital_name")
    readonly_fields = ("submitted_at", "reviewed_at")
    list_per_page = 25

    fieldsets = (
        ("Doctor Info", {"fields": ("user", "full_name", "phone_number", "hospital_name", "license_number")}),
        ("Verification Details", {"fields": ("document", "status", "remarks")}),
        ("Timestamps", {"fields": ("submitted_at", "reviewed_at")}),
    )


# ================================
# ⚙️ Admin Branding
# ================================
admin.site.site_header = "Auralis Health Monitoring Administration"
admin.site.site_title = "Auralis Admin Portal"
admin.site.index_title = "Manage Users, Health Data & Doctor Verification"

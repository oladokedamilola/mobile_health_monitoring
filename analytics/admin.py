from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DoctorVerification
from analytics.models import Anomaly, HealthSummary


# ============================
# 📊 Inline Admins
# ============================

class HealthSummaryInline(admin.TabularInline):
    model = HealthSummary
    extra = 0
    fields = ("average_heart_rate", "average_respiratory_rate", "activity_level", "period_start", "period_end")
    readonly_fields = ("period_start", "period_end", "average_heart_rate", "average_respiratory_rate")
    show_change_link = True
    verbose_name = "Health Summary"
    verbose_name_plural = "Health Summaries"


class AnomalyInline(admin.TabularInline):
    model = Anomaly
    extra = 0
    fields = ("parameter", "value", "severity", "remark", "detected_at")
    readonly_fields = ("parameter", "value", "severity", "remark", "detected_at")
    show_change_link = True
    verbose_name = "Anomaly"
    verbose_name_plural = "Detected Anomalies"


# ============================
# 👤 Custom User Admin
# ============================

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Customized admin for Auralis user management."""

    model = CustomUser
    list_display = ("username", "email", "role", "is_verified", "is_active", "date_joined")
    list_filter = ("role", "is_verified", "is_active", "date_joined")
    search_fields = ("username", "email", "role")
    ordering = ("-date_joined",)
    list_per_page = 25

    fieldsets = (
        ("Authentication", {"fields": ("username", "email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone", "date_of_birth", "profile_picture")}),
        ("Professional Info", {"fields": ("role", "location", "bio", "is_verified")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    readonly_fields = ("last_login", "date_joined")
    inlines = [HealthSummaryInline, AnomalyInline]


# ============================
# 🩺 Doctor Verification Admin
# ============================

@admin.register(DoctorVerification)
class DoctorVerificationAdmin(admin.ModelAdmin):
    """Admin interface for verifying doctors."""

    list_display = (
        "user",
        "full_name",
        "hospital_name",
        "license_number",
        "status",
        "submitted_at",
        "reviewed_at",
    )
    list_filter = ("status", "submitted_at")
    search_fields = ("user__username", "hospital_name", "license_number")
    ordering = ("-submitted_at",)
    readonly_fields = ("submitted_at", "reviewed_at")

    fieldsets = (
        ("Doctor Info", {
            "fields": (
                "user",
                "full_name",
                "phone_number",
                "hospital_name",
                "license_number",
                "document",
            )
        }),
        ("Review", {"fields": ("status", "remarks", "submitted_at", "reviewed_at")}),
    )

    def save_model(self, request, obj, form, change):
        """Automatically update verification flag when approved."""
        super().save_model(request, obj, form, change)
        if obj.status == "approved" and not obj.user.is_verified:
            obj.user.is_verified = True
            obj.user.save(update_fields=["is_verified"])


# ============================
# 🧭 Admin Branding
# ============================

admin.site.site_header = "Auralis Health Administration"
admin.site.site_title = "Auralis Health"
admin.site.index_title = "User Management & Doctor Verification"

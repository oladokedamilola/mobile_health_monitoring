from django.contrib import admin
from .models import Notification, AlertThreshold


# ================================
# 🔔 Notification Admin
# ================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "notification_type",
        "title",
        "is_read",
        "created_at",
    )
    list_filter = (
        "notification_type",
        "is_read",
        "created_at",
    )
    search_fields = (
        "title",
        "message",
        "user__username",
        "user__email",
    )
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 25

    fieldsets = (
        (None, {
            "fields": ("user", "notification_type", "title", "message")
        }),
        ("Status & Timestamps", {
            "fields": ("is_read", "created_at")
        }),
    )

    actions = ["mark_selected_as_read"]

    @admin.action(description="Mark selected notifications as read")
    def mark_selected_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notification(s) marked as read.")


# ================================
# ⚙️ Alert Threshold Admin
# ================================
@admin.register(AlertThreshold)
class AlertThresholdAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "max_heart_rate",
        "max_respiratory_rate",
        "updated_at",
    )
    search_fields = ("user__username", "user__email")
    readonly_fields = ("updated_at",)
    list_per_page = 25
    ordering = ("-updated_at",)

    fieldsets = (
        ("User", {
            "fields": ("user",)
        }),
        ("Threshold Settings", {
            "fields": ("max_heart_rate", "max_respiratory_rate")
        }),
        ("Timestamps", {
            "fields": ("updated_at",)
        }),
    )

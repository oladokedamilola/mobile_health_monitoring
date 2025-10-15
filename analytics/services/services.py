from django.utils import timezone
from datetime import timedelta
from monitoring.models import HealthRecord, ActivityRecord
from ..models import HealthSummary

class AnalyticsService:
    @staticmethod
    def generate_summary(user):
        """Generate health summary for a given user."""
        now = timezone.now()
        one_week_ago = now - timedelta(days=7)

        records = HealthRecord.objects.filter(user=user, timestamp__gte=one_week_ago)
        activities = ActivityRecord.objects.filter(user=user, timestamp__gte=one_week_ago)

        if not records.exists():
            return None

        avg_heart_rate = records.aggregate(avg=models.Avg("heart_rate"))["avg"] or 0
        avg_resp_rate = records.aggregate(avg=models.Avg("respiratory_rate"))["avg"] or 0

        activity_level = "Low"
        if activities.count() > 100:
            activity_level = "High"
        elif activities.count() > 50:
            activity_level = "Moderate"

        summary = HealthSummary.objects.create(
            user=user,
            average_heart_rate=avg_heart_rate,
            average_respiratory_rate=avg_resp_rate,
            activity_level=activity_level,
            period_start=one_week_ago,
            period_end=now,
        )
        return summary

    @staticmethod
    def get_trends(user):
        """Return past summaries for trend visualization."""
        return HealthSummary.objects.filter(user=user).order_by("created_at")

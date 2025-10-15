# monitoring/repsotories/health_repository.py
from monitoring.models import HealthRecord, ActivityRecord

class HealthRepository:
    def save_record(self, user, heart_rate=None, respiratory_rate=None, spo2=None):
        rec = HealthRecord.objects.create(
            user=user,
            heart_rate=heart_rate,
            respiratory_rate=respiratory_rate,
            spo2=spo2,
        )
        return rec

    def get_recent(self, user, limit=50):
        return HealthRecord.objects.filter(user=user).order_by("-timestamp")[:limit]

class ActivityRepository:
    def save_activity(self, user, activity_type, intensity=None):
        rec = ActivityRecord.objects.create(user=user, activity_type=activity_type, intensity=intensity)
        return rec

    def get_recent(self, user, limit=50):
        return ActivityRecord.objects.filter(user=user).order_by("-timestamp")[:limit]

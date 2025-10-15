# sync/repositories.py
from .models import SyncLog

class SyncRepository:
    def create_log(self, user, payload):
        return SyncLog.objects.create(user=user, payload=payload)

    def get_pending_logs(self, user=None):
        qs = SyncLog.objects.filter(status="pending")
        if user:
            qs = qs.filter(user=user)
        return qs.order_by("created_at")

    def mark_synced(self, log):
        log.status = "synced"
        log.save()
        return log

# sync/services.py
from sync.repositories import SyncRepository

class SyncService:
    def __init__(self, repo: SyncRepository = None):
        self.repo = repo or SyncRepository()

    def queue_payload(self, user, payload):
        return self.repo.create_log(user=user, payload=payload)

    def process_pending(self, user=None, sender=None):
        """
        Attempts to process pending logs. 'sender' is a callable that accepts payload and returns True/False.
        This function can be used by Celery tasks or manual background worker.
        """
        pending = self.repo.get_pending_logs(user=user)
        results = []
        for log in pending:
            try:
                ok = True
                if sender:
                    ok = sender(log.payload)
                if ok:
                    self.repo.mark_synced(log)
                else:
                    log.status = "failed"
                    log.save()
                results.append((log.id, ok))
            except Exception:
                log.status = "failed"
                log.save()
                results.append((log.id, False))
        return results

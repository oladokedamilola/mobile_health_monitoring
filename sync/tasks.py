# sync/tasks.py
from celery import shared_task
from .services import SyncService

@shared_task
def process_sync_queue():
    service = SyncService()
    # In real usage, define a sender function that calls your DRF endpoints or cloud API.
    def fake_sender(payload):
        # replace with actual logic to post to cloud
        return True

    return service.process_pending(sender=fake_sender)

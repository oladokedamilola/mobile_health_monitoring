# sync/tests/test_services.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from sync.services.sync_service import SyncService

User = get_user_model()

class SyncServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="syncer", email="s@example.com", password="p")
        self.service = SyncService()

    def test_queue_and_process(self):
        log = self.service.queue_payload(self.user, {"a": 1})
        assert log.status == "pending"
        results = self.service.process_pending(sender=lambda p: True)
        assert results and results[0][1] is True

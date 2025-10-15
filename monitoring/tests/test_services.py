# monitoring/tests/test_services.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from monitoring.services.services import HealthService

User = get_user_model()

class HealthServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", email="t@example.com", password="pass")
        self.service = HealthService()

    def test_store_ppg(self):
        rec = self.service.process_ppg_and_store(self.user, heart_rate_signal=[1,2,3], estimated_bpm=72.5)
        self.assertIsNotNone(rec.id)
        self.assertAlmostEqual(rec.heart_rate, 72.5)

    def test_record_activity(self):
        act = self.service.record_activity(self.user, activity_type="walking", intensity=2.3)
        self.assertEqual(act.activity_type, "walking")

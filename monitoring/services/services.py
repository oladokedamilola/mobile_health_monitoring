# monitoring/services/services.py
from ..repositories.health_repository import HealthRepository, ActivityRepository

class HealthService:
    def __init__(self, health_repo=None, activity_repo=None):
        self.health_repo = health_repo or HealthRepository()
        self.activity_repo = activity_repo or ActivityRepository()

    def process_ppg_and_store(self, user, heart_rate_signal, estimated_bpm=None):
        # For now assume estimated_bpm is provided; real implementation would process signal
        return self.health_repo.save_record(user=user, heart_rate=estimated_bpm)

    def store_respiratory(self, user, respiratory_rate):
        return self.health_repo.save_record(user=user, respiratory_rate=respiratory_rate)

    def record_activity(self, user, activity_type, intensity=None):
        return self.activity_repo.save_activity(user=user, activity_type=activity_type, intensity=intensity)

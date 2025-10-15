# accounts/services/user_service.py
from ..repositories.user_repository import UserRepository
from django.contrib.auth import authenticate

class UserService:
    def __init__(self, repo: UserRepository = None):
        self.repo = repo or UserRepository()

    def register(self, username, email, password, role="patient", **extra):
        # basic validation could be extended
        existing = self.repo.get_by_email(email)
        if existing:
            raise ValueError("Email already in use")
        return self.repo.create_user(username=username, email=email, password=password, role=role, **extra)

    def authenticate(self, email, password):
        # Use Django's authenticate (requires AUTHENTICATION_BACKENDS config)
        user = authenticate(username=email, password=password)
        return user

    def get_profile(self, user_id):
        return self.repo.get_by_id(user_id)

    def update_profile(self, user_id, **fields):
        return self.repo.update_user(user_id, **fields)

# accounts/tests/test_services.py
import pytest
from django.test import TestCase
from accounts.services.user_service import UserService
from accounts.repositories.user_repository import UserRepository
from accounts.models import CustomUser

class UserServiceTest(TestCase):
    def setUp(self):
        self.repo = UserRepository()
        self.service = UserService(repo=self.repo)

    def test_register_and_get_profile(self):
        user = self.service.register(username="jdoe", email="jdoe@example.com", password="pass1234")
        assert user is not None
        fetched = self.service.get_profile(user.id)
        assert fetched.email == "jdoe@example.com"

    def test_register_duplicate_email_raises(self):
        self.service.register(username="a", email="dup@example.com", password="x")
        with self.assertRaises(ValueError):
            self.service.register(username="b", email="dup@example.com", password="y")

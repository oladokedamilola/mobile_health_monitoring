# accounts/repositories/user_repository.py
from accounts.models import CustomUser
from django.db import IntegrityError

class UserRepository:
    def get_by_id(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None

    def get_by_email(self, email):
        return CustomUser.objects.filter(email__iexact=email).first()

    def create_user(self, username, email, password=None, **extra_fields):
        user = CustomUser(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        try:
            user.save()
            return user
        except IntegrityError:
            return None

    def update_user(self, user_id, **fields):
        user = self.get_by_id(user_id)
        if not user:
            return None
        for k, v in fields.items():
            setattr(user, k, v)
        user.save()
        return user

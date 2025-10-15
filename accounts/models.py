# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("patient", "Patient"),
        ("doctor", "Doctor"),
        ("admin", "Admin"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="patient")
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    
    class Meta:
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"


class DoctorVerification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    hospital_name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100)
    document = models.FileField(upload_to='doctor_documents/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"
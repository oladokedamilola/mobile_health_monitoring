# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("patient", "Patient"),
        ("doctor", "Doctor"),
        ("admin", "Admin"),
    )
    
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
        ("prefer_not_to_say", "Prefer not to say"),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="patient")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Email verification fields
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    email_verification_expiry = models.DateTimeField(blank=True, null=True)
    verification_sent_count = models.IntegerField(default=0)
    verification_rate_limit_expiry = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def can_resend_verification(self):
        """Check if user can resend verification email based on rate limits."""
        if not self.verification_rate_limit_expiry:
            return True
        return timezone.now() > self.verification_rate_limit_expiry
    
    def mark_verification_sent(self):
        """Track verification email sends and apply rate limits."""
        self.verification_sent_count += 1
        
        # First 3 attempts: 1-minute cooldown
        if self.verification_sent_count <= 3:
            self.verification_rate_limit_expiry = timezone.now() + timedelta(minutes=1)
        # 4th+ attempt: 1-hour cooldown
        else:
            self.verification_rate_limit_expiry = timezone.now() + timedelta(hours=1)
        
        self.save(update_fields=['verification_sent_count', 'verification_rate_limit_expiry'])


class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    
    def is_expired(self):
        """Check if token is expired (1 hour)"""
        expiry_time = self.created_at + timedelta(hours=1)
        return timezone.now() > expiry_time
    
    class Meta:
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['created_at']),
        ]


class PasswordResetAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    attempted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    @classmethod
    def recent_attempts(cls, user, minutes=30):
        """Count recent password reset attempts for a user"""
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(user=user, attempted_at__gte=cutoff).count()


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
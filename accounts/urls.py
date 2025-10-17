# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('register/<str:role>/', views.register_view, name='register_with_role'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Email Verification
    path('verify-email/', views.verify_email_notice, name='verify_email_notice'),
    path('verify-email/direct/', views.verify_email, name='verify_email'),
    
    # Password Reset
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    
    
    # ✅ Doctor verification URLs
    path("doctor/verification/", views.doctor_verification, name="doctor_verification"),
    path("doctor/verification/status/", views.verification_status, name="verification_status"),
    
]

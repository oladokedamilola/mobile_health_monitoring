# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/<str:role>/', views.register_view, name='register_with_role'),
    path('register/', views.register_view, name='register'),
    
    
    # ✅ Doctor verification URLs
    path("doctor/verification/", views.doctor_verification, name="doctor_verification"),
    path("doctor/verification/status/", views.verification_status, name="verification_status"),
    
    
    path('login/', views.login_view, name='login'),
    
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    
    
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('verify/', views.verify_view, name='verify'),
]

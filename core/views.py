# core/views.py
from django.shortcuts import render

def home_view(request):
    """Landing page for Auralis Health"""
    return render(request, "home.html")

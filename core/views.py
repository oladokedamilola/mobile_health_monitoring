# core/views.py
from django.shortcuts import render

def home_view(request):
    """Landing page for Auralis Health"""
    return render(request, "home.html")


from django.shortcuts import render
from django.http import HttpResponse

# Error handlers
def bad_request(request, exception=None):
    return render(request, "errors/400.html", status=400)

def unauthorized(request, exception=None):
    return render(request, "errors/401.html", status=401)

def forbidden(request, exception=None):
    return render(request, "errors/403.html", status=403)

def not_found(request, exception=None):
    return render(request, "errors/404.html", status=404)

def method_not_allowed(request, exception=None):
    return render(request, "errors/405.html", status=405)

def request_timeout(request, exception=None):
    return render(request, "errors/408.html", status=408)

def payload_too_large(request, exception=None):
    return render(request, "errors/413.html", status=413)

def too_many_requests(request, exception=None):
    return render(request, "errors/429.html", status=429)

def server_error(request):
    return render(request, "errors/500.html", status=500)

def bad_gateway(request, exception=None):
    return render(request, "errors/502.html", status=502)

def service_unavailable(request, exception=None):
    return render(request, "errors/503.html", status=503)

def gateway_timeout(request, exception=None):
    return render(request, "errors/504.html", status=504)
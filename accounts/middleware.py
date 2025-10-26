# core/middleware.py
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied, SuspiciousOperation

class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # Handle specific exceptions and return appropriate error responses
        if isinstance(exception, PermissionDenied):
            from .views import forbidden
            return forbidden(request)
        elif isinstance(exception, SuspiciousOperation):
            from .views import bad_request
            return bad_request(request)
        return None
# accounts/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def count_unverified(doctors):
    """Count unverified doctors from a queryset"""
    return doctors.filter(is_verified=False).count()

@register.filter
def filter_unverified(doctors):
    """Filter unverified doctors from a queryset"""
    return doctors.filter(is_verified=False)

@register.filter
def filter_verified(doctors):
    """Filter verified doctors from a queryset"""
    return doctors.filter(is_verified=True)

@register.filter
def filter_by_severity(anomalies, severity_levels):
    """Filter anomalies by severity levels (comma-separated)"""
    severity_list = [s.strip() for s in severity_levels.split(',')]
    return anomalies.filter(severity__in=severity_list)

@register.filter
def filter_by_severity(anomalies, severity_levels):
    """Filter anomalies by severity levels (comma-separated)"""
    severity_list = [s.strip() for s in severity_levels.split(',')]
    return anomalies.filter(severity__in=severity_list)
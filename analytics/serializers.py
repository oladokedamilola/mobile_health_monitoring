from rest_framework import serializers
from .models import HealthSummary

class HealthSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthSummary
        fields = "__all__"

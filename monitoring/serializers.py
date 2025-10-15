# monitoring/serializers.py
from rest_framework import serializers
from .models import HealthRecord, ActivityRecord

class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = ["id", "user", "heart_rate", "respiratory_rate", "spo2", "timestamp"]

class ActivityRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityRecord
        fields = ["id", "user", "activity_type", "intensity", "timestamp"]

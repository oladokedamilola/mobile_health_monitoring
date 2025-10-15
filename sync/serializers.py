from rest_framework import serializers
from .models import SyncLog, OfflineRecord

class SyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncLog
        fields = ('id', 'user', 'payload', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'status', 'created_at', 'updated_at', 'user')


class OfflineRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfflineRecord
        fields = ["id", "data_type", "payload", "created_at", "synced"]
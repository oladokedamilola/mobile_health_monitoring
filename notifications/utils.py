from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .serializers import NotificationSerializer

def push_notification_to_user(notification):
    """Send WebSocket message to user in real-time."""
    channel_layer = get_channel_layer()
    data = NotificationSerializer(notification).data
    async_to_sync(channel_layer.group_send)(
        f"notifications_{notification.user.id}",
        {"type": "send_notification", "notification": data},
    )

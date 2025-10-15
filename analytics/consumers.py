import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .services.services import AnalyticsService

class AnalyticsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        await self.accept()

    async def receive(self, text_data):
        data = AnalyticsService.get_trends(self.user)
        trends = [{"heart_rate": s.average_heart_rate, "created": s.created_at.isoformat()} for s in data]
        await self.send(json.dumps({"trends": trends}))

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


@sync_to_async
def user_from_token(token):
    try:
        return User.objects.get(pk=AccessToken(token)['user_id'])
    except Exception:
        return None


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            query_string = self.scope.get('query_string', b'').decode()
            token = next((part.split('=', 1)[1] for part in query_string.split('&') if part.startswith('token=')), '')
            user = await user_from_token(token)
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return
        self.group_name = f'notifications_{user.pk}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notification_event(self, event):
        await self.send_json(event['payload'])

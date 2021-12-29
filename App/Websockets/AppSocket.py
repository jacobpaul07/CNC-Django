import os
from datetime import datetime
import websockets
import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class AppSocket(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope.get('user', False)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = self.room_name

        mode = os.environ['ApplicationMode']
        if mode == "web":
            print('user websocket connecting with web mode')
            if not user:
                print("Un authorized user")
                await self.accept()
                await self.send(text_data=json.dumps({
                    'error': "Not Authenticated.."
                }))
                await self.close()
                return
            else:
                self.user = user
                print('connected')
                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
        else:
            print('user websocket connecting with iot mode')
            self.user = user
            print('connected')
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=message)

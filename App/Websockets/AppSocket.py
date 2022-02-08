import os
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

# import asyncio
# import copy
# import collections
# import functools
# import json
# import os
# from channels.consumer import get_handler_name
# from channels.generic.websocket import AsyncWebsocketConsumer
#
#
# class AppSocket(AsyncWebsocketConsumer):
#     MAX_ACTIVE_TASKS = 2
#
#     def __init__(self, *args, **kwargs):
#         super(AppSocket, self).__init__(*args, **kwargs)
#         self.handler_tasks = collections.defaultdict(list)
#         self.joined_groups = set()
#
#         self.room_name = None
#         self.room_group_name = None
#
#     def complete_task(self, task_instance, handler_name):
#         print(f'Complete task for handler {handler_name}, task instance {task_instance}')
#         self.handler_tasks[handler_name].remove(task_instance)
#         # print(
#         #     f'There are still {len(self.handler_tasks[handler_name])} active tasks for'
#         #     f' handler {handler_name}'
#         # )
#
#     async def dispatch(self, message):
#         handler_name = get_handler_name(message)
#         handler = getattr(self, handler_name, None)
#         if handler:
#             if handler_name:
#                 # Create a task to process message
#                 loop = asyncio.get_event_loop()
#                 if len(self.handler_tasks[handler_name]) >= self.MAX_ACTIVE_TASKS:
#                     await self.send(text_data=json.dumps({
#                         'message': 'MAX_ACTIVE_TASKS reached'
#                     }))
#                 else:
#                     handler_task = loop.create_task(handler(message))
#                     # don't forget to remove the task from self.handler_tasks
#                     # when task completed
#                     handler_task.add_done_callback(
#                         functools.partial(self.complete_task, handler_name=handler_name)
#                     )
#                     self.handler_tasks[handler_name].append(handler_task)
#             else:
#                 # The old way to process message
#                 await handler(message)
#         else:
#             raise ValueError("No handler for message type %s" % message["type"])
#
#     async def clear_handler_tasks(self):
#         for handler_name in self.handler_tasks:
#             task_instances = self.handler_tasks[handler_name]
#             for task_instance in task_instances:
#                 task_instance.cancel()
#
#     async def leave_group(self, group_name):
#         await self.channel_layer.group_discard(
#             group_name, self.channel_name
#         )
#         self.joined_groups.remove(group_name)
#
#     async def join_group(self, group_name):
#         await self.channel_layer.group_add(
#             group_name, self.channel_name
#         )
#         self.joined_groups.add(group_name)
#
#     async def connect(self):
#         user = self.scope.get('user', False)
#         mode = os.environ['ApplicationMode']
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = self.room_name
#         if mode == "web":
#             print('Websocket is Connected in Web Mode')
#             if not user:
#                 print("Un authorized user")
#                 await self.accept()
#                 await self.send(text_data=json.dumps({
#                     'error': "Not Authenticated.."
#                 }))
#                 await self.close()
#                 return
#             else:
#                 self.user = user
#                 print('connected')
#                 # Join room group
#                 await self.join_group(self.room_group_name)
#                 await self.accept()
#         else:
#             print('User Websocket is Connected in Mobile Mode')
#             self.user = user
#             print('connected')
#             await self.join_group(self.room_group_name)
#             await self.accept()
#
#     # disconnection from websocket
#     async def disconnect(self, code):
#         # Leave room group
#         joined_groups = copy.copy(self.joined_groups)
#         for group_name in joined_groups:
#             await self.leave_group(group_name)
#         self.joined_groups.clear()
#         await self.clear_handler_tasks()
#
#     # Receive message from WebSocket
#     async def receive(self, text_data=None, bytes_data=None):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )
#
#     # Receive message from room group
#     async def chat_message(self, event):
#         print('message sent')
#         message = event['message']
#         await self.send(text_data=message)

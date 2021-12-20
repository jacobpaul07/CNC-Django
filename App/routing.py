# chat/routing.py
from django.urls import re_path
from App.Websockets import AppSocket

websocket_urlpatterns = [
    # re_path(r'ws/app/notifications/',  AppSocket.AppSocket.as_asgi())
    re_path(r'ws/app/(?P<room_name>\w+)/$', AppSocket.AppSocket.as_asgi()),
]

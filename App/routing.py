# chat/routing.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from App.Websockets import AppSocket

websocket_urlpatterns = [re_path(r'ws/app/(?P<room_name>\w+)/$', AppSocket.AppSocket.as_asgi()),
                         ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


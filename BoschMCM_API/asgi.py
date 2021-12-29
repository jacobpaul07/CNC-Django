"""
ASGI config for BoschMCM_API project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import App.routing
from . import userAuthMiddleware
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BoschMCM_API.settings')

# application = get_asgi_application()
# application = ProtocolTypeRouter({
#     # 'http': get_asgi_application(),
#     'websocket': AuthMiddlewareStack(
#         URLRouter(
#             App.routing.websocket_urlpatterns
#         )
#     ),
# })


mode = os.environ['ApplicationMode']
if mode == "web":
    print("web mode in asgi")
    application = ProtocolTypeRouter({
        # "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            userAuthMiddleware.UserAuthMiddleware(
                URLRouter(
                    App.routing.websocket_urlpatterns
                )
            )
        ),
    })

else:
    application = ProtocolTypeRouter({
        # "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    App.routing.websocket_urlpatterns
                )
            )
        ),
    })

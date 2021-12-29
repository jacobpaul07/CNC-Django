import asyncio
from channels.db import DatabaseSyncToAsync
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.backends import TokenBackend , TokenBackendError , InvalidTokenError
from django.conf import settings

   
class UserAuthMiddleware:
    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):

        token = False
        query = scope["query_string"]
        if(query):
            query = query.decode()
        if(query):
            query = query.split('=')
            if(query[0] == 'token'):
                token = query[1]

        if(token):
            try:
                data = {'token': token}
                algoritham = settings.SIMPLE_JWT["ALGORITHM"]
                valid_data = TokenBackend(algorithm=algoritham).decode(token, verify=False)
                user = valid_data['user_id']
                scope['user'] = user
            except Exception as v:
                print("error on token validation", v)

        return await self.app(scope, receive, send)

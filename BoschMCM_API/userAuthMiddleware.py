import datetime
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings


class UserAuthMiddleware:
    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):

        token = False
        query = scope["query_string"]
        if query:
            query = query.decode()
        if query:
            query = query.split('=')
            if query[0] == 'token':
                token = query[1]

        if token:
            try:
                algorithm = settings.SIMPLE_JWT["ALGORITHM"]
                valid_data = TokenBackend(algorithm=algorithm).decode(token, verify=False)
                token_current_time = int(datetime.datetime.now().timestamp())
                token_exp_time = valid_data['exp']
                if token_exp_time < token_current_time:
                    raise Exception
                user = valid_data['user_id']
                scope['user'] = user
            except Exception as v:
                print("error on token validation", v)

        return await self.app(scope, receive, send)

from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from ..authentication import bearer as bear_token_auth
from ..users.models import User
from ..users.db_queries import base as user_db_query


@database_sync_to_async
def get_user(user_id: str) -> User | AnonymousUser:
    user = user_db_query.get_user_by_id(user_id)
    if user:
        return user
    else:
        AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):

    def __init__(self, inner):
        super().__init__(inner)
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            token_name, token_key = headers[b'authorization'].decode().split()  # noqa
            if token_name.lower() == 'bearer':
                token_auth = bear_token_auth.TokenAuthentication()
                token_auth_payload, _ = token_auth.authenticate_token(token_key)
                if token_auth_payload and isinstance(token_auth_payload, dict):
                    user_id = token_auth_payload.get('sub', '')
                    if user_id:
                        scope['user'] = await get_user(user_id)
                    else:
                        scope['user'] = AnonymousUser()
        return await super().__call__(scope, receive, send)

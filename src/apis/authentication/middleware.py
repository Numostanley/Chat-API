from rest_framework.authentication import get_authorization_header

from . import bearer as bear_token_auth


class TokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # set the following values before getting the response i.e self.get_response(request)
        # because the response would have processed the initial request and will invalidate
        # any other request

        auth = get_authorization_header(request).split()

        if len(auth) == 2:
            auth_keyword, auth_secret = auth[0].decode(), auth[1].decode()
            if auth_keyword.lower() == 'bearer':
                token_auth = bear_token_auth.TokenAuthentication()
                token_auth_payload, _ = token_auth.authenticate_token(auth_secret)

                if token_auth_payload and isinstance(token_auth_payload, dict):
                    request.role = token_auth_payload.get('role', '')
                    request.user_id = token_auth_payload.get('sub', '')
                    request.user_email = token_auth_payload.get('email', '')
                    request.full_name = token_auth_payload.get('full_name', '')
                    request.scope = token_auth_payload.get('scope', '')
                    request.two_fa_verified = token_auth_payload.get('two_fa_verified', False)
        response = self.get_response(request)
        return response

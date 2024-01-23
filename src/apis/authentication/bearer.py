import logging

from datetime import datetime

import jwt
from django.conf import settings

from django.utils.translation import gettext_lazy as _
from jwt import exceptions as jwt_exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from ..base import exceptions as custom_exceptions
from ..clients import enums as role_enums
from ..users.db_queries import base as user_base_db_queries


log = logging.getLogger(__name__)


def decode_token(token, verify_signature=True) -> dict:
    """
    DANGER ZONE: Do not set `verify_signature` to False. Setting it to
    False is not safe for the API.
    NB: `verify_signature` was set to False only because there's need to
    extract values from the token even if it has expired to control
    the response sent back to user
    """

    public_key = settings.PUBLIC_KEY
    alg = settings.SIGNING_ALGORITHM

    if verify_signature:
        t = jwt.decode(
            token,
            public_key,
            algorithms=[alg],
            audience=settings.AUDIENCE,
        )
    else:
        t = jwt.decode(
            token,
            public_key,
            algorithms=[alg],
            options={'verify_signature': False}
        )
    return t


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Bearer ".  For example:

        Authorization: Bearer ey.sdAsx.apad...
    """

    keyword = 'Bearer'
    admin_role_name = role_enums.RoleEnum.ADMIN_USER.upper()
    users_role_name = role_enums.RoleEnum.APP_USER.upper()

    def authenticate(self, request):
        auth = get_authorization_header(request).split()  # noqa

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            msg = _("The Authorization header isn't BEARER authorization header.")
            raise custom_exceptions.InvalidBearerHeader(msg)

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise custom_exceptions.AuthenticationError(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise custom_exceptions.AuthenticationError(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise custom_exceptions.AuthenticationError(msg)

        jwt_payload, _ignore = self.authenticate_token(token)

        if jwt_payload and isinstance(jwt_payload, dict):
            expiry_time = jwt_payload['expiry_time']
            issuer = jwt_payload['issuer']

            if datetime.now() > expiry_time:
                # if JWT is expired, raise `Token is expired`
                raise custom_exceptions.JWTExpired()

            if issuer.lower() != settings.ISSUER:
                # if issuer is invalid, raise `Invalid Token`
                raise custom_exceptions.InvalidJWT()

            user = user_base_db_queries.get_user_by_id(
                id=jwt_payload['sub']
            )

            # check if user associated with the token exists in the DB
            if not user:
                raise custom_exceptions.InvalidUser()

            if user.two_fa_enabled and not jwt_payload['two_fa_verified']:
                raise custom_exceptions.TwoFactorAuthenticationFailed()

            return jwt_payload, None
        else:
            raise custom_exceptions.InvalidJWT()

    def authenticate_token(self, token) -> tuple[dict, None]:  # noqa
        """
        authenticate token passed in the Authorization header
        return type: tuple (dict, None). `dict` contains the decoded JWT
         if it succeeds or JWT is expired else empty dict
        """
        try:
            decoded_jwt = decode_token(token)
            expiry_time = datetime.fromtimestamp(decoded_jwt['exp'])
            sub = decoded_jwt['sub']
            decoded_jwt_payload: dict = {
                'sub': sub,
                'email': decoded_jwt['email'],
                'role': decoded_jwt['role'],
                'expiry_time': expiry_time,
                'full_name': decoded_jwt['full_name'],
                'issuer': decoded_jwt['iss'],
                'scope': decoded_jwt['scope'],
                'two_fa_verified': decoded_jwt['two_fa_verified']
            }
            return decoded_jwt_payload, None
        except jwt_exceptions.ExpiredSignatureError as e:
            log.error('TokenAuthentication.ExpiredSignatureError@Error')
            log.error(e)
            decoded_jwt = decode_token(token, verify_signature=False)
            expiry_time = datetime.fromtimestamp(decoded_jwt['exp'])
            sub = decoded_jwt['sub']
            decoded_jwt_payload: dict = {
                'sub': sub,
                'email': decoded_jwt['email'],
                'role': decoded_jwt['role'],
                'expiry_time': expiry_time,
                'full_name': decoded_jwt['full_name'],
                'issuer': decoded_jwt['iss'],
                'scope': decoded_jwt['scope'],
                'two_fa_verified': decoded_jwt['two_fa_verified']
            }
            return decoded_jwt_payload, None
        except Exception as e:
            log.error('TokenAuthentication.authenticate_token@Error')
            log.error(e)
            return {}, None

    def authenticate_header(self, request):
        return self.keyword


class AdminTokenAuthentication(TokenAuthentication):

    def authenticate(self, request):
        jwt_payload, _ = super(AdminTokenAuthentication, self).authenticate(request)
        jwt_role = jwt_payload['role'].upper()
        role_name = role_enums.RoleEnum.ADMIN_USER
        if jwt_role.upper() == role_name.upper():
            return jwt_payload, None
        raise custom_exceptions.UnauthorizedUser()


class GenericTenantAuthentication(TokenAuthentication):

    def authenticate(self, request):
        jwt_payload, _ = super(GenericTenantAuthentication, self).authenticate(request)
        jwt_role = jwt_payload['role'].upper()

        if jwt_role in [self.admin_role_name, self.users_role_name]:
            return jwt_payload, None
        raise custom_exceptions.AccountNotActivated()


class UserTokenAuthentication(TokenAuthentication):

    def authenticate(self, request):
        jwt_payload, _ = super(UserTokenAuthentication, self).authenticate(request)
        jwt_role = jwt_payload['role'].upper()

        if jwt_role in [self.admin_role_name, self.users_role_name]:
            return jwt_payload, None

        raise custom_exceptions.AccountNotActivated()

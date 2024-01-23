from django.conf import settings
from rest_framework import serializers

from . import enums as authentication_enums, models as authentication_models
from .db_queries import base as authentication_base_db_queries
from ..base import serializers_validators as serializer_validators
from ..clients import models as client_models
from ..users.db_queries import base as user_base_db_queries


class AuthorizationGrantSerializer(serializers.Serializer):  # noqa
    client_id = serializers.CharField()
    scope = serializers.CharField()
    code = serializers.CharField()
    response_type = serializers.CharField()
    state = serializers.CharField()
    redirect_uri = serializers.CharField()


class TokenSerializer(serializers.Serializer):  # noqa
    client_id = serializers.CharField()
    client_secret = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()
    grant_type = serializers.CharField()
    scope = serializers.CharField()
    # redirect_uri = serializers.CharField()

    def validate(self, attrs):
        client_id = attrs['client_id']
        grant_type = attrs['grant_type']
        client = client_models.Client.get_by_id(client_id)

        if not client:
            raise serializers.ValidationError(
                'invalid_client'
            )

        if not client.validate_grant_type(grant_type):
            raise serializers.ValidationError(
                'invalid_grant_type'
            )
        return attrs


class RefreshTokenRequestSerializer(serializers.Serializer):  # noqa
    client_id = serializers.CharField()
    client_secret = serializers.CharField()
    code = serializers.CharField()
    grant_type = serializers.CharField()

    def save(self):
        user_id: str = self.context.get('user_id', '')
        two_fa_verified: bool = self.context.get('two_fa_verified', '')

        code = self.validated_data.get('code', '')

        user = user_base_db_queries.get_user_by_id(id=user_id)
        refresh_token = authentication_base_db_queries.get_refresh_token_by_code(code)
        refresh_token.delete()
        new_refresh_token = authentication_models.RefreshToken.create(user_id)
        scope: str = 'offline_access email'

        if two_fa_verified:
            access_token = user.get_token_for_successful_2fa_verification(scope)
        else:
            access_token = user.get_token(scope)

        response_data: dict = {
            'access_token': access_token,
            'refresh_token': new_refresh_token.code,
            'token_type': 'Bearer',
            'expires_in': settings.TOKEN_EXPIRY_TIME,
            'scope': scope
        }
        return response_data

    def validate(self, attrs):
        user_id: str = self.context.get('user_id', '')

        client_id: str = attrs['client_id']
        grant_type: str = attrs['grant_type']
        code: str = attrs['code']

        client = client_models.Client.get_by_id(client_id)
        if not client:
            raise serializers.ValidationError(
                'invalid_client!'
            )

        if not client.validate_grant_type(grant_type):
            raise serializers.ValidationError(
                'invalid_grant_type!'
            )

        refresh_token = authentication_base_db_queries.get_refresh_token_by_code(code)
        if not refresh_token.is_valid(user_id):
            raise serializers.ValidationError(
                'Invalid refresh token!'
            )

        if grant_type != authentication_enums.GrantTypesEnum.REFRESH_TOKEN:
            raise serializers.ValidationError(
                'Invalid grant type!'
            )

        user = user_base_db_queries.get_user_by_id(id=user_id)
        if not user.validate_user_against_client_id(client_id):
            raise serializers.ValidationError(
                'Invalid client and user!'
            )
        return attrs


class SendEmailConfirmationLinkRequestSerializer(serializers.Serializer):  # noqa
    email = serializers.EmailField(validators=[
        serializer_validators.validate_email
    ])


class ChangePasswordSerializer(serializers.Serializer):  # noqa
    current_password = serializers.CharField(validators=[
        serializer_validators.validate_password
    ])
    new_password = serializers.CharField(validators=[
        serializer_validators.validate_password
    ])


class ForgotPasswordRequestSerializer(serializers.Serializer):  # noqa
    email = serializers.CharField(validators=[
        serializer_validators.validate_email
    ])


class ResetPasswordSerializer(serializers.Serializer):  # noqa
    password = serializers.CharField(validators=[
        serializer_validators.validate_password
    ])

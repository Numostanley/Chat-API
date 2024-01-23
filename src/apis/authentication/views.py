from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import FormParser

from .db_queries import base as authentication_base_db_queries
from . import models as auth_models, serializers as auth_serializers
from ..base import helpers as base_repo_helpers, responses as base_repo_responses, views as base_repo_views
from ..clients import models as client_models
from ..users.db_queries import base as user_base_db_queries


class AuthorizationGrantAPIView(base_repo_views.BaseAPIView):
    parser_classes = [FormParser]

    @extend_schema(
        request=auth_serializers.AuthorizationGrantSerializer
    )
    def get(self, request, *args, **kwargs):  # noqa
        try:
            serializer = auth_serializers.AuthorizationGrantSerializer(
                data=request.data
            )
            if serializer.is_valid():
                data = serializer.validated_data
                client_id = data['client_id']
                client = client_models.Client.get_by_id(client_id)
                if not client:
                    return base_repo_responses.http_response_401(
                        'Invalid client!'
                    )

                return base_repo_responses.http_response_200(
                    'Authentication successful!', data=serializer.data
                )
            return base_repo_responses.http_response_400(
                'Bad request!', errors=serializer.errors
            )
        except Exception as e:
            self._log.error('AuthorizationGrantAPIView.get@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)


class TokenAPIView(base_repo_views.BaseAPIView):
    parser_classes = [FormParser]

    @extend_schema(
        request=auth_serializers.TokenSerializer
    )
    def post(self, request, *args, **kwargs):  # noqa
        try:
            serializer = auth_serializers.TokenSerializer(
                data=request.data
            )
            if serializer.is_valid():
                data: dict = serializer.validated_data
                client_id: str = data['client_id']
                client_secret: str = data['client_secret']
                grant_type: str = data['grant_type']
                username: str = data['username']
                password: str = data['password']
                scope: str = data['scope']

                client = client_models.Client.get_by_id(client_id)
                if not client:
                    errors: dict = {
                        'error_message': 'invalid_client'
                    }
                    return base_repo_responses.http_response_401(
                        'Authentication Error!', errors=errors
                    )

                if not client.validate_secret(client_secret):
                    errors: dict = {
                        'error_message': 'invalid_credentials'
                    }
                    return base_repo_responses.http_response_401(
                        'Authentication Error!', errors=errors
                    )

                if not client.validate_grant_type(grant_type):
                    errors: dict = {
                        'error_message': 'invalid_grant_type'
                    }
                    return base_repo_responses.http_response_401(
                        'Authentication Error!', errors=errors
                    )

                if not client.validate_scope(scope):
                    errors: dict = {
                        'error_message': 'invalid_scope'
                    }
                    return base_repo_responses.http_response_401(
                        'Authentication Error!', errors=errors
                    )

                user = user_base_db_queries.get_user_by_username(username=username)
                if not user:
                    errors: dict = {
                        'error_message': 'invalid_user'
                    }
                    return base_repo_responses.http_response_401(
                        'Authentication Error!', errors=errors
                    )

                if not user.is_active:
                    errors: dict = {
                        'error_message': 'invalid_user'
                    }
                    return base_repo_responses.http_response_401(
                        'Authentication Error!', errors=errors
                    )

                if not user.validate_password(password):
                    errors: dict = {
                        'error_message': 'invalid_user_credentials'
                    }
                    return base_repo_responses.http_response_401(
                        'Authentication Error!', errors=errors
                    )

                if not user.validate_user_against_client_id(client_id):
                    errors: dict = {
                        'error_message': 'invalid_client_and_user!'
                    }
                    return base_repo_responses.http_response_401(
                        'Authentication Error!', errors=errors
                    )

                if settings.ENVIRONMENT == settings.PROD_ENV_VALUE:
                    if user.has_an_active_session:
                        errors: dict = {
                            'error_message': 'user_has_an_active_session'
                        }
                        return base_repo_responses.http_response_401(
                            'Authentication Error!', errors=errors
                        )

                refresh_token = auth_models.RefreshToken.create(user.id)
                response_data: dict = {
                    'access_token': user.get_token(scope),
                    'refresh_token': refresh_token.code,
                    'token_type': 'Bearer',
                    'expires_in': settings.TOKEN_EXPIRY_TIME,
                    'scope': scope
                }
                return base_repo_responses.http_response_200(
                    'Authentication successful!', data=response_data, headers={'Cache-Control': 'no-store'}
                )
            return base_repo_responses.http_response_400(
                'Bad request!', errors=serializer.errors
            )
        except Exception as e:  # noqa
            self._log.error('TokenAPIView.post@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)


class RefreshTokenAPIView(base_repo_views.TokenAuthenticationAPIView):
    parser_classes = [FormParser]

    @extend_schema(
        request=auth_serializers.RefreshTokenRequestSerializer
    )
    def post(self, request, *args, **kwargs):  # noqa
        try:
            two_fa_verified: bool = request.two_fa_verified
            user_id: str = request.user_id

            context: dict = {
                'user_id': user_id,
                'two_fa_verified': two_fa_verified
            }
            serializer = auth_serializers.RefreshTokenRequestSerializer(
                data=request.data, context=context
            )
            if serializer.is_valid():
                response_data = serializer.save()
                return base_repo_responses.http_response_200(
                    'Authentication successful!', data=response_data
                )
            return base_repo_responses.http_response_400(
                'Bad request!', errors=serializer.errors
            )
        except Exception as e:  # noqa
            self._log.error('RefreshTokenAPIView.post@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)


class SendEmailConfirmationLinkAPIView(base_repo_views.BasicAuthenticationAPIView):

    @extend_schema(
        request=auth_serializers.SendEmailConfirmationLinkRequestSerializer
    )
    def post(self, request, *args, **kwargs):  # noqa
        try:
            serializer = auth_serializers.SendEmailConfirmationLinkRequestSerializer(
                data=request.data
            )
            if serializer.is_valid():
                data = serializer.validated_data
                email = data['email']
                user = user_base_db_queries.get_user_by_email(email=email)
                if not user:
                    return base_repo_responses.http_response_404(
                        'Invalid user. Email cannot be sent for verification!'
                    )
                user_id = user.id
                uid = urlsafe_base64_encode(force_bytes(user_id))
                token = default_token_generator.make_token(user)
                domain = get_current_site(request).domain
                email_confirmation_link: str = f'{request.scheme}://{domain}/confirm-email?uid={uid}&token={token}'
                subject: str = 'Email Confirmation!'
                message: str = f'Kindly confirm your email!\n\n {email_confirmation_link}'
                base_repo_helpers.send_email(email, subject, message)
                return base_repo_responses.http_response_200(
                    'Email confirmation link sent!'
                )
            return base_repo_responses.http_response_400(
                'Bad request!', errors=serializer.errors
            )
        except Exception as e:
            self._log.error('SendEmailConfirmationLinkAPIView.post@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)


class VerifyEmailAPIView(base_repo_views.BasicAuthenticationAPIView):

    def get(self, request, *args, **kwargs):  # noqa
        try:
            query_params = request.query_params
            try:
                uid = urlsafe_base64_decode(query_params.get('uid', '')).decode()
                user = user_base_db_queries.get_user_by_id(id=uid)
                token = query_params.get('token', '')
                decoded_token = default_token_generator.check_token(user, token)
            except UnicodeDecodeError:
                return base_repo_responses.http_response_401(
                    'Invalid email confirmation link!'
                )

            if not user:
                return base_repo_responses.http_response_400(
                    'Invalid email confirmation link!'
                )

            if user and decoded_token:
                user.email_verified = True
                user.save()
                return base_repo_responses.http_response_200(
                    'Email verified successfully!'
                )
            return base_repo_responses.http_response_400(
                'Email confirmation link has expired!'
            )
        except Exception as e:
            self._log.error('VerifyEmailAPIView.get@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)


class ChangePasswordAPIView(base_repo_views.TokenAuthenticationAPIView):

    @extend_schema(
        request=auth_serializers.ChangePasswordSerializer
    )
    def post(self, request, *args, **kwargs):  # noqa
        try:
            user = user_base_db_queries.get_user_by_id(
                id=request.user_id
            )
            serializer = auth_serializers.ChangePasswordSerializer(
                data=request.data
            )
            if serializer.is_valid():
                data = serializer.validated_data
                current_password = data['current_password']
                new_password = data['new_password']

                if not user.validate_password(current_password):
                    return base_repo_responses.http_response_400(
                        'Incorrect password!'
                    )

                user.set_new_password = new_password
                user.save()
                return base_repo_responses.http_response_200(
                    'Password changed successfully!'
                )
            return base_repo_responses.http_response_400(
                'Bad request!', errors=serializer.errors
            )
        except Exception as e:  # noqa
            self._log.error('ChangePasswordAPIView.post@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)


class ForgotPasswordAPIView(base_repo_views.BasicAuthenticationAPIView):

    @extend_schema(
        request=auth_serializers.ForgotPasswordRequestSerializer
    )
    def post(self, request, *args, **kwargs):  # noqa
        try:
            serializer = auth_serializers.ForgotPasswordRequestSerializer(
                data=request.data
            )
            if serializer.is_valid():
                data: dict = serializer.validated_data
                email: str = data['email']
                user = user_base_db_queries.get_user_by_email(email=email)
                if user:
                    user_id = user.id
                    uid = urlsafe_base64_encode(force_bytes(user_id))
                    token = default_token_generator.make_token(user)
                    domain = get_current_site(request).domain
                    reset_link: str = f'{request.scheme}://{domain}/auth/verify-email?uid={uid}&token={token}'
                    subject: str = 'Reset Password'
                    message: str = (f'Kindly click this link to reset your password! This link expires in the next 8 '
                                    f'minutes \n\n {reset_link}')
                    base_repo_helpers.send_email(email, subject, message)
                return base_repo_responses.http_response_200(
                    'A link has been sent to your email with instructions to reset your password!'
                )
            return base_repo_responses.http_response_400(
                'Bad request!', errors=serializer.errors
            )
        except Exception as e:  # noqa
            self._log.error('ForgotPasswordAPIView.post@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)


class VerifyPasswordResetTokenAPIView(base_repo_views.BasicAuthenticationAPIView):

    def get(self, request, *args, **kwargs):  # noqa
        try:
            query_params = request.query_params
            try:
                uid = urlsafe_base64_decode(query_params.get('uid', '')).decode()
                user = user_base_db_queries.get_user_by_id(id=uid)
                token = query_params.get('token', '')
                decoded_token = default_token_generator.check_token(user, token)
            except UnicodeDecodeError:
                return base_repo_responses.http_response_401(
                    'Invalid password reset token!'
                )

            if not user:
                return base_repo_responses.http_response_400(
                    'Invalid reset token!'
                )

            if user and decoded_token:
                domain = get_current_site(request).domain
                user_id = user.id
                uid = urlsafe_base64_encode(force_bytes(user_id))
                new_token: str = default_token_generator.make_token(user)
                reset_link: str = f'{request.scheme}://{domain}/auth/reset-password?uid={uid}&token={new_token}'
                password_reset_url_payload: dict = {
                    'user_id': user.id,
                    'token': new_token
                }
                auth_models.PasswordResetUrl.create(password_reset_url_payload)
                data: dict = {
                    'url': reset_link
                }
                return base_repo_responses.http_response_200(
                    'Password reset link verified successfully!', data=data
                )
            return base_repo_responses.http_response_401(
                'Password reset token has expired!'
            )
        except Exception as e:  # noqa
            self._log.error('VerifyPasswordResetTokenAPIView.get@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)


class ResetPasswordAPIView(base_repo_views.BasicAuthenticationAPIView):

    @extend_schema(
        request=auth_serializers.ResetPasswordSerializer
    )
    def post(self, request, *args, **kwargs):  # noqa
        try:
            query_params = request.query_params
            try:
                uid = urlsafe_base64_decode(query_params.get('uid', '')).decode()
                user = user_base_db_queries.get_user_by_id(id=uid)
            except UnicodeDecodeError:
                return base_repo_responses.http_response_401(
                    'Invalid password reset link!'
                )

            if not user:
                return base_repo_responses.http_response_400(
                    'Invalid reset token!'
                )

            token = query_params.get('token', '')
            token = authentication_base_db_queries.get_password_reset_url_by_token(token=token)
            if user and token and token.is_valid(user.id):
                serializer = auth_serializers.ResetPasswordSerializer(
                    data=request.data
                )
                if serializer.is_valid():
                    data: dict = serializer.validated_data
                    password: str = data['password']

                    user.set_new_password = password
                    user.save()

                    token.used = True
                    token.save()
                    return base_repo_responses.http_response_200(
                        'Password reset successfully!'
                    )
                return base_repo_responses.http_response_400(
                    'Bad request!', errors=serializer.errors
                )
            return base_repo_responses.http_response_401(
                'Password reset link has expired!'
            )
        except Exception as e:  # noqa
            self._log.error('ResetPasswordAPIView.post@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)

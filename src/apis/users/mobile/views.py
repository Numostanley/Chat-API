from ...base import responses as base_repo_responses, views as base_repo_views
from .serializers import requests as mobile_user_request_serializers
from ..db_queries import base as user_base_db_queries
from .serializers import responses as mobile_user_response_serializers


class SignupAPIView(base_repo_views.BasicAuthenticationAPIView):

    def post(self, request, *args, **kwargs):  # noqa
        try:
            serializer = mobile_user_request_serializers.SignupRequestSerializer(
                data=request.data
            )
            if serializer.is_valid():
                data: dict = serializer.validated_data
                created_user = serializer.create(data)
                response_data: dict = {
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'phone_number': data['phone_number'],
                    'username': data['username'],
                    'user_id': created_user.id
                }
                return base_repo_responses.http_response_200(
                    'Account created successfully!', data=response_data
                )
            return base_repo_responses.http_response_400(
                'Bad request!', errors=serializer.errors
            )
        except Exception as e:
            self._log.error('SignupAPIView.post@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)


class UserDetailAPIView(base_repo_views.UserAuthenticationAPIView):

    def get(self, request, *args, **kwargs):  # noqa
        try:
            user = user_base_db_queries.get_user_by_id(id=self.request.user_id)
            if not user:
                return base_repo_responses.http_response_404(
                    'User does not exist!'
                )
            serializer = mobile_user_response_serializers.UserDetailSerializer(
                instance=user
            )
            return base_repo_responses.http_response_200(
                'User profile retrieved successfully!', data=serializer.data
            )
        except Exception as e:
            self._log.error('UserDetailAPIView.get@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)


class UserListAPIView(base_repo_views.UserAuthenticationAPIView):

    def get(self, request, *args, **kwargs):  # noqa
        try:
            users = user_base_db_queries.get_all_users()
            if not users:
                return base_repo_responses.http_response_404(
                    'No users exist!'
                )
            serializer = mobile_user_response_serializers.UserDetailSerializer(
                instance=users, many=True
            )
            return base_repo_responses.http_response_200(
                'Users list retrieved successfully!', data=serializer.data
            )
        except Exception as e:
            self._log.error('UserListAPIView.get@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)

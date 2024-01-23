from rest_framework import serializers

from ....clients import enums as role_enums
from ... import models as user_models
from ...db_queries import base as user_base_db_queries


class SignupRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.User
        fields: list[str] = [
            'first_name', 'last_name', 'email', 'password', 'phone_number', 'username'
        ]
        extra_kwargs: dict = {
            'first_name': {'required': True}, 'last_name': {'required': True},
            'email': {'required': True}, 'password': {'required': True},
            'phone_number': {'required': True}, 'username': {'required': True}
        }

    def create(self, validated_data):
        try:
            role: str = role_enums.RoleEnum.APP_USER
            payload: dict = {
                'first_name': validated_data.get('first_name', ''),
                'last_name': validated_data.get('last_name', ''),
                'email': validated_data.get('email', ''),
                'phone_number': validated_data.get('phone_number', ''),
                'password': validated_data.get('password', ''),
                'username': validated_data.get('username', ''),
                'role': role
            }
            user = user_models.User.create(payload)
            return user
        except Exception:  # noqa
            return None

    def validate(self, attrs):
        email: str = attrs['email']
        phone_number: str = attrs['phone_number']
        username: str = attrs['username']

        user_with_email = user_base_db_queries.get_user_by_email(email=email)
        if user_with_email:
            raise serializers.ValidationError(
                'Email already exist!'
            )

        user_with_username = user_base_db_queries.get_user_by_username(username=username)
        if user_with_username:
            raise serializers.ValidationError(
                'Email already exist!'
            )

        user_with_phone_number = user_base_db_queries.get_user_by_phone_number(phone_number=phone_number)
        if user_with_phone_number:
            raise serializers.ValidationError(
                'Phone number already exist!'
            )

        return attrs

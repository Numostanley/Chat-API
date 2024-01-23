from datetime import timedelta

import jwt
from django.conf import settings

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from ..base import helpers as base_repo_helpers, models as base_repo_models
from ..clients import enums as client_enums
from .import enums as user_enums, model_helpers as user_model_helpers


class User(base_repo_models.BaseModel, AbstractUser):
    id = models.CharField(primary_key=True, default=user_model_helpers.generate_user_id, db_index=True,
                          max_length=60, editable=False, unique=True)
    first_name = models.CharField(max_length=70, default="", blank=True)
    middle_name = models.CharField(max_length=70, default="", blank=True)
    last_name = models.CharField(max_length=70, default="", blank=True)
    gender = models.CharField(max_length=10, default="", blank=True)
    email = models.EmailField(max_length=100, default="", blank=True)
    email_verified = models.BooleanField(default=False)
    username = models.CharField(max_length=50, default="", blank=True, unique=True)
    phone_number = models.CharField(max_length=15, default="", blank=True)
    profile_picture = models.URLField(default="", blank=True)
    password = models.CharField(max_length=240, default="", blank=True, null=True)
    two_fa_enabled = models.BooleanField(default=False)
    two_fa_medium = models.CharField(max_length=15, default=user_enums.TwoFactorAuthenticationMedium.SMS)
    phone_number_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True)
    address = models.CharField(max_length=200, default="", blank=True)
    city = models.CharField(max_length=50, default="", blank=True)
    state = models.CharField(max_length=50, default="", blank=True)
    state_of_residence = models.CharField(max_length=50, default="", blank=True)
    postal_code = models.CharField(max_length=50, default="", blank=True)
    groups = models.JSONField(default=list, null=True)
    is_first_login = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default="")
    marital_status = models.CharField(max_length=20, default="")
    state_of_origin = models.CharField(max_length=40, default="")
    is_super_user = models.BooleanField(default=False)
    role = models.CharField(max_length=20, default="")

    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]
    USERNAME_FIELD = "username"

    class Meta:
        ordering = ['first_name', 'last_name']

    def validate_password(self, password: str) -> bool:
        return self.check_password(password)

    @property
    def has_an_active_session(self) -> bool:
        time_difference = timezone.now() - self.last_login
        return time_difference < timedelta(minutes=30)

    @property
    def set_new_password(self):
        raise AttributeError('Password is not readable!')

    @set_new_password.setter
    def set_new_password(self, password: str):
        self.password = make_password(password)

    @staticmethod
    def validate_user_against_client_id(client_id: str) -> bool:
        clients: list[str] = [
            client_enums.ClientTypeEnum.APP_CLIENT,
            client_enums.ClientTypeEnum.ADMIN_USER_CLIENT
        ]
        return client_id in clients

    def get_token(self, scope) -> str:
        key: str = settings.PRIVATE_KEY
        alg: str = settings.SIGNING_ALGORITHM
        aud: str = settings.AUDIENCE
        now = timezone.now()

        headers: dict = {
            'alg': alg
        }

        payload: dict = {
            'iss': settings.ISSUER,
            'sub': self.id,
            'full_name': self.get_full_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'role': self.role,
            'address': self.address,
            'two_fa_verified': False,
            'scope': scope,
            'iat': now,
            'aud': aud,
            'exp': now + timedelta(seconds=settings.TOKEN_EXPIRY_TIME)
        }
        token = jwt.encode(payload, key, algorithm=alg, headers=headers)
        self.last_login = now
        self.save()
        return token

    @property
    def get_full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @staticmethod
    def append_phone_number(phone_number: str) -> str:
        return base_repo_helpers.append_phone_no_with_0(phone_number)

    @staticmethod
    def append_plus_to_country_code(country_code: str):
        return base_repo_helpers.append_country_code_with_plus(country_code)

    @staticmethod
    def create(payload: dict):
        phone_number = f"{payload.get('phone_number', '')}"
        return User.objects.create(
            first_name=payload.get('first_name', ''),
            last_name=payload.get('last_name', ''),
            email=payload.get('email', ''),
            phone_number=User.append_phone_number(phone_number),
            username=payload.get('username', ''),
            role=payload.get('role', ''),
            password=make_password(payload.get('password', None))
        )

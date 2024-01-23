from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db import models
from django.utils import timezone

from ..base import helpers as base_repo_helpers, models as base_repo_models
from . import model_helpers as authentication_model_helpers
from ..users.db_queries import base as user_db_queries


class RefreshToken(base_repo_models.BaseModel):
    id = models.CharField(primary_key=True, editable=False, db_index=True, max_length=60,
                          default=authentication_model_helpers.generate_refresh_token_id, unique=True)
    code = models.CharField(max_length=70, default="", db_index=True)
    user_id = models.CharField(max_length=70, default="")
    used = models.BooleanField(default=True)
    expiry_time = models.DateTimeField(default=timezone.now)

    def is_valid(self, user_id: str) -> bool:
        if self.user_id == user_id and self.expiry_time > timezone.now():
            return True
        return False

    @staticmethod
    def refresh_token_generator() -> tuple[str, datetime]:
        code = base_repo_helpers.generate_refresh_token_code()
        expiry_time = timezone.now() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRY_TIME)
        return code, expiry_time

    @staticmethod
    def create(user_id: str):
        code, expiry_time = RefreshToken.refresh_token_generator()
        return RefreshToken.objects.create(  # noqa
            user_id=user_id,
            code=code,
            used=False,
            expiry_time=expiry_time
        )


class PasswordResetUrl(base_repo_models.BaseModel):
    id = models.CharField(primary_key=True, editable=False, db_index=True, max_length=60,
                          default=authentication_model_helpers.generate_password_reset_token_id, unique=True)
    user_id = models.CharField(max_length=70, default="")
    used = models.BooleanField(default=True)
    token = models.CharField(max_length=100, default="", db_index=True)

    def is_valid(self, user_id: str) -> bool:
        user = user_db_queries.get_user_by_id(id=self.user_id)  # noqa
        token = default_token_generator.check_token(user, self.token)
        if self.user_id == user_id and not self.used and token:
            return True
        return False

    @staticmethod
    def create(payload: dict):
        return PasswordResetUrl.objects.create(  # noqa
            user_id=payload.get('user_id', ''),
            token=payload.get('token', ''),
            used=False
        )

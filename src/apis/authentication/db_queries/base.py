from datetime import timedelta

from django.db import models
from django.utils import timezone

from .. import models as authentication_models


def get_refresh_token_by_code(code: str):
    try:
        return authentication_models.RefreshToken.objects.get(code=code)
    except (Exception, authentication_models.RefreshToken.DoesNotExist):
        return None


def scheduler_get_used_or_expired_refresh_tokens():
    now = timezone.now()
    return authentication_models.RefreshToken.objects.filter(
        models.Q(used=True) | models.Q(expiry_time__lt=now)
    )


def get_password_reset_url_by_token(token: str):
    try:
        return authentication_models.PasswordResetUrl.objects.get(token=token)
    except (Exception, authentication_models.PasswordResetUrl.DoesNotExist):
        return None


def scheduler_get_used_or_expired_password_reset_tokens():
    time_delta = timezone.now() - timedelta(minutes=13)
    return authentication_models.PasswordResetUrl.objects.filter(
        models.Q(used=True) | models.Q(date_created__lte=time_delta)
    )

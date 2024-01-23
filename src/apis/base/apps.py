from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apis.base"

    def ready(self):
        from . import schedulers
        schedulers.schedule()

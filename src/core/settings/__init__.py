from .base import ENVIRONMENT, PROD_ENV_VALUE, DEV_ENV_VALUE


def get_settings_environment() -> str:
    if ENVIRONMENT == PROD_ENV_VALUE:
        ENV_SETTINGS = 'core.settings.prod'
    elif ENVIRONMENT == DEV_ENV_VALUE:
        ENV_SETTINGS = 'core.settings.dev'
    else:
        ENV_SETTINGS = 'core.settings.local'
    return ENV_SETTINGS

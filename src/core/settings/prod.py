from .base import *


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES: dict = {
    'default': {
        'ENGINE': env_config['DATABASE_ENGINE'],
        "NAME": env_config['DATABASE_NAME'],
        "HOST": env_config['DATABASE_HOST'],
        "USER": env_config['DATABASE_USER'],
        "PASSWORD": env_config['DATABASE_PASSWORD'],
        'PORT': env_config['DATABASE_PORT']
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static')
#     ]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

from enum import StrEnum


class GrantTypesEnum(StrEnum):
    AUTHORIZATION_CODE = 'authorization_code'
    PASSWORD = 'password'
    REFRESH_TOKEN = 'refresh_token'

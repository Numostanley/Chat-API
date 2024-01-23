from enum import StrEnum


class ClientTypeEnum(StrEnum):
    ADMIN_USER_CLIENT: str = "AdminClient"
    APP_CLIENT: str = "AppClient"


class RoleEnum(StrEnum):
    ADMIN_USER: str = "AdminUser"
    APP_USER: str = "AppUser"

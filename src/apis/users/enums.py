from enum import StrEnum, IntEnum


class TwoFactorAuthenticationMedium(StrEnum):
    EMAIL = "email"
    SMS = "sms"

    @classmethod
    def list_attributes(cls):
        return list(map(lambda x: {'name': x.name.replace('_', ' ').title(), 'value': x.value}, cls))

    @classmethod
    def list_attributes_values(cls):
        return list(map(lambda x: x.value, cls))


class UserOnboardingStatusEnum(StrEnum):
    ACTIVATED = "activated"
    DECLINED = "declined"
    DISABLED = "disabled"
    PENDING = "pending"

    @classmethod
    def list_attributes(cls) -> list[dict]:
        return list(map(lambda x: {'name': x.name.replace('_', ' ').title(), 'value': x.value}, cls))

    @classmethod
    def list_attributes_values(cls) -> list[str]:
        return list(map(lambda x: x.value, cls))

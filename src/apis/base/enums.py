from enum import StrEnum


class ModelPrefixEnum(StrEnum):
    AUTHORIZATION_GRANT = 'auth_grant_'
    FILE = 'file_'
    GROUP = 'grp_'
    OTP = 'otp_'
    PASSWORD_RESET_TOKEN = 'pswd_rst_tkn_'
    REFRESH_TOKEN = 'rfsh_tkn_'
    USER = 'user_'
    CHAT = 'chat_'


class QueryParamsEnum(StrEnum):
    A_Z = 'a-z'
    Z_A = 'z-a'
    ASCENDING = 'ascending'
    DESCENDING = 'descending'
    LAST_7_DAYS = '7'
    LAST_15_DAYS = '15'
    LAST_30_DAYS = '30'
    LAST_90_DAYS = '90'
    LAST_12_MONTHS = '12_months'
    ALL_TIME = 'all_time'
    CUSTOM = 'custom'

    @classmethod
    def list_attributes(cls):
        return list(map(lambda x: {'name': x.name.replace('_', ' ').title(), 'value': x.value}, cls))

    @classmethod
    def list_attributes_values(cls):
        return list(map(lambda x: x.value, cls))

from .db_queries import base as authentication_base_db_queries


def delete_used_refresh_tokens_scheduler():
    used_or_expired_refresh_tokens = authentication_base_db_queries.scheduler_get_used_or_expired_refresh_tokens()
    for token in used_or_expired_refresh_tokens:
        token.delete()


def delete_used_password_reset_tokens_scheduler():
    used_or_expired_password_reset_tokens = authentication_base_db_queries.scheduler_get_used_or_expired_password_reset_tokens()
    for token in used_or_expired_password_reset_tokens:
        token.delete()

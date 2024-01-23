from django.contrib.postgres.search import SearchVector, SearchQuery

from ...base import enums as apis_base_repo_enums
from .. import models as user_models


def get_user_by_id(id: str = None):  # noqa
    try:
        return user_models.User.objects.get(id=id)
    except (Exception, user_models.User.DoesNotExist):  # noqa
        return None


def get_all_users(search_query: str = None, order_by: str = None):
    search_vector = SearchVector('first_name', 'last_name', 'middle_name', 'email')
    if search_query:
        query = SearchQuery(search_query)
        ##################################
        # When search_query is specified #
        ##################################
        if order_by == apis_base_repo_enums.QueryParamsEnum.A_Z:
            return user_models.User.objects.annotate(search=search_vector) \
                .filter(search=query).order_by('first_name', 'last_name')
        elif order_by == apis_base_repo_enums.QueryParamsEnum.Z_A:
            return user_models.User.objects.annotate(search=search_vector) \
                .filter(search=query).order_by('-first_name', '-last_name')
        elif order_by == apis_base_repo_enums.QueryParamsEnum.ASCENDING:
            return user_models.User.objects.annotate(search=search_vector) \
                .filter(search=query).order_by('date_created')
        else:
            return user_models.User.objects.annotate(search=search_vector) \
                .filter(search=query).order_by('-date_created')
    else:
        return user_models.User.objects.all()


def get_total_number_of_users() -> int:
    return user_models.User.objects.all().count()


def get_users_by_ids(user_ids: list[str]):
    return user_models.User.objects.filter(id__in=user_ids)


def get_user_by_email(email: str = None):
    try:
        return user_models.User.objects.get(email=email)
    except (Exception, user_models.User.DoesNotExist):  # noqa
        return None


def get_user_by_username(username: str = None):
    try:
        return user_models.User.objects.get(username=username)
    except (Exception, user_models.User.DoesNotExist):  # noqa
        return None


def get_user_by_phone_number(phone_number: str = None):
    try:
        return user_models.User.objects.get(phone_number=phone_number)
    except (Exception, user_models.User.DoesNotExist):  # noqa
        return None


def get_total_number_of_members() -> int:
    return user_models.User.objects.count()

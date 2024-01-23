import logging

from django.core.paginator import Paginator, EmptyPage, InvalidPage
from rest_framework.generics import GenericAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from ..authentication import basic, bearer


log = logging.getLogger(__name__)


class BaseAPIView(GenericAPIView, APIView):
    _log = log
    per_page = 10
    renderer_classes = [JSONRenderer]
    server_error_msg = 'An error occurred!'

    def paginate_response(self, queryset, request, *args, **kwargs) -> dict:  # noqa
        items_per_page = request.query_params.get('items_per_page', self.per_page)

        # check if `items_per_page` is an instance of int, if not an instance of int,
        # then set the `items_per_page` to the default `self.per_page`
        try:
            items_per_page = int(items_per_page)
        except Exception:  # noqa
            items_per_page = self.per_page

        # if itemsPerPage is less than or equal to zero, then set it to `self.per_page` default
        # this is done for validation reason, so users won't provide invalid values
        if items_per_page <= 0:
            items_per_page = self.per_page
        p = Paginator(queryset, items_per_page)
        page_num = request.query_params.get('page', 1)

        try:
            page = p.page(page_num)
        except (EmptyPage, InvalidPage):
            page = p.page(1)
        number_of_pages = p.num_pages

        return {
            'number_of_pages': number_of_pages,
            'number_of_items': len(queryset),
            'results': page.object_list,
            **kwargs
        }

    def paginate_response2(self, queryset, serializer_data, request, *args, **kwargs) -> dict:  # noqa
        items_per_page = request.query_params.get('items_per_page', self.per_page)

        # check if `items_per_page` is an instance of int, if not an instance of int,
        # then set the `items_per_page` to the default `self.per_page`
        try:
            items_per_page = int(items_per_page)
        except Exception:  # noqa
            items_per_page = self.per_page

        # if itemsPerPage is less than or equal to zero, then set it to `self.per_page` default
        # this is done for validation reason, so users won't provide invalid values
        if items_per_page <= 0:
            items_per_page = self.per_page
        p = Paginator(serializer_data, items_per_page)
        page_num = request.query_params.get('page', 1)

        try:
            page = p.page(page_num)
        except (EmptyPage, InvalidPage):
            page = p.page(1)
        number_of_pages = p.num_pages

        return {
            'number_of_pages': number_of_pages,
            'number_of_items': queryset.count(),
            'results': page.object_list,
            **kwargs
        }


class BasicAuthenticationAPIView(BaseAPIView):
    authentication_classes = [basic.BasicAuth]


class TokenAuthenticationAPIView(BaseAPIView):
    authentication_classes = [bearer.TokenAuthentication]


class AdminAuthenticationAPIView(BaseAPIView):
    authentication_classes = [bearer.AdminTokenAuthentication]


class GenericTenantAuthenticationAPIView(BaseAPIView):
    authentication_classes = [bearer.GenericTenantAuthentication]


class UserAuthenticationAPIView(BaseAPIView):
    authentication_classes = [bearer.UserTokenAuthentication]


class NotFoundAPIView(APIView):
    authentication_classes = []
    schema = None

    def get(self, request, *args, **kwargs):  # noqa
        message = f'{request.path} not found'
        return Response(
            data={'message': message}, status=404
        )

    def post(self, request, *args, **kwargs):  # noqa
        message = f'{request.path} not found'
        return Response(
            data={'message': message}, status=404
        )

    def put(self, request, *args, **kwargs):  # noqa
        message = f'{request.path} not found'
        return Response(
            data={'message': message}, status=404
        )

    def patch(self, request, *args, **kwargs):  # noqa
        message = f'{request.path} not found'
        return Response(
            data={'message': message}, status=404
        )

    def delete(self, request, *args, **kwargs):  # noqa
        message = f'{request.path} not found'
        return Response(
            data={'message': message}, status=404
        )

import math
from typing import Any

from django.db.models import QuerySet
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from collections import OrderedDict
from django.core.paginator import Paginator
from django.http.response import JsonResponse
from rest_framework.response import Response


# Custom Pagination for general purposes
class PaginationHandlerMixin(object):
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator

    def paginate_queryset(self, queryset):

        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset,
                self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    last_page_number = 1

    def paginate_queryset(self, queryset, request, view=None):
        self.last_page_number = math.ceil(len(queryset) / self.page_size)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        response = OrderedDict([
            ('count', len(data)),
            #    ('next', self.get_next_link()),
            #    ('previous', self.get_previous_link()),
            ('current_page', self.page.number),
            ('last_page', self.last_page_number),
            ('results', data),
        ])

        return Response(response)


# Pagination for list without serialization
# https://stackoverflow.com/questions/38284440/drf-pagination-without-queryset
class ListPagination:
    def __init__(self, request: Request):
        self._url_scheme = request.scheme
        self._host = request.get_host()
        self._path_info = request.path_info

    def paginate_list(self, data: list, page_size: int, page_number: int) -> JsonResponse:
        paginator = Paginator(data, page_size)
        page = paginator.page(page_number)

        previous_url = None
        next_url = None
        if self._host and self._path_info:
            if page.has_previous():
                previous_url = '{}://{}{}?limit={}&page={}'.format(self._url_scheme, self._host, self._path_info,
                                                                   page_size, page.previous_page_number())
            if page.has_next():
                next_url = '{}://{}{}?limit={}&page={}'.format(self._url_scheme, self._host, self._path_info, page_size,
                                                               page.next_page_number())
        response_dict = OrderedDict([
            ('count', len(data)),
            #   ('next', next_url),
            #   ('previous', previous_url),
            ('current_page', page_number),
            ('last_page', paginator.num_pages),
            ('results', page.object_list),
        ])

        return JsonResponse(response_dict, status=200, safe=False)

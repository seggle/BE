from multiprocessing import context
from pickle import TRUE

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models import Faq
from ..serializers import FaqSerializer
from rest_framework.permissions import AllowAny
from utils.pagination import PaginationHandlerMixin, BasicPagination
# Create your views here.


class FaqView(APIView, PaginationHandlerMixin):
    permission_classes = [AllowAny]
    pagination_class = BasicPagination

    # 02-01 Faq 보기
    def get(self, request: Request) -> Response:
        faq_list = Faq.objects.exclude(visible=False)

        page = self.paginate_queryset(faq_list)
        if page is not None:
            faq_list_serializer = self.get_paginated_response(FaqSerializer(page, many=True).data)
        else:
            faq_list_serializer = FaqSerializer(page, many=True)

        return Response(faq_list_serializer.data, status=status.HTTP_200_OK)

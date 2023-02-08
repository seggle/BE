from multiprocessing import context
from pickle import TRUE
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from utils.get_obj import *
from utils.message import *
from ..models import Faq
from ..serializers import FaqSerializer, FaqAllGetSerializer, FaqPatchSerializer
from utils.pagination import BasicPagination, PaginationHandlerMixin
from rest_framework.request import Request
from utils.permission import IsAdmin
# Create your views here.


class FaqAdminView(APIView, PaginationHandlerMixin):
    permission_classes = [IsAdmin]
    pagination_class = BasicPagination

    # 00-06
    def post(self, request: Request) -> Response:

        data = request.data.copy()
        data["created_user"] = request.user
        serializer = FaqSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 00-03-00, 00-05
    def get(self, request: Request, faq_id: int = None) -> Response:
        if faq_id is None:
            faq_list = Faq.objects.all()

            page = self.paginate_queryset(faq_list)

            if page is not None:
                faq_list_serializer = self.get_paginated_response(FaqAllGetSerializer(page, many=True).data)
            else:
                faq_list_serializer = FaqAllGetSerializer(faq_list, many=True)

            return Response(faq_list_serializer.data, status=status.HTTP_200_OK)
        else:
            faq = get_faq(faq_id)
            serializer = FaqSerializer(faq)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # 00-09
    def patch(self, request: Request, faq_id: int = None) -> Response:
        if faq_id is None:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)
        faq = get_faq(faq_id)
        data = request.data
        obj = {
            "question": data.get("question"),
            "answer": data.get("answer"),
            "visible": data.get("visible", False)
        }
        if faq.created_user == request.user:
            serializer = FaqPatchSerializer(faq, data=obj)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)
        return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)

    # 00-08
    def delete(self, request: Request, faq_id: int = None) -> Response:
        if faq_id is None:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)
        faq = get_faq(faq_id)
        if faq.created_user == request.user:
            faq.delete()
            return Response(msg_success, status=status.HTTP_200_OK)
        return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)


class FaqCheckAdminView(APIView):
    permission_classes = [IsAdmin]

    # 00-10
    def post(self, request: Request) -> Response:
        data = request.data

        faq_id = data['id']
        faq = get_faq(faq_id)

        if faq.created_user == request.user:
            faq.visible = not faq.visible
            faq.save()
            serializer = FaqSerializer(faq)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)

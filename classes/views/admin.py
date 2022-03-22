from django.contrib import auth
from django.db.models import Q
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination #pagination
from utils.pagination import PaginationHandlerMixin #pagination
from ..models import Class, ClassUser
from ..serializers import ClassSerializer
from utils.get_obj import *

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class ClassAdminInfoView(APIView, PaginationHandlerMixin):
    # pagination
    pagination_class = BasicPagination

    def get(self, request):
        uid = request.GET.get('uid', None)
        if uid is None:
            keyword = request.GET.get('keyword', '')
            class_list = Class.objects.all()
            if keyword:
                class_list = class_list.filter(Q(name__icontains=keyword) | Q(created_user__username__icontains=keyword))
            page = self.paginate_queryset(class_list)
            if page is not None:
                serializer = self.get_paginated_response(ClassSerializer(page, many=True).data)
            else:
                serializer = ClassSerializer(class_list)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            class_name_list = []
            class_lists = ClassUser.objects.filter(username=uid)
            for class_list in class_lists:
                class_list_serializer = ClassSerializer(class_list.class_id)
                if class_list_serializer.is_valid():
                    class_add = class_list_serializer.data
                    class_add = {
                        "privilege" : class_list.privilege,
                        "is_show" : class_list.is_show
                    }
                    class_name_list.append(class_add)
            return Response(class_name_list, status=status.HTTP_200_OK)
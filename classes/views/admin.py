from django.db.models import Q
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.pagination import PageNumberPagination #pagination

import seggle.settings
from utils.pagination import PaginationHandlerMixin, BasicPagination, ListPagination  # pagination
from ..models import Class, ClassUser
from ..serializers import ClassSerializer
from utils.get_obj import *
from django.http import Http404, JsonResponse
from utils.permission import IsAdmin


class ClassAdminInfoView(APIView, PaginationHandlerMixin):
    # pagination
    permission_classes = [IsAdmin]
    pagination_class = BasicPagination

    # 00-19
    def get(self, request: Request) -> Response or JsonResponse:
        uid = request.GET.get('uid', None)
        if uid is None:
            keyword = request.GET.get('keyword', '')
            class_list = Class.objects.all().order_by('-id').active()
            if keyword:
                class_list = class_list.filter(Q(name__icontains=keyword) |
                                               Q(created_user__username__icontains=keyword))
                
            page = self.paginate_queryset(class_list)
            if page is not None:
                serializer = self.get_paginated_response(ClassSerializer(page, many=True).data)
            else:
                serializer = ClassSerializer(class_list)

            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            class_result_list = []
            created_user = ClassUser.objects.filter(username=uid).first()
            class_lists = Class.objects.filter(created_user=created_user.username).order_by('-id')

            for class_elem in class_lists:
                cur_class = get_class(id=class_elem.id)

                class_serializer = ClassSerializer(cur_class)

                class_info = class_serializer.data
                class_info['privilege'] = created_user.privilege
                class_info['is_show'] = created_user.is_show
                class_result_list.append(class_info)

            list_paginator = ListPagination(request)

            return list_paginator.paginate_list(class_result_list, seggle.settings.REST_FRAMEWORK
                                                .get('PAGE_SIZE', 15), request.GET.get('page', 1))

from rest_framework.request import Request
from rest_framework.views import APIView
from utils.get_obj import *
from ..models import Problem
from ..serializers import AllProblemSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from utils.pagination import PaginationHandlerMixin, BasicPagination
from django.db.models import Q
from rest_framework import status
from utils.common import IP_ADDR
import os
import shutil
from utils.permission import IsAdmin


class AdminProblemView(APIView, PaginationHandlerMixin):
    permission_classes = [IsAdmin]
    pagination_class = BasicPagination

    # 00-17
    def get(self, request: Request) -> Response:
        problems = Problem.objects.active().order_by('-created_time')

        keyword = request.GET.get('keyword', '')
        if keyword:
            problems = problems.filter(title__icontains=keyword)

        new_problems = []
        for problem in problems:
            # data_url = "http://{0}/api/problems/{1}/download/data".format(IP_ADDR, problem.id)
            # solution_url = "http://{0}/api/problems/{1}/download/solution".format(IP_ADDR, problem.id)

            problem_json = {
                "id": problem.id,
                "title": problem.title,
                "created_time": problem.created_time,
                "created_user": problem.created_user.username,
                # "data" : data_url,
                # "solution" : solution_url,
                "public": problem.public,
            }
            
            new_problems.append(problem_json)

        page = self.paginate_queryset(new_problems)
        if page is not None:
            serializer = self.get_paginated_response(page)
        else:
            serializer = AllProblemSerializer(page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

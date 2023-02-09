import platform

from rest_framework.views import APIView
from ..models import Problem
from ..serializers import ProblemSerializer, AllProblemSerializer, ProblemDetailSerializer, ProblemPutSerializer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from utils.pagination import PaginationHandlerMixin
import utils.download as download
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import status
from utils.get_obj import *
from utils.message import *
from utils.get_error import get_error_msg
from rest_framework.exceptions import ParseError, NotFound
from utils.common import IP_ADDR
import os
import shutil
import uuid
import mimetypes
import urllib
from wsgiref.util import FileWrapper
from utils.permission import *

# permission import
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from utils.permission import IsRightUser, IsProf, IsTA, IsProblemOwnerOrReadOnly, IsAdmin


class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class ProblemView(APIView, PaginationHandlerMixin):
    permission_classes = [(IsAuthenticated & (IsProf | IsTA)) | IsAdmin]
    pagination_class = BasicPagination

    # 03-01 problem 전체 조회
    def get(self, request):
        if request.user.privilege == 0:
            problems = Problem.objects.filter(Q(created_user=request.user)).active()
        else:
            problems = Problem.objects.filter(
                (Q(public=True) | Q(professor=request.user)) & ~Q(class_id=None)).active()
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
                "created_time" : problem.created_time,
                "created_user" : problem.created_user.username,
                # "data" : data_url,
                # "solution" : solution_url,
                "public" : problem.public,
                "class_id" : problem.class_id.id
            }
            new_problems.append(problem_json)

        page = self.paginate_queryset(new_problems)
        if page is not None:
            serializer = self.get_paginated_response(page)
        else:
            serializer = AllProblemSerializer(page, many=True)
        return Response(serializer.data)

    # 03-02 problem 생성
    def post(self, request):
        data = request.data.copy()

        if data['data'] == '':
            return Response(msg_ProblemView_post_e_1, status=status.HTTP_400_BAD_REQUEST)
        if data['solution'] == '':
            return Response(msg_ProblemView_post_e_1, status=status.HTTP_400_BAD_REQUEST)

        data_str = data['data'].name.split('.')[-1]
        solution_str = data['solution'].name.split('.')[-1]
        if data_str != 'zip':
            return Response(msg_ProblemView_post_e_2, status=status.HTTP_400_BAD_REQUEST)
        if solution_str != 'csv':
            return Response(msg_ProblemView_post_e_3, status=status.HTTP_400_BAD_REQUEST)

        data['created_user'] = request.user

        class_ = get_class(data['class_id'])

        data['professor'] = class_.created_user
        problem = ProblemSerializer(data=data)

        if problem.is_valid():
            problem.save()
            return Response(problem.data, status=status.HTTP_200_OK)
        else:
            msg = get_error_msg(problem)
            return Response(data={
                "code": status.HTTP_400_BAD_REQUEST,
                "message": msg
            }, status=status.HTTP_400_BAD_REQUEST)


class ProblemDetailView(APIView):
    permission_classes = [IsProblemOwnerOrReadOnly|IsAdmin]

    # 03-04 problem 세부 조회
    def get(self, request, problem_id):
        problem = get_problem(problem_id)

        if problem is False:
            return Response(msg_ProblemDetailView_delete_e_2, status=status.HTTP_204_NO_CONTENT)

        serializer = ProblemDetailSerializer(problem)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 03-03 problem 수정
    def put(self, request, problem_id):
        problem = get_problem(problem_id)

        if problem is False:
            return Response(msg_ProblemDetailView_delete_e_2, status=status.HTTP_204_NO_CONTENT)

        data = request.data
        obj = {
            "title": data.get("title"),
            "description": data.get("description"),
            "data_description": data.get("data_description"),
            "evaluation": data.get("evaluation"),
            "public": data.get("public")
        }
        if data.get('data', '') != '':
            data_str = data['data'].name.split('.')[-1]
            print(data_str)
            if data_str != 'zip':
                return Response(msg_ProblemView_post_e_2, status=status.HTTP_400_BAD_REQUEST)
            # 폴더 삭제
            if os.path.isfile(problem.data.path):
                path = (problem.data.path).split("uploads/problem/")
                path = path[1].split("/", 1)
                shutil.rmtree('./uploads/problem/' + path[0] + '/')  # 폴더 삭제 명령어 - shutil
                # 윈도우라면 위 코드 대신 다음 코드 실행
                # path = os.path.normpath((problem.data.path).split('problem')[1])
                # path = path.split("\\")[1]
                # shutil.rmtree('./uploads/problem/' + path + '/')  # 폴더 삭제 명령어 - shutil

        if data.get('solution', '') != '':
            solution_str = data['solution'].name.split('.')[-1]
            if solution_str != 'csv':
                return Response(msg_ProblemView_post_e_3, status=status.HTTP_400_BAD_REQUEST)
            if os.path.isfile(problem.solution.path):
                path = (problem.solution.path).split("uploads/solution/")
                path = path[1].split("/", 1)
                shutil.rmtree('./uploads/solution/' + path[0] + '/')
                # 윈도우라면 위 코드 대신 다음 코드 실행
                # path = os.path.normpath((problem.solution.path).split('solution')[1])
                # path = path.split("\\")[1]
                # shutil.rmtree('./uploads/solution/' + path + '/')  # 폴더 삭제 명령어 - shutil

        serializer = ProblemPutSerializer(problem, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data={
            "code": status.HTTP_400_BAD_REQUEST,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    # 03-05 문제 삭제
    def delete(self, request, problem_id):
        problem = get_problem(problem_id)

        if problem is False:
            return Response(msg_ProblemDetailView_delete_e_2, status=status.HTTP_204_NO_CONTENT)

        problem.is_deleted = True
        temp = str(uuid.uuid4()).replace("-", "")
        problem.title = problem.title + ' - ' + temp
        problem.save()
        return Response(msg_ProblemDetailView_delete_e_1, status=status.HTTP_200_OK)


class ProblemVisibilityView(APIView):
    permission_classes = [IsProblemOwnerOrReadOnly]

    # 03-06 problem의 public 수정
    def post(self, request, problem_id):
        problem = get_problem(problem_id)

        if problem is False:
            return Response(msg_ProblemDetailView_delete_e_2, status=status.HTTP_204_NO_CONTENT)

        if problem.public:
            problem.public = False
        else:
            problem.public = True
        problem.save()
        return Response(msg_success, status=status.HTTP_200_OK)

class ProblemDataDownloadView(APIView):
    permission_classes = [IsProblemDownloadableUser | IsAdmin]
    # 03-07 problem의 data 다운로드
    def get(self, request, problem_id):
        problem = get_problem(problem_id)

        if problem is False:
            return Response(msg_ProblemDetailView_delete_e_2, status=status.HTTP_204_NO_CONTENT)

        os_info = platform.system()

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        (filename, filepath) = download.csv_download_windows(problem.data.path, BASE_DIR, "problem") \
            if os_info == 'Windows' else download.csv_download_nix(problem.data.path, BASE_DIR, "problem")

        # Open the file for reading content
        path = open(filepath, 'rb')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % filename

        return response

class ProblemSolutionDownloadView(APIView):
    permission_classes = [IsProblemOwner]
    # 03-08 problem solution 다운로드
    def get(self, request, problem_id):
        problem = get_problem(problem_id)

        if problem is False:
            return Response(msg_ProblemDetailView_delete_e_2, status=status.HTTP_204_NO_CONTENT)

        os_info = platform.system()

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        (filename, filepath) = download.csv_download_windows(problem.solution.path, BASE_DIR, "problem") \
            if os_info == 'Windows' else download.csv_download_nix(problem.solution.path, BASE_DIR, "problem")

        # Open the file for reading content
        path = open(filepath, 'r')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % filename

        return response
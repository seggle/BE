from rest_framework.views import APIView
from ..models import Problem
from ..serializers import ProblemSerializer, AllProblemSerializer, ProblemPutSerializer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from utils.pagination import PaginationHandlerMixin
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import status
from utils.get_obj import *
from utils.message import *
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

    # 03-01
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

    # 03-02
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
            return Response(problem.errors, status=status.HTTP_400_BAD_REQUEST)


class ProblemDetailView(APIView):
    permission_classes = [IsProblemOwnerOrReadOnly|IsAdmin]

    # 03-04
    def get(self, request, problem_id):
        problem = get_problem(problem_id)

        # data_url = "http://{0}/api/problems/{1}/download/data".format(IP_ADDR, problem.id)
        # solution_url = "http://{0}/api/problems/{1}/download/solution".format(IP_ADDR, problem.id)

        cp_json = {
            "id": problem.id,
            "title": problem.title,
            "description": problem.description,
            "created_time": problem.created_time,
            "created_user": problem.created_user.username,
            # "data": data_url,
            "data_description": problem.data_description,
            # "solution": solution_url,
            "evaluation": problem.evaluation,
            "public": problem.public,
            "class_id": problem.class_id.id
        }

        return Response(cp_json, status=status.HTTP_200_OK)

    # 03-03
    def put(self, request, problem_id):
        problem = get_problem(problem_id)
        
        data = request.data
        obj = {
            "title": data["title"],
            "description": data["description"],
            "data_description": data["data_description"],
            "evaluation": data["evaluation"],
            "public": data["public"]
        }

        if data['data']:
            data_str = data['data'].name.split('.')[-1]
            if data_str != 'zip':
                return Response(msg_ProblemView_post_e_2, status=status.HTTP_400_BAD_REQUEST)
            # 폴더 삭제
            if os.path.isfile(problem.data.path):
                path = (problem.data.path).split("uploads/problem/")
                path = path[1].split("/", 1)
                shutil.rmtree('./uploads/problem/' + path[0] + '/')  # 폴더 삭제 명령어 - shutil
            obj['data'] = data['data']
        if data['solution']:
            solution_str = data['solution'].name.split('.')[-1]
            if solution_str != 'csv':
                return Response(msg_ProblemView_post_e_3, status=status.HTTP_400_BAD_REQUEST)
            if os.path.isfile(problem.solution.path):
                path = (problem.solution.path).split("uploads/solution/")
                path = path[1].split("/", 1)
                shutil.rmtree('./uploads/solution/' + path[0] + '/')
            obj['solution'] = data['solution']

        serializer = ProblemPutSerializer(problem, data=obj, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 03-05
    def delete(self, request, problem_id):
        problem = get_problem(problem_id)
        problem.is_deleted = True
        temp = str(uuid.uuid4()).replace("-", "")
        problem.title = problem.title + ' - ' + temp
        problem.save()
        return Response(msg_ProblemDetailView_delete_e_1, status=status.HTTP_200_OK)


class ProblemVisibilityView(APIView):
    permission_classes = [IsProblemOwnerOrReadOnly]

    # 03-06
    def post(self, request, problem_id):
        problem = get_problem(problem_id)
        if problem.public:
            problem.public = False
        else:
            problem.public = True
        problem.save()
        return Response(msg_success, status=status.HTTP_200_OK)

class ProblemDataDownloadView(APIView):
    permission_classes = [IsProblemDownloadableUser | IsAdmin]
    # 0315 정범님 퍼미션 부탁드립니다. ㅎㅎ

    def get(self, request, problem_id):
        problem = get_problem(problem_id)

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # result = /Users/ingyu/Desktop/BE/problem
        BASE_DIR = BASE_DIR.replace("/problem", "")
        
        data_path = str(problem.data.path).split('uploads/', 1)[1]
        filename = data_path.split('/', 2)[2]
        filename = urllib.parse.quote(filename.encode('utf-8'))
        filepath = BASE_DIR + '/uploads/' + data_path
        
        # Open the file for reading content
        path = open(filepath, 'rb')

        response = HttpResponse(FileWrapper(path), content_type='application/zip')
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % filename
        return response

class ProblemSolutionDownloadView(APIView):
    permission_classes = [IsProblemOwner]

    def get(self, request, problem_id):
        problem = get_problem(problem_id)

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # result = /Users/ingyu/Desktop/BE/problem
        BASE_DIR = BASE_DIR.replace("/problem", "")

        solution_path = str(problem.solution.path).split('uploads/', 1)[1]
        filename = solution_path.split('/', 2)[2]
        filename = urllib.parse.quote(filename.encode('utf-8'))
        filepath = BASE_DIR + '/uploads/' + solution_path

        # Open the file for reading content
        path = open(filepath, 'r')

        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(FileWrapper(path), content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % filename
        return response
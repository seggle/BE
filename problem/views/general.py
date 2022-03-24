from rest_framework.views import APIView
from ..models import Problem
from classes.models import Class
from ..serializers import ProblemSerializer, AllProblemSerializer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from utils.pagination import PaginationHandlerMixin
from django.db.models import Q
from django.http import Http404, HttpResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from utils.get_obj import *
from utils.message import *
from utils.common import IP_ADDR
import os
import shutil
import uuid
import mimetypes
from wsgiref.util import FileWrapper

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
            problems = Problem.objects.filter(Q(created_user=request.user) & Q(is_deleted=False))
        else:
            problems = Problem.objects.filter(
                (Q(public=True) | Q(professor=request.user)) & Q(is_deleted=False) & ~Q(class_id=None))
        keyword = request.GET.get('keyword', '')
        if keyword:
            problems = problems.filter(title__icontains=keyword)

        new_problems = []
        for problem in problems:
            # ip_addr = "3.37.186.158:8000"
            data_url = "http://{0}/api/problems/{1}/download/data".format(IP_ADDR, problem.id)
            solution_url = "http://{0}/api/problems/{1}/download/solution".format(IP_ADDR, problem.id)

            problem_json = {
                "id": problem.id,
                "title": problem.title,
                "created_time" : problem.created_time,
                "created_user" : problem.created_user.username,
                "data" : data_url,
                "solution" : solution_url,
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
        # if problem == Http404:
        #     message = {"error": "Problem이 존재하지 않습니다."}
        #     return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

        data_url = "http://{0}/api/problems/{1}/download/data".format(IP_ADDR, problem.id)
        solution_url = "http://{0}/api/problems/{1}/download/solution".format(IP_ADDR, problem.id)

        cp_json = {
            "id": problem.id,
            "title": problem.title,
            "description": problem.description,
            "created_time": problem.created_time,
            "created_user": problem.created_user.username,
            "data": data_url,
            "data_description": problem.data_description,
            "solution": solution_url,
            "evaluation": problem.evaluation,
            "public": problem.public,
            "class_id": problem.class_id.id
        }

        return Response(cp_json, status=status.HTTP_200_OK)

    # 03-03
    def put(self, request, problem_id):
        problem = get_problem(problem_id)
        # if problem == Http404:
        #     message = {"error": "Problem이 존재하지 않습니다."}
        #     return Response(data=message, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        obj = {
            "title": data["title"],
            "description": data["description"],
            "data_description": data["data_description"],
            "evaluation": data["evaluation"],
            "public": data["public"]
        }

        if data['data']:
            # 폴더 삭제
            if os.path.isfile(problem.data.path):
                path = (problem.data.path).split("uploads/problem/")
                path = path[1].split("/", 1)
                shutil.rmtree('./uploads/problem/' + path[0] + '/')  # 폴더 삭제 명령어 - shutil
            obj['data'] = data['data']
        if data['solution']:
            if os.path.isfile(problem.solution.path):
                path = (problem.solution.path).split("uploads/solution/")
                path = path[1].split("/", 1)
                shutil.rmtree('./uploads/solution/' + path[0] + '/')
            obj['solution'] = data['solution']

        serializer = ProblemSerializer(problem, data=obj)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

    # 03-05
    def delete(self, request, problem_id):
        problem = get_problem(problem_id)
        problem.is_deleted = True
        temp = str(uuid.uuid4()).replace("-", "")
        problem.title = problem.title + ' - ' + temp
        problem.save()
        return Response(msg_ProblemDetailView_delete_e_1, status=status.HTTP_200_OK)


class ProblemVisibilityView(APIView):
    # permission_classes = [AllowAny]

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
    # permission_classes = [IsAuthenticated]
    # 0315 정범님 퍼미션 부탁드립니다. ㅎㅎ

    def get(self, request, problem_id):
        problem = get_problem(problem_id)

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # result = /Users/ingyu/Desktop/BE/problem
        BASE_DIR = BASE_DIR.replace("/problem", "")
        
        data_path = str(problem.data.path).split('uploads/', 1)[1]
        filename = data_path.split('/', 2)[2]
        filepath = BASE_DIR + '/uploads/' + data_path
        
        # Open the file for reading content
        path = open(filepath, 'rb')

        response = HttpResponse(FileWrapper(path), content_type='application/zip')
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response

class ProblemSolutionDownloadView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, problem_id):
        problem = get_problem(problem_id)

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # result = /Users/ingyu/Desktop/BE/problem
        BASE_DIR = BASE_DIR.replace("/problem", "")

        data_path = str(problem.solution.path).split('uploads/', 1)[1]
        filename = data_path.split('/', 2)[2]
        filepath = BASE_DIR + '/uploads/' + data_path

        # Open the file for reading content
        path = open(filepath, 'r')

        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(FileWrapper(path), content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
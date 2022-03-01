from utils import permission
from rest_framework.views import APIView
from ..models import Problem
from classes.models import Class
from ..serializers import ProblemSerializer, AllProblemSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from utils.pagination import PaginationHandlerMixin
from django.db.models import Q
from django.http import Http404, HttpResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
import os
import shutil


class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class AdminProblemView(APIView,PaginationHandlerMixin):
    permission_classes = [permission.Is_Admin]
    pagination_class = BasicPagination

    def get(self, request):
        problems = Problem.objects.filter(Q(is_deleted=False))
        if problems.count() != 0:

            keyword = request.GET.get('keyword', '')
            if keyword:
                problems = problems.filter(title__icontains=keyword)

            new_problems = []
            for problem in problems:
                ip_addr = "3.37.186.158"
                try:
                    path = str(problem.data.path).replace("/home/ubuntu/BE/uploads/", "")
                except ValueError:
                    path = ""
                url = "http://{0}/{1}".format(ip_addr, path)
                try:
                    path2 = str(problem.solution.path).replace("/home/ubuntu/BE/uploads/", "")
                except ValueError:
                    path2 = ""
                url2 = "http://{0}/{1}".format(ip_addr, path2)
                problem_json = {}
                problem_json['id'] = problem.id
                problem_json['title'] = problem.title
                problem_json['created_time'] = problem.created_time
                problem_json['created_user'] = problem.created_user.username
                problem_json['data'] = url
                problem_json['solution'] = url2
                problem_json['public'] = problem.public
                problem_json['class_id'] = problem.class_id.id
                new_problems.append(problem_json)

            # page = self.paginate_queryset(problems)
            page = self.paginate_queryset(new_problems)
            if page is not None:
                # serializer = self.get_paginated_response(AllProblemSerializer(page, many=True).data)
                serializer = self.get_paginated_response(page)
            else:
                serializer = AllProblemSerializer(page, many=True)
            return Response(serializer.data)
        else:
            return Response([], status=status.HTTP_200_OK)


class AdminProblemDetailView(APIView):
    permission_classes = [permission.Is_Admin]

    # parser_classes = [MultiPartParser, JSONParser]

    def get_object(self, problem_id):
        problem = get_object_or_404(Problem, id=problem_id)
        if problem.is_deleted:
            return Http404
        return problem

    def get(self, request, problem_id):
        problem = self.get_object(problem_id)
        if problem == Http404:
            message = {"error": "Problem이 존재하지 않습니다."}
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

        ip_addr = "3.37.186.158"
        try:
            data_path = str(problem.data.path).replace("/home/ubuntu/BE/uploads/", "")
            data_url = "http://{0}/{1}".format(ip_addr, data_path)
        except ValueError:
            data_url = ""
        try:
            solution_path = str(problem.solution.path).replace("/home/ubuntu/BE/uploads/", "")
            solution_url = "http://{0}/{1}".format(ip_addr, solution_path)
        except ValueError:
            data_url = ""

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
        print("problem.class_id", problem.class_id)

        return Response(cp_json, status=status.HTTP_200_OK)

    def put(self, request, problem_id):
        problem = self.get_object(problem_id)
        if problem == Http404:
            message = {"error": "Problem이 존재하지 않습니다."}
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        obj = {"title": data["title"],
               "description": data["description"],
               "data_description": data["data_description"],
               "evaluation": data["evaluation"],
               "public": data["public"]}

        if data['data']:
            # 폴더 삭제
            if os.path.isfile(problem.data.path):
                path = (problem.data.path).split("uploads/problem/")
                path = path[1].split("/")
                shutil.rmtree('./uploads/problem/' + path[0] + '/')  # 폴더 삭제 명령어 - shutil
            obj['data'] = data['data']
        if data['solution']:
            if os.path.isfile(problem.solution.path):
                path = (problem.solution.path).split("uploads/solution/")
                path = path[1].split("/")
                shutil.rmtree('./uploads/solution/' + path[0] + '/')
            obj['solution'] = data['solution']

        serializer = ProblemSerializer(problem, data=obj)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            data = serializer.errors
            return Response(data)

    def delete(self, request, problem_id):
        problem = self.get_object(problem_id)
        if problem == Http404:
            message = {"error": "Problem이 존재하지 않습니다."}
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)
        else:
            problem.is_deleted = True
            problem.save()
            message = {"success": "문제가 제거되었습니다."}
        return Response(data=message, status=status.HTTP_200_OK)

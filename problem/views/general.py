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


class ProblemView(APIView, PaginationHandlerMixin):
    # permission_classes = [AllowAny]
    pagination_class = BasicPagination
    # parser_classes = [MultiPartParser, JSONParser]

    def get(self, request):
        problems = Problem.objects.filter((Q(public=True) | Q(created_user=request.user)) & Q(is_deleted=False))
        if problems.count() != 0:

            keyword = request.GET.get('keyword', '')
            if keyword:
                problems = problems.filter(title__icontains=keyword)
            page = self.paginate_queryset(problems)
            if page is not None:
                serializer = self.get_paginated_response(AllProblemSerializer(page, many=True).data)
            else:
                serializer = AllProblemSerializer(page, many=True)
            return Response(serializer.data)
        else:
            return Response([], status=status.HTTP_200_OK)

    """def modify_input_for_multiple_files(self, title, description, data,
                                        data_description, public, c_u):
        dict = {}
        dict['title'] = title
        dict['description'] = description
        dict['data_description'] = data_description
        dict['public'] = public
        dict['created_user'] = c_u
        dict['data'] = data
        return dict"""

    def post(self, request):
        """title = request.data['title']
        description = request.data['description']
        data_description = request.data['data_description']
        public = request.data['public']
        data = request.data['data']
        c_u = request.user
        modified_data = self.modify_input_for_multiple_files(title, description, data, data_description, public, c_u)
        """
        data = request.data.copy()
        data['created_user'] = request.user
        print('Class.objects.filter(id = data["class_id"])', Class.objects.filter(id = data["class_id"]))
        print('Class.objects.filter(id = data["class_id"]).count()', Class.objects.filter(id = data["class_id"]).count())
        # 존재하는 class_id인지 확인
        if (Class.objects.filter(id = data["class_id"]).count()) == 0:
            return Response({"error": "존재하지 않는 class 입니다."}, status=status.HTTP_400_BAD_REQUEST)
        # problem = ProblemGenerateSerializer(data=data)
        problem = ProblemSerializer(data=data)

        if problem.is_valid():
            problem.save()
            return Response(problem.data)
        else:
            return Response(problem.errors, status=status.HTTP_400_BAD_REQUEST)


class ProblemDetailView(APIView):

    # permission_classes = [AllowAny]
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
        path = str(problem.data.path).replace("/home/ubuntu/BE/uploads/", "")
        url = "http://{0}/{1}" . format (ip_addr, path)

        cp_json = {
            "id": problem.id,
            "title": problem.title,
            "description": problem.description,
            "created_time": problem.created_time,
            "created_user": problem.created_user.username,
            "data": url,
            "data_description": problem.data_description,
            "evaluation": problem.evaluation,
            "public": problem.public,
        }

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
                shutil.rmtree('./uploads/problem/' + path[0] + '/') # 폴더 삭제 명령어 - shutil
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


class ProblemVisibilityView(APIView):
    # permission_classes = [AllowAny]

    def get_object(self, problem_id):
        problem = get_object_or_404(Problem, id=problem_id)
        if problem.is_deleted:
            return Http404
        return problem

    def post(self, request, problem_id):
        problem = self.get_object(problem_id)
        if problem == Http404:
            message = {"error": "Problm이 존재하지 않습니다."}
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)
        if problem.public:
            problem.public = False
        else:
            problem.public = True
        problem.save()
        return Response(data=ProblemSerializer(problem).data)

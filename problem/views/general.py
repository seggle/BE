from rest_framework.views import APIView
from ..models import Problem
from ..serializers import ProblemGenerateSerializer, ProblemSerializer, AllProblemSerializer, ProblemPatchSerializer
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


class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class ProblemView(APIView, PaginationHandlerMixin):
    serializer_class = ProblemGenerateSerializer
    permission_classes = [AllowAny]
    pagination_class = BasicPagination
    parser_classes = [MultiPartParser, JSONParser]

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
            return Response(status=status.HTTP_400_BAD_REQUEST)

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
        data = request.data
        data['created_user'] = request.user
        # problem = ProblemGenerateSerializer(data=data)
        problem = ProblemSerializer(data=data)
        
        if problem.is_valid():
            problem.save()
            return Response(problem.data)
        else:
            return Response(problem.errors, status=400)


class ProblemDetailView(APIView):

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, JSONParser]

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
        serializer = ProblemSerializer(problem)
        return Response(serializer.data)

    def put(self, request, problem_id):
        problem = self.get_object(problem_id)
        if problem == Http404:
            message = {"error": "Problem이 존재하지 않습니다."}
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        obj = {"title": data["title"],
               "description": data["description"],
               "data_description": data["data_description"],
               "public": data["public"]}

        if data['data']:
            obj['data'] = data['data']
        if data['solution']:
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
    permission_classes = [AllowAny]

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

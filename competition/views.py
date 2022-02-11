from competition.serializers import (
    CompetitionDetailSerializer, CompetitionGenerateSerializer,
    CompetitionProblemCheckSerializer, CompetitionPutSerializer,
    CompetitionListSerializer,
)
from problem.serializers import ProblemSerializer, ProblemGenerateSerializer
from competition.models import Competition
from problem.models import Problem
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from utils.pagination import PaginationHandlerMixin
from django.db.models import Q
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from utils.permission import CustomPermissionMixin

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class CompetitionView(APIView, PaginationHandlerMixin, CustomPermissionMixin):
    parser_classes = [MultiPartParser, JSONParser]

    # pagination
    pagination_class = BasicPagination
    serializer_class = CompetitionListSerializer

    # 06-00 대회 리스트 조회
    def get(self, request):
        competitions = Competition.objects.filter(problem_id__is_deleted=False)
        keyword = request.GET.get('keyword', '')
        if keyword:
            competitions = competitions.filter(problem_id__title__icontains=keyword) # 제목에 keyword가 포함되어 있는 레코드만 필터링
        obj_list = []
        for competition in competitions:
            obj = {}
            obj["problem"] = Problem.objects.get(id=competition.problem_id.id)
            obj["id"] = competition.id
            obj["start_time"] = competition.start_time
            obj["end_time"] = competition.end_time
            obj_list.append(obj)
        page = self.paginate_queryset(obj_list)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(competitions, many=True, problem=competitions.problem_id)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 06-01 대회 생성
    def post(self, request):
        # permission check
        if self.check_student(request.user.privilege):
            return Response({'error':'Competition 생성 권한 없음'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data['created_user'] = request.user
        check = CompetitionProblemCheckSerializer(data=data)
        if check.is_valid():
            problem = ProblemGenerateSerializer(data=data)
            if problem.is_valid():
                problem_obj = problem.save() # save() calls create() of the Serializer which returns an object instance
            else:
                return Response(problem.errors, status=status.HTTP_400_BAD_REQUEST)
            data["problem_id"] = problem_obj.id
            competition = CompetitionGenerateSerializer(data=data)
            if competition.is_valid():
                competition_obj = competition.save()
                obj = {}
                obj["problem"] = problem_obj
                obj["id"] = competition_obj.id
                obj["start_time"] = competition_obj.start_time
                obj["end_time"] = competition_obj.end_time
                serializer = CompetitionDetailSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(competition.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(check.errors, status=status.HTTP_400_BAD_REQUEST)

class CompetitionDetailView(APIView, CustomPermissionMixin):
    parser_classes = [MultiPartParser, JSONParser]

    def get_object(self, competition_id):
        competition = get_object_or_404(Competition, id=competition_id)
        problem = get_object_or_404(Problem, id=competition.problem_id.id) # competition.problem_id -> Problem object (1)
        if problem.is_deleted: # 삭제된 problem일 경우 불러올 수 없음.
            return Response({'error':"Problem이 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        return competition

    # 06-02 대회 개별 조회
    def get(self, request, competition_id):
        obj = {}
        competition = self.get_object(competition_id=competition_id)
        obj["problem"] = get_object_or_404(Problem, id=competition.problem_id.id)
        obj["id"] = competition.id
        obj["start_time"] = competition.start_time
        obj["end_time"] = competition.end_time
        serializer = CompetitionDetailSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 06-03-01 대회 개별 수정
    def put(self, request, competition_id):
        # permission check
        if self.check_student(request.user.privilege):
            return Response({'error':'Competition 수정 권한 없음'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        competition = self.get_object(competition_id=competition_id)
        problem = get_object_or_404(Problem, id=competition.problem_id.id)
        # problem 수정
        obj = {"title": data["title"],
            "description": data["description"],
            "data_description": data["data_description"],
            "public": data["public"]}
        if data['data']:
            obj['data'] = data['data']
        if data['solution']:
            obj['solution'] = data['solution']
        problem_serializer = ProblemSerializer(problem, data=obj)
        if problem_serializer.is_valid():
            problem_obj = problem_serializer.save()
        else:
            return Response(problem_serializer.error, status=status.HTTP_400_BAD_REQUEST)
        # competition 수정
        competition_serializer = CompetitionPutSerializer(competition, data=data)
        if competition_serializer.is_valid():
            competition_obj = competition_serializer.save()
        else:
            return Response(competition_serializer.error, status=status.HTTP_400_BAD_REQUEST)
        obj2 = {"problem":problem_obj,
                "id":competition_obj.id,
                "start_time":competition_obj.start_time,
                "end_time":competition_obj.end_time}
        serializer = CompetitionDetailSerializer(obj2)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 06-03-02 대회 삭제
    def delete(self, request, competition_id):
        # permission check
        if self.check_student(request.user.privilege):
            return Response({'error':'Competition 삭제 권한 없음'}, status=status.HTTP_400_BAD_REQUEST)
        competition = self.get_object(competition_id=competition_id)
        problem = get_object_or_404(Problem, id=competition.problem_id.id)
        problem.is_deleted = True
        problem.save()
        return Response({"success": "competition 삭제 완료"}, status=status.HTTP_200_OK)

class CompetitionUserView(APIView, CustomPermissionMixin):
    pass
from competition.serializers import CompetitionDetailSerializer, CompetitionGenerateSerializer, CompetitionProblemCheckSerializer
from competition.models import Competition
# problem의 view 내용
from rest_framework.views import APIView
from problem.models import Problem
from problem.serializers import ProblemGenerateSerializer, ProblemSerializer, AllProblemSerializer, ProblemPatchSerializer
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
    serializer_class = CompetitionGenerateSerializer
    pagination_class = BasicPagination
    parser_classes = [MultiPartParser, JSONParser]

    def get(self, request):
        problems = Problem.objects.filter((Q(public=True) | Q(created_user=request.user))&Q(is_deleted=False))
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

    # 06-01 대회 생성
    def post(self, request):
        data = request.data
        # permission check
        if self.check_student(request.user.privilege):
            return Response({'error':'Competition 생성 권한 없음'}, status=status.HTTP_400_BAD_REQUEST)
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

class CompetitionDetailView(APIView):

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

    # 06-03 대회 개별 수정
    def put(self, request, competition_id):
        competition = self.get_object(competition_id=competition_id)

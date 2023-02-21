from rest_framework.views import APIView
from submission.models import SubmissionClass, SubmissionCompetition
from utils.get_obj import get_competition, get_contest_problem, get_competition_problem
from .serializers import LeaderboardClassSerializer, LeaderboardCompetitionSerializer
from rest_framework.response import Response
from rest_framework import status
from utils.common import IP_ADDR
from utils.permission import *
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination  # pagination
from utils.pagination import PaginationHandlerMixin, BasicPagination  # pagination
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from utils.message import *

class LeaderboardClassView(APIView, PaginationHandlerMixin):
    permission_classes = [IsCPUser]
    pagination_class = BasicPagination

    # 09-01 수업에 속한 문제 리더보드 조회
    def get(self, request, cp_id=None):
        contest_problem = get_contest_problem(cp_id)
        class_id = contest_problem.contest_id.class_id.id
        submission_class_list = SubmissionClass.objects.filter(c_p_id=cp_id)

        # 정렬
        if contest_problem.problem_id.evaluation in ["CategorizationAccuracy", "F1-score", "mAP"]: # 내림차순
            submission_class_list = submission_class_list.order_by('-score', 'created_time')
        else:
            submission_class_list = submission_class_list.order_by('score', 'created_time')

        obj_list = []
        count = 1
        for submission in submission_class_list:
            if not submission.on_leaderboard:
                continue

            obj = {
                "id": count,
                "submission_id": submission.id,
                "username": submission.username,
                "name": submission.username.name,
                "score": submission.score,
                "created_time": submission.created_time,
            }
            if ClassUser.objects.filter(username=submission.username, privilege=1, class_id=class_id).exists() or ClassUser.objects.filter(username=submission.username, privilege=2, class_id=class_id).exists():
                obj["id"] = 0
                count = count -1
            obj_list.append(obj)
            count = count + 1

        page = self.paginate_queryset(obj_list)

        if page is not None:
            serializer = self.get_paginated_response(LeaderboardClassSerializer(page, many=True).data)
        else:
            serializer = LeaderboardClassSerializer(obj_list, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class LeaderboardCompetitionView(APIView, PaginationHandlerMixin):
    permission_classes = [AllowAny]
    pagination_class = BasicPagination

    # 09-00 대회 문제 리더보드 조회
    def get(self, request: Request, comp_p_id: int) -> Response:

        problem = get_competition_problem(comp_p_id)
        submission_competition_list = SubmissionCompetition\
            .objects.filter(comp_p_id=comp_p_id)

        # 정렬
        if problem.problem_id.evaluation in ["CategorizationAccuracy", "F1-score", "mAP"]: # 내림차순
            submission_competition_list = submission_competition_list.order_by('-score', 'created_time')
        else:
            submission_competition_list = submission_competition_list.order_by('score', 'created_time')

        obj_list = []
        count = 1
        for submission in submission_competition_list:
            if submission.on_leaderboard == False:
                continue
            obj = {
                "id": count,
                "submission_id": submission.id,
                "username": submission.username,
                "name": submission.username.name,
                "score": submission.score,
                "created_time": submission.created_time,
            }
            competition_id = submission.competition_id
            if CompetitionUser.objects.filter(username=submission.username, privilege=1, competition_id=competition_id).exists() or CompetitionUser.objects.filter(username=submission.username, privilege=2, competition_id=competition_id).exists():
                obj["id"] = 0
                count = count -1
            obj_list.append(obj)
            count = count + 1
        if not obj_list:
            return Response(msg_error_no_on_leaderboard_submission, status=HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(obj_list)
        if page is not None:
            serializer = self.get_paginated_response(LeaderboardCompetitionSerializer(page, many=True).data)
        else:
            serializer = LeaderboardCompetitionSerializer(obj_list, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

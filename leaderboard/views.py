from rest_framework.views import APIView
from submission.models import SubmissionClass, SubmissionCompetition
from utils.get_obj import get_competition, get_contest_problem
from .serializers import LeaderboardClassSerializer, LeaderboardCompetitionSerializer
from rest_framework.response import Response
from rest_framework import status
from utils.common import IP_ADDR
from utils.permission import *
from rest_framework.permissions import AllowAny

def order(evaluation, obj_list):
    if evaluation in ["F1-score", "Accuracy"]:
        # 내림차순 (User.object.order_by('-name'))
        pass
    else:
        # 올림차순
        pass
    return obj_list


class LeaderboardClassView(APIView):
    permission_classes = [IsCPUser]

    def get(self, request, cp_id=None):
        contest_problem = get_contest_problem(cp_id)
        submission_class_list = SubmissionClass.objects.filter(c_p_id=cp_id)

        # 정렬
        if contest_problem.problem_id.evaluation in ["F1-score", "Accuracy"]:  # 내림차순
            submission_class_list = submission_class_list.order_by('-score')
        else:
            submission_class_list = submission_class_list.order_by('score')

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
            obj_list.append(obj)
            count = count + 1

        serializer = LeaderboardClassSerializer(obj_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LeaderboardCompetitionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, competition_id):
        competition = get_competition(competition_id)
        submission_competition_list = SubmissionCompetition.objects.filter(competition_id=competition_id)

        # 정렬
        if competition.problem_id.evaluation in ["F1-score", "Accuracy"]:  # 내림차순
            submission_competition_list = submission_competition_list.order_by('-score')
        else:
            submission_competition_list = submission_competition_list.order_by('score')

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

            obj_list.append(obj)
            count = count + 1

        serializer = LeaderboardCompetitionSerializer(obj_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from contest.models import Contest, Contest_problem
from submission.models import SubmissionClass, SubmissionCompetition, Path
from competition.models import Competition, Competition_user
from .serializers import LeaderboardClassSerializer, LeaderboardCompetitionSerializer
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status

class LeaderboardClassView(APIView):
    def get_object_contest_problem(self, cp_id):
        cpid = get_object_or_404(Contest_problem, id = cp_id)
        return cpid

    def get(self, request, **kwargs):
        # competition_id = kwargs.get('competition_id')
        if kwargs.get('cp_id') is None:
            return Response({"error": "cp_id"}, status=status.HTTP_400_BAD_REQUEST)
        cp_id = kwargs.get('cp_id')
        cpid = self.get_object_contest_problem(cp_id)

        # user check
        # if User.objects.filter(username = username).count() == 0:
        #     return Response({"error":"존재 하지 않는 유저 입니다. "}, status=status.HTTP_400_BAD_REQUEST)
        submission_class_list = SubmissionClass.objects.filter(c_p_id=cp_id)

        # if username:
        #     submission_class_list = submission_class_list.filter(username=username)
        # if cpid:
        #     submission_class_list = submission_class_list.filter(c_p_id=cpid)

        obj_list = []
        ip_addr = "3.37.186.158"
        count = 1
        for submission in submission_class_list:
            if submission.path.on_leaderboard == False:
                continue
            path = Path.objects.get(id=submission.path.id)
            csv_path = str(submission.csv.path).replace("/home/ubuntu/BE/uploads/", "")
            csv_url = "http://{0}/{1}" . format (ip_addr, csv_path)
            ipynb_path = str(submission.ipynb.path).replace("/home/ubuntu/BE/uploads/", "")
            ipynb_url = "http://{0}/{1}" . format (ip_addr, ipynb_path)
            obj = {
                "id": count,
                "username": submission.username,
                "name": submission.username.name,
                "score": path.score,
                "created_time": path.created_time,
                "csv": csv_url,
                "ipynb": ipynb_url,
            }
            obj_list.append(obj)
            count = count + 1
        serializer = LeaderboardClassSerializer(obj_list, many=True)

        # page = self.paginate_queryset(obj_list)
        # if page is not None:
        #     serializer = self.get_paginated_response(SumissionClassListSerializer(page, many=True).data)
        # else:
        #     serializer = SumissionClassListSerializer(obj_list, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LeaderboardCompetitionView(APIView):

    def get_object(self, competition_id):
        competition = get_object_or_404(Competition, id=competition_id)
        # problem = get_object_or_404(Problem, id=competition.problem_id.id) # competition.problem_id -> Problem object (1)
        # if problem.is_deleted: # 삭제된 problem일 경우 불러올 수 없음.
        #     return False
        # else:
        #     return competition
        return competition

    def get(self, request, competition_id):
        competition = self.get_object(competition_id)
        # problem 삭제 확인 -> leaderboard 보여줄 경우, problem 삭제 여부 확인 안함. (삭제 상관 없이 단순히 기록을 보는 것이라 생각되기 때문)
        # if competition is False:
        #     return Response({'error':"Problem이 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        submission_competition_list = SubmissionCompetition.objects.filter(competition_id=competition.id)

        obj_list = []
        ip_addr = "3.37.186.158"
        count = 1
        for submission in submission_competition_list:
            if submission.path.on_leaderboard == False:
                continue
            path = Path.objects.get(id=submission.path.id)
            csv_path = str(submission.csv.path).replace("/home/ubuntu/BE/uploads/", "")
            csv_url = "http://{0}/{1}" . format (ip_addr, csv_path)
            ipynb_path = str(submission.ipynb.path).replace("/home/ubuntu/BE/uploads/", "")
            ipynb_url = "http://{0}/{1}" . format (ip_addr, ipynb_path)
            obj = {
                "id": count,
                "username": submission.username,
                "name": submission.username.name,
                "score": path.score,
                "created_time": path.created_time,
                "csv": csv_url,
                "ipynb": ipynb_url,
            }
            obj_list.append(obj)
            count = count + 1
        serializer = LeaderboardCompetitionSerializer(obj_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
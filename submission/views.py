from rest_framework.views import APIView
from classes.models import Class
from contest.models import Contest, Contest_problem
from .serializers import SubmissionClassSerializer, PathSerializer, SubmissionCompetition
from competition.models import Competition, Competition_user
from problem.models import Problem
from account.models import User
from utils.evaluation import EvaluationMixin
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status
import uuid


class SubmissionClassView(APIView):
    def get_object_class(self, class_id):
        classid = get_object_or_404(Class, id = class_id)
        return classid

    def get_object_contest(self, contest_id):
        contestid = get_object_or_404(Contest, id = contest_id)
        return contestid

    def get_object_contest_problem(self, cp_id):
        cpid = get_object_or_404(Contest_problem, id = cp_id)
        return cpid

    # 05-16
    def post(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response({"error": "class_id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object_class(class_id)

            if kwargs.get('contest_id') is None:
                return Response({"error": "contest_id"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                contest_id = kwargs.get('contest_id')
                contestid = self.get_object_contest(contest_id)

                if kwargs.get('cp_id') is None:
                    return Response({"error": "cp_id"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    cp_id = kwargs.get('cp_id')
                    cpid = self.get_object_contest_problem(cp_id)

                    username = kwargs.get('username')

                    if username != request.user.username:
                        return Response({"error": "username"}, status=status.HTTP_400_BAD_REQUEST)

                    contest_problem_id = Contest_problem.objects.get(id=cp_id)

                    if (contest_problem_id.contest_id.id != contest_id) or (contest_problem_id.contest_id.class_id.id != class_id):
                        return Response({"error": "id"}, status=status.HTTP_400_BAD_REQUEST)

                    #
                    # csv, ipynb file check
                    #

                    data = request.data.copy()

                    path_json = {}
                    temp = str(uuid.uuid4()).replace("-","")
                    path_json['username'] = request.user
                    path_json['path'] = temp
                    path_json['problem_id'] = contest_problem_id.id
                    path_json['score'] = None
                    path_json['ip_address'] = data['ip_address']
                    # path_json['on_leaderboard'] = request.user
                    # path_json['status'] = 0

                    submission_json = {}
                    submission_json['username'] = request.user
                    submission_json['class_id'] = contest_problem_id.contest_id.class_id.id
                    submission_json['contest_id'] = contest_problem_id.contest_id.id
                    submission_json['c_p_id'] = contest_problem_id.id
                    submission_json['csv'] = data['csv']
                    submission_json['ipynb'] = data['ipynb']


                    path_serializer = PathSerializer(data=path_json)
                    if path_serializer.is_valid():
                        path = path_serializer.save()
                        submission_json['path'] = path.id
                        submission_serializer = SubmissionClassSerializer(data=submission_json)

                        if submission_serializer.is_valid():
                            submission_serializer.save()
                            return Response(submission_serializer.data, status=status.HTTP_200_OK)
                        else:
                            return Response(submission_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubmissionCompetitionView(APIView, EvaluationMixin):

    def get_competition(self, competition_id):
        competition = get_object_or_404(Competition, id=competition_id)
        problem = get_object_or_404(Problem, id=competition.problem_id.id)
        if problem.is_deleted: # 삭제된 문제인 경우 False 반환
            return False
        else:
            return competition

    def get_user(self, username):
        user = get_object_or_404(User, username=username)
        return user

    def check_participation(self, **kwargs):
        competition_id = kwargs.get('competition_id')
        username = kwargs.get('username')

        user = self.get_user(username)
        if Competition_user.objects.filter(username = username).filter(competition_id = competition_id).count() == 0:
            return False
        return user

    # 06-04 대회 유저 파일 제출
    def post(self, request, **kwargs):
        competition_id = kwargs.get('competition_id')
        username = kwargs.get('username')

        # username check
        if username != request.user.username:
            return Response({"error": "username"}, status=status.HTTP_400_BAD_REQUEST)
        # problem check
        competition = self.get_competition(competition_id=competition_id)
        if competition is False:
            return Response({'error':"Problem이 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        # permission check - 대회에 참가한 학생만 제출 가능
        user = self.check_participation(username=username, competition_id=competition_id)
        if user is False:
            return Response({'error':"대회에 참가하지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        temp = str(uuid.uuid4()).replace("-","")

        path_json = {
            "username":request.user,
            "path":temp,
            "problem_id":competition.problem_id.id,
            "score":None,
            "ip_address":data["ip_address"]
        }
        submission_json = {
            "username": request.user,
            "competition_id":competition.id,
            "csv":data["csv"],
            "ipynb":data["ipynb"]
        }

        path_serializer = PathSerializer(data=path_json)
        if path_serializer.is_valid():
            path = path_serializer.save()
            submission_json["pass"] = path.id
            submission_serializer = SubmissionClassSerializer(data=submission_json)
            if submission_serializer.is_valid():
                submission = submission_serializer.save()
                # return Response(submission_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(submission_serializer.error, status=status.HTTP_400_BAD_REQUEST)

        # evaluation
        problem = get_object_or_404(Problem, id=competition.problem_id.id)
        print("evaluate 전")
        self.evaluate(path, problem.solution, submission.csv, problem.evaluation)
        print("evaluate 후")
        print("path.score", path.score)
        print("path.status", path.status)

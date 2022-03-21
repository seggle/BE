from rest_framework.views import APIView
from contest.models import Contest, Contest_problem
from submission.models import SubmissionClass, SubmissionCompetition, Path
from competition.models import Competition, Competition_user
from .serializers import LeaderboardClassSerializer, LeaderboardCompetitionSerializer
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status

def order(evaluation, obj_list):
    if evaluation in ["F1-score", "Accuracy"]:
        # 내림차순 (User.object.order_by('-name'))
        pass
    else:
        # 올림차순
        pass
    return obj_list

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
        submission_class_list = SubmissionClass.objects.filter(c_p_id=cp_id)

        # 정렬
        if cpid.problem_id.evaluation in ["F1-score", "Accuracy"]: # 내림차순
            submission_class_list = submission_class_list.order_by('path__score')
        else:
            submission_class_list = submission_class_list.order_by('-path__score')

        obj_list = []
        ip_addr = "3.37.186.158:8000"
        count = 1
        for submission in submission_class_list:
            if submission.path.on_leaderboard == False:
                continue
            path = Path.objects.get(id=submission.path.id)
            # csv_path = str(submission.csv.path).replace("/home/ubuntu/BE/uploads/", "")
            # csv_url = "http://{0}/{1}" . format (ip_addr, csv_path)
            # ipynb_path = str(submission.ipynb.path).replace("/home/ubuntu/BE/uploads/", "")
            # ipynb_url = "http://{0}/{1}" . format (ip_addr, ipynb_path)
            csv_url = "http://{0}/api/submissions/class/{1}/download/csv".format(ip_addr, submission.id)
            ipynb_url = "http://{0}/api/submissions/class/{1}/download/ipynb".format(ip_addr, submission.id)

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

        return Response(serializer.data, status=status.HTTP_200_OK)

class LeaderboardCompetitionView(APIView):

    def get_object(self, competition_id):
        competition = get_object_or_404(Competition, id=competition_id)
        return competition

    def get(self, request, competition_id):
        competition = self.get_object(competition_id)
        submission_competition_list = SubmissionCompetition.objects.filter(competition_id=competition.id)

        # 정렬
        if competition.problem_id.evaluation in ["F1-score", "Accuracy"]: # 내림차순
            submission_competition_list = submission_competition_list.order_by('-path__score')
        else:
            submission_competition_list = submission_competition_list.order_by('path__score')


        obj_list = []
        ip_addr = "3.37.186.158:8000"
        count = 1
        for submission in submission_competition_list:
            if submission.path.on_leaderboard == False:
                continue
            path = Path.objects.get(id=submission.path.id)
            # csv_path = str(submission.csv.path).replace("/home/ubuntu/BE/uploads/", "")
            # csv_url = "http://{0}/{1}" . format (ip_addr, csv_path)
            # ipynb_path = str(submission.ipynb.path).replace("/home/ubuntu/BE/uploads/", "")
            # ipynb_url = "http://{0}/{1}" . format (ip_addr, ipynb_path)
            csv_url = "http://{0}/api/submissions/competition/{1}/download/csv".format(ip_addr, submission.id)
            ipynb_url = "http://{0}/api/submissions/competition/{1}/download/ipynb".format(ip_addr, submission.id)

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
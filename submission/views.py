from rest_framework.views import APIView
from classes.models import Class
from contest.models import Contest, Contest_problem
from submission.models import SubmissionClass, SubmissionCompetition, Path
from .serializers import PathSerializer, SubmissionClassSerializer, SumissionClassListSerializer, SubmissionCompetitionSerializer, SumissionCompetitionListSerializer
from competition.models import Competition, Competition_user
from problem.models import Problem
from account.models import User
from rest_framework.pagination import PageNumberPagination #pagination
from utils.pagination import PaginationHandlerMixin #pagination
from utils.evaluation import EvaluationMixin
from utils.get_ip import GetIpAddr
from utils.common import IP_ADDR
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status
import uuid
from django.http import Http404, HttpResponse
import mimetypes
import os

# submission-class 관련
class SubmissionClassView(APIView, EvaluationMixin):
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
        if kwargs.get('contest_id') is None:
            return Response({"error": "contest_id"}, status=status.HTTP_400_BAD_REQUEST)
        if kwargs.get('cp_id') is None:
            return Response({"error": "cp_id"}, status=status.HTTP_400_BAD_REQUEST)
        class_id = kwargs.get('class_id')
        classid = self.get_object_class(class_id)
        contest_id = kwargs.get('contest_id')
        contestid = self.get_object_contest(contest_id)
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
        path_json['problem_id'] = contest_problem_id.problem_id.id
        path_json['score'] = None
        # path_json['ip_address'] = data['ip_address']
        path_json['ip_address'] = GetIpAddr(request)
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
            path_obj = path_serializer.save()
            submission_json['path'] = path_obj.id
            submission_serializer = SubmissionClassSerializer(data=submission_json)

            if submission_serializer.is_valid():
                submission = submission_serializer.save()
                # evaluation
                problem = get_object_or_404(Problem, id=contest_problem_id.problem_id.id)
                self.evaluate(path=path_obj, solution_csv=problem.solution, submission_csv=submission.csv, evaluation=problem.evaluation)

                return Response(submission_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(submission_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(path_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class SubmissionClassListView(APIView, PaginationHandlerMixin):
    # pagination
    pagination_class = BasicPagination

    # 07-00 유저 submission 내역 조회
    def get(self, request, **kwargs):
        # competition_id = kwargs.get('competition_id')
        username = request.GET.get('username', '')
        cpid = request.GET.get('cpid', '')

        # user check
        # if User.objects.filter(username = username).count() == 0:
        #     return Response({"error":"존재 하지 않는 유저 입니다. "}, status=status.HTTP_400_BAD_REQUEST)
        submission_class_list = SubmissionClass.objects.all()

        if username:
            submission_class_list = submission_class_list.filter(username=username)
        if cpid:
            submission_class_list = submission_class_list.filter(c_p_id=cpid)

        obj_list = []
        # ip_addr = "3.37.186.158"
        # ip_addr = "3.37.186.158:8000"

        for submission in submission_class_list:
            path = Path.objects.get(id=submission.path.id)
            # csv_path = str(submission.csv.path).replace("/home/ubuntu/BE/uploads/", "")
            # csv_url = "http://{0}/{1}" . format (ip_addr, csv_path)
            # ipynb_path = str(submission.ipynb.path).replace("/home/ubuntu/BE/uploads/", "")
            # ipynb_url = "http://{0}/{1}" . format (ip_addr, ipynb_path)
            csv_url = "http://{0}/api/submissions/class/{1}/download/csv".format(IP_ADDR, submission.id)
            ipynb_url = "http://{0}/api/submissions/class/{1}/download/ipynb".format(IP_ADDR, submission.id)

            obj = {
                "id": submission.id,
                "username": submission.username,
                "score": path.score,
                "csv": csv_url,
                "ipynb": ipynb_url,
                "created_time": path.created_time,
                "status": path.status,
                "on_leaderboard": path.on_leaderboard
            }
            obj_list.append(obj)
        #serializer = SumissionClassListSerializer(obj_list, many=True)

        page = self.paginate_queryset(obj_list)
        if page is not None:
            serializer = self.get_paginated_response(SumissionClassListSerializer(page, many=True).data)
        else:
            serializer = SumissionClassListSerializer(obj_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SubmissionClassCheckView(APIView):
    def get_object_class(self, class_id):
        classid = get_object_or_404(Class, id = class_id)
        return classid

    def get_object_contest(self, contest_id):
        contestid = get_object_or_404(Contest, id = contest_id)
        return contestid

    def get_object_contest_problem(self, cp_id):
        cpid = get_object_or_404(Contest_problem, id = cp_id)
        return cpid

    # 05-17
    def patch(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response({"error": "class_id"}, status=status.HTTP_400_BAD_REQUEST)
        if kwargs.get('contest_id') is None:
            return Response({"error": "contest_id"}, status=status.HTTP_400_BAD_REQUEST)
        if kwargs.get('cp_id') is None:
            return Response({"error": "cp_id"}, status=status.HTTP_400_BAD_REQUEST)
        class_id = kwargs.get('class_id')
        classid = self.get_object_class(class_id)
        contest_id = kwargs.get('contest_id')
        contestid = self.get_object_contest(contest_id)
        cp_id = kwargs.get('cp_id')
        cpid = self.get_object_contest_problem(cp_id)

        data = request.data
        class_submission = SubmissionClass.objects.get(id=data['id'])

        if class_submission.username.username != request.user.username:
            return Response({"error": "username"}, status=status.HTTP_400_BAD_REQUEST)

        # submission의 on_leaderboard를 True로 설정
        class_path = class_submission.path
        class_path.on_leaderboard = True
        class_path.save()

        # on_leaderboard를 True로 설정한 submission 외의 것의 on_leaderboard를 모두 False로 설정
        submission_list = SubmissionClass.objects.filter(username = request.user.username)
        submission_list = submission_list.filter(c_p_id=cp_id)
        for submission in submission_list:
            if submission.id == class_submission.id:
                continue
            path = submission.path
            path.on_leaderboard = False
            path.save()
            print("path.on_leaderboard", path.on_leaderboard)

        return Response({'success':'성공'}, status=status.HTTP_200_OK)


# submission-competition 관련
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

    def check_participation(self, competition_id, username):
        user = self.get_user(username)
        if Competition_user.objects.filter(username = username).filter(competition_id = competition_id).count() == 0:
            return False
        return user

    # 06-04 대회 유저 파일 제출
    def post(self, request, **kwargs):
        if kwargs.get('competition_id') is None:
            return Response({"error": "competition_id"}, status=status.HTTP_400_BAD_REQUEST)
        if kwargs.get('username') is None:
            return Response({"error": "username"}, status=status.HTTP_400_BAD_REQUEST)
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
            "ip_address":GetIpAddr(request)
        }
        submission_json = {
            "username": request.user,
            "competition_id":competition.id,
            "csv":data["csv"],
            "ipynb":data["ipynb"]
        }

        path_serializer = PathSerializer(data=path_json)
        if path_serializer.is_valid():
            path_obj = path_serializer.save()
            submission_json["path"] = path_obj.id
            submission_serializer = SubmissionCompetitionSerializer(data=submission_json)
            if submission_serializer.is_valid():
                submission = submission_serializer.save()
                # return Response(submission_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(submission_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # evaluation
        problem = get_object_or_404(Problem, id=competition.problem_id.id)
        self.evaluate(path=path_obj, solution_csv=problem.solution, submission_csv=submission.csv, evaluation=problem.evaluation)

        return Response({"success":"submission 성공"}, status=status.HTTP_200_OK)

class SubmissionCompetitionListView(APIView, PaginationHandlerMixin):

    # pagination
    pagination_class = BasicPagination

    # 06-07 유저 submission 내역 조회
    def get(self, request, **kwargs):
        competition_id = kwargs.get('competition_id')
        username = request.GET.get('username', '')
        # competition check
        if Competition.objects.filter(id = competition_id).count() == 0:
            return Response({"error":"존재 하지 않는 대회 입니다. "}, status=status.HTTP_400_BAD_REQUEST)

        submission_comptition_list =SubmissionCompetition.objects.filter(competition_id = competition_id)
        if username:
            submission_comptition_list = submission_comptition_list.filter(username=username)
        obj_list = []
        # ip_addr = "3.37.186.158:8000"
        for submission in submission_comptition_list:
            path = Path.objects.get(id=submission.path.id)
            # csv_path = str(submission.csv.path).replace("/home/ubuntu/BE/uploads/", "")
            # csv_url = "http://{0}/{1}" . format (ip_addr, csv_path)
            # ipynb_path = str(submission.ipynb.path).replace("/home/ubuntu/BE/uploads/", "")
            # ipynb_url = "http://{0}/{1}" . format (ip_addr, ipynb_path)
            csv_url = "http://{0}/api/submissions/competition/{1}/download/csv".format(IP_ADDR, submission.id)
            ipynb_url = "http://{0}/api/submissions/competition/{1}/download/ipynb".format(IP_ADDR, submission.id)

            obj = {
                "id": submission.id,
                "username": submission.username,
                "score": path.score,
                "csv": csv_url,
                "ipynb": ipynb_url,
                "created_time": path.created_time,
                "status": path.status,
                "on_leaderboard": path.on_leaderboard
            }
            obj_list.append(obj)
        # serializer = SumissionCompetitionListSerializer(obj_list, many=True)

        page = self.paginate_queryset(obj_list)
        if page is not None:
            serializer = self.get_paginated_response(SumissionCompetitionListSerializer(page, many=True).data)
        else:
            serializer = SumissionCompetitionListSerializer(obj_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SubmissionCompetitionCheckView(APIView):

    def get_competition(self, competition_id):
        competition = get_object_or_404(Competition, id=competition_id)
        return competition

    def get_submissionCompetition(self, id):
        competition_submission = get_object_or_404(SubmissionCompetition, id=id)
        return competition_submission

    # 06-06 submission 리더보드 체크
    def patch(self, request, competition_id):
        competition = self.get_competition(competition_id)

        data = request.data
        competition_submission = self.get_submissionCompetition(id=data["id"])

        if competition_submission.username.username != request.user.username:
            return Response({"error": "username"}, status=status.HTTP_400_BAD_REQUEST)

        # submission의 on_leaderboard를 True로 설정
        competition_path = competition_submission.path
        competition_path.on_leaderboard = True
        competition_path.save()

        # on_leaderboard를 True로 설정한 submission 외의 것의 on_leaderboard를 모두 False로 설정
        submission_list = SubmissionCompetition.objects.filter(username = request.user.username)
        submission_list = submission_list.filter(competition_id=competition.id)

        for submission in submission_list:
            if submission.id == competition_submission.id:
                continue
            path = submission.path
            path.on_leaderboard = False
            path.save()
            print("path.on_leaderboard", path.on_leaderboard)

        return Response({'success':'성공'}, status=status.HTTP_200_OK)

class SubmissionClassCsvDownloadView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, submission_id):
        submission = get_object_or_404(SubmissionClass, id=submission_id)
        return submission

    def get(self, request, submission_id):
        submission = self.get_object(submission_id)

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # result = /Users/ingyu/Desktop/BE/problem
        BASE_DIR = BASE_DIR.replace("/submission", "")
        # print(BASE_DIR)

        csv_path = str(submission.csv.path).split('uploads/', 1)[1]
        filename = csv_path.split('/', 2)[2]
        filepath = BASE_DIR + '/uploads/' + csv_path
        print(filepath)
        # Open the file for reading content
        path = open(filepath, 'r')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        # Return the response value
        return response

class SubmissionClassIpynbDownloadView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, submission_id):
        submission = get_object_or_404(SubmissionClass, id=submission_id)
        return submission

    def get(self, request, submission_id):
        submission = self.get_object(submission_id)

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # result = /Users/ingyu/Desktop/BE/problem
        BASE_DIR = BASE_DIR.replace("/submission", "")
        # print(BASE_DIR)

        csv_path = str(submission.ipynb.path).split('uploads/', 1)[1]
        filename = csv_path.split('/', 2)[2]
        filepath = BASE_DIR + '/uploads/' + csv_path
        print(filepath)
        # Open the file for reading content
        path = open(filepath, 'r')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        # Return the response value
        return response

class SubmissionCompetitionCsvDownloadView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, submission_id):
        submission = get_object_or_404(SubmissionCompetition, id=submission_id)
        return submission

    def get(self, request, submission_id):
        submission = self.get_object(submission_id)

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # result = /Users/ingyu/Desktop/BE/problem
        BASE_DIR = BASE_DIR.replace("/submission", "")
        # print(BASE_DIR)

        csv_path = str(submission.csv.path).split('uploads/', 1)[1]
        filename = csv_path.split('/', 2)[2]
        filepath = BASE_DIR + '/uploads/' + csv_path
        print(filepath)
        # Open the file for reading content
        path = open(filepath, 'r')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        # Return the response value
        return response

class SubmissionCompetitionIpynbDownloadView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, submission_id):
        submission = get_object_or_404(SubmissionCompetition, id=submission_id)
        return submission

    def get(self, request, submission_id):
        submission = self.get_object(submission_id)

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # result = /Users/ingyu/Desktop/BE/problem
        BASE_DIR = BASE_DIR.replace("/submission", "")
        # print(BASE_DIR)

        csv_path = str(submission.ipynb.path).split('uploads/', 1)[1]
        filename = csv_path.split('/', 2)[2]
        filepath = BASE_DIR + '/uploads/' + csv_path
        print(filepath)
        # Open the file for reading content
        path = open(filepath, 'r')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        # Return the response value
        return response

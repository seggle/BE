from __future__ import annotations
import zipfile

import rest_framework.status
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from submission.models import SubmissionClass, SubmissionCompetition
from utils.compression import creat_archive
from .serializers import PathSerializer, SubmissionClassSerializer, SumissionClassListSerializer, \
    SubmissionCompetitionSerializer, SumissionCompetitionListSerializer
from competition.models import CompetitionUser
from rest_framework.pagination import PageNumberPagination  # pagination
from utils.pagination import BasicPagination, PaginationHandlerMixin  # pagination
from utils.evaluation import EvaluationMixin
from utils.get_ip import GetIpAddr
from utils.get_obj import *
from utils.message import *
from utils.common import IP_ADDR
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
import uuid
import mimetypes
import os
import platform
import pathlib
import urllib
from django.http import HttpResponse
from django.utils import timezone
from utils.permission import *
from rest_framework.permissions import IsAuthenticated
import utils.download as download
from datetime import datetime
from utils.common import make_mult_level_dir, convert_date_format, is_temp

COMPETITION_ZIP_ARCHIVE_PATH = 'uploads/zipcache/competition'
CLASS_PROBLEM_ZIP_ARCHIVE_PATH = 'uploads/zipcache/class'
CUSTOM_ZIP_ARCHIVE_PATH = 'uploads/zipcache/custom'


# submission-class 관련
class SubmissionClassView(APIView, EvaluationMixin):
    permission_classes = [IsClassUser]

    # 05-16
    def post(self, request: Request, class_id: int, contest_id: int, cp_id: int) -> Response:
        class_ = get_class(class_id)
        contest = get_contest(contest_id)
        contest_problem = get_contest_problem(cp_id)

        if (contest_problem.contest_id.id != contest_id) or (contest_problem.contest_id.class_id.id != class_id):
            return Response(msg_error_id, status=status.HTTP_400_BAD_REQUEST)

        time_check = timezone.now()
        if (contest.start_time > time_check) or (contest.end_time < time_check):
            return Response(msg_time_error, status=status.HTTP_400_BAD_REQUEST)

        # exam인 경우
        is_class_student = ClassUser.objects.filter(username=request.user, privilege=0).exists()
        if contest.is_exam and is_class_student:
            # ip 중복 체크
            exam = Exam.objects.get(user=request.user, contest=contest)
            if exam.is_duplicated:  # 중복이면 에러
                return Response(msg_SubmissionClassView_post_e_3, status=status.HTTP_400_BAD_REQUEST)

        data = request.data

        csv_file = data.get('csv')
        if csv_file is None:
            return Response(msg_SubmissionClassView_post_e_1, status=status.HTTP_400_BAD_REQUEST)
        csv_str = csv_file.name.split('.')[-1]

        ipynb_file = data.get('ipynb')
        if ipynb_file is None:
            return Response(msg_SubmissionClassView_post_e_2, status=status.HTTP_400_BAD_REQUEST)
        ipynb_str = ipynb_file.name.split('.')[-1]

        if csv_str != 'csv':
            return Response(msg_SubmissionClassView_post_e_1, status=status.HTTP_400_BAD_REQUEST)
        if ipynb_str != 'ipynb':
            return Response(msg_SubmissionClassView_post_e_2, status=status.HTTP_400_BAD_REQUEST)

        temp = str(uuid.uuid4()).replace("-", "")

        path_json = {
            "path": temp
        }

        submission_json = {
            "username": request.user,
            "class_id": contest_problem.contest_id.class_id.id,
            "contest_id": contest_problem.contest_id.id,
            "c_p_id": contest_problem.id,
            "csv": csv_file,
            "ipynb": ipynb_file,
            "problem_id": contest_problem.problem_id.id,
            "score": None,
            "ip_address": GetIpAddr(request)
        }

        path_serializer = PathSerializer(data=path_json)
        if path_serializer.is_valid():
            path_obj = path_serializer.save()
            submission_json['path'] = path_obj.id
            submission_serializer = SubmissionClassSerializer(data=submission_json)

            if submission_serializer.is_valid():
                submission = submission_serializer.save()
                # evaluation
                problem = get_problem(submission.problem_id.id)
                self.evaluate(submission=submission, problem=problem)

                return Response(msg_success, status=status.HTTP_200_OK)
            else:
                return Response(submission_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(path_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmissionClassPerProblemListView(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    # 05-18 클래스 contest 내 제출 보기
    def get(self, request: Request, class_id: int, contest_id: int, cp_id: int) -> Response:

        submissions = SubmissionClass.objects.filter(class_id=class_id, contest_id=contest_id, c_p_id=cp_id) \
            .order_by('-created_time')

        username = request.GET.get('username', '')
        if username:
            submissions = submissions.filter(username=username)

        if submissions.count() == 0:
            return Response({'message': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        outputs = []

        for submission in submissions:
            obj = {
                "id": submission.id,
                "username": submission.username,
                "score": submission.score,
                # "csv": csv_url,
                # "ipynb": ipynb_url,
                "created_time": submission.created_time,
                "status": submission.status,
                "on_leaderboard": submission.on_leaderboard
            }
            outputs.append(obj)

        page = self.paginate_queryset(outputs)

        if page is not None:
            serializer = self.get_paginated_response(SumissionClassListSerializer(page, many=True).data)
        else:
            serializer = SumissionClassListSerializer(outputs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionClassListView(APIView, PaginationHandlerMixin):
    permission_classes = [IsAuthenticated]
    pagination_class = BasicPagination

    # 07-00 유저 submission 내역 조회
    def get(self, request: Request) -> Response:
        cp_id = request.GET.get('cpid', 0)
        contest_problem = get_contest_problem(cp_id)
        submission_class_list = SubmissionClass.objects.all().filter(username=request.user).filter(
            c_p_id=cp_id).order_by('-created_time')

        obj_list = []

        for submission in submission_class_list:
            # csv_url = "http://{0}/api/submissions/class/{1}/download/csv".format(IP_ADDR, submission.id)
            # ipynb_url = "http://{0}/api/submissions/class/{1}/download/ipynb".format(IP_ADDR, submission.id)

            obj = {
                "id": submission.id,
                "username": submission.username,
                "score": submission.score,
                # "csv": csv_url,
                # "ipynb": ipynb_url,
                "created_time": submission.created_time,
                "status": submission.status,
                "on_leaderboard": submission.on_leaderboard
            }
            obj_list.append(obj)

        page = self.paginate_queryset(obj_list)
        if page is not None:
            serializer = self.get_paginated_response(SumissionClassListSerializer(page, many=True).data)
        else:
            serializer = SumissionClassListSerializer(obj_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionClassCheckView(APIView):
    # 05-17
    permission_classes = [IsClassUser]

    def patch(self, request: Request, class_id: int, contest_id: int, cp_id: int) -> Response:
        class_ = get_class(class_id)
        contest = get_contest(contest_id)
        contest_problem = get_contest_problem(cp_id)

        data = request.data
        class_submission_list = []
        for submission in data:
            sub_id = submission.id
            class_submission = get_submission_class(sub_id)
            if class_submission.username.username != request.user.username:
                return Response(msg_SubmissionCheckView_patch_e_1, status=status.HTTP_400_BAD_REQUEST)
            class_submission_list.append(class_submission)

        # on_leaderboard를 모두 False로 설정
        submission_list = SubmissionClass.objects.filter(username=request.user.username).filter(c_p_id=cp_id)
        for submission in submission_list:
            submission.on_leaderboard = False
            submission.save()

        # submission의 on_leaderboard를 True로 설정
        for class_submission in class_submission_list:
            class_submission.on_leaderboard = True
            class_submission.save()

        # contest 마감 이후 leaderboard 제출 시도 시 msg_time_error 반환
        if contest.end_time < timezone.now():
            return Response(msg_time_error, status=status.HTTP_400_BAD_REQUEST)

        return Response(msg_success, status=status.HTTP_200_OK)


# submission-competition 관련
class SubmissionCompetitionView(APIView, EvaluationMixin):
    permission_classes = [IsCompetitionUser]

    # 06-04 대회 유저 파일 제출
    def post(self, request: Request, competition_id: int) -> Response:
        competition = get_competition(competition_id)
        # permission check - 대회에 참가한 학생만 제출 가능

        time_check = timezone.now()
        if (competition.start_time > time_check) or (competition.end_time < time_check):
            return Response(msg_time_error, status=status.HTTP_400_BAD_REQUEST)

        user = get_username(request.user.username)
        if CompetitionUser.objects.filter(username=request.user.username).filter(
                competition_id=competition_id).count() == 0:
            return Response(msg_SubmissionCompetitionView_post_e_1, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()

        csv_str = data.get('csv', '')
        if csv_str != '':
            csv_str = csv_str.name.split('.')[-1]
        ipynb_str = data.get('ipynb', '')
        if ipynb_str != '':
            ipynb_str = ipynb_str.name.split('.')[-1]
        if csv_str != 'csv':
            return Response(msg_SubmissionClassView_post_e_1, status=status.HTTP_400_BAD_REQUEST)
        if ipynb_str != 'ipynb':
            return Response(msg_SubmissionClassView_post_e_2, status=status.HTTP_400_BAD_REQUEST)

        temp = str(uuid.uuid4()).replace("-", "")
        path_json = {
            "path": temp
        }

        submission_json = {
            "username": request.user,
            "competition_id": competition.id,
            "csv": data.get("csv"),
            "ipynb": data.get("ipynb"),
            "problem_id": competition.problem_id.id,
            "score": None,
            "ip_address": GetIpAddr(request)
        }

        path_serializer = PathSerializer(data=path_json)
        if path_serializer.is_valid():
            path_obj = path_serializer.save()
            submission_json["path"] = path_obj.id
            submission_serializer = SubmissionCompetitionSerializer(data=submission_json)

            if submission_serializer.is_valid():
                submission = submission_serializer.save()
                # evaluation
                problem = get_problem(submission.problem_id.id)
                self.evaluate(submission=submission, problem=problem)

                return Response(msg_success, status=status.HTTP_200_OK)
            else:
                return Response(submission_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(path_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmissionCompetitionListView(APIView, PaginationHandlerMixin):
    # pagination
    pagination_class = BasicPagination

    # 06-07 유저 submission 내역 조회
    def get(self, request: Request, competition_id: int) -> Response:
        competition = get_competition(competition_id)
        username = request.GET.get('username', '')

        submission_competition_list = SubmissionCompetition.objects.filter(competition_id=competition_id).order_by(
            '-created_time')
        if username:
            submission_competition_list = submission_competition_list.filter(username=username)

        obj_list = []

        for submission in submission_competition_list:
            # csv_url = "http://{0}/api/submissions/competition/{1}/download/csv".format(IP_ADDR, submission.id)
            # ipynb_url = "http://{0}/api/submissions/competition/{1}/download/ipynb".format(IP_ADDR, submission.id)

            obj = {
                "id": submission.id,
                "username": submission.username,
                "score": submission.score,
                # "csv": csv_url,
                # "ipynb": ipynb_url,
                "created_time": submission.created_time,
                "status": submission.status,
                "on_leaderboard": submission.on_leaderboard
            }
            obj_list.append(obj)

        page = self.paginate_queryset(obj_list)
        if page is not None:
            serializer = self.get_paginated_response(SumissionCompetitionListSerializer(page, many=True).data)
        else:
            serializer = SumissionCompetitionListSerializer(obj_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionCompetitionCheckView(APIView):
    permission_classes = [IsCompetitionUser]

    # 06-06 submission 리더보드 체크
    def patch(self, request: Request, competition_id: int) -> Response:
        competition = get_competition(competition_id)

        data = request.data
        competition_submission_list = []
        for submission in data:
            competition_submission = get_submission_competition(id=submission.get("id"))
            if competition_submission.username.username != request.user.username:
                return Response(msg_SubmissionCheckView_patch_e_1, status=status.HTTP_400_BAD_REQUEST)
            competition_submission_list.append(competition_submission)

        # on_leaderboard를 모두 False로 설정
        submission_list = SubmissionCompetition.objects.filter(username=request.user.username).filter(
            competition_id=competition.id)

        for submission in submission_list:
            submission.on_leaderboard = False
            submission.save()

        # submission의 on_leaderboard를 True로 설정
        for competition_submission in competition_submission_list:
            competition_submission.on_leaderboard = True
            competition_submission.save()

        # competition 마감 이후 leaderboard 제출 시도 시 msg_time_error 반환
        if competition.end_time < timezone.now():
            return Response(msg_time_error, status=status.HTTP_400_BAD_REQUEST)

        return Response(msg_success, status=status.HTTP_200_OK)


class SubmissionClassCsvDownloadView(APIView):
    permission_classes = [IsSubClassDownloadableUser]

    def get(self, request: Request, submission_id: int) -> HttpResponse:
        submission = get_submission_class(submission_id)

        os_info = platform.system()

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        (filename, filepath) = download.csv_download_windows(submission.csv.path, BASE_DIR, "submission") \
            if os_info == 'Windows' else download.csv_download_nix(submission.csv.path, BASE_DIR, "submission")

        # Open the file for reading content
        path = open(filepath, 'r')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % filename

        return response


class SubmissionClassIpynbDownloadView(APIView):
    permission_classes = [IsSubClassDownloadableUser]

    # 
    def get(self, request: Request, submission_id: int) -> HttpResponse:
        submission = get_submission_class(submission_id)

        os_info = platform.system()

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        (filename, filepath) = download.ipynb_download_windows(submission.ipynb.path, BASE_DIR) \
            if os_info == 'Windows' else download.ipynb_download_nix(submission.ipynb.path, BASE_DIR)

        # Open the file for reading content
        path = open(filepath, 'r')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % filename

        return response


class SubmissionCompetitionCsvDownloadView(APIView):
    permission_classes = [IsSubCompDownloadableUser]

    def get(self, request: Request, submission_id: int) -> HttpResponse:
        submission = get_submission_competition(submission_id)

        # It should be considered what operating system is running

        os_info = platform.system()

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        (filename, filepath) = download.csv_download_windows(submission.csv.path, BASE_DIR, "submission") \
            if os_info == 'Windows' else download.csv_download_nix(submission.csv.path, BASE_DIR, "submission")

        # Open the file for reading content
        path = open(filepath, 'r')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % filename

        return response


class SubmissionCompetitionIpynbDownloadView(APIView):
    permission_classes = [IsSubCompDownloadableUser]

    def get(self, request: Request, submission_id: int) -> HttpResponse:
        submission = get_submission_competition(submission_id)

        os_info = platform.system()

        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        (filename, filepath) = download.ipynb_download_windows(submission.ipynb.path, BASE_DIR) \
            if os_info == 'Windows' else download.ipynb_download_nix(submission.ipynb.path, BASE_DIR)

        # Open the file for reading content
        path = open(filepath, 'r')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % filename

        return response


class SubmissionClassDownloadView(APIView):
    permission_classes = [IsTA | IsProf | IsAdmin]

    def post(self, request: Request, class_id: int, contest_id: int, cp_id: int) -> Response or HttpResponse:
        username = request.GET.get('username', None)
        download_option = request.GET.get('dloption', None)
        use_subdirectory = request.data.get('useSubdirectory', False)
        contest_info = Contest.objects.filter(id=contest_id).first()

        if download_option is None:
            return Response(data=msg_error_no_download_option,
                            status=status.HTTP_400_BAD_REQUEST)

        # Setting path of the archive file
        base_dir_obj = pathlib.Path(__file__).parents[1].absolute()
        base_dir = base_dir_obj
        base_dir_obj /= CLASS_PROBLEM_ZIP_ARCHIVE_PATH
        base_dir_obj /= str(class_id)
        base_dir_obj /= str(contest_id)

        # This could be implemented match-case statement on Python 3.10 or later
        if download_option == 'custom':
            entries = request.data.get('customTarget', None)
            if isinstance(entries, list) is False or len(entries) == 0:
                return Response(data=msg_error_no_selection, status=status.HTTP_400_BAD_REQUEST)

            targets = {}
            failed = []
            for submission_id in entries:
                submission = SubmissionClass.objects.filter(id=submission_id).distinct()
                if submission.count() == 0:
                    failed.append(submission_id)
                    continue

                submitter = submission.first().username.username
                if targets.get(submitter, None) is None:
                    targets[submitter] = [submission[0]]
                else:
                    targets[submitter].append(submission[0])
            tail = str(uuid.uuid4())[:8]
            base_dir_obj /= CUSTOM_ZIP_ARCHIVE_PATH

        elif download_option == 'latest' or download_option == 'highest' or download_option == 'leaderboard'\
                or download_option == 'all':
            queryset = SubmissionClass.objects.filter(class_id=class_id, contest_id=contest_id, c_p_id=cp_id)
            if download_option == 'leaderboard':
                queryset = queryset.filter(on_leaderboard=True)

            if len(queryset) == 0:
                return Response(data=msg_notfound, status=status.HTTP_404_NOT_FOUND)

            if not isinstance(username, str):
                targets = {key: [] for key in queryset.values_list('username', flat=True).distinct()}
            else:
                targets = {username: []}

            download.get_download_targets(targets, download_option, queryset)
            tail = download_option
            base_dir_obj /= COMPETITION_ZIP_ARCHIVE_PATH

        else:
            return Response(data=msg_error_url, status=status.HTTP_400_BAD_REQUEST)

        zip_filename = f'c_{class_id}_t_{str(contest_id)}_p_{cp_id}_' \
                       f'{convert_date_format(contest_info.start_time)}_{tail}.zip'
        zip_filepath = base_dir_obj / zip_filename

        if os.path.exists(str(base_dir_obj)) is False:
            make_mult_level_dir(base_dir, f'{CLASS_PROBLEM_ZIP_ARCHIVE_PATH}/{str(class_id)}/{str(contest_id)}')
            make_mult_level_dir(base_dir, CUSTOM_ZIP_ARCHIVE_PATH)

        temp_flag = is_temp(contest_info.end_time)

        if download_option != 'custom' and os.path.exists(str(zip_filepath)) and not temp_flag:
            mime_type = download.get_mimetype(zip_filepath)
            return download.get_attachment_response(zip_filepath, mime_type)
        # elif is_temp is True:
        #    update_archive()
        else:
            creat_archive(zip_filepath, base_dir, targets, download_option, use_subdirectory)

        mime_type = download.get_mimetype(zip_filepath)
        return download.get_attachment_response(zip_filepath, mime_type)


class SubmissionCompetitionDownloadView(APIView):
    permission_classes = [IsTA | IsProf | IsAdmin]

    #
    def post(self, request: Request, competition_id: int) -> Response or HttpResponse:
        username = request.GET.get('username', None)
        download_option = request.GET.get('dloption', None)
        use_subdirectory = request.data.get('useSubdirectory', False)
        competition_info = Competition.objects.filter(id=competition_id).first()

        if download_option is None:
            return Response(data=msg_error_no_download_option,
                            status=status.HTTP_400_BAD_REQUEST)

        # Setting path of the archive file
        base_dir_obj = pathlib.Path(__file__).parents[1].absolute()
        base_dir = base_dir_obj

        # This could be implemented match-case statement on Python 3.10 or later
        if download_option == 'custom':
            entries = request.data.get('customTarget', None)
            if isinstance(entries, list) is False or len(entries) == 0:
                return Response(data=msg_error_no_selection, status=status.HTTP_400_BAD_REQUEST)

            targets = {}
            failed = []
            for submission_id in entries:
                submission = SubmissionCompetition.objects.filter(id=submission_id).distinct()
                if submission.count() == 0:
                    failed.append(submission_id)
                    continue

                submitter = submission.first().username.username
                if targets.get(submitter, None) is None:
                    targets[submitter] = [submission[0]]
                else:
                    targets[submitter].append(submission[0])
            tail = str(uuid.uuid4())[:8]
            base_dir_obj /= CUSTOM_ZIP_ARCHIVE_PATH

        elif download_option == 'latest' or download_option == 'highest' or download_option == 'leaderboard'\
                or download_option == 'all':
            queryset = SubmissionCompetition.objects.filter(id=competition_id)

            if download_option == 'leaderboard':
                queryset = queryset.filter(on_leaderboard=True)

            if len(queryset) == 0:
                return Response(data=msg_notfound, status=status.HTTP_404_NOT_FOUND)

            if not isinstance(username, str):
                targets = {key: [] for key in queryset.values_list('username', flat=True).distinct()}
            else:
                targets = {username: []}

            download.get_download_targets(targets, download_option, queryset)
            tail = download_option
            base_dir_obj /= COMPETITION_ZIP_ARCHIVE_PATH

        else:
            return Response(data=msg_error_url, status=status.HTTP_400_BAD_REQUEST)

        zip_filename = f'comp_{str(competition_id)}_{convert_date_format(competition_info.start_time)}' \
                       f'_{tail}.zip'
        zip_filepath = base_dir_obj / zip_filename

        if os.path.exists(str(base_dir_obj)) is False:
            make_mult_level_dir(base_dir, COMPETITION_ZIP_ARCHIVE_PATH)
            make_mult_level_dir(base_dir, CUSTOM_ZIP_ARCHIVE_PATH)

        temp_flag = is_temp(competition_info.end_time)

        if download_option != 'custom' and os.path.exists(str(zip_filepath)) and not temp_flag:
            mime_type = download.get_mimetype(zip_filepath)
            return download.get_attachment_response(zip_filepath, mime_type)
        # elif is_temp is True:
        #    update_archive()
        else:
            creat_archive(zip_filepath, base_dir, targets, download_option, use_subdirectory)

        mime_type = download.get_mimetype(zip_filepath)
        return download.get_attachment_response(zip_filepath, mime_type)

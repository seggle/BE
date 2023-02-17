from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request

from competition.serializers import (
    CompetitionDetailSerializer, CompetitionSerializer,
    CompetitionProblemCheckSerializer, CompetitionPutSerializer,
    CompetitionUserGetSerializer, CompetitionUserSerializer, CompetitionProblemSerializer,
    CompetitionProblemDetailSerializer, CompetitionProblemInfoSerializer,
)
from problem.serializers import ProblemSerializer
from competition.models import Competition, CompetitionUser
from problem.models import Problem
from account.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from utils.pagination import PaginationHandlerMixin, BasicPagination
from utils.permission import *
from utils.get_obj import *
from utils.common import IP_ADDR
import os
import shutil
import uuid
from django.http import Http404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from utils.message import *


class CompetitionView(APIView, PaginationHandlerMixin):
    permission_classes = [IsProfAdminOrReadOnly]
    pagination_class = BasicPagination

    # 06-00 대회 리스트 조회
    def get(self, request: Request) -> Response:
        competitions = Competition.objects.filter(is_deleted=False, visible=True).order_by('id').active()
        keyword = request.GET.get('keyword', '')
        if keyword:
            # 제목에 keyword가 포함되어 있는 레코드만 필터링
            competitions = competitions.filter(title__icontains=keyword)

        page = self.paginate_queryset(competitions)
        if page is not None:
            competition_detail_serializer = self.get_paginated_response \
                (CompetitionDetailSerializer(page, many=True).data)
        else:
            competition_detail_serializer = CompetitionDetailSerializer(competitions)

        return Response(competition_detail_serializer.data, status=status.HTTP_200_OK)

    # 06-01 대회 생성
    def post(self, request: Request) -> Response:

        # title, description, is_exam, visible, start_time, end_time, created_user
        data = request.data.copy()

        data['created_user'] = request.user.username

        serializer = CompetitionSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        competition_obj = serializer.save()

        professor = {
            'competition_id': competition_obj.id,
            'username': request.user.username,
            'privilege': 2,
        }

        user_serializer = CompetitionUserSerializer(data=professor)
        if not user_serializer.is_valid():
            competition_obj.delete()
            return Response(msg_error_invalid_user, status=status.HTTP_400_BAD_REQUEST)
        user_serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CompetitionDetailView(APIView, PaginationHandlerMixin):
    permission_classes = [IsCompetitionManagerOrReadOnly]
    pagination_class = BasicPagination

    # 06-02 대회 개별 조회 및 문제 목록 조회
    def get(self, request: Request, competition_id: int) -> Response:
        is_detail_mode = bool(request.GET.get('detail', False))
        competition = get_competition(id=competition_id)

        # 대회 정보만 보여줌
        if is_detail_mode:
            serializer = CompetitionDetailSerializer(competition, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 문제들을 보여줌
        problems = CompetitionProblem.objects.filter(competition_id=competition_id, is_deleted=False).order_by('order')
        obj_list = []
        for problem in problems:
            obj = {
                'id': problem.id,
                'competition_id': problem.competition_id,
                'problem_id': problem.problem_id,
                'order': problem.order,
                'title': problem.title,
                'start_time': competition.start_time,
                'end_time': competition.end_time,
            }
            obj_list.append(obj)

        page = self.paginate_queryset(obj_list)
        if page is not None:
            serializer = self.get_paginated_response(CompetitionProblemSerializer(page, many=True).data)
        else:
            serializer = CompetitionProblemSerializer(page, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # 06-03-01 대회 개별 수정
    def put(self, request: Request, competition_id: int) -> Response:
        competition = get_competition(id=competition_id)

        data = request.data
        obj = {
            'title': data.get('title'),
            'description': data.get('description'),
            'start_time': data.get('start_time'),
            'end_time': data.get('end_time'),
            'visible': data.get('visible', competition.visible),
            'is_exam': data.get('exam', competition.is_exam)
        }

        serializer = CompetitionSerializer(competition, data=obj, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 06-03-02 대회 삭제
    def delete(self, request: Request, competition_id: int) -> Response:
        competition = Competition.objects.get(id=competition_id)

        if competition.is_deleted:
            return Response(msg_error_already_deleted, status=status.HTTP_404_NOT_FOUND)
        # Warning : 1 object in queryset
        contest_problems = CompetitionProblem.objects.filter(competition_id=competition_id)

        for cprob in contest_problems:
            cprob.is_deleted = True
            cprob.save()
        competition.is_deleted = True
        competition.save()

        return Response(msg_success_delete_competition, status=status.HTTP_200_OK)


class CompetitionProblemConfigurationView(APIView):
    permission_classes = [IsCompetitionManagerOrReadOnly]

    def post(self, request: Request, competition_id: int) -> Response:
        # 문제 추가
        targets = request.data.get('targets', None)

        if targets is None:
            return Response(msg_error_no_selection, status=status.HTTP_400_BAD_REQUEST)

        competition = get_competition(competition_id)

        error = {'error_problem_id': []}

        obj_list = []
        for elem in targets:

            if Problem.objects.filter(id=elem).active().count() == 0 or \
                    CompetitionProblem.objects.filter(competition_id=competition_id,
                                                      problem_id=elem).active().count() != 0:
                error['error_problem_id'].append(elem)
                continue

            target = get_problem(id=elem)
            order = CompetitionProblem.objects.filter(competition_id=competition_id).active().count() + 1

            obj = {
                'title': target.title,
                'description': target.description,
                'data_description': target.data_description,
                'competition_id': competition_id,
                'problem_id': elem,
                'order': order,
            }
            obj_list.append(obj)

        serializer = CompetitionProblemDetailSerializer(data=obj_list, many=True)

        if serializer.is_valid():
            serializer.save()

        if len(error.get('error_problem_id')) == 0:
            return Response(msg_success_create, status=status.HTTP_201_CREATED)
        else:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, competition_id: int) -> Response:
        targets = request.data.get('targets', None)

        if targets is None:
            return Response(msg_error_no_selection, status=status.HTTP_400_BAD_REQUEST)

        competition = get_competition(competition_id)

        error = {'error_problem_id': []}

        for elem in targets:
            if CompetitionProblem.objects.filter(id=elem).active().count() == 0 or \
                    CompetitionProblem.objects.filter(competition_id=competition_id,
                                                      id=elem).active().count() == 0:
                error['error_problem_id'].append(elem)
                continue

            target = get_competition_problem(elem)
            target.is_deleted = True

            target.save()

        if len(error.get('error_problem_id')) == 0:
            return Response(msg_success_create, status=status.HTTP_201_CREATED)
        else:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class CompetitionUserView(APIView, PaginationHandlerMixin):
    permission_classes = [IsAuthenticated]
    pagination_class = BasicPagination

    # 06-05-03 대회 참가자, 관리자 전체 조회
    def get(self, request: Request, competition_id: int) -> Response:
        competition = get_competition(competition_id)
        user_list = CompetitionUser.objects.filter(competition_id=competition.id).order_by('-privilege', 'username')

        page = self.paginate_queryset(user_list)
        if page is not None:
            competition_userlist_serializer = self \
                .get_paginated_response(CompetitionUserGetSerializer(page, many=True).data)
        else:
            competition_userlist_serializer = CompetitionUserGetSerializer(user_list)

        return Response(competition_userlist_serializer.data, status=status.HTTP_200_OK)

    # 06-05-01 대회 유저 참가
    def post(self, request: Request, competition_id: int) -> Response:
        competition = get_competition(competition_id)

        time_check = timezone.now()
        if (competition.start_time > time_check) or (competition.end_time < time_check):
            return Response(msg_time_error, status=status.HTTP_400_BAD_REQUEST)

        # competition_user에 username이 이미 존재하는지 체크
        if CompetitionUser.objects.filter(username=request.user).filter(competition_id=competition_id).count():
            return Response(msg_error_already_participated, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "username": request.user.username,
            "privilege": 0,
            "competition_id": competition_id
        }
        serializer = CompetitionUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(msg_success_participation, status=status.HTTP_200_OK)
        else:
            return Response(msg_error_participation, status=status.HTTP_400_BAD_REQUEST)


class CompetitionTaView(APIView):
    permission_classes = [IsCompetitionManagerOrReadOnly]

    # 06-05-02 대회 유저 참가
    def post(self, request: Request, competition_id: int) -> Response:
        competition = get_competition(competition_id)

        # 0315
        # 기존 TA 삭제
        if (competition.created_user == request.user) or \
                request.user.privilege == 2:  # 대회 담당 교수, admin인 경우에만
            user_list = CompetitionUser.objects.filter(competition_id=competition.id)
            for users in user_list:
                if users.privilege == 1:
                    users.delete()
        else:
            return Response(msg_error_no_permission, status=status.HTTP_400_BAD_REQUEST)

        # TA 추가
        user_does_not_exist = {
            "does_not_exist": [],
            "is_existed": []
        }
        people = request.data.get('users', [])
        if len(people) == 0:
            return Response(msg_error_no_selection, status=status.HTTP_400_BAD_REQUEST)

        registered = []

        for user in people:
            is_check_user = User.objects.filter(username=user).count()
            is_check_competition_user_ta = CompetitionUser.objects \
                .filter(username=user, competition_id=competition_id, privilege__gte=1).count()
            if is_check_user == 0:
                user_does_not_exist['does_not_exist'].append(user)
                continue
            if is_check_competition_user_ta:
                user_does_not_exist['is_existed'].append(user)
                continue
            is_check_competition_user = CompetitionUser.objects.filter(username=user,
                                                                       competition_id=competition_id, privilege=0)
            if is_check_competition_user.count():
                is_check_competition_user[0].delete()

            obj = {
                "username": user,
                "is_show": True,
                "privilege": 1,
                "competition_id": competition_id
            }
            registered.append(obj)

        serializer = CompetitionUserSerializer(data=registered, many=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 출력
        if (len(user_does_not_exist['does_not_exist']) == 0) and (len(user_does_not_exist['is_existed']) == 0):
            return Response(msg_success_create, status=status.HTTP_201_CREATED)
        else:
            return Response(user_does_not_exist, status=status.HTTP_201_CREATED)


class CompetitionProblemOrderView(APIView):
    permission_classes = [IsCompetitionProfOrTA | IsAdmin]

    def patch(self, request: Request, competition_id: int) -> Response:
        datas = request.data.get('data', None)

        if datas is None:
            return Response(msg_error_no_selection, status=status.HTTP_400_BAD_REQUEST)

        accepted = []
        for data in datas:
            competition_problem_id = data.get('id', None)
            order = data.get('order', None)

            if competition_problem_id is None or competition_problem_id <= 0:
                return Response(msg_error_invalid_id, status=status.HTTP_400_BAD_REQUEST)
            if order is None or order <= 0:
                return Response(msg_error_invalid_order, status=status.HTTP_400_BAD_REQUEST)

            problem = get_competition_problem(competition_problem_id)

            if problem.competition_id.id != competition_id:
                return Response(msg_error_invalid_url, status=status.HTTP_400_BAD_REQUEST)

            accepted.append({'problem': problem, 'order': order})

        for elem in accepted:
            problem = elem.get('problem')
            problem.order = elem.get('order')
            problem.save()

        return Response(msg_success_patch_order, status=status.HTTP_200_OK)


class CompetitionCheckView(APIView):
    permission_classes = [IsCompetitionProfOrTA]

    def patch(self, request: Request, competition_id: int) -> Response:
        competition = get_competition(id=competition_id)

        if competition.visible:
            competition.visible = False
            competition.save()
            return Response(msg_success_check_public, status=status.HTTP_200_OK)
        else:
            competition.visible = True
            competition.save()
            return Response(msg_success_check_private, status=status.HTTP_200_OK)


class CompetitionProblemView(APIView):
    permission_classes = [IsAdmin | IsCompetitionProfOrTA | IsCompetitionUser]

    def get(self, request: Request, competition_id: int, comp_p_id: int) -> Response:
        competition = get_competition(id=competition_id)

        time_check = timezone.now()
        if (competition.start_time > time_check) or (competition.end_time < time_check):
            return Response(msg_time_error, status=status.HTTP_400_BAD_REQUEST)

        comp_problem = get_competition_problem(comp_p_id)

        if comp_problem.competition_id.id != competition.id:
            return Response(msg_error_invalid_problem, status=status.HTTP_400_BAD_REQUEST)

        orig_problem = get_problem(comp_problem.problem_id.id)

        problem = {
            'id': comp_problem.id,
            'title': comp_problem.title,
            'description': comp_problem.description,
            'data_description': comp_problem.data_description,
            'problem_id': comp_problem.problem_id.id,
            'order': comp_problem.order,
            'data': orig_problem.data,
            'evaluation': orig_problem.evaluation
        }

        serializer = CompetitionProblemInfoSerializer(data=problem, many=False)

        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(msg_error_wrong_problem, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.db.models import Q
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework.pagination import PageNumberPagination
from utils.pagination import PaginationHandlerMixin
from ..models import User
from ..serializers import UserRegisterSerializer, UserInfoClassCompetitionSerializer, ContributionsSerializer, \
    UserCompetitionSerializer, UserGetClassInfo, TokenObtainResultSerializer
from classes.models import ClassUser
from classes.serializers import ClassGetSerializer
from competition.models import CompetitionUser
from submission.models import SubmissionClass, SubmissionCompetition
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenObtainPairView,
)
from utils.get_obj import *

from utils.permission import *
from utils.pagination import BasicPagination, PaginationHandlerMixin


class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = UserRegisterSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            if request.data.get("password") != request.data.get("password2"):
                data["error"] = "Passwords must match"
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            else:

                user = User.objects.create(
                    username=request.data.get("username"),
                    email=request.data.get("email"),
                    name=request.data.get("name")
                )
                user.set_password(request.data.get("password"))
                user.save()
                data['response'] = "successfully registered a new user"
                data['email'] = user.email
                data['username'] = user.username
        else:
            data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# class LogoutAllView(APIView):
#     permission_classes = (IsAuthenticated,)
#     def post(self, request):
#         tokens = OutstandingToken.objects.filter(user_id=request.user.username)
#         for token in tokens:
#             t, _ = BlacklistedToken.objects.get_or_create(token=token)
#         return Response(status=status.HTTP_205_RESET_CONTENT)

class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class UserInfoView(APIView):
    permission_classes = [IsRightUser]

    # 01-07 유저 조회
    def get(self, request: Request, username: str, format: str = None) -> Response:
        user = get_username(username)
        # permission check
        if request.user.username != user.username:
            return Response({"error": "접근 권한이 없습니다"}, status=status.HTTP_400_BAD_REQUEST)
        competition = CompetitionUser.objects.filter(username=user.username)
        classes = ClassUser.objects.filter(username=user.username)
        obj = {"id": user.id,
               "email": user.email,
               "username": user.username,
               "name": user.name,
               "privilege": user.privilege,
               "dated_joined": user.date_joined,
               "is_active": user.is_active,

               "competition": competition,
               "classes": classes
               }

        serializer = UserInfoClassCompetitionSerializer(obj)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # 01-06 비밀번호 변경
    def patch(self, request: Request, username: str) -> Response:
        data = request.data
        current_password = data.get("current_password")
        user = get_username(username)
        if check_password(current_password, user.password):
            new_password = data.get("new_password")
            password_confirm = data.get("new_password2")
            if new_password == password_confirm:
                user.set_password(new_password)
                user.save()
                return Response({'success': "비밀번호 변경 완료"}, status=status.HTTP_200_OK)
            else:
                return Response({'error': "새로운 비밀번호 일치하지 않음"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': "현재 비밀번호 일치하지 않음"}, status=status.HTTP_400_BAD_REQUEST)

    # 01-08 회원탈퇴
    def delete(self, request: Request, username: str) -> Response:
        data = request.data
        user = get_username(username)
        # permission check
        if request.user.username != user.username:
            return Response({"error": "탈퇴권한 없음"}, status=status.HTTP_400_BAD_REQUEST)
        # 비밀번호 일치 확인
        current_password = data.get("password", '')
        if check_password(current_password, user.password):
            user.is_active = False
            user.save()
            return Response({'success': '회원 탈퇴 성공'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': "현재 비밀번호가 일치하지 않음"}, status=status.HTTP_400_BAD_REQUEST)


class ClassInfoView(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    # 01-09 유저 Class 조회
    def get(self, request: Request) -> Response:
        class_name_list = []
        class_lists = ClassUser.objects.filter(username=request.user)
        for class_list in class_lists:
            if class_list.class_id.is_deleted:
                continue
            class_add_is_show = {}
            class_list_serializer = ClassGetSerializer(class_list.class_id)
            class_add_is_show = class_list_serializer.data
            class_add_is_show["privilege"] = class_list.privilege
            class_add_is_show["is_show"] = class_list.is_show
            class_name_list.append(class_add_is_show)
        page = self.paginate_queryset(class_name_list)

        if page is not None:
            serializer = self.get_paginated_response(UserGetClassInfo(page, many=True).data)
        else:
            serializer = UserGetClassInfo(class_name_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 01-10 유저 수업 리스트 is_show 수정
    def patch(self, request: Request) -> Response:
        datas = request.data

        class_user_list = ClassUser.objects.filter(username=request.user)

        for user in class_user_list:
            user.is_show = False
            user.save()

        does_not_exist = {}
        does_not_exist['does_not_exist'] = []

        for data in datas:
            class_id = data.get('class_id')
            class_user = class_user_list.filter(class_id=class_id)
            if class_user.count() == 0:
                does_not_exist['does_not_exist'].append(class_id)
                continue

            user = class_user[0]
            user.is_show = True
            user.save()
        if len(does_not_exist['does_not_exist']) == 0:
            return Response("Success", status=status.HTTP_200_OK)
        else:
            return Response(does_not_exist, status=status.HTTP_200_OK)


class ContributionsView(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    # 01-12 유저 잔디밭 조회
    def get(self, request: Request, username: str) -> Response:
        user = get_username(username)
        # permission check
        if request.user.username != user.username:
            return Response({"error": "접근 권한이 없습니다"}, status=status.HTTP_400_BAD_REQUEST)

        submission_class = SubmissionClass.objects.filter(username=username)
        submission_competition = SubmissionCompetition.objects.filter(username=username)
        date_list = []

        if submission_class.count() != 0:
            for submission in submission_class:
                date = str(submission.created_time).split(' ')[0]
                date_list.append(date)

        if submission_competition.count() != 0:
            for submission in submission_competition:
                date = str(submission.created_time).split(' ')[0]
                date_list.append(date)
        date_list.sort()

        sort_dict = {}
        for i in date_list:
            try:
                sort_dict[i] += 1
            except:
                sort_dict[i] = 1

        sort_list = []
        for key, val in sort_dict.items():
            temp = {}
            temp["date"] = key
            temp["count"] = val
            sort_list.append(temp)

        page = self.paginate_queryset(sort_list)

        if page is not None:
            serializer = self.get_paginated_response(ContributionsSerializer(page, many=True).data)
        else:
            serializer = ContributionsSerializer(sort_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCompetitionInfoView(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    # 01-11 user 참가 대회 리스트 조회
    def get(self, request: Request, username: str) -> Response:
        user = get_username(username)

        # permission check
        if request.user.username != user.username:
            return Response({"error": "접근 권한이 없습니다"}, status=status.HTTP_400_BAD_REQUEST)

        competition_list = CompetitionUser.objects.filter(username=user.username)

        if competition_list.count() == 0:
            return Response({"count": 0, "next": None, "previous": None}, status=status.HTTP_200_OK)

        obj_list = []
        for competition in competition_list:

            if competition.competition_id.is_deleted:
                continue
            obj = {}
            obj["id"] = competition.competition_id.id
            obj["problem_id"] = competition.competition_id.problem_id
            obj["title"] = competition.competition_id.problem_id.title
            obj["start_time"] = competition.competition_id.start_time
            obj["end_time"] = competition.competition_id.end_time
            obj["user_total"] = CompetitionUser.objects.filter(
                Q(competition_id=competition.competition_id.id) & Q(privilege=0)).count()
            obj["rank"] = None

            leaderboard_list = SubmissionCompetition.objects.filter(
                Q(competition_id=competition.competition_id.id) & Q(on_leaderboard=True))
            if leaderboard_list.filter(username=username).count() != 0:  # submission 내역이 있다면
                # 정렬
                if competition.competition_id.problem_id.evaluation in ["CategorizationAccuracy", "F1-score",
                                                                        "mAP"]:  # 내림차순
                    leaderboard_list = leaderboard_list.order_by('-score', 'created_time')
                else:
                    leaderboard_list = leaderboard_list.order_by('score', 'created_time')
                temp_list = []
                for temp in leaderboard_list:
                    temp_list.append(temp.username.username)
                obj["rank"] = temp_list.index(username) + 1

            obj_list.append(obj)

        page = self.paginate_queryset(obj_list)

        if page is not None:
            serializer = self.get_paginated_response(UserCompetitionSerializer(page, many=True).data)
        else:
            serializer = UserCompetitionSerializer(obj_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserClassPrivilege(APIView):

    # 01-13 유저의 클래스 내 권한 조회
    def get(self, request: Request, class_id: int) -> Response:
        _class = get_class(class_id)
        username = request.user
        try:
            privilege = ClassUser.objects.get(class_id=_class, username=username).privilege
        except:
            privilege = -1
        data = {'privilege': privilege}

        return Response(data, status=status.HTTP_200_OK)


class UserCompetitionPrivilege(APIView):

    # 01-14 유저의 competition 내 권한 조회
    def get(self, request: Request, competition_id: int) -> Response:
        competition = get_competition(competition_id)
        username = request.user
        try:
            privilege = CompetitionUser.objects.get(competition_id=competition, username=username).privilege
        except:
            privilege = -1
        data = {'privilege': privilege}

        return Response(data, status=status.HTTP_200_OK)


# TokenObtainPairView with username field
class TokenObtainResultView(TokenObtainPairView):

    serializer_class = TokenObtainResultSerializer
    token_obtain_pair = TokenObtainPairView.as_view()

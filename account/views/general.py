from django.db.models import Q
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import status, generics
from django.contrib.auth.hashers import check_password
from ..models import User
from ..serializers import UserRegisterSerializer, UserInfoClassCompetitionSerializer, ContributionsSerializer, \
    UserCompetitionSerializer
from classes.models import Class, Class_user
from classes.serializers import ClassGetSerializer
from competition.models import Competition_user
from submission.models import SubmissionClass, SubmissionCompetition
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from utils import permission

"""
# 이메일 확인 완료
def send_email(request):
    subject = "message"
    to = ["seggle.sejong@gmail.com"]
    from_email = "seggle.sejong@gmail.com"
    message = "메지시 테스트"
    EmailMessage(subject=subject, body=message, to=to, from_email=from_email).send()
"""


class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            if request.data["password"] != request.data["password2"]:
                data["error"] = "Passwords must match"
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            else:

                user = User.objects.create(
                    username=request.data["username"],
                    email=request.data["email"],
                    name=request.data["name"]
                )
                user.set_password(request.data["password"])
                user.save()
                data['response'] = "successfully registered a new user"
                data['email'] = user.email
                data['username'] = user.username
        else:
            data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
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
    permission_classes = [permission.IsRightUser]

    def get_object(self, username):  # 존재하는 인스턴스인지 판단
        user = get_object_or_404(User, username=username)
        return user

    # 01-07 유저 조회
    def get(self, request, username, format=None):
        user = self.get_object(username)
        # permission check
        if request.user.username != user.username:
            return Response({"error": "접근 권한이 없습니다"}, status=status.HTTP_400_BAD_REQUEST)
        competition = Competition_user.objects.filter(username=user.username)
        classes = Class_user.objects.filter(username=user.username)
        obj = {"id": user.id,
               "email": user.email,
               "username": user.username,
               "name": user.name,
               "privilege": user.privilege,
               "dated_joined": user.date_joined,
               "is_active": user.is_active}
        obj["competition"] = competition
        obj["classes"] = classes
        serializer = UserInfoClassCompetitionSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 01-06 비밀번호 변경
    def patch(self, request, username):
        data = request.data
        current_password = data["current_password"]
        user = self.get_object(username)
        if check_password(current_password, user.password):
            new_password = data["new_password"]
            password_confirm = data["new_password2"]
            if new_password == password_confirm:
                user.set_password(new_password)
                user.save()
                return Response({'success': "비밀번호 변경 완료"}, status=status.HTTP_200_OK)
            else:
                return Response({'error': "새로운 비밀번호 일치하지 않음"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': "현재 비밀번호 일치하지 않음"}, status=status.HTTP_400_BAD_REQUEST)

    # 01-08 회원탈퇴
    def delete(self, request, username):
        data = request.data
        user = self.get_object(username)
        # permission check
        if request.user.username != user.username:
            return Response({"error": "탈퇴권한 없음"}, status=status.HTTP_400_BAD_REQUEST)
        # 비밀번호 일치 확인
        current_password = data["password"]
        if check_password(current_password, user.password):
            user.is_active = False
            user.save()
            return Response({'success': '회원 탈퇴 성공'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': "현재 비밀번호가 일치하지 않음"}, status=status.HTTP_400_BAD_REQUEST)


class ClassInfoView(APIView):
    # def get_object(self, username): # 존재하는 인스턴스인지 판단
    #     user = get_object_or_404(User, username = username)
    #     return user
    def get_object(self, class_id):
        classid = generics.get_object_or_404(Class, id=class_id)
        return classid

    # 01-09 유저 Class 조회
    def get(self, request):
        class_name_list = []
        class_lists = Class_user.objects.filter(username=request.user)
        for class_list in class_lists:
            # print(class_list)
            class_add_is_show = {}
            # class_add = {}

            class_list_serializer = ClassGetSerializer(class_list.class_id)
            class_add_is_show = class_list_serializer.data
            class_add_is_show["privilege"] = class_list.privilege
            class_add_is_show["is_show"] = class_list.is_show
            class_name_list.append(class_add_is_show)
        return Response(class_name_list, status=status.HTTP_200_OK)

    def patch(self, request):
        # class_id = kwargs.get('class_id')
        datas = request.data

        class_user_list = Class_user.objects.filter(username=request.user)

        for user in class_user_list:
            user.is_show = False
            user.save(force_update=True)

        does_not_exist = {}
        does_not_exist['does_not_exist'] = []

        for data in datas:
            # classid = self.get_object(data['class_id'])
            class_user = class_user_list.filter(class_id=data['class_id'])
            if class_user.count() == 0:
                does_not_exist['does_not_exist'].append(data['class_id'])
                continue

            user = class_user[0]
            user.is_show = True
            user.save(force_update=True)
        if len(does_not_exist['does_not_exist']) == 0:
            return Response("Success", status=status.HTTP_200_OK)
        else:
            return Response(does_not_exist, status=status.HTTP_200_OK)


class ContributionsView(APIView):

    def get_user(self, username):  # 존재하는 인스턴스인지 판단
        user = get_object_or_404(User, username=username)
        return user

    # 01-12 유저 잔디밭 조회
    def get(self, request, username):
        user = self.get_user(username)

        # permission check
        if request.user.username != user.username:
            return Response({"error": "접근 권한이 없습니다"}, status=status.HTTP_400_BAD_REQUEST)

        submission_class = SubmissionClass.objects.filter(username=username)
        submission_competition = SubmissionCompetition.objects.filter(username=username)
        date_list = []

        if submission_class.count() != 0:
            for submission in submission_class:
                date = str(submission.path.created_time).split(' ')[0]
                date_list.append(date)

        if submission_competition.count() != 0:
            for submission in submission_competition:
                date = str(submission.path.created_time).split(' ')[0]
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

        serializer = ContributionsSerializer(sort_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCompetitionInfoView(APIView):

    def get_object(self, username):  # 존재하는 인스턴스인지 판단
        user = get_object_or_404(User, username=username)
        return user

    # 01-11 user참가 대회 리스트 조회
    def get(self, request, username):
        user = self.get_object(username)
        # permission check
        if request.user.username != user.username:
            return Response({"error": "접근 권한이 없습니다"}, status=status.HTTP_400_BAD_REQUEST)

        competition_list = Competition_user.objects.filter(username=user.username)

        if competition_list.count() == 0:
            return Response({"error": "참가 중인 대회가 없습니다."}, status=status.HTTP_200_OK)

        obj_list = []
        for competition in competition_list:
            obj = {
                "id": competition.competition_id.id,
                "problem_id": competition.competition_id.problem_id,
                "title": competition.competition_id.problem_id.title,
                "start_time": competition.competition_id.start_time,
                "end_time": competition.competition_id.end_time,
            }
            obj["user_total"] = Competition_user.objects.filter(
                Q(competition_id=competition.competition_id.id) & Q(privilege=0)).count()
            obj["rank"] = None

            leaderboard_list = SubmissionCompetition.objects.filter(
                Q(competition_id=competition.competition_id.id) & Q(path__on_leaderboard=True))
            if leaderboard_list.filter(username=username).count() != 0:  # submission 내역이 있다면
                # 정렬
                if competition.competition_id.problem_id.evaluation in ["F1-score", "Accuracy"]:  # 내림차순
                    leaderboard_list = leaderboard_list.order_by('-path__score')
                else:
                    leaderboard_list = leaderboard_list.order_by('path__score')
                temp_list = []
                for temp in leaderboard_list:
                    temp_list.append(temp.username.username)
                obj["rank"] = temp_list.index(username) + 1

            obj_list.append(obj)

        serializer = UserCompetitionSerializer(obj_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

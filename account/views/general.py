from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import status
from django.contrib.auth.hashers import check_password
from ..models import User
from .. import serializers

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

    def post(self,request):
        serializer = serializers.UserRegisterSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            data['response'] = "successfully registered a new user"
            data['email'] = user.email
            data['username'] = user.username
        else:
            data = serializer.errors
        return Response(data)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
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

class UserInfoView(APIView):

    def get_object(self, username): # 존재하는 인스턴스인지 판단
        user = get_object_or_404(User, username = username)
        return user

    # 01-07 유저 조회
    # @login_required
    def get(self, request, username, format=None):
        user = self.get_object(username)
        try:
            serializer = serializers.UserInfoSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            raise Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

    # 01-06 비밀번호 변경
    def patch(self, request, username):
        data = request.data
        current_password = data["current_password"]
        user = self.get_object(username)
        print("확인1")
        if check_password(current_password, user.password):
            print("확인2")
            new_password = data["new_password"]
            password_confirm = data["new_password2"]
            print("확인3")
            if new_password == password_confirm:
                user.set_password(new_password)
                print("확인4")
                user.save()
                print("확인5")
                return Response({'success': "비밀번호 변경 완료"}, status=status.HTTP_200_OK)
            else:
                return Response({'error': "새로운 비밀번호 일치하지 않음"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error':"현재 비밀번호 일치하지 않음"}, status=status.HTTP_400_BAD_REQUEST)

    # 01-08 회원탈퇴
    def delete(self, request, username):
        data = request.data
        user = self.get_object(username)
        if check_password(data["password"], user.password):
            user.is_active = False
            user.save()
            return Response({'success': '회원 탈퇴 성공'}, status=status.HTTP_200_OK)
        else:
            return Response({'error':"현재 비밀번호가 일치하지 않음"}, status=status.HTTP_400_BAD_REQUEST)

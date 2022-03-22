from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import EmailMessage
from rest_framework.response import Response
from rest_framework import status
from account.models import User
from datetime import timedelta
from django.utils.timezone import now
from django.utils.crypto import get_random_string
import random

def rand_str(length=10, type="lower_hex"):
    if type == "str":
        return get_random_string(length, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
    elif type == "lower_str":
        return get_random_string(length, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789")
    elif type == "lower_hex":
        return random.choice("123456789abcdef") + get_random_string(length - 1, allowed_chars="0123456789abcdef")
    else:
        return random.choice("123456789") + get_random_string(length - 1, allowed_chars="0123456789")

class ApplyResetPasswordView(APIView):
    permission_classes = [AllowAny]
    # 11-00
    def post(self, request):
        email = request.data.get('email', '')
        try:
            user = User.objects.get(email=email)
        except:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        if user.reset_password_token_expire_time and 0 < int((user.reset_password_token_expire_time - now()).total_seconds()) < 5 * 60:
            return Response({'error': 'You can only reset password once per 5 minutes'}, status=status.HTTP_401_UNAUTHORIZED) # , status=status.HTTP_200_OK)self.error("You can only reset password once per 5 minutes")
        user.reset_password_token = rand_str()
        user.reset_password_token_expire_time = now() + timedelta(minutes=5)
        user.save()
        email_body = f"{user.username}님 안녕하세요.\n비밀번호 리셋 인증 번호입니다.\n{user.reset_password_token}\n해당 Key를 비밀번호 리셋 페이지에서 입력해주세요."
        EmailMessage(subject="Reset your passsword", body=email_body, to=[user.email], from_email="seggle.sejong@gmail.com").send()
        return Response({'success': 'We have sent you a mail to reset your password'}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    # 11-02
    def post(self, request):
        data = request.data
        user = User.objects.get(reset_password_token=data["token"])

        if data["password1"] == data["password2"]:
            user.set_password(data["password1"])
            user.reset_password_token = None
            user.save()
            return Response({'success': "password reset done"}, status=status.HTTP_200_OK)
        else:
            return Response({'error': "password1, password2 not same"}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordTokenView(APIView):
    permission_classes = [AllowAny]
    # 11-01
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(reset_password_token=data["token"])
        except:
            return Response({'error': "Token does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if user.reset_password_token_expire_time < now():
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'success': "token valid"}, status=status.HTTP_200_OK)


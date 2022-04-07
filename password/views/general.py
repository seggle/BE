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


class ApplyResetPasswordAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email', '')
        # if User.objects.filter(email=email).exists():
        try:
            user = User.objects.get(email=email)
        except:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        if user.reset_password_token_expire_time and 0 < int((user.reset_password_token_expire_time - now()).total_seconds()) < 5 * 60:
            return Response({'error': 'You can only reset password once per 5 minutes'}, status=status.HTTP_401_UNAUTHORIZED) # , status=status.HTTP_200_OK)self.error("You can only reset password once per 5 minutes")
        user.reset_password_token = rand_str()
        user.reset_password_token_expire_time = now() + timedelta(minutes=5)
        user.save()
        email_body = f"{user.username}님 비밀번호 리셋 인증 번호입니다.\n{user.reset_password_token}\n까먹지마세요"
        EmailMessage(subject="Reset your passsword", body=email_body, to=[user.email], from_email="seggle.sejong@gmail.com").send()
        return Response({'success': 'We have sent you a mail to reset your password'}, status=status.HTTP_200_OK)
        # return Response({'error': 'user email does not exist'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        # print(data)
        # try:
        user = User.objects.get(reset_password_token=data["token"])
        # except:
            # return Response({'error': "Token does not exist"}, status=status.HTTP_400_BAD_REQUEST) # self.error("Token does not exist")
        # if user.reset_password_token_expire_time < now():
        #     return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST) #self.error("Token has expired")

        if data["password1"] == data["password2"]:
            user.set_password(data["password1"])
            user.reset_password_token = None
            user.save()
            return Response({'success': "password reset done"}, status=status.HTTP_200_OK)
        else:
            return Response({'error': "password1, password2 not same"}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordToken(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(reset_password_token=data["token"])
        except:
            return Response({'error': "인증코드가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)# self.error("Token does not exist")
        if user.reset_password_token_expire_time < now():
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'success': "token valid"}, status=status.HTTP_200_OK)


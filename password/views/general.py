from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.response import Response
from django.urls import reverse
from rest_framework import status
from account.models import User
from ..serializers import ApplyResetPasswordSerializer
import os
from django.http import HttpResponsePermanentRedirect











from datetime import timedelta
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
import random

def rand_str(length=10, type="lower_hex"):
    """
    生成指定长度的随机字符串或者数字, 可以用于密钥等安全场景
    :param length: 字符串或者数字的长度
    :param type: str 代表随机字符串，num 代表随机数字
    :return: 字符串
    """
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
    # @validate_serializer(ApplyResetPasswordSerializer)
    def post(self, request):
        email = request.data.get('email', '')
        if User.objects.filter(email=email).exists():
        # if request.user.is_authenticated:
        #     return self.error("You have already logged in, are you kidding me? ")
        # data = request.data
            try:
                # user = User.objects.get(email__iexact=data["email"])
                user = User.objects.get(email=email)
            except: #User.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            if user.reset_password_token_expire_time and 0 < int((user.reset_password_token_expire_time - now()).total_seconds()) < 5 * 60:
                return Response({'error': 'You can only reset password once per 5 minutes'}, status=status.HTTP_400_BAD_REQUEST) # , status=status.HTTP_200_OK)self.error("You can only reset password once per 5 minutes")
            user.reset_password_token = rand_str()
            user.reset_password_token_expire_time = now() + timedelta(minutes=5)
            user.save()
            # render_data = {
            #     "username": user.username,
            #     "website_name": SysOptions.website_name,
            #     "link": f"{SysOptions.website_base_url}/reset-password/{user.reset_password_token}"
            # }
            email_body = f"{user.username}님 비밀번호 리셋 인증 번호입니다.\n{user.reset_password_token}\n까먹지마세요"
            # email_html = render_to_string("reset_password_email.html", render_data)
            # send_email_async.send(from_name=SysOptions.website_name_shortcut,
            #                       to_email=user.email,
            #                       to_name=user.username,
            #                       subject="Reset your password",
            #                       content=email_html)
            EmailMessage(subject="Reset your passsword", body=email_body, to=[user.email], from_email="seggle.sejong@gmail.com").send()
            return Response({'success': 'We have sent you a mail to reset your password'}, status=status.HTTP_200_OK)
        return Response({'error': 'user email does not exist'}, status=status.HTTP_400_BAD_REQUEST)




class ResetPasswordAPI(APIView):
    permission_classes = [AllowAny]
    # @validate_serializer(ResetPasswordSerializer)
    def post(self, request):
        data = request.data
        print(data)
        try:
            user = User.objects.get(reset_password_token=data["token"])
        except: # User.DoesNotExist:
            return Response({'error': "Token does not exist"}, status=status.HTTP_400_BAD_REQUEST) # self.error("Token does not exist")
        if user.reset_password_token_expire_time < now():
            return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST) #self.error("Token has expired")
        user.reset_password_token = None
        # user.two_factor_auth = False
        # user.set_password(data["password"])



        if data["password1"] == data["password2"]:
            user.set_password(data["password1"])
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
        except: # User.DoesNotExist:
            return Response({'error': "Token does not exist"}, status=status.HTTP_400_BAD_REQUEST)# self.error("Token does not exist")
        if user.reset_password_token_expire_time < now():
            return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': "token valid"}, status=status.HTTP_200_OK)















































# class CustomRedirect(HttpResponsePermanentRedirect):

#     allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']
# class Test(APIView):
#     serializer_class = ResetPasswordEmailRequestSerializer
#     permission_classes = [AllowAny]
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         # EmailMessage(subject="SUBSUB", body="testestestestestestestestes", to=["seggle.sejong@gmail.com"], from_email="seggle.sejong@gmail.com").send()
#         email = request.data.get('email', '')

#         if User.objects.filter(email=email).exists():
#             user = User.objects.get(email=email)
#             uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
#             token = PasswordResetTokenGenerator().make_token(user)
#             current_site = get_current_site(request=request).domain
#             relativeLink = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
#             redirect_url = request.data.get('redirect_url', '')
#             absurl = 'http://'+current_site + relativeLink
#             email_body = 'Hello, \n Use link below to reset your password  \n' + \
#                 absurl +"?redirect_url="+redirect_url
#             print('user.email', user.email)
#             data = {'email_body': email_body, 'to_email': user.email,
#                     'email_subject': 'Reset your passsword'}
#             print('333333')
#             EmailMessage(subject="Reset your passsword", body=email_body, to=[user.email], from_email="seggle.sejong@gmail.com").send()
#             # send_email2(data)
#             print('44444')
#         else:
#             print('User filter else print')
#         return Response({'success': 'W222e have sent you a link to reset your password'}, status=status.HTTP_200_OK)

# class PasswordTokenCheckAPI(APIView):
#     serializer_class = SetNewPasswordSerializer

#     def get(self, request, uidb64, token):

#         redirect_url = request.GET.get('redirect_url')

#         try:
#             id = smart_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(id=id)
#             print('token', token)
#             print('user', user)
#             # if not PasswordResetTokenGenerator().check_token(user, token):
#             #     if len(redirect_url) > 3:
#             #         return CustomRedirect(redirect_url+'?token_valid=False')
#             #     else:
#             #         return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

#             if redirect_url and len(redirect_url) > 3:
#                 return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
#             else:
#                 return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

#         except DjangoUnicodeDecodeError as identifier:
#             try:
#                 if not PasswordResetTokenGenerator().check_token(user):
#                     return CustomRedirect(redirect_url+'?token_valid=False')
                    
#             except UnboundLocalError as e:
#                 return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)



# class SetNewPasswordAPIView(APIView):
#     serializer_class = SetNewPasswordSerializer

#     def patch(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)
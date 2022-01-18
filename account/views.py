from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import User
from . import serializers
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class UserRegister(APIView):
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

class UserLoginAPI(APIView):
    #@validate_serializer(UserLoginSerializer)
    def post(self, request):
        """
        user login api
        """
        data = request.data
        # 인증

class UserLogoutAPI(APIView):
    """
    user logout api
    """
    def get(self, request):
        auth.logout(request)
        return self.success()

class UserChangePasswordAPI(APIView):
    #@validate_serializer(UserChangePasswordSerializer)
    @login_required
    def post(self, request):
        """
        user change password api
        """
        data = request.data
        user_id = request.data.user_id
        user = auth.authenticate(id=user_id, password=data["user_password"])
        if user:
            # 인증 확인 이후 코드 진행
            user.set_password(data["new_password"])
            user.save()
            return self.success("Succeeded")
        else:
            return self.error("Invalid old password")
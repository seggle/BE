from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import User

# Create your views here.
class UserRegister(APIView):
    def post(self,request):
        data = request.data

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
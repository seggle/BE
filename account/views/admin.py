from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import User
from .. import serializers
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class ListUsersAPI(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, format = None):
        users = User.objects.all()
        serializer = serializers.UserInfoSerializer(users,many = True)
        return Response(serializer.data)

class AdminUserModifyAPI(APIView):
    # permission_classes = [IsAdminUser]
    permission_classes = (IsAdminUser, )

    def put(self,request,user_id,format = None):
        data = request.data
        user = User.objects.get(username=user_id)
        user.email = data["user_email"]
        user.username = data["user_id"]
        user.privilege = data["user_privilege"]
        user.name = data["user_name"]
        user.save(force_update=True)
        return Response({True})
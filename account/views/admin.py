from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import User
from .. import serializers
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class ListUsersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, format = None):
        users = User.objects.all()
        serializer = serializers.UserInfoSerializer(users,many = True)
        return Response(serializer.data)

class AdminUserModifyView(APIView):
    # permission_classes = [IsAdminUser]

    def put(self, request, username, format = None):
        data = request.data
        user = User.objects.get(username=username)
        user.email = data["email"]
        user.username = data["username"]
        user.privilege = data["privilege"]
        user.name = data["name"]
        user.save(force_update=True)
        return Response({True})
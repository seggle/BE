from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.pagination import PageNumberPagination #pagination
from utils.pagination import PaginationHandlerMixin #pagination
from ..models import User
from .. import serializers

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class ListUsersView(APIView, PaginationHandlerMixin):
    permission_classes = [IsAdminUser]

    pagination_class = BasicPagination
    serializer_class = serializers.UserInfoSerializer

    # 00-00 유저 전체 조회
    def get(self, request, format = None):
        users = User.objects.exclude(is_active=False)

        # keyword - username
        keyword = request.GET.get('keyword', '')
        if keyword:
            users = users.filter(username__icontains=keyword)
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(users, many=True)
        # serializer = serializers.UserInfoSerializer(users, many = True)
        return Response(serializer.data)

class AdminUserInfoView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, username): # 존재하는 인스턴스인지 판단
        user = get_object_or_404(User, username = username)
        return user

    # 00-01 유저 정보 수정
    # privilege만 수정할 수 있음
    def put(self, request, username, format = None):
        user = self.get_object(username=username)
        data = request.data
        obj = {}
        obj["privilege"] = data["privilege"]
        serializer = serializers.UserModifySerializer(user, data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializers.UserInfoSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 00-01-02 유저 조회
    def get(self, request, username, format=None):
        user = self.get_object(username)
        try:
            serializer = serializers.UserInfoSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            raise Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

    # 00-01-03 회원탈퇴
    def delete(self, request, username):
        user = self.get_object(username)
        if user.is_active == False:
            return Response({'error': '이미 탈퇴 되었습니다.'})
        else:
            user.is_active = False
            user.save()
            return Response({'success': '회원 탈퇴 성공'}, status=status.HTTP_200_OK)
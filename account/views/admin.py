from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination #pagination
from utils.pagination import PaginationHandlerMixin #pagination
from ..models import User
from ..serializers import UserInfoSerializer, UserModifySerializer
from utils import permission
from utils.get_obj import *

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class ListUsersView(APIView, PaginationHandlerMixin):
    permission_classes = [permission.IsAdmin] # 어드민만 가능한것

    pagination_class = BasicPagination
    serializer_class = UserInfoSerializer

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
        return Response(serializer.data)

class AdminUserInfoView(APIView):

    # 0315
    # permission_classes = [IsAdminUser]

    # 00-01 유저 정보 수정
    # privilege만 수정할 수 있음
    def put(self, request, username):
        user = get_username(username=username)
        data = request.data
        obj = {
            "privilege": data["privilege"]
        }
        serializer = UserModifySerializer(user, data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(UserInfoSerializer(user).data) # 0315
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 00-01-02 유저 조회
    def get(self, request, username): # 0315
        user = get_username(username)
        try:
            serializer = UserInfoSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            raise Response(serializer.error, status=status.HTTP_400_BAD_REQUEST) # 0315

    # 00-01-03 회원탈퇴
    def delete(self, request, username):
        user = get_username(username)
        if user.is_active == False:
            return Response({'error': '이미 탈퇴 되었습니다.'}, status=status.HTTP_200_OK) # 0315
        else:
            user.is_active = False
            user.save()
            return Response({'success': '회원 탈퇴 성공'}, status=status.HTTP_200_OK)
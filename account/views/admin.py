from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from utils.get_obj import *
from utils.pagination import PaginationHandlerMixin #pagination
from ..models import User
from ..serializers import UserInfoSerializer, UserModifySerializer
from utils.permission import IsAdmin
class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class ListUsersView(APIView, PaginationHandlerMixin):
    permission_classes = [IsAdmin]

    pagination_class = BasicPagination

    # 00-00 유저 전체 조회
    def get(self, request, format = None):
        users = User.objects.exclude(is_active=False)
        users = users.order_by('-date_joined').order_by('-privilege')
        # keyword - username
        keyword = request.GET.get('keyword', '')
        if keyword:
            users = users.filter(username__icontains=keyword)
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.get_paginated_response(UserInfoSerializer(page, many=True).data)
        else:
            serializer = UserInfoSerializer(users, many=True)
        
        return Response(serializer.data)

class AdminUserInfoView(APIView):
    permission_classes = [IsAdmin]

    # 00-01 유저 정보 수정
    # privilege만 수정할 수 있음
    def put(self, request, username):
        user = get_username(username)
        data = request.data
        obj = {}
        obj["privilege"] = data["privilege"]
        serializer = UserModifySerializer(user, data=obj)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserInfoSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 00-01-02 유저 조회
    def get(self, request, username, format=None):
        user = get_username(username)
        try:
            serializer = UserInfoSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            raise Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 00-01-03 회원탈퇴
    def delete(self, request, username):
        user = get_username(username)
        if user.is_active == False:
            return Response({'error': '이미 탈퇴 되었습니다.'})
        else:
            user.is_active = False
            user.save()
            return Response({'success': '회원 탈퇴 성공'}, status=status.HTTP_200_OK)
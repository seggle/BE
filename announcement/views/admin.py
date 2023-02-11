from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination  # pagination
from utils.pagination import PaginationHandlerMixin, BasicPagination  # pagination
from ..models import Announcement, User
from ..serializers import AnnouncementSerializer, AnnouncementInfoSerializer, AnnouncementCheckSerializer
from utils.get_obj import *
from utils.permission import IsAdmin


class AnnouncementAdminView(APIView, PaginationHandlerMixin):
    permission_classes = [IsAdmin]

    # pagination
    pagination_class = BasicPagination

    # 00-07 공지 리스트 조회
    def get(self, request):
        announcements = Announcement.objects.all()

        keyword = request.GET.get('keyword', '')
        if keyword:
            announcements = announcements.filter(title__icontains=keyword) # 제목에 keyword가 포함되어 있는 레코드만 필터링

        announcements = announcements.order_by('-important', '-created_time')
        page = self.paginate_queryset(announcements)
        if page is not None:
            serializer = self.get_paginated_response(AnnouncementInfoSerializer(page, many=True).data)
        else:
            serializer = AnnouncementInfoSerializer(announcements, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 00-08 공지 생성
    def post(self, request):
        data = request.data
        announcement = {
            "title" : data['title'],
            "context" : data['context'],
            "visible" : data['visible'],
            "important" : data['important'],
            "created_user" : request.user
        }
        
        serializer = AnnouncementSerializer(data=announcement)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnnouncementDetailAdminView(APIView):
    permission_classes = [IsAdmin]

    # 00-12 announcement_id인 announcement 조회
    def get(self, request, announcement_id):
        announcement = get_announcement(announcement_id)
        serializer = AnnouncementSerializer(announcement)
        return Response(serializer.data)

    # 00-09 announcement_id인 announcement 수정
    def put(self, request, announcement_id):
        announcement = get_announcement(announcement_id)
        data = request.data
        obj = {
            "title" : data['title'],
            "context" : data['context'],
            "visible" : data['visible'],
            "important" : data['important'],
            "created_user" : announcement.created_user
        }
        serializer = AnnouncementSerializer(announcement, data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 00-10 announcement 삭제
    def delete(self, request, announcement_id):
        announcement = get_announcement(announcement_id)
        announcement.delete()
        return Response(status=status.HTTP_200_OK)

class AnnouncementCheckAdminView(APIView):
    permission_classes = [IsAdmin]

    # 00-11 announcement_id인 announcement 수정 (important, visible)
    def put(self, request, announcement_id):
        announcement = get_announcement(announcement_id)
        data = request.data
        obj = {}
        if "visible" in data:
            obj["visible"] = data.get("visible")
        if "important" in data:
            obj["important"] = data.get("important")
        serializer = AnnouncementCheckSerializer(announcement, data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
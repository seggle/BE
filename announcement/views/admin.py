from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination #pagination
from utils.pagination import PaginationHandlerMixin #pagination
from ..models import Announcement, User
from ..serializers import AnnouncementSerializer, AnnouncementInfoSerializer, AnnouncementCheckSerializer
from utils import permission
from utils.get_obj import *
from utils.message import *

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class AnnouncementAdminView(APIView, PaginationHandlerMixin):
    permission_classes = [permission.IsAdmin] # 어드민만 가능한것

    # pagination
    pagination_class = BasicPagination

    # 00-07 공지 리스트 조회
    def get(self, request):
        announcements = Announcement.objects.all().order_by("-created_time")
        keyword = request.GET.get('keyword', '')
        if keyword:
            announcements = announcements.filter(title__icontains=keyword) # 제목에 keyword가 포함되어 있는 레코드만 필터링
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
            "title": data["title"],
            "context": data["context"],
            "visible": data["visible"],
            "important": data["important"],
            "created_user": request.user
        }
        serializer = AnnouncementSerializer(data=announcement)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnnouncementDetailAdminView(APIView):
    permission_classes = [permission.IsAdmin] # 어드민만 가능한것

    # 00-12 announcement_id인 announcement 조회
    def get(self, request, announcement_id):
        announcement = get_announcement(announcement_id)
        serializer = AnnouncementSerializer(announcement)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 00-09 announcement_id인 announcement 수정
    def put(self, request, announcement_id):
        announcement = get_announcement(announcement_id)
        data = request.data
        obj = {
            "title": data["title"],
            "context": data["context"],
            "visible": data["visible"],
            "important": data["important"],
            "creted_user": announcement.created_user
        }
        serializer = AnnouncementSerializer(announcement, data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data) # 0315
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 00-10 announcement 삭제
    def delete(self, request, pk):
        announcement = get_announcement(pk)
        announcement.delete()
        return Response(msg_success, status=status.HTTP_204_NO_CONTENT)

class AnnouncementCheckAdminView(APIView):
    permission_classes = [permission.IsAdmin] # 어드민만 가능한것

    # 00-11 announcement_id인 announcement 수정 (important, visible)
    def put(self, request, pk):
        announcement = get_announcement(pk)
        data = request.data
        obj = {
            "visible": data["visible"],
            "important": data["important"],
        }
        serializer = AnnouncementCheckSerializer(announcement, data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
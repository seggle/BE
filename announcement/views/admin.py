from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination #pagination
from utils.pagination import PaginationHandlerMixin #pagination
from ..models import Announcement, User
from ..serializers import AnnouncementSerializer, AnnouncementInfoSerializer, AnnouncementCheckSerializer

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class AnnouncementAdminView(APIView, PaginationHandlerMixin):
    permission_classes = [IsAdminUser] # 0315

    # pagination
    pagination_class = BasicPagination
    serializer_class = AnnouncementInfoSerializer

    # 00-07 공지 리스트 조회
    def get(self, request):
        announcements = Announcement.objects.all()

        keyword = request.GET.get('keyword', '')
        if keyword:
            announcements = announcements.filter(title__icontains=keyword) # 제목에 keyword가 포함되어 있는 레코드만 필터링

        # serializer = serializers.AnnouncementInfoSerializer(announcements, many=True)
        page = self.paginate_queryset(announcements)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(announcements, many=True)
        # return Response(serializer.data)
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
    permission_classes = [IsAdminUser] # 0315

    def get_object(self, pk): # 존재하는 인스턴스인지 판단 # 0315
        announcement = get_object_or_404(Announcement, pk = pk)
        return announcement

    # 00-12 announcement_id인 announcement 조회
    def get(self, request, pk):
        announcement = self.get_object(pk)
        serializer = AnnouncementSerializer(announcement)
        return Response(serializer.data) # 0315

    # 00-09 announcement_id인 announcement 수정
    def put(self, request, pk):
        announcement = self.get_object(pk)
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
        announcement = self.get_object(pk)
        announcement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) # 0315

class AnnouncementCheckAdminView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk): # 존재하는 인스턴스인지 판단
        announcement = get_object_or_404(Announcement, pk = pk)
        return announcement

    # 00-11 announcement_id인 announcement 수정 (important, visible)
    def put(self, request, pk):
        announcement = self.get_object(pk)
        data = request.data
        obj = {
            "visible": data["visible"],
            "important": data["important"],
        }
        serializer = AnnouncementCheckSerializer(announcement, data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data) # 0315
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
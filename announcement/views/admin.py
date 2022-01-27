from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import get_object_or_404
from ..models import Announcement, User
from .. import serializers

class AnnouncementAdminAPI(APIView):
    permission_classes = [IsAdminUser]

    # 00-07 공지 리스트 조회
    def get(self, request):
        announcements = Announcement.objects.all()
        serializer = serializers.AnnouncementInfoSerializer(announcements, many=True)
        return Response(serializer.data)

    # 00-08 공지 생성
    def post(self, request):
        data = request.data
        announcement = {}
        announcement["title"] = data["announcement_title"]
        announcement["context"] = data["announcement_context"]
        announcement["visible"] = data["announcement_visible"]
        announcement["important"] = data["announcement_important"]
        serializer = serializers.AnnouncementSerializer(data=announcement)
        if serializer.is_valid():
            serializer.save(created_user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnnouncementDetailAdminAPI(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk): # 존재하는 인스턴스인지 판단
        announcement = get_object_or_404(Announcement, pk = pk)
        return announcement

    # 04-02 announcement_id인 announcement 조회
    def get(self, request, pk):
        announcement = self.get_object(pk)
        serializer = serializers.AnnouncementSerializer(announcement)
        return Response(serializer.data)

    # 00-09 announcement_id인 announcement 수정
    def put(self, request, pk):
        announcement = self.get_object(pk)
        data = request.data
        obj = {}
        obj["title"] = data["announcement_title"]
        obj["context"] = data["announcement_context"]
        obj["visible"] = data["announcement_visible"]
        obj["important"] = data["announcement_important"]
        serializer = serializers.AnnouncementSerializer(announcement, data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 00-10 announcement 삭제
    def delete(self, request, pk):
        announcement = self.get_object(pk)
        announcement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AnnouncementCheckAdminAPI(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk): # 존재하는 인스턴스인지 판단
        announcement = get_object_or_404(Announcement, pk = pk)
        return announcement

    # 00-11 announcement_id인 announcement 수정 (important, visible)
    def put(self, request, pk):
        announcement = self.get_object(pk)
        data = request.data
        obj = {}
        obj["visible"] = data["announcement_visible"]
        obj["important"] = data["announcement_important"]
        serializer = serializers.AnnouncementCheckSerializer(announcement, data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status
from django.http import Http404
from ..models import Announcement
from ..serializers import (
    AnnouncementSerializer,
    CreateAnnouncementSerializer,
    EditAnnouncementSerializer
)
from announcement import serializers

class AnnouncementAPI(APIView):
    def get(self, request):
        announcements = Announcement.objects

class AnnouncementAdminAPI(APIView):
    def post(self, request): # 공지 생성
        data = request.data
        announcement = Announcement.objects.create(title=data["announcement_title"],
                                                    context=data["announcement_context"],
                                                    created_user=data["announcement_created_user"],
                                                    visible=data["announcement_visible"],
                                                    important=data["announcement_important"])
        return self.success(AnnouncementSerializer(announcement).data)

    def get(self, request):
        page = request.GET.get("page")
        announcements = Announcement.objects.all().order_by("-created_time")

class AnnouncementDetailAPI(APIView):
    def get_object(self, pk): # 존재하는 인스턴스인지 판단
        announcement = get_object_or_404(Announcement, pk = pk)
        return announcement

    def get(self, request, pk):
        announcement = self.get_object(pk)
        serializer = AnnouncementSerializer(announcement)
        return Response(serializer.data)

    def put(self, request, pk):
        announcement = self.get_object(pk)
        serializer = AnnouncementSerializer(announcement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status
from django.http import Http404
from ..models import Announcement
from .. import serializers


class AnnouncementAPI(APIView):
    # 04-01 공지 리스트 전체 조회
    def get(self, request):
        announcements = Announcement.objects.all()
        serializer = serializers.AnnouncementInfoSerializer(announcements, many=True)
        return Response(serializer.data)


class AnnouncementDetailAPI(APIView):

    def get_object(self, pk): # 존재하는 인스턴스인지 판단
        announcement = get_object_or_404(Announcement, pk = pk)
        return announcement

    # 04-02 announcement_id인 announcement 조회
    def get(self, request, pk):
        announcement = self.get_object(pk)
        serializer = serializers.AnnouncementSerializer(announcement)
        return Response(serializer.data)
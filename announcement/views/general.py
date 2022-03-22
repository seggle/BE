from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status
from django.http import Http404
from rest_framework.pagination import PageNumberPagination #pagination
from utils.pagination import PaginationHandlerMixin #pagination
from ..models import Announcement
from ..serializers import AnnouncementInfoSerializer, AnnouncementSerializer
from utils.get_obj import *

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class AnnouncementView(APIView, PaginationHandlerMixin):
    # pagination
    pagination_class = BasicPagination

    # 04-01 공지 리스트 전체 조회
    def get(self, request):
        announcements = Announcement.objects.exclude(visible=False)
        keyword = request.GET.get('keyword', '')
        if keyword:
            announcements = announcements.filter(title__icontains=keyword)
        page = self.paginate_queryset(announcements)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data) # 0315
        else:
            serializer = AnnouncementInfoSerializer(announcements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AnnouncementDetailView(APIView):

    # 04-02 announcement_id인 announcement 조회
    def get(self, request, announcement_id):
        announcement = get_announcement(announcement_id)
        serializer = AnnouncementSerializer(announcement)
        return Response(serializer.data) # 0315
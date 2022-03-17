from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status
from django.http import Http404
from rest_framework.pagination import PageNumberPagination #pagination
from utils.pagination import PaginationHandlerMixin #pagination
from ..models import Announcement
from ..serializers import AnnouncementInfoSerializer, AnnouncementSerializer

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class AnnouncementView(APIView, PaginationHandlerMixin):
    # pagination
    pagination_class = BasicPagination
    serializer_class = AnnouncementInfoSerializer

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
            serializer = self.serializer_class(announcements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AnnouncementDetailView(APIView):
    def get_object(self, pk): # 존재하는 인스턴스인지 판단
        announcement = get_object_or_404(Announcement, pk = pk)
        return announcement

    # 04-02 announcement_id인 announcement 조회
    def get(self, request, pk):
        announcement = self.get_object(pk)
        serializer = AnnouncementSerializer(announcement)
        return Response(serializer.data) # 0315
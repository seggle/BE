from multiprocessing import context
from pickle import TRUE
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import status
from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination #pagination
from utils.pagination import PaginationHandlerMixin #pagination
from ..models import Faq
from .. import serializers

# Create your views here.

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class FaqView(APIView, PaginationHandlerMixin):
    # pagination
    pagination_class = BasicPagination
    serializer_class = serializers.FaqSerializer

    def get_object(self, faq_id):
        faq = generics.get_object_or_404(Faq, id = faq_id)
        return faq

    def get(self, request):
        faq_list = Faq.objects.exclude(visible=False)
        page = self.paginate_queryset(faq_list)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(faq_list, many=True)
        
        faq_list_serializer = serializers.FaqSerializer(faq_list, many=True)
        #return Response(faq_list_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)

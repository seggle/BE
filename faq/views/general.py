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
from ..models import Faq
from ..serializers import FaqSerializer
from utils.get_obj import *

# Create your views here.

class FaqView(APIView):

    def get(self, request):
        faq_list = Faq.objects.exclude(visible=False)
        faq_list_serializer = FaqSerializer(faq_list, many=True)
        return Response(faq_list_serializer.data, status=status.HTTP_200_OK)

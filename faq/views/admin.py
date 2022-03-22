from multiprocessing import context
from pickle import TRUE
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import status
from django.http import JsonResponse
from ..models import Faq
from ..serializers import FaqSerializer, FaqPatchSerializer
from utils import permission
from utils.get_obj import *
from utils.message import *

# Create your views here.

class FaqAdminView(APIView):
    permission_classes = [permission.IsAdmin] # 어드민만 가능한것

    # 00
    def post(self,request):
        data = request.data
        data["created_user"] = request.user
        serializer = FaqSerializer(data=data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 00-03-00
    def get(self, request, faq_id):
        faq = get_faq(faq_id)
        serializer = FaqSerializer(faq)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 00-05
    def patch(self, request, faq_id):
        faq = get_faq(faq_id)
        data = request.data
        if faq.created_user == request.user:
            serializer = FaqPatchSerializer(faq, data=data) #Request의 data를 UserSerializer로 변환
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, faq_id):
        faq = get_faq(faq_id)
        if kwargs.get('faq_id') is None:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)
        else:
            faq_id = kwargs.get('faq_id')
            faq = get_faq(faq_id)

            user = Faq.objects.get(id=faq_id)
            if user.created_user == request.user:
                user.delete()
                return Response(msg_success, status=status.HTTP_200_OK)
            else:
                return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)

class FaqCheckAdminView(APIView):
    permission_classes = [permission.IsAdmin] # 어드민만 가능한것

    def post(self,request):
        data = request.data

        faq_id = data['id']
        faq = get_faq(faq_id)

        user = Faq.objects.get(id=faq_id)
        if user.created_user == request.user:
            user.visible = not user.visible
            user.save(force_update=True)
            serializer = FaqSerializer(Faq.objects.get(id=faq_id)) #Request의 data를 UserSerializer로 변환
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)

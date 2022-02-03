from multiprocessing import context
from pickle import TRUE
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import status
from django.http import JsonResponse
from ..models import Faq
from .. import serializers

# Create your views here.

class FaqAdminView(APIView):
    permission_classes = (IsAdminUser, )

    def get_object(self, faq_id):
        faq = generics.get_object_or_404(Faq, id = faq_id)
        return faq

    def post(self,request):
        data = request.data
        data["created_user"] = request.user
        serializer = serializers.FaqSerializer(data=data) #Request의 data를 UserSerializer로 변환

        if serializer.is_valid():
            serializer.save() #UserSerializer의 유효성 검사를 한 뒤 DB에 저장
            #return Response(serializer.data, status=status.HTTP_201_CREATED) #client에게 JSON response 전달
            return Response("Success", status=status.HTTP_201_CREATED) #client에게 JSON response 전달
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, **kwargs):

        if kwargs.get('faq_id') is None:
            faq_list = Faq.objects.values('id', 'question', 'created_time', 'last_modified', 'visible')
            faq_list_serializer = serializers.FaqAllGetSerializer(faq_list, many=True)
            #faq_list = Faq.objects.values('id', 'question', 'created_time', 'last_modified', 'visible')
            return Response(faq_list, status=status.HTTP_200_OK)
        else:
            faq_id = kwargs.get('faq_id')
            faq = self.get_object(faq_id)

            faq_list_serializer = serializers.FaqSerializer(Faq.objects.get(id=faq_id))
            return Response(faq_list_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, **kwargs):
        if kwargs.get('faq_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            faq_id = kwargs.get('faq_id')
            faq = self.get_object(faq_id)

            data = request.data
            user = Faq.objects.get(id=faq_id)
            if user.created_user == request.user:
                user.question = data["question"]
                user.answer = data["answer"]
                user.visible = data["visible"]
                user.save(force_update=True)
                return Response("Success", status=status.HTTP_200_OK)
            else:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        if kwargs.get('faq_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            faq_id = kwargs.get('faq_id')
            faq = self.get_object(faq_id)

            user = Faq.objects.get(id=faq_id)
            if user.created_user == request.user:
                user.delete()
                return Response("Success", status=status.HTTP_200_OK)
            else:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)

class FaqCheckAdminView(APIView):
    permission_classes = (IsAdminUser, )

    def get_object(self, faq_id):
        faq = generics.get_object_or_404(Faq, id = faq_id)
        return faq

    def post(self,request):
        data = request.data

        faq_id = data['id']
        faq = self.get_object(faq_id)

        user = Faq.objects.get(id=faq_id)
        if user.created_user == request.user:
            user.visible = not user.visible
            user.save(force_update=True)
            return Response("Success", status=status.HTTP_200_OK)
        else:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)

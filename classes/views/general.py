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
from ..models import Class, Class_user
from .. import serializers

# Create your views here.

class ClassView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    def post(self,request):
        data = request.data
        data._mutable = True
        data["created_user"] = request.user
        #print(data)
        serializer = serializers.ClassSerializer(data=data) #Request의 data를 UserSerializer로 변환

        if serializer.is_valid():
            serializer.save() #UserSerializer의 유효성 검사를 한 뒤 DB에 저장
            #return Response(serializer.data, status=status.HTTP_201_CREATED) #client에게 JSON response 전달
            return Response("Success", status=status.HTTP_201_CREATED) #client에게 JSON response 전달
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object(class_id)
            class_list_serializer = serializers.ClassGetSerializer(Class.objects.get(id=class_id))
            return Response(class_list_serializer.data, status=status.HTTP_200_OK)

class ClassUserView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    def post(self,request, class_id):
        #print(class_id)
        #class_id = request.query_params
        #print(class_id)
        classid = self.get_object(class_id)
        datas = request.data
        #print(datas)
        for data in datas:
            #user_name = data['username']
            is_check_user = Class_user.objects.filter(username = data['username']).filter(class_id = class_id).count()
            #is_check_user = Class_user.objects.filter(username = data['username']).annotate(Count(class_id))
            #is_check_user = Class.users.through.objects.filter(class_id = class_id).filter(username = data['username'])
            if is_check_user != 0:
                continue
            #print(data)
            #data._mutable = True
            data["is_show"] = True
            data["class_id"] = class_id
            #print(data)

            serializer = serializers.Class_user_Serializer(data=data) #Request의 data를 UserSerializer로 변환

            if serializer.is_valid():
                serializer.save() #UserSerializer의 유효성 검사를 한 뒤 DB에 저장
                #return Response(serializer.data, status=status.HTTP_201_CREATED) #client에게 JSON response 전달
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("Success", status=status.HTTP_201_CREATED) #client에게 JSON response 전달


    def get(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object(class_id)
            #print(Class.users.through.objects.values())
            data = Class.users.through.objects.filter(class_id = class_id)
            class_Userlist_serializer = serializers.Class_user_Get_Serializer(data, many=True)
            return Response(class_Userlist_serializer.data, status=status.HTTP_200_OK)

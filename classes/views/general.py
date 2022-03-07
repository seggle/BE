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
from account.models import User
from .. import serializers
#from utils.user_permission import user_perm, class_user_check

# Create your views here.

class ClassView(APIView):
    #permission_classes = [IsAdminUser]

    def get_object(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)

        return classid

    def post(self,request):

        # result = user_perm(request.user, 1)
        # if not result: return Response(status=status.HTTP_400_BAD_REQUEST)

        data = request.data

        #Create_Class = Class(name=data['name'], year=data['year'], semester=data['semester'], created_user=request.user)
        #Create_Class.save()

        data['created_user'] = request.user
        serializer = serializers.ClassSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            class_id = serializer.data['id']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        #print(Create_Class.id)
        # 교수 본인 추가
        data = {}
        data['username'] = request.user
        data['privilege'] = 2
        data["is_show"] = True
        data["class_id"] = class_id
        serializer = serializers.Class_user_Serializer(data=data) #Request의 data를 UserSerializer로 변환

        if serializer.is_valid():
            serializer.save() #UserSerializer의 유효성 검사를 한 뒤 DB에 저장
            # user = Class_user.objects.filter(username = request.user).filter(class_id = class_id)
            # class_user_add = Class.objects.get(id = class_id)
            # class_user_add.users.add(user[0])

            # serializer = serializers.ClassSerializer(class_user_add)
            return Response(serializer.data, status=status.HTTP_201_CREATED) #client에게 JSON response 전달
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object(class_id)
            class_list_serializer = serializers.ClassSerializer(Class.objects.get(id=class_id))
            return Response(class_list_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object(class_id)

            data = request.data
            user = Class.objects.get(id=class_id)
            if user.created_user == request.user:
                user.name = data["name"]
                user.year = data["year"]
                user.semester = data["semester"]
                user.save(force_update=True)
                class_list_serializer = serializers.ClassSerializer(user)
                return Response(class_list_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object(class_id)

            user = Class.objects.get(id=class_id)
            if user.created_user == request.user:
                user.delete()
                return Response("Success", status=status.HTTP_200_OK)
            else:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)


class ClassUserInfoView(APIView):
    #permission_classes = [IsAdminUser]

    def get_object(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    def get(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object(class_id)
            user = Class.objects.get(id=class_id)
            datas = user.users.all()
            #print(datas)
            class_Userlist_serializer = serializers.Class_user_Get_Serializer(datas, many=True)
            #return Response(data, status=status.HTTP_200_OK)
            return Response(class_Userlist_serializer.data, status=status.HTTP_200_OK)

class ClassStdView(APIView):
    #permission_classes = [IsAdminUser]

    def get_object(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    def post(self,request, class_id):
        classid = self.get_object(class_id)

        # 기존 std 삭제
        user = Class.objects.get(id=class_id)
        if user.created_user == request.user:
            user_list = user.users.all()
            for users in user_list:
                if users.privilege == 0:
                    user.users.remove(users.id)
                    users.delete()

        # std 추가
        user_does_not_exist = {}
        user_does_not_exist['does_not_exist'] = []
        user_does_not_exist['is_existed'] = []
        datas = request.data
        user_add = Class.objects.get(id=class_id)
        for data in datas:
            is_check_user = User.objects.filter(username = data['username']).count()
            is_check_class_user = Class_user.objects.filter(username = data['username']).filter(class_id = class_id).count()
            if is_check_user == 0:
                user_does_not_exist['does_not_exist'].append(data['username'])
                continue
            if is_check_class_user != 0:
                user_does_not_exist['is_existed'].append(data['username'])
                continue

            data["is_show"] = True
            data["privilege"] = 0
            data["class_id"] = class_id

            serializer = serializers.Class_user_Serializer(data=data)

            if serializer.is_valid():
                serializer.save()
                # user = Class_user.objects.filter(username = data['username']).filter(class_id = class_id)
                # user_add.users.add(user[0])
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 출력
        if (len(user_does_not_exist['does_not_exist']) == 0) and (len(user_does_not_exist['is_existed']) == 0):
            # users_datas = user_add.users.all()
            users_datas = Class_user.objects.all()
            class_Userlist_serializer = serializers.Class_user_Get_Serializer(users_datas, many=True)
            return Response(class_Userlist_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(user_does_not_exist, status=status.HTTP_201_CREATED)

class ClassTaView(APIView):
    #permission_classes = [IsAdminUser]

    def get_object(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    def post(self,request, class_id):
        classid = self.get_object(class_id)

        # 기존 ta 삭제
        user = Class.objects.get(id=class_id)
        if user.created_user == request.user:
            user_list = user.users.all()
            for users in user_list:
                if users.privilege == 1:
                    user.users.remove(users.id)
                    users.delete()

        # ta 추가
        user_does_not_exist = {}
        user_does_not_exist['does_not_exist'] = []
        user_does_not_exist['is_existed'] = []
        datas = request.data
        user_add = Class.objects.get(id=class_id)
        for data in datas:
            is_check_user = User.objects.filter(username = data['username']).count()
            is_check_class_user = Class_user.objects.filter(username = data['username']).filter(class_id = class_id).count()
            if is_check_user == 0:
                user_does_not_exist['does_not_exist'].append(data['username'])
                continue
            if is_check_class_user != 0:
                user_does_not_exist['is_existed'].append(data['username'])
                continue

            data["is_show"] = True
            data["privilege"] = 1
            data["class_id"] = class_id

            serializer = serializers.Class_user_Serializer(data=data)

            if serializer.is_valid():
                serializer.save()
                # user = Class_user.objects.filter(username = data['username']).filter(class_id = class_id)
                # user_add.users.add(user[0])
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 출력
        if (len(user_does_not_exist['does_not_exist']) == 0) and (len(user_does_not_exist['is_existed']) == 0):
            # users_datas = user_add.users.all()
            users_datas = Class_user.objects.all()
            class_Userlist_serializer = serializers.Class_user_Get_Serializer(users_datas, many=True)
            return Response(class_Userlist_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(user_does_not_exist, status=status.HTTP_201_CREATED)

# class ClassTaView(APIView):
#     #permission_classes = [IsAdminUser]

#     def get_object(self, class_id):
#         classid = generics.get_object_or_404(Class, id = class_id)
#         return classid

#     def post(self,request, class_id):
#         #print(class_id)
#         #class_id = request.query_params
#         #print(class_id)
#         classid = self.get_object(class_id)

#         #print(datas)
#         user = Class.objects.get(id=class_id)
#         if user.created_user == request.user:
#             user_list = user.users.all()
#             for users in user_list:
#                 print(users.privilege)
#                 users.delete()
#             user.users.clear()

#         user_do_not_exist = {}
#         user_do_not_exist['user_do_not_exist'] = []
#         # 교수 본인 추가
#         data = {}
#         data['username'] = request.user
#         data['privilege'] = 2
#         data["is_show"] = True
#         data["class_id"] = class_id
#         serializer = serializers.Class_user_Serializer(data=data) #Request의 data를 UserSerializer로 변환

#         if serializer.is_valid():
#             serializer.save() #UserSerializer의 유효성 검사를 한 뒤 DB에 저장
#             user = Class_user.objects.filter(username = request.user).filter(class_id = class_id)
#             user_add = Class.objects.get(id=class_id)
#             user_add.users.add(user[0])

#         # 학생 추가
#         datas = request.data
#         for data in datas:

#             is_check_user = User.objects.filter(username = data['username']).count()
#             is_check_classuser = Class_user.objects.filter(username = data['username']).filter(class_id = class_id).count()
#             #is_check_user = Class_user.objects.filter(username = data['username']).annotate(Count(class_id))
#             #is_check_user = Class.users.through.objects.filter(class_id = class_id).filter(username = data['username'])
#             if is_check_user == 0:
#                 #user_do_not_exit.append(data['username'])
#                 user_do_not_exist['user_do_not_exist'].append(data['username'])
#                 continue
#             if is_check_classuser != 0:
#                 continue
#             #print(data)
#             #data._mutable = True
#             data["is_show"] = True
#             data["class_id"] = class_id
#             #print(data)

#             serializer = serializers.Class_user_Serializer(data=data) #Request의 data를 UserSerializer로 변환

#             if serializer.is_valid():
#                 serializer.save() #UserSerializer의 유효성 검사를 한 뒤 DB에 저장
#                 user = Class_user.objects.filter(username = data['username']).filter(class_id = class_id)
#                 user_add = Class.objects.get(id=class_id)
#                 user_add.users.add(user[0])
#                 #return Response(serializer.data, status=status.HTTP_201_CREATED) #client에게 JSON response 전달
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#             #username = User.objects.get(username=data['username'])

#             #user_add.users
#             # user = Class_user(class_id=class_id, username=username, privilege=data['privilege'], is_show=True)
#             # user.save()
#             # user_add = Class.objects.get(id=class_id)
#             # user_add.users.add(user)
#         return Response(user_do_not_exist, status=status.HTTP_201_CREATED) #client에게 JSON response 전달
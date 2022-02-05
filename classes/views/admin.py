from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import status, generics
from ..models import Class, Class_user
from .. import serializers

class ClassInfoView(APIView):
    # def get_object(self, username): # 존재하는 인스턴스인지 판단
    #     user = get_object_or_404(User, username = username)
    #     return user
    def get_object(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    # 01-09 유저 Class 조회
    def get(self, request):
        class_name_list = []
        class_lists = Class_user.objects.filter(username=request.user)
        for class_list in class_lists:
            #print(class_list)
            class_add_is_show = {}
            class_add = {}

            class_list_serializer = serializers.ClassGetSerializer(class_list.class_id)
            class_add_is_show = class_list_serializer.data
            class_add_is_show["is_show"] = class_list.is_show
            class_add['id'] = class_add_is_show['id']
            class_add['name'] = class_add_is_show['name']
            class_add['semester'] = str(class_add_is_show['year']) + '-' + str(class_add_is_show['semester']) + '학기'
            class_add['is_show'] = class_add_is_show['is_show']
            class_name_list.append(class_add)
        return Response(class_name_list, status=status.HTTP_200_OK)
    
    def patch(self, request):
        #class_id = kwargs.get('class_id')
        datas = request.data
        for data in datas:
            classid = self.get_object(data['class_id'])
            class_user = Class_user.objects.filter(username=request.user).filter(class_id=data['class_id'])
            if class_user.count() == 0:
                continue
            user = class_user[0]
            user.is_show = not user.is_show
            user.save(force_update=True)
        return Response("Success", status=status.HTTP_200_OK)
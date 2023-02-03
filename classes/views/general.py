from pickle import TRUE

from django.http import QueryDict
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from ..models import ClassUser
from account.models import User
from ..serializers import ClassSerializer, ClassPatchSerializer, ClassUserSerializer, ClassUserGetSerializer
from utils.get_obj import *
from utils.message import *
from utils.permission import *
from utils.pagination import PaginationHandlerMixin, BasicPagination

# from utils.user_permission import user_perm, class_user_check

# Create your views here.


class ClassView(APIView):
    permission_classes = [IsProf | IsAdmin]

    # 05-01
    def post(self, request: Request) -> Response:

        data = request.data
        data._mutable = True

        data['created_user'] = request.user
        serializer = ClassSerializer(data=data)

        if serializer.is_valid():
            class_ = serializer.save()
            class_id = class_.id
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 교수 본인 추가
        data = {
            "username": request.user,
            "privilege": 2,
            "is_show": True,
            "class_id": class_id
        }

        serializer = ClassUserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # client에게 JSON response 전달
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClassDetailView(APIView):
    permission_classes = [ClassProfOrReadOnly]

    # 05-02
    def get(self, request: Request, class_id: int) -> Response:
        class_ = get_class(class_id)
        serializer = ClassSerializer(class_)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 05-03
    def patch(self, request: Request, class_id: int) -> Response:
        class_ = get_class(class_id)
        data = request.data

        if class_.created_user == request.user:
            serializer = ClassPatchSerializer(class_, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)

    # 05-04
    def delete(self, request: Request, class_id: int) -> Response:
        class_ = get_class(class_id)
        if class_.created_user == request.user:
            class_.is_deleted = True
            class_.save()
            return Response(msg_success, status=status.HTTP_200_OK)
        else:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)


class ClassStdView(APIView, PaginationHandlerMixin):
    permission_classes = [IsClassProfOrTA]
    pagination_class = BasicPagination

    # 05-05-01
    def get(self, request: Request, class_id: int) -> Response:
        datas = ClassUser.objects.filter(class_id=class_id).filter(privilege=0)

        page = self.paginate_queryset(datas)
        if page is not None:
            serializer = self.get_paginated_response(ClassUserGetSerializer(page, many=True).data)
        else:
            serializer = ClassUserGetSerializer(datas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # 05-06
    def post(self, request: Request, class_id: int) -> Response:

        class_ = get_class(class_id)
        # 기존 std 삭제
        if class_.created_user == request.user:
            classuser_list = ClassUser.objects.filter(class_id=class_id)
            for classuser in classuser_list:
                if classuser.privilege == 0:
                    classuser.delete()

        # std 추가
        user_does_not_exist = {
            "does_not_exist": [],
            "is_existed": []
        }
        datas = request.data.get('username')
        for username in datas:
            is_check_user = User.objects.filter(username=username).count()
            is_check_ClassUser = ClassUser.objects.filter(username=username).filter(class_id=class_id).count()
            if is_check_user == 0:
                user_does_not_exist['does_not_exist'].append(username)
                continue
            if is_check_ClassUser != 0:
                user_does_not_exist['is_existed'].append(username)
                continue

            data = {
                "username": username,
                "is_show": True,
                "privilege": 0,
                "class_id": class_id
            }
            serializer = ClassUserSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 출력
        if (len(user_does_not_exist.get('does_not_exist')) == 0) and (len(user_does_not_exist.get('is_existed')) == 0):
            return Response(msg_success, status=status.HTTP_201_CREATED)
        else:
            return Response(user_does_not_exist, status=status.HTTP_201_CREATED)


class ClassTaView(APIView, PaginationHandlerMixin):
    permission_classes = [IsClassProf]
    pagination_class = BasicPagination

    # 05-05-02
    def get(self, request: Request, class_id: int) -> Response:
        datas = ClassUser.objects.filter(class_id=class_id).filter(privilege=1)

        page = self.paginate_queryset(datas)
        if page is not None:
            serializer = self.get_paginated_response(ClassUserGetSerializer(page, many=True).data)
        else:
            serializer = ClassUserGetSerializer(datas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # 05-07
    def post(self, request: Request, class_id: int) -> Response:
        class_ = get_class(class_id)
        # 기존 ta 삭제
        if class_.created_user == request.user:
            classuser_list = ClassUser.objects.filter(class_id=class_id)
            for classuser in classuser_list:
                if classuser.privilege == 1:
                    classuser.delete()

        # ta 추가
        user_does_not_exist = {
            "does_not_exist": [],
            "is_existed": []
        }
        datas = request.data.get('username')
        for username in datas:
            is_check_user = User.objects.filter(username=username).count()
            is_check_ClassUser = ClassUser.objects.filter(username=username).filter(class_id=class_id).count()
            if is_check_user == 0:
                user_does_not_exist['does_not_exist'].append(username)
                continue
            if is_check_ClassUser != 0:
                user_does_not_exist['is_existed'].append(username)
                continue

            data = {
                "username": username,
                "is_show": True,
                "privilege": 1,
                "class_id": class_id
            }

            serializer = ClassUserSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 출력
        if (len(user_does_not_exist.get('does_not_exist')) == 0) and (len(user_does_not_exist.get('is_existed')) == 0):
            return Response(msg_success, status=status.HTTP_201_CREATED)
        else:
            return Response(user_does_not_exist, status=status.HTTP_201_CREATED)
